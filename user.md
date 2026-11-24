# ClearPath AI · Partner and demo guide

## Open the project

| What | Where |
| --- | --- |
| Source code | [megidocs/HackatonIntel](https://github.com/megidocs/HackatonIntel), branch `main` |
| Desktop demo | [Manhattan simulator](http://127.0.0.1:8000/simulator) on the demo laptop or a partner’s own running checkout |
| Backend checks | [FastAPI docs](http://127.0.0.1:8000/docs) and [health](http://127.0.0.1:8000/health) on that same machine |
| Public Supabase project URL | [https://uodbkiyevjwgmjnofcpj.supabase.co](https://uodbkiyevjwgmjnofcpj.supabase.co). This is Hackathon-supa’s hosted API base URL. FastAPI and the simulator run on the laptop. |
| Presentation | [Four-slide Hebrew deck](https://claude.ai/artifact/3L7NETeH58eRGv3aj2tF8r). Ask the deck owner for access or an export before presenting. Use the [guidance index](TeacherAndStudentguidance/README.md) if the deck is unavailable. |
| Reference material | [Specification](docs/specification.md), [judging rubric](docs/rubric.html), [T-model reference](docs/T-model-STEM-final-project.pdf), and [development logbook](logbooks/2026-11-24-lenovo-hackatonintel.md) |

## Run and present

1. Clone `https://github.com/megidocs/HackatonIntel` or sync an existing checkout to `main`. Follow the [Windows setup](backend/README.md) for Python, Node, the Manhattan graph, and the FastAPI startup command.
2. Open the simulator in a desktop browser. Start with Bellevue Hospital to Times Square. Show the route, start traffic, and close a road on the highlighted route. Reopen it and explain the route change using the location and one-way constraints in the road graph.
3. Use the deck to explain the learning goals and T model. Use the logbook and routing check to show how the team verified the result. The simulator and its road data are served locally. Supabase is on Free with automatic production deployment off.

## Executive test summary

| Test | Expected evidence |
| --- | --- |
| Startup | `/health` returns `ok` and graph counts. The simulator shows Manhattan, both route endpoints, and the default route. |
| Routing | Bellevue → Times Square is about 3.16 km and 4.7 modeled minutes with the demo graph. `backend.check_routing` compares A* with Dijkstra on 100 pairs. |
| Traffic and signals | **Start simulation** moves vehicles and advances the clock. Cars wait at red, proceed on green, and stop updating on **Pause**. Try 500 vehicles. |
| Closures and recovery | Close a segment on the highlighted route, see it marked closed, and verify the rescue route changes. Reopen the segment and use **Reset** to restore the scenario. `backend.check_simulation` exercises these controls. |
| Presentation access | Open the deck with the presenter’s account or use an offline export. Confirm that each partner who will run the demo can access the GitHub repo. |
