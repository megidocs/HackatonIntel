# ClearPath AI · Partner and demo guide

## Open the project

| What | Where |
| --- | --- |
| Source code | [megidocs/HackatonIntel](https://github.com/megidocs/HackatonIntel), branch `main` |
| Public simulator | [ClearPath Manhattan simulator](https://clearpath-hackatonintel.onrender.com/simulator). Open it before presenting so the Free service has time to wake up. |
| Desktop demo | [Manhattan simulator](http://127.0.0.1:8000/simulator) on the demo laptop or a partner’s own running checkout |
| Android demo | [Build and connect the rescue and citizen app](mobile/README.md) to the same simulator as the desktop browser. |
| Backend checks | [FastAPI docs](http://127.0.0.1:8000/docs) and [health](http://127.0.0.1:8000/health) on that same machine |
| Public Supabase project URL | [https://uodbkiyevjwgmjnofcpj.supabase.co](https://uodbkiyevjwgmjnofcpj.supabase.co). This is Hackathon-supa’s hosted API base URL. |
| Dispatch database | [Milestone 5 setup and verification](docs/dispatch.md) for authorized accounts and a local Redis instance. |
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

For the signed-in dispatch rehearsal on Lenovo, the private configuration and demo credentials are in `C:\Users\3stra\AndroidStudioProjects\HackatonIntel\.env.dispatch.local`. Git ignores this file. Use the [dispatch startup instructions](docs/dispatch.md#start-with-the-private-local-file).

## Brief test plan before presenting

| Where | What to test | What you should see |
| --- | --- | --- |
| Public, in a private browser window | Open the Render URL and check the map, route and controls. Allow about a minute if the service is waking up. | Manhattan loads with Bellevue Hospital → Times Square at about 3.16 km and 4.7 modeled minutes. **Start simulation** is disabled for viewers. |
| Public, with a presenter | In a second window, unlock **Presenter access** with the code from the Render service’s Environment page. Start, pause and reset while the first window stays open. | The presenter can control the scenario. The viewer sees the same traffic and clock changes. **Reset** restores the paused default route. |
| Local, routing and signals | Start traffic, try 500 vehicles, close a street on the highlighted route, then reopen it and reset. | Vehicles respond to red and green signals. The closure is marked and the rescue route changes when a detour is available. |
| Local, green wave | Run the same scenario twice at the same traffic density, with **Green wave and alerts** off and on. | With priority enabled, look for the moving corridor, changes to upcoming signals and gold yielding vehicles. Compare modeled arrival times. |
| Android, rescue and citizen | Reset and pause the desktop scenario. Connect both roles to the same server. Switch priority off and on from Rescue, using the presenter code on Render. | The desktop priority switch follows the phone. Citizen vehicle 1 clears its alert and then shows and reads it aloud when priority returns. |
| Presentation rehearsal | Open the slides and the simulator on the demo laptop. Rehearse switching to the local page after starting the local server. | The presenter can show the same route and traffic scenario on either page. |

For automated results, see the [local routing, simulation and priority checks](backend/README.md) and [public HTTPS smoke check](deploy/README.md).
