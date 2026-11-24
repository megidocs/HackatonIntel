"""Rehearse and measure ClearPath on a disposable local simulator."""

import argparse
import asyncio
import gzip
import json
import os
import platform
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import mean
from time import perf_counter
from urllib.parse import urlsplit, urlunsplit

import httpx
import networkx as nx
from websockets.asyncio.client import connect

from .check_priority import run_scenario
from .mobile import mobile_snapshot
from .priority import PriorityCorridor
from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter
from .simulation import Simulation

worker_router: ManhattanRouter | None = None


def init_worker(graph_path):
    global worker_router
    worker_router = ManhattanRouter(graph_path)


def worker_route(pair):
    return worker_router.route(*pair)


def summary(values):
    sorted_values = sorted(values)
    rank = max(0, (95 * len(sorted_values) + 99) // 100 - 1)
    return {"n": len(values), "mean": round(mean(values), 2),
            "p95": round(sorted_values[rank], 2), "max": round(sorted_values[-1], 2)}


def ms_since(start):
    return (perf_counter() - start) * 1000


def measure_routes(simulation):
    router = simulation.router
    graph = router.graph
    component = sorted(max(nx.strongly_connected_components(graph), key=len))
    rng = random.Random(40)
    pairs = [tuple(rng.sample(component, 2)) for _ in range(100)]
    travel = []
    detours = []
    no_path = 0
    for pair in pairs:
        start = perf_counter()
        _, _, cost, _ = router.route(*pair)
        travel.append(ms_since(start))
        reference = nx.dijkstra_path_length(graph, *pair, weight="travel_time")
        assert abs(cost - reference) < 1e-7
        _, edges = router.path(*pair)
        blocked = simulation.roads[edges[len(edges) // 2]].segment
        def is_open(u, v, key):
            edge = simulation.roads.get((u, v, key))
            return edge is not None and edge.segment != blocked
        alternate = nx.subgraph_view(graph, filter_edge=is_open)
        start = perf_counter()
        try:
            _, new_edges = router.path(*pair, graph=alternate)
            assert all(simulation.roads[edge].segment != blocked for edge in new_edges)
        except nx.NetworkXNoPath:
            no_path += 1
        detours.append(ms_since(start))
    return {"a_star_ms": summary(travel), "single_road_closure_ms": summary(detours),
            "no_alternate_route": no_path}, pairs


async def heartbeat_benchmark(solve, pairs):
    loop = asyncio.get_running_loop()
    finished = asyncio.Event()
    delays = []

    async def pulse():
        while not finished.is_set():
            scheduled = loop.time() + .01
            await asyncio.sleep(.01)
            delays.append(max(0.0, loop.time() - scheduled) * 1000)

    heartbeat = asyncio.create_task(pulse())
    await asyncio.sleep(0)
    started = perf_counter()
    try:
        for pair in pairs:
            await solve(pair)
    finally:
        finished.set()
        await heartbeat
    return {"routes": len(pairs), "batch_ms": round(ms_since(started), 2),
            "heartbeat_delay_ms": summary(delays)}


async def compare_workers(router, graph_path, pairs):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=1, initializer=init_worker, initargs=(graph_path,)) as pool:
        await loop.run_in_executor(pool, worker_route, pairs[0])

        async def inline(pair):
            return router.route(*pair)

        async def thread(pair):
            return await asyncio.to_thread(router.route, *pair)

        async def process(pair):
            return await loop.run_in_executor(pool, worker_route, pair)

        return {
            "inline_event_loop": await heartbeat_benchmark(inline, pairs),
            "thread_offload": await heartbeat_benchmark(thread, pairs),
            "warm_separate_process": await heartbeat_benchmark(process, pairs),
        }


def geofence_and_payload(simulation):
    simulation.set_density(10_000)
    wave = PriorityCorridor()
    route = list(simulation.pending)
    sample = []
    for _ in range(40):
        started = perf_counter()
        wave.update(0, simulation.emergency, route, simulation.signals, simulation.traffic)
        sample.append(ms_since(started))
    result = {"vehicles": len(simulation.traffic), "matches": len(wave.alerted), "update_ms": summary(sample)}
    simulation.reset()
    simulation.set_density(500)
    snapshot = simulation.snapshot()
    messages = {
        "full_desktop_state": snapshot,
        "rescue_mobile": mobile_snapshot(simulation, "rescue", 1),
        "citizen_mobile": mobile_snapshot(simulation, "citizen", 1),
    }
    sizes = {}
    for name, message in messages.items():
        raw = json.dumps(message, separators=(",", ":")).encode()
        sizes[name] = {"json_bytes": len(raw), "gzip_bytes": len(gzip.compress(raw, compresslevel=3))}
    return result, sizes


async def until(feed, condition):
    async with asyncio.timeout(8):
        while True:
            state = json.loads(await feed.recv())
            if condition(state):
                return state


async def receive_rate(feed, count):
    timestamps = []
    for _ in range(count):
        await asyncio.wait_for(feed.recv(), 8)
        timestamps.append(perf_counter())
    intervals = [(after - before) * 1000 for before, after in zip(timestamps, timestamps[1:])]
    return {"updates_per_second": round((count - 1) / (timestamps[-1] - timestamps[0]), 2),
            "interval_ms": summary(intervals)}


async def probe(base, *, exercise=False):
    address = urlsplit(base)
    if exercise and (address.scheme != "http" or address.hostname not in {"127.0.0.1", "::1", "localhost"}):
        raise ValueError("Scenario changes require a disposable loopback simulator.")
    ws = urlunsplit(("wss" if address.scheme == "https" else "ws", address.netloc, "/simulation/mobile", "", ""))
    token = os.getenv("CLEARPATH_CONTROL_TOKEN", "")
    headers = {"X-ClearPath-Control-Token": token} if exercise and token else {}
    async with httpx.AsyncClient(base_url=base, timeout=12, headers=headers) as client:
        health = (await client.get("/health")).raise_for_status().json()
        http_samples = []
        for _ in range(10):
            started = perf_counter()
            (await client.get("/health")).raise_for_status()
            http_samples.append(ms_since(started))

        async def control(**payload):
            return (await client.post("/simulation/control", json=payload)).raise_for_status().json()

        async with (
            connect(ws + "?role=rescue", open_timeout=20) as rescue,
            connect(ws + "?role=citizen&vehicle=1", open_timeout=20) as citizen,
        ):
            route = await until(rescue, lambda state: bool(state["route"]))
            role = await until(citizen, lambda state: state["assigned"])
            assert "route" not in role and "position" not in role
            pong_ms = []
            for _ in range(10):
                started = perf_counter()
                await asyncio.wait_for(await rescue.ping(), 8)
                pong_ms.append(ms_since(started))
            result = {"release": health.get("release"), "initial_running": route["running"],
                      "http_health_rtt_ms": summary(http_samples), "websocket_ping_rtt_ms": summary(pong_ms),
                      "both_mobile_roles_received": True}
            if not exercise:
                return result

            try:
                baseline = await control(reset=True)
                assert baseline["priority_enabled"] and baseline["alerted_count"]
                await until(citizen, lambda state: state["alerted"])
                started = perf_counter()
                desktop = await control(priority=False)
                notification = await until(citizen, lambda state: not state["alerted"])
                assert desktop["running"] == notification["running"] is False
                assert desktop["alerted_count"] == 0
                result["paused_priority_change_to_citizen_ms"] = round(ms_since(started), 2)
                await control(priority=True)
                await until(citizen, lambda state: state["alerted"])
                await control(density=500, speed=1, running=True)
                await until(rescue, lambda state: state["running"])
                result["rescue_stream_500_vehicles"] = await receive_rate(rescue, 31)
                await control(running=False)
                await until(rescue, lambda state: not state["running"])
                result["play_pause_and_priority_synced"] = True
            finally:
                await control(reset=True)
            return result


async def measure(args):
    graph_path = Path(os.getenv("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH)).resolve()
    simulation = Simulation(ManhattanRouter(graph_path))
    routes, pairs = measure_routes(simulation)
    loop = await compare_workers(simulation.router, graph_path, pairs[:20])
    geofence, payload_sizes = geofence_and_payload(simulation)
    ordinary = run_scenario(simulation, False)
    priority = run_scenario(simulation, True)
    result = {
        "environment": {"system": platform.platform(), "python": platform.python_version(),
                        "graph_nodes": len(simulation.router.graph)},
        "routing": routes, "routing_execution": loop,
        "geofence": geofence, "payload_sizes": payload_sizes,
        "paired_arrival": {"normal_simulated_seconds": round(ordinary, 2),
                           "priority_simulated_seconds": round(priority, 2),
                           "reduction_percent": round((ordinary - priority) / ordinary * 100, 2)},
        "laptop": await probe(args.local, exercise=True),
    }
    if args.public:
        try:
            result["public_render"] = await probe(args.public)
        except (OSError, ValueError, AssertionError, httpx.HTTPError, asyncio.TimeoutError) as error:
            result["public_render"] = {"status": "incomplete", "error": type(error).__name__}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", default="http://127.0.0.1:8014", help="Disposable loopback simulator.")
    parser.add_argument("--public", help="Optional live URL for read-only HTTPS/WSS probes.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.public and urlsplit(args.public).scheme != "https":
        parser.error("--public must be HTTPS.")
    report = json.dumps(asyncio.run(measure(args)), indent=2)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
