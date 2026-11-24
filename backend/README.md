# ClearPath AI · Local demo

Run these commands from the repository root in PowerShell on the demo laptop.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm ci --prefix frontend
if (-not (Test-Path -LiteralPath 'backend/data/manhattan.graphml')) {
    New-Item -ItemType Directory -Force backend/data/osm-cache | Out-Null
    curl.exe --fail --location --output backend/data/osm-cache/NewYork.osm.pbf https://download.bbbike.org/osm/bbbike/NewYork/NewYork.osm.pbf
    .\.venv\Scripts\python.exe -m backend.prepare_graph --pbf backend/data/osm-cache/NewYork.osm.pbf
}
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

The importer saves the Manhattan driving network in `backend/data/manhattan.graphml`.
The server loads that file once at startup and can route offline after the import.
Regenerate the graph to use a fresh map snapshot. `CLEARPATH_GRAPH_PATH` can point
the server and check script to a different prepared GraphML file.

The laptop import used the [BBBike New York OSM extract](https://download.bbbike.org/osm/bbbike/NewYork/).
OSMnx clips the PBF to the Manhattan boundary from Nominatim or its local cache.
When Overpass is available, `python -m backend.prepare_graph` from the project
virtual environment can download just the Manhattan network.

## Routing API

Open the [interactive API docs](http://127.0.0.1:8000/docs) or check
[server health](http://127.0.0.1:8000/health). Try a route from Bellevue to Times Square.

```powershell
$body = @{
    origin = @{ lat = 40.7391; lon = -73.9760 }
    destination = @{ lat = 40.7580; lon = -73.9855 }
} | ConvertTo-Json -Depth 3
Invoke-RestMethod http://127.0.0.1:8000/route -Method Post -ContentType 'application/json' -Body $body
```

`POST /route` returns the ordered OpenStreetMap node IDs, distance, modeled
travel time, and a GeoJSON line with longitude before latitude. A* uses estimated
free-flow travel times and preserves the mapped one-way directions. The API snaps
each coordinate to a drivable node within 500 m and returns `422` for points farther
away or `404` when the snapped nodes have no directed route between them.

With the server running, open another terminal at the repository root and run
the HTTP checks and 100-pair comparison with Dijkstra.

```powershell
.\.venv\Scripts\python.exe -m backend.check_routing
```

## Desktop simulator

### Tel Aviv dispatch rehearsal

Open [Tel Aviv dispatch](http://127.0.0.1:8000/simulator/tel-aviv/dispatch).
Before writing the report, the fleet panel shows each simulated vehicle, its
Tel Aviv base, and whether it is available. The base markers appear on the map.
The shared public demo requires the presenter code to propose or approve a dispatch.

1. Enter a simulated report, such as **אירוע רפואי בדרך יפו. נדרש אמבולנס.**
2. Choose **Jaffa Road · דרך יפו** as the location and **Ambulance** as the
   response. Click **Propose dispatch** to compare the available units and their
   modeled drive times.
3. Review the report and vehicle, then click **Approve dispatch**. The vehicle
   leaves its listed base and the map follows the trip. Its status changes to
   **Dispatched**, then **Available** when it reaches the incident.
4. Once it arrives, approve another report or click **Reset** to restart the rehearsal.

This workflow uses a synthetic fleet and the dispatcher's location and response
choices. It runs on the simulator itself with one active trip at a time. The
simulated fleet resets at server restart. The signed-in report workflow is
documented in [ClearPath dispatch](../docs/dispatch.md).

On a disposable local instance, the browser check can run the full sequence:

```powershell
.\.venv\Scripts\python.exe -m backend.check_tel_aviv_browser --channel chrome --dispatch
```

### Tel Aviv rehearsal

Open the [Tel Aviv simulator](http://127.0.0.1:8000/simulator/tel-aviv), or click
**Tel Aviv** above the rescue route. The map covers central Tel Aviv on
OpenStreetMap roads, with Hebrew labels for the landmarks. The default route
runs from Ichilov Hospital to Rabin Square. For a repeatable demo:

1. Click **Reset**. The route shows **Ichilov Hospital** and **Rabin Square**.
2. Under **Simulated incident location**, choose **Habima Square · כיכר הבימה**.
   Click **Set incident**. The destination and the teal route update.
3. Click **Start simulation**. Wait for the clock to advance, then click
   **Pause**. Click **Reset** to restore the Rabin Square route.

To place an incident elsewhere, click **Edit** on the **Destination** row and
click a road on the map. On the public preview, unlock **Presenter access**
before changing the shared Tel Aviv scenario.

On a disposable local instance, the same sequence can be checked with
Playwright. Install Playwright and Chromium once if they are missing.

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m backend.check_tel_aviv_browser
```

Pass `--channel chrome` or `--channel msedge` to use an installed browser.

The server uses the bundled Tel Aviv graph. See the
[graph source and regeneration steps](../deploy/README.md#tel-aviv-graph).

### Manhattan rehearsal

Open the [Manhattan simulator](http://127.0.0.1:8000/simulator). Start playback, set
the civilian vehicle count or playback speed, and use the origin and destination
buttons to choose new points on the map. To reroute the rescue vehicle, select
**Toggle road closure** and click a street on its route. Click the same street
again to reopen it. **Reset** restores Bellevue to Times Square and pauses playback.

FastAPI owns the simulation clock, positions, fixed-cycle simulated signals, and
closures. A closure applies to the physical segment in both mapped directions.
The browser renders the saved OpenStreetMap streets with local MapLibre assets
and interpolates vehicle positions between updates. The land outline is derived
from the road-node geometry. The map and simulation run on laptop loopback without
map tile requests or cloud services.

**Green wave and alerts** enables simulated approach priority and a moving
400 m corridor. The simulator reserves signals when their modeled ETA is
within 20 seconds, includes a clearance interval on activation and release,
and alerts civilian vehicles ahead on the same directed route. Gold markers
show yielding vehicles. Reset the scenario with the same traffic density
and run once with the control off and once with it on to compare arrival times.
The alerts are simulated on the desktop. Android synchronization is milestone 4.
Use one FastAPI worker because the demo state is in process memory.

Verify the simulator once the server is running. This check resets the local
scenario and covers vehicle motion, route changes, and signal behavior.

```powershell
.\.venv\Scripts\python.exe -m backend.check_simulation
.\.venv\Scripts\python.exe -m backend.check_priority
```

The priority check verifies signal clearance and restoration, route-only alerts,
and a paired run with seeded traffic. The reported times are simulator results.

Road data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
The graph and data download cache are generated locally.
