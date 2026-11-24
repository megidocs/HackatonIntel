"""Record a synthetic dispatch lifecycle using real demo Supabase tokens."""

import argparse
import json
from pathlib import Path
from time import perf_counter, time
from urllib.parse import urlsplit
from uuid import uuid4

import httpx

from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter


def rehearsal(base: str, settings: dict[str, str], graph: Path) -> dict:
    address = urlsplit(base)
    if address.scheme != "http" or address.hostname not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("This rehearsal sends demo tokens only to a loopback FastAPI server.")
    project = settings["CLEARPATH_SUPABASE_URL"]
    if urlsplit(project).scheme != "https":
        raise ValueError("Supabase Auth must use HTTPS.")
    tokens = {}
    trace = []

    def record(label, response, started, expected=200):
        trace.append({"step": label, "status": response.status_code,
                      "duration_ms": round((perf_counter() - started) * 1000, 2)})
        if response.status_code != expected:
            raise RuntimeError(f"{label} returned HTTP {response.status_code}; expected {expected}.")
        return response.json()

    with httpx.Client(base_url=project, timeout=15,
                      headers={"apikey": settings["CLEARPATH_SUPABASE_PUBLISHABLE_KEY"]}) as auth:
        for role in ("dispatcher", "rescue", "citizen"):
            prefix = f"CLEARPATH_DEMO_{role.upper()}"
            started = perf_counter()
            response = auth.post("/auth/v1/token?grant_type=password", json={
                "email": settings[f"{prefix}_EMAIL"], "password": settings[f"{prefix}_PASSWORD"],
            })
            tokens[role] = record(f"{role} sign-in", response, started)["access_token"]

    router = ManhattanRouter(graph)
    node = next(node for node, data in router.graph.nodes(data=True) if "traffic_signals" in str(data.get("highway", "")))
    with httpx.Client(base_url=base, timeout=20, trust_env=False) as api:
        def call(label, method, path, role, payload=None, expected=200):
            started = perf_counter()
            response = api.request(method, f"/dispatch/{path}", json=payload,
                                   headers={"Authorization": f"Bearer {tokens[role]}"})
            return record(label, response, started, expected)

        for role in tokens:
            assert call(f"{role} role", "GET", "me", role)["role"] == role
        board = call("available units", "GET", "board", "dispatcher")
        unit = next(unit for unit in board["units"] if unit["unit_type"] == "medical" and unit["dispatch_id"] is None)
        report = call("dispatcher report draft", "POST", "report-suggestions", "dispatcher", {
            "report": "A person collapsed at Bellevue Hospital and is unresponsive.",
        })
        assert report["requires_review"]
        incident_id = str(uuid4())
        dispatch_id = str(uuid4())
        request_id = str(uuid4())
        call("open synthetic incident", "POST", "incidents", "dispatcher", {
            "incident_id": incident_id, "incident_type": "medical", "severity": 4,
            "lat": 40.7391, "lon": -73.9760,
        })
        assigned = False
        try:
            call("assign rescue unit", "POST", "assignments", "dispatcher", {
                "dispatch_id": dispatch_id, "incident_id": incident_id, "unit_id": unit["unit_id"],
            })
            assigned = True
            rescue_board = call("rescue sees assignment", "GET", "board", "rescue")
            assert any(unit["dispatch_id"] == dispatch_id for unit in rescue_board["units"])
            command = {"request_id": request_id, "dispatch_id": dispatch_id, "osm_node_id": node}
            call("citizen priority denied", "POST", "preemption", "citizen", command, 403)
            assert call("assigned rescue priority audited", "POST", "preemption", "rescue", command)["request_id"] == request_id
            sample = {"time_ms": int(time() * 1000), "nonce": str(uuid4()), "lat": 40.7391, "lon": -73.9760}
            call("citizen position accepted", "POST", "position", "citizen", sample)
            call("replayed position denied", "POST", "position", "citizen", sample, 409)
        finally:
            if assigned:
                call("rescue arrives", "POST", f"assignments/{dispatch_id}/arrive", "rescue")
            call("dispatcher closes incident", "POST", f"incidents/{incident_id}/close", "dispatcher")

        call("completed rescue priority denied", "POST", "preemption", "rescue",
             {**command, "request_id": str(uuid4())}, 403)
    return {"incident_id": incident_id, "dispatch_id": dispatch_id, "audit_request_id": request_id,
            "draft_requires_review": report["requires_review"], "trace": trace}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8003")
    parser.add_argument("--env-file", type=Path, default=Path(".env.dispatch.local"))
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings = dict(line.split("=", 1) for line in args.env_file.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#"))
    report = json.dumps(rehearsal(args.base, settings, args.graph), indent=2)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
