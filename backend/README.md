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

This milestone models signal cycles, traffic queues, and route changes. The
emergency green wave, civilian alerts, and Android synchronization are later
milestones. Use a single FastAPI worker because the demo state is in process memory.

Verify the simulator once the server is running. This check resets the local
scenario and covers vehicle motion, route changes, and signal behavior.

```powershell
.\.venv\Scripts\python.exe -m backend.check_simulation
```

Road data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
The graph and data download cache are generated locally.
