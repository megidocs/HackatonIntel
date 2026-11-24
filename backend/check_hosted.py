"""Verify the published simulator without changing its shared scenario."""

import argparse
import gzip
import json
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def read(base: str, path: str, headers: dict | None = None) -> bytes:
    with urlopen(Request(base + path, headers=headers or {}), timeout=15) as response:
        body = response.read()
        return gzip.decompress(body) if response.headers.get("Content-Encoding") == "gzip" else body


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("--release", help="Wait for this Git commit to be live.")
    parser.add_argument("--wait", type=int, default=0)
    args = parser.parse_args()
    base = args.base.rstrip("/")
    deadline = monotonic() + args.wait

    while True:
        try:
            health = json.loads(read(base, "/health"))
            if health["status"] == "ok" and (not args.release or health.get("release") == args.release):
                break
            error = f"Unexpected health response: {health}"
        except (OSError, ValueError, KeyError) as failure:
            error = str(failure)
        if monotonic() >= deadline:
            raise RuntimeError(f"The requested release did not become healthy: {error}")
        sleep(5)

    assert health["nodes"] > 4000 and health["directed_edges"] > 8000
    assert b"Manhattan Traffic Simulator" in read(base, "/")
    assert b"/simulation/map" in read(base, "/sim/assets/simulator.js")
    assert read(base, "/sim/vendor/maplibre-gl.mjs")
    packed = read(base, "/simulation/map", {"Accept-Encoding": "gzip"})
    plain = read(base, "/simulation/map", {"Accept-Encoding": "identity"})
    assert packed == plain
    assert len(json.loads(plain)["roads"]["features"]) > 4000
    assert json.loads(read(base, "/simulation/state"))["vehicles"]
    assert b'href="/simulator/tel-aviv"' in read(base, "/simulator/tel-aviv")
    tel_aviv_map = json.loads(read(base, "/simulation/tel-aviv/map", {"Accept-Encoding": "gzip"}))
    assert tel_aviv_map["scenario"]["name"] == "Tel Aviv"
    assert len(tel_aviv_map["roads"]["features"]) > 1000
    assert tel_aviv_map["signals"]["features"]
    tel_aviv = json.loads(read(base, "/simulation/tel-aviv/state"))
    for lon, lat in (tel_aviv["default_origin"], tel_aviv["default_destination"]):
        assert 34.75 < lon < 34.81 and 32.04 < lat < 32.11
    assert json.loads(read(base, "/simulation/access")) == {"restricted": True, "allowed": False}
    for path in ("/simulation/control", "/simulation/tel-aviv/control"):
        try:
            urlopen(Request(
                base + path, data=b"{}",
                headers={"Content-Type": "application/json"},
            ), timeout=15)
        except HTTPError as failure:
            if failure.code != 403:
                raise
        else:
            raise AssertionError(f"Anonymous requests could control {path}.")
    print(f"Verified both simulator cities, release {health.get('release', 'unknown')}, and read-only viewer access.")


if __name__ == "__main__":
    main()
