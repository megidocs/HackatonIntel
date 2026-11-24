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
| Rescue login for Amit | [Demo email/password sign-in and role enrollment](docs/rescue-accounts.md). |
| Incident report models | [Local report review and model comparison](models/README.md) for the authenticated dispatcher rehearsal. |
| Model development for presenters | [Technical brief for the slide team](docs/model-development-brief.md) with the training method, benchmark, and demo example. |
| Rehearsal and measurements | [Performance report and demo sequence](docs/rehearsal.md), including browser frame timing and the authenticated dispatch check. |
| Dispatcher copilot | [Final rehearsal, approval flow and benchmark](docs/copilot.md). |
| Dispatch-driven simulator | [Lenovo traffic map](http://127.0.0.1:8004/simulator) and [dispatch approval](http://127.0.0.1:8004/dispatch/reports). Start civilian traffic before approving a report. |
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
| Android, rescue and citizen | Reset and pause the desktop scenario. Connect both phones to the same server. Keep the presenter code on the desktop and toggle priority there. | Rescue follows the route. Citizen vehicle 1 clears its alert and then shows and reads it aloud when priority returns. The phone needs a presenter code only for the optional demo of Android changing priority. |
| Presentation rehearsal | Open the slides and the simulator on the demo laptop. Rehearse switching to the local page after starting the local server. | The presenter can show the same route and traffic scenario on either page. |

For automated results, see the [local routing, simulation and priority checks](backend/README.md) and [public HTTPS smoke check](deploy/README.md).

## Dispatch rehearsal reports

In [ClearPath Dispatch on Lenovo](http://127.0.0.1:8003/dispatch/reports), sign in as dispatcher, paste either example into **Incident report**, and click **Propose dispatch**.

**Bellevue Hospital**

```text
Medical emergency at Bellevue Hospital. One adult is having a seizure. Ambulance needed.
```

Use this to rehearse approval and the Rescue assignment. The modeled ETA is zero because the demo ambulance is based at Bellevue.

**Bryant Park**

```text
Medical emergency at Bryant Park. One adult has collapsed and is unresponsive. Send an ambulance.
```

The modeled route from Bellevue crosses 14 traffic-signal points and takes about 3 minutes 49 seconds before traffic delays. After dispatch approval, click **Refresh assignment** in the signed-in Rescue browser. If the copilot reports no available medical unit, finish the previous assignment and close its incident to free the ambulance. Simulator **Reset** only resets the traffic scene. See the [copilot guide](docs/copilot.md#run-the-demo) for the dispatch reset steps.

For the **dispatch-driven demo**, open the [Lenovo map on port 8004](http://127.0.0.1:8004/simulator) and click **Start traffic** before proposing a report. The map shows civilian traffic and **Waiting for an approved dispatch**. Approve from the [dispatcher page on port 8004](http://127.0.0.1:8004/dispatch/reports). The incident pin, route and rescue vehicle appear automatically. For the Android emulator, connect the app in **Rescue** mode to `http://10.0.2.2:8004` so it follows that same scene. See the [startup instructions](docs/dispatch.md#start-with-the-private-local-file).

For the **standalone traffic demo** on Render, unlock **Presenter access**, use **Destination → Edit** if you want a different route, and click **Start simulation**. **Reset** restores Bellevue Hospital → Times Square. Android viewers on the Render server follow that standalone scene.
