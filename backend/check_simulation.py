"""Verify the desktop simulator against a running local server."""

import argparse
import os
from pathlib import Path
from time import sleep

from .check_routing import get_json
from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter
from .simulation import SIGNAL_CYCLE, Simulation, Vehicle


def check_signal(simulation: Simulation) -> None:
    road = next(
        road for road in simulation.roads.values()
        if road.meters > 10
        and road.key[1] in simulation.signals
        and simulation.outgoing[road.key[1]]
    )
    car = Vehicle(1, road, road.meters - 4)
    simulation.traffic = [car]
    simulation.emergency = None
    simulation.running = True
    simulation.speed = 1
    offset = simulation.signals[road.key[1]]
    simulation.time = ((13 if road.north_south else 1) - offset) % SIGNAL_CYCLE
    for _ in range(6):
        simulation.advance(.1)
    assert car.road == road and car.meters <= road.meters - 2 and car.stopped
    simulation.time = ((3 if road.north_south else 13) - offset) % SIGNAL_CYCLE
    for _ in range(15):
        simulation.advance(.1)
        if car.road != road:
            break
    assert car.road != road


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    router = ManhattanRouter(Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH)))
    simulation = Simulation(router)
    segment = list(simulation.pending)[4].segment
    check_signal(simulation)

    baseline = get_json(base, "/simulation/control", {"reset": True})
    try:
        features = get_json(base, "/simulation/map")
        assert len(features["roads"]["features"]) > 4000
        assert len(features["signals"]["features"]) == baseline["signal_count"] > 1000
        assert baseline["route_status"] == "en_route"
        assert baseline["closures"] == [] and not baseline["running"]
        closed = get_json(base, f"/simulation/closure/{segment}", {})
        assert closed["closures"] == [segment]
        assert closed["route_status"] == "en_route" and closed["route"] != baseline["route"]
        assert closed["destination"] == baseline["destination"]
        restored = get_json(base, f"/simulation/closure/{segment}", {})
        assert restored["closures"] == [] and restored["route"] == baseline["route"]
        get_json(base, "/simulation/closure/-1", {}, 404)

        lon, lat = baseline["destination"]
        changed = get_json(base, "/simulation/point", {"target": "origin", "lat": lat, "lon": lon})
        assert changed["origin"] == baseline["destination"] and changed["route_status"] == "arrived"
        get_json(base, "/simulation/control", {"reset": True})

        rush = get_json(base, "/simulation/control", {"density": 500, "running": True})
        assert rush["running"] and len(rush["vehicles"]) == 501
        sleep(.5)
        moved = get_json(base, "/simulation/state")
        assert moved["time"] > rush["time"] and moved["vehicles"] != rush["vehicles"]
        paused = get_json(base, "/simulation/control", {"running": False})
        sleep(.25)
        assert get_json(base, "/simulation/state")["time"] == paused["time"]
    finally:
        get_json(base, "/simulation/control", {"reset": True})

    print(f"Map: {len(features['roads']['features']):,} road segments and {baseline['signal_count']:,} signal nodes.")
    print("Verified red-light stops, green-light passage, route changes and reopening,")
    print("endpoint selection, 500 moving civilian vehicles, playback, and pause.")


if __name__ == "__main__":
    main()
