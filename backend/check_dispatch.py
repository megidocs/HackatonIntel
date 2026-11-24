"""Exercise the dispatch API with disposable PostgreSQL and Redis services."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep, time
from uuid import uuid4

import httpx
import psycopg
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from .app import app
from .dispatch import DispatchServices


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="Admin DSN for an empty test database.")
    args = parser.parse_args()
    identities = {role: uuid4() for role in ("dispatcher", "rescue", "citizen", "outsider")}
    vehicle = uuid4()
    with psycopg.connect(args.owner, autocommit=True) as owner:
        if owner.execute("select to_regnamespace('clearpath')").fetchone()[0] is not None:
            parser.error("The verification requires an empty disposable test database.")
        owner.execute("create schema auth; create table auth.users (id uuid primary key)")
        for migration in sorted(Path("supabase/migrations").glob("*.sql")):
            owner.execute(migration.read_text(encoding="utf-8"))
        owner.execute("alter role clearpath_app login")
        for role, user in identities.items():
            owner.execute("insert into auth.users values (%s)", (user,))
            if role != "outsider":
                owner.execute("insert into clearpath.users values (%s, %s, %s)", (user, role, role))
        owner.execute("insert into clearpath.units values (%s, 'medical', %s)", (vehicle, identities["rescue"]))

        with TestClient(app) as client:
            dispatch: DispatchServices = app.state.dispatch
            dispatch.identity.close()
            auth_delay = 0

            def auth(request: httpx.Request):
                assert request.url.path == "/auth/v1/user" and request.headers["apikey"]
                token = request.headers["authorization"].removeprefix("Bearer ")
                if token not in identities:
                    return httpx.Response(401)
                if token == "citizen" and auth_delay:
                    sleep(auth_delay)
                return httpx.Response(200, json={"id": str(identities[token]), "user_metadata": {"role": "dispatcher"}})

            dispatch.identity = httpx.Client(
                base_url="https://test.supabase.co", headers={"apikey": "test"}, transport=httpx.MockTransport(auth)
            )
            with dispatch.database.connection() as limited:
                try:
                    limited.execute("update clearpath.users set role = 'dispatcher'")
                except psycopg.errors.InsufficientPrivilege:
                    limited.rollback()
                else:
                    raise AssertionError("The backend database role can change an account's role.")

            def call(method, path, role=None, payload=None, expected=200):
                headers = {"Authorization": f"Bearer {role}"} if role else {}
                response = client.request(method, "/dispatch/" + path, headers=headers, json=payload)
                assert response.status_code == expected, (path, response.status_code, response.text)
                return response.json()

            call("GET", "me", expected=401)
            call("GET", "me", "invalid", expected=401)
            call("GET", "me", "outsider", expected=403)
            assert call("GET", "me", "citizen")["role"] == "citizen"
            call("GET", "board", "citizen", expected=403)
            assert call("GET", "board", "rescue")["incidents"] == []

            incident = {
                "incident_id": str(uuid4()), "incident_type": "medical",
                "severity": 3, "lat": 40.7391, "lon": -73.9760,
            }
            call("POST", "incidents", "citizen", incident, 403)
            first = call("POST", "incidents", "dispatcher", incident)
            assert call("POST", "incidents", "dispatcher", incident) == first
            second = call("POST", "incidents", "dispatcher", dict(incident, incident_id=str(uuid4())))
            assignments = [
                {"dispatch_id": str(uuid4()), "incident_id": entry["incident_id"], "unit_id": str(vehicle)}
                for entry in (first, second)
            ]

            def race(payload):
                response = client.post("/dispatch/assignments", json=payload, headers={"Authorization": "Bearer dispatcher"})
                return response.status_code, payload

            with ThreadPoolExecutor(max_workers=2) as workers:
                results = list(workers.map(race, assignments))
            assert sorted(code for code, _ in results) == [200, 409], results
            assigned = next(payload for code, payload in results if code == 200)
            assignment_id = assigned["dispatch_id"]
            incident_id = assigned["incident_id"]
            assert call("POST", "assignments", "dispatcher", assigned)["dispatch_id"] == assignment_id
            assert [row["incident_id"] for row in call("GET", "board", "rescue")["incidents"]] == [incident_id]
            call("POST", f"incidents/{incident_id}/close", "dispatcher", expected=409)

            node = next(iter(app.state.simulation.signals))
            priority = {"request_id": str(uuid4()), "dispatch_id": assignment_id, "osm_node_id": node}
            call("POST", "preemption", "citizen", priority, 403)
            stored = call("POST", "preemption", "rescue", priority)
            assert call("POST", "preemption", "rescue", priority) == stored
            call("POST", f"assignments/{assignment_id}/arrive", "citizen", expected=404)
            call("POST", f"assignments/{assignment_id}/arrive", "rescue")
            call("POST", "preemption", "rescue", dict(priority, request_id=str(uuid4())), 403)
            assert call("POST", f"incidents/{incident_id}/close", "dispatcher")["status"] == "closed"

            proposal = {"incident": {"incident_type": "medical", "severity": 4, "lat": 40.7391, "lon": -73.9760},
                        "candidates": [{"unit_id": str(vehicle)}], "recommended_unit_ids": [str(vehicle)]}
            draft_id = uuid4()
            dispatcher = identities["dispatcher"]
            dispatch.query("select clearpath.save_dispatch_draft(%s, %s, %s, %s)",
                           (dispatcher, draft_id, Jsonb(proposal), Jsonb([])))
            review = {"decision": "approved", "unit_ids": [str(vehicle)]}
            call("POST", f"copilot/drafts/{draft_id}/review", "citizen", review, 403)
            call("POST", f"copilot/drafts/{draft_id}/review", "dispatcher", dict(review, unit_ids=[str(uuid4())]), 409)
            accepted = call("POST", f"copilot/drafts/{draft_id}/review", "dispatcher", review)
            assert len(accepted["assignments"]) == 1 and not accepted["edited"]
            assert call("POST", f"copilot/drafts/{draft_id}/review", "dispatcher", review) == accepted

            occupied = uuid4()
            dispatch.query("select clearpath.save_dispatch_draft(%s, %s, %s, %s)",
                           (dispatcher, occupied, Jsonb(proposal), Jsonb([])))
            before = owner.execute("select count(*) from clearpath.incidents").fetchone()[0]
            call("POST", f"copilot/drafts/{occupied}/review", "dispatcher", review, 409)
            assert owner.execute("select count(*) from clearpath.incidents").fetchone()[0] == before
            assert call("POST", f"copilot/drafts/{occupied}/review", "dispatcher",
                        {"decision": "rejected"})["status"] == "rejected"
            call("POST", f"assignments/{accepted['assignments'][0]['dispatch_id']}/arrive", "rescue")
            call("POST", f"incidents/{accepted['incident_id']}/close", "dispatcher")

            now = int(time() * 1000)
            sample = {"nonce": str(uuid4()), "lat": 40.7391, "lon": -73.9760, "time_ms": now}
            call("POST", "position", "citizen", dict(sample, time_ms=now - 3000), 409)
            assert call("POST", "position", "citizen", sample)["expires_in_seconds"] == 60
            call("POST", "position", "citizen", sample, 409)
            jump = dict(sample, nonce=str(uuid4()), time_ms=now + 200, lat=40.7580, lon=-73.9855)
            call("POST", "position", "citizen", jump, 422)
            key = f"clearpath:position:{identities['citizen']}"
            assert 0 < dispatch.redis.ttl(f"{key}:latest") <= 60
            assert 0 < dispatch.redis.ttl(f"{key}:nonce:{sample['nonce']}") <= 60

            auth_delay = 2.1
            fresh = dict(sample, nonce=str(uuid4()), time_ms=int(time() * 1000))
            assert call("POST", "position", "citizen", fresh)["accepted"]

        assert owner.execute("select count(*) from clearpath.preemption_log").fetchone() == (1,)
        print("Verified PostgreSQL persistence, assignment concurrency, role enforcement and Redis replay/TTL checks.")


if __name__ == "__main__":
    main()
