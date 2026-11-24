# ClearPath public preview

The Render Free service builds the Dockerfile from HackatonIntel and serves
both FastAPI and the simulator. Keep the service at one instance. Render
uses the runtime port and checks `/health`. The GitHub Actions workflow
builds the same container, exercises the API under Free-tier limits, and
checks that anonymous viewers cannot change the scenario. Render deploys
from `main` after CI checks pass. Supabase remains on Free with its own
auto-deploy switch off.

The public page shows the shared simulation. The presenter enters the value
of `CLEARPATH_CONTROL_TOKEN` from the Render environment to unlock controls.
Store the code only in Render and share it privately with presenters.

Run the public HTTPS smoke check with the Render service's base URL after
the deploy finishes. Include the expected Git SHA to verify the release.

```text
python -m backend.check_hosted https://YOUR-SERVICE.onrender.com --release YOUR-GIT-SHA --wait 180
```

The bundled Manhattan graph is the 2026-11-21 OpenStreetMap snapshot used in
the laptop demo. It was built with OSMnx from the [BBBike New York extract](https://download.bbbike.org/osm/bbbike/NewYork/)
and clipped to Manhattan using the Nominatim boundary. See the
[import runbook](../backend/README.md). The graph database is ©
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright) and
is distributed under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
The build verifies its SHA-256 checksum and unpacks it before startup.
