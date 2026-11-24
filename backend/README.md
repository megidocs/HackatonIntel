# ClearPath AI · Milestone 1

Run these commands from the repository root in PowerShell on the demo laptop.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
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

Milestone 1 runs on laptop loopback. Supabase, Redis, and phone connectivity
are later integration work.

Road data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
The graph and data download cache are generated locally.
