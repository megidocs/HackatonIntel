"""Check the running API and compare A* costs with Dijkstra."""

import argparse
import json
import math
import os
import random
from pathlib import Path
from statistics import mean, quantiles
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import networkx as nx

from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter

BELLEVUE = {"lat": 40.7391, "lon": -73.9760}
TIMES_SQUARE = {"lat": 40.7580, "lon": -73.9855}


def get_json(base_url: str, path: str, payload: dict | None = None, status: int = 200) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(base_url + path, data=data, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(request, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        if response.status != status:
            raise AssertionError(f"{path} returned {response.status}, expected {status}.")
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    router = ManhattanRouter(Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH)))
    graph = router.graph
    health = get_json(base_url, "/health")
    assert health == {"status": "ok", "nodes": len(graph), "directed_edges": graph.number_of_edges()}

    demo = get_json(base_url, "/route", {"origin": BELLEVUE, "destination": TIMES_SQUARE})
    nodes = demo["nodes"]
    first, last = nodes[0], nodes[-1]
    assert first == router.nearest_node(**BELLEVUE)
    assert last == router.nearest_node(**TIMES_SQUARE)
    assert first != last and demo["distance_m"] > 0
    assert demo["geometry"]["type"] == "LineString"
    coordinates = demo["geometry"]["coordinates"]
    assert coordinates[0] == [graph.nodes[first]["x"], graph.nodes[first]["y"]]
    assert coordinates[-1] == [graph.nodes[last]["x"], graph.nodes[last]["y"]]
    assert all(graph.has_edge(u, v) for u, v in zip(nodes, nodes[1:]))
    expected = nx.dijkstra_path_length(graph, first, last, weight="travel_time")
    assert demo["travel_time_s"] == round(expected, 2)

    stationary = get_json(base_url, "/route", {"origin": BELLEVUE, "destination": BELLEVUE})
    assert stationary["nodes"] == [first]
    assert stationary["distance_m"] == stationary["travel_time_s"] == 0
    get_json(base_url, "/route", {"origin": {"lat": 91, "lon": 0}, "destination": BELLEVUE}, 422)
    get_json(base_url, "/route", {"origin": {"lat": 0, "lon": 0}, "destination": BELLEVUE}, 422)

    # Sample from a strongly connected component so each pair has a directed route.
    component = sorted(max(nx.strongly_connected_components(graph), key=len))
    randomizer = random.Random(40)
    elapsed_ms = []
    for _ in range(100):
        source, destination = randomizer.sample(component, 2)
        start = perf_counter()
        _, _, actual, _ = router.route(source, destination)
        elapsed_ms.append((perf_counter() - start) * 1000)
        expected = nx.dijkstra_path_length(graph, source, destination, weight="travel_time")
        assert math.isclose(actual, expected, rel_tol=1e-9), (source, destination, actual, expected)

    print(f"Graph: {health['nodes']:,} nodes, {health['directed_edges']:,} directed edges")
    print(f"Bellevue to Times Square: {demo['distance_m'] / 1000:.2f} km, "
          f"{demo['travel_time_s'] / 60:.1f} min modeled free-flow, {len(nodes)} nodes")
    print("HTTP health, demo route, same-point route, and both invalid-input cases passed.")
    print(f"A* matched Dijkstra for 100 pairs. Mean {mean(elapsed_ms):.1f} ms, "
          f"p95 {quantiles(elapsed_ms, n=100)[94]:.1f} ms (local routing, excludes HTTP).")


if __name__ == "__main__":
    main()
