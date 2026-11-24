"""Check simulated signal clearance, route-based alerts, and a paired demo run."""

import argparse
import os
from pathlib import Path

from .check_routing import get_json
from .priority import CLEARANCE_SECONDS, PriorityCorridor
from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter
from .simulation import Simulation, Vehicle


def check_clearance(sim: Simulation) -> None:
    wave = PriorityCorridor()
    road = next(road for road in sim.roads.values() if road.key[1] in sim.signals)
    node = road.key[1]
    rescue = Vehicle(0, road, max(0.0, road.meters - 5))
    matching = Vehicle(1, road, road.meters)
    opposite_or_other = Vehicle(2, next(other for other in sim.roads.values() if other.key != road.key))
    wave.update(0, rescue, [], sim.signals, [matching, opposite_or_other])
    assert wave.alerted == {1}
    assert wave.can_enter(0, node, road.north_south) is False
    assert wave.can_enter(0, node, not road.north_south) is False
    assert wave.can_enter(CLEARANCE_SECONDS, node, road.north_south) is True
    assert wave.can_enter(CLEARANCE_SECONDS, node, not road.north_south) is False

    departure = CLEARANCE_SECONDS + 1
    wave.update(departure, None, [], sim.signals, [matching])
    assert not wave.line and not wave.alerted
    assert wave.can_enter(departure, node, road.north_south) is False
    wave.update(departure + CLEARANCE_SECONDS, None, [], sim.signals, [])
    assert wave.can_enter(departure + CLEARANCE_SECONDS, node, road.north_south) is None


def run_scenario(sim: Simulation, priority: bool) -> float:
    sim.reset()
    sim.set_priority(priority)
    sim.running = True
    saw_alerts = False
    saw_override = False
    for _ in range(3000):
        sim.advance(.1)
        saw_alerts |= bool(sim.priority.alerted)
        saw_override |= bool(sim.priority.signals)
        if sim.arrival_time is not None:
            assert saw_alerts == saw_override == priority
            return sim.arrival_time
    raise AssertionError("Rescue vehicle did not arrive in the demo scenario.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    sim = Simulation(ManhattanRouter(Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH))))
    check_clearance(sim)
    baseline = run_scenario(sim, False)
    preferred = run_scenario(sim, True)

    current = get_json(base, "/simulation/control", {"reset": True})
    try:
        assert current["priority_enabled"] and current["alerted_count"] > 0
        assert len(current["corridor"]) >= 2 and current["priority_signals"]
        disabled = get_json(base, "/simulation/control", {"priority": False})
        assert not disabled["priority_enabled"] and not disabled["corridor"]
        assert disabled["alerted_count"] == 0 and not disabled["priority_signals"]
    finally:
        get_json(base, "/simulation/control", {"reset": True})

    print("Verified clearance, conflicting red, normal-cycle restoration, and route-only alerts.")
    print(f"Same seeded demo: baseline {baseline:.1f}s, green wave {preferred:.1f}s "
          f"({(baseline - preferred) / baseline:.1%} less simulated time).")


if __name__ == "__main__":
    main()
