"""Verify the two phone streams against a disposable presenter-protected demo."""

import argparse
import asyncio
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus


async def receive_until(feed, condition):
    async with asyncio.timeout(10):
        while True:
            state = json.loads(await feed.recv())
            if condition(state):
                return state


async def verify(base: str, token: str) -> None:
    parsed = urlsplit(base)
    ws_base = urlunsplit(("wss" if parsed.scheme == "https" else "ws", parsed.netloc, "/simulation/mobile", "", ""))

    def request(path, payload, code=token):
        headers = {"Content-Type": "application/json"}
        if code:
            headers["X-ClearPath-Control-Token"] = code
        with urlopen(Request(base + path, json.dumps(payload).encode(), headers), timeout=10) as response:
            return json.load(response)

    def control(**payload):
        return request("/simulation/control", payload)

    try:
        request("/simulation/control", {"priority": False}, code="")
    except HTTPError as error:
        assert error.code == 403
    else:
        raise AssertionError("An anonymous request changed presenter controls.")

    try:
        async with connect(f"{ws_base}?role=citizen&vehicle=0"):
            raise AssertionError("A citizen opened the rescue unit as a civilian vehicle.")
    except InvalidStatus as error:
        assert error.response.status_code == 403

    control(reset=True)
    try:
        async with (
            connect(f"{ws_base}?role=rescue") as rescue,
            connect(f"{ws_base}?role=citizen&vehicle=1") as citizen,
        ):
            route = await receive_until(rescue, lambda state: bool(state["route"]))
            assert route["route_status"] == "en_route" and route["position"]
            alert = await receive_until(citizen, lambda state: state["alerted"])
            assert set(alert) == {"role", "time", "running", "vehicle_id", "assigned", "alerted"}
            assert alert["assigned"] and alert["vehicle_id"] == 1

            control(priority=False)
            await receive_until(citizen, lambda state: not state["alerted"])
            await receive_until(rescue, lambda state: not state["priority_enabled"])
            control(priority=True, running=True)
            await receive_until(rescue, lambda state: state["running"] and state["time"] > 0)
            control(running=False, density=0)
            await receive_until(citizen, lambda state: not state["running"] and not state["assigned"])
            control(reset=True)
            await receive_until(citizen, lambda state: state["alerted"])
    finally:
        control(reset=True)

    print("Verified synchronized rescue and citizen streams, priority changes, and protected controls.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    token = os.environ.get("CLEARPATH_CONTROL_TOKEN")
    if not token:
        parser.error("Set CLEARPATH_CONTROL_TOKEN to match the disposable test server.")
    asyncio.run(verify(args.base_url.rstrip("/"), token))


if __name__ == "__main__":
    main()
