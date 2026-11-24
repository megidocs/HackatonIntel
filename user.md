# ClearPath AI · Partner and demo guide

## Open the project

| What | Where |
| --- | --- |
| Source code | [megidocs/HackatonIntel](https://github.com/megidocs/HackatonIntel), branch `main` |
| Public simulator | [ClearPath Manhattan simulator](https://clearpath-hackatonintel.onrender.com/simulator). Open it before presenting so the Free service has time to wake up. |
| Desktop demo | [Manhattan simulator](http://127.0.0.1:8000/simulator) on the demo laptop or a partner’s own running checkout |
| Backend checks | [FastAPI docs](http://127.0.0.1:8000/docs) and [health](http://127.0.0.1:8000/health) on that same machine |
| Public Supabase project URL | [https://uodbkiyevjwgmjnofcpj.supabase.co](https://uodbkiyevjwgmjnofcpj.supabase.co). This is Hackathon-supa’s hosted API base URL. |
| Presentation | [Hebrew slide deck and offline setup](docs/slides/pedagogy-deck/README.md) and [teacher and student guidance](TeacherAndStudentguidance/README.md). |
| Reference material | [Specification](docs/specification.md), [judging rubric](docs/rubric.html), [T-model reference](docs/T-model-STEM-final-project.pdf), [development logbook](logbooks/2026-11-24-lenovo-hackatonintel.md), and [public deployment log](logbooks/2026-11-24-hackatonintel-public-hosting.md) |

## Run locally on Windows

Install Python 3.13 and Node.js with npm. Clone the repo or sync your copy to `main`, then run these commands from the repository root in PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd ci --prefix frontend
$env:CLEARPATH_GRAPH_PATH = (Resolve-Path 'deploy/manhattan.graphml.gz').Path
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Keep that terminal open and visit the [local simulator](http://127.0.0.1:8000/simulator). The bundled graph is the same snapshot used on Render. Local controls are available immediately and the demo can run offline once setup is complete. For a fresh OpenStreetMap snapshot, use the [graph import instructions](backend/README.md).

## Brief test plan before presenting

| Where | What to test | What you should see |
| --- | --- | --- |
| Public, in a private browser window | Open the Render URL and check the map, route and controls. Allow about a minute if the service is waking up. | Manhattan loads with Bellevue Hospital → Times Square at about 3.16 km and 4.7 modeled minutes. **Start simulation** is disabled for viewers. |
| Public, with a presenter | In a second window, unlock **Presenter access** with the code from the Render service’s Environment page. Start, pause and reset while the first window stays open. | The presenter can control the scenario. The viewer sees the same traffic and clock changes. **Reset** restores the paused default route. |
| Local, routing and signals | Start traffic, try 500 vehicles, close a street on the highlighted route, then reopen it and reset. | Vehicles respond to red and green signals. The closure is marked and the rescue route changes when a detour is available. |
| Local, green wave | Run the same scenario twice at the same traffic density, with **Green wave and alerts** off and on. | With priority enabled, look for the moving corridor, changes to upcoming signals and gold yielding vehicles. Compare modeled arrival times. |
| Presentation rehearsal | Open the slides and the simulator on the demo laptop. Rehearse switching to the local page after starting the local server. | The presenter can show the same route and traffic scenario on either page. |

For automated results, see the [local routing, simulation and priority checks](backend/README.md) and [public HTTPS smoke check](deploy/README.md).
