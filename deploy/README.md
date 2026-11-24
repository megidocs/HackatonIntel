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

## Tel Aviv graph

`tel-aviv.graphml.gz` contains OpenStreetMap driving roads in central Tel Aviv
from the [Geofabrik Israel and Palestine extract](https://download.geofabrik.de/asia/israel-and-palestine/index.html)
downloaded on 2026-11-24 (OSM replication timestamp 2026-11-23 21:21:17 UTC).
The simulator reads the compressed graph locally. The build verifies its SHA-256
checksum. The same OpenStreetMap attribution and ODbL terms as above apply.
The road envelope is used as the background outline.

To regenerate the bundle from a regional PBF, use the commands below. For a
local preview of a newly prepared graph, set `CLEARPATH_TEL_AVIV_GRAPH_PATH`
to `backend/data/tel-aviv.graphml` before starting FastAPI.

```powershell
New-Item -ItemType Directory -Force backend/data/osm-cache | Out-Null
curl.exe --fail --location --output backend/data/osm-cache/israel-and-palestine.osm.pbf https://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf
.\.venv\Scripts\python.exe -m backend.prepare_graph --city tel-aviv --pbf backend/data/osm-cache/israel-and-palestine.osm.pbf
.\.venv\Scripts\python.exe -c "import gzip, pathlib; pathlib.Path('deploy/tel-aviv.graphml.gz').write_bytes(gzip.compress(pathlib.Path('backend/data/tel-aviv.graphml').read_bytes(), mtime=0))"
$hash = (Get-FileHash deploy/tel-aviv.graphml.gz -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText((Join-Path (Get-Location) 'deploy/tel-aviv.graphml.gz.sha256'), "$hash  deploy/tel-aviv.graphml.gz`n")
```
