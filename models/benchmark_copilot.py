"""Compare the live local copilot with a one-vehicle nearest-ETA baseline."""

import argparse
import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from uuid import NAMESPACE_URL, uuid5

import httpx

from backend.copilot import plan_dispatch, unit_etas
from backend.report_extraction import LOCATIONS
from backend.routing import ManhattanRouter

CASES = (
    ("medical", "Bellevue Hospital", ("medical",), (
        "A person suddenly stopped breathing", "Someone has severe chest pain",
        "A visitor collapsed and is unresponsive", "An adult is choking", "A person is having a seizure",
    )),
    ("fire", "Union Square", ("fire",), (
        "Flames are visible in an empty shop", "A dumpster is burning and there are no injuries",
        "A fire started in an unattended kitchen", "A small electrical flame is spreading",
        "A vacant kiosk has caught fire",
    )),
    ("compound crash", "Fifth Avenue and 34th Street", ("fire", "medical"), (
        "Two cars collided and a person is trapped while smoke rises from an engine",
        "A crash left a driver pinned and smoke is coming from the hood",
        "A taxi hit a truck, one person cannot get out and there is smoke",
        "A collision left someone trapped and the engine is smoking",
        "Two vehicles crashed, a passenger is pinned and a fire is visible",
    )),
    ("roadblock", "Times Square", ("police",), (
        "A fallen pole blocks the road and nobody is injured", "A skip is blocking both lanes",
        "A tree fell across the street with no injuries", "Broken scaffolding closed the road",
        "A truck broke down, blocking the intersection, and no one is hurt",
    )),
    ("duplicate", "Bellevue Hospital", (), (
        "A person is having chest pain", "Someone collapsed and is unresponsive",
        "An adult is choking", "A person is having an allergic reaction", "A visitor is having a seizure",
    )),
    ("ambiguous", "", (), (
        "There is a fire near either Times Square or Bryant Park",
        "There was a crash, either Union Square or Columbus Circle",
        "A person is choking at an unknown location",
        "A truck blocks a road near Bellevue Hospital or Madison Square Park",
        "Someone is trapped after a collision and the caller cannot name a location",
    )),
)

FLEET = (
    ("medical", "Bellevue Hospital"), ("medical", "Madison Square Park"),
    ("fire", "Union Square"), ("fire", "Bryant Park"),
    ("police", "Times Square"), ("police", "Columbus Circle"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-url", default="http://127.0.0.1:8011")
    parser.add_argument("--graph", type=Path, default=Path("deploy/manhattan.graphml.gz"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    router = ManhattanRouter(args.graph)
    units = [{"unit_id": str(uuid5(NAMESPACE_URL, f"clearpath-fixture:{kind}:{station}")),
              "unit_type": kind, "station": station, "dispatch_id": None} for kind, station in FLEET]
    by_id = {row["unit_id"]: row["unit_type"] for row in units}
    rows = []

    with httpx.Client(timeout=10, trust_env=False) as client:
        for group, location, expected, reports in CASES:
            for index, fragment in enumerate(reports, 1):
                board = {"units": units, "incidents": []}
                if group == "duplicate":
                    lat, lon, _ = LOCATIONS[location]
                    board["incidents"] = [{"incident_id": "fixture-open-incident", "incident_type": "medical",
                                           "latitude": lat, "longitude": lon}]
                report = f"{fragment} near {location}." if location else fragment
                baseline_start = perf_counter()
                baseline = []
                if location:
                    lat, lon, _ = LOCATIONS[location]
                    destination = {"osm_node_id": router.nearest_node(lat, lon)}
                    ranked = unit_etas(router, destination, units, frozenset())
                    baseline = [ranked[0]["unit_type"]] if ranked else []
                baseline_ms = (perf_counter() - baseline_start) * 1000
                result = plan_dispatch(report, client, args.model_url, router, lambda: board)
                proposed = [by_id[unit_id] for unit_id in result.get("proposal", {}).get("recommended_unit_ids", [])]
                assistant_correct = sorted(proposed) == sorted(expected) and (
                    result["status"] == ("pending" if expected else "needs_clarification")
                )
                rows.append({"case": f"{group}-{index}", "expected_unit_types": expected,
                             "copilot_unit_types": proposed, "copilot_status": result["status"],
                             "copilot_correct": assistant_correct, "copilot_ms": result["elapsed_ms"],
                             "tools": len(result["trace"]), "model_tokens": result["model_tokens"],
                             "baseline_unit_types": baseline, "baseline_correct": sorted(baseline) == sorted(expected),
                             "baseline_ms": round(baseline_ms, 2)})

    summary = {"cases": len(rows), "copilot_correct": sum(row["copilot_correct"] for row in rows),
               "baseline_correct": sum(row["baseline_correct"] for row in rows),
               "copilot_mean_ms": round(mean(row["copilot_ms"] for row in rows), 2),
               "baseline_mean_ms": round(mean(row["baseline_ms"] for row in rows), 2),
               "mean_tool_calls": round(mean(row["tools"] for row in rows), 2)}
    if args.output:
        args.output.write_text(json.dumps({"summary": summary, "cases": rows}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
