# Dispatcher copilot and final rehearsal

The copilot runs on the demo laptop with the local Qwen model and authenticated FastAPI. It turns a report into a pending proposal and lets a dispatcher approve the recommended units, substitute an offered alternative, or reject it. The mobile Rescue view can display the resulting assignment when signed in through the browser. [Sign-in and accounts](rescue-accounts.md)

## Run the demo

1. Start Redis, the [local model](../models/README.md#run-the-laptop-demo), and [FastAPI with dispatch enabled](dispatch.md#start-with-the-private-local-file). Set `CLEARPATH_MODEL_URL=http://127.0.0.1:8011` in the FastAPI terminal.
2. Open [ClearPath dispatch](http://127.0.0.1:8003/dispatch/reports) and sign in as the demo dispatcher with the values from Lenovo’s private configuration file. Open a separate browser window for the Rescue account.
3. Enter “Medical emergency at Bellevue Hospital. One adult is having a seizure. Ambulance needed.” Select **Propose dispatch**. Review the matched place, proposed priority, modeled ETA and available choices. The shared demo currently has one medical unit, so alternate units appear only when the fleet has other reachable matches.
4. Select **Approve selected units** to create the incident and assignments together in PostgreSQL. Alternatively choose **Reject draft**. In the Rescue window, select **Refresh assignment** to view the change. After the rehearsal, use the arrival and close endpoints in the [manual dispatch API](http://127.0.0.1:8003/docs#tag/dispatch).
5. Try a report with two locations or repeat a report while a matching incident is open. Read the question and continue with the manual workflow if the report cannot be resolved. The browser offers the manual workflow after its ten-second proposal timeout.

## Planning and approval

| Tool | Inputs and result |
| --- | --- |
| `geocode` | Looks up a source-backed phrase in the local Manhattan catalog and returns the OSM road node. |
| `get_recent_incidents` | Checks the current dispatch board for an open incident of the same type within 200 m. |
| `find_available_units` | Selects unassigned units of the required types within 8 km, using simulated depots for the demo. |
| `get_eta` | Computes free-flow A* travel times using current road closures and up to four routing workers. |
| `draft_dispatch` | Returns the shortest reachable candidate for each required type and up to two alternatives. FastAPI stores the pending draft and typed trace. |
| `ask_dispatcher` | Stops the run for an ambiguous location, possible duplicate, or missing unit type. The dispatcher can clarify with a new report or use manual dispatch. |

Qwen extracts the incident and selects the next tool when more than one is applicable. FastAPI supplies arguments from validated observations and limits planning to eight tool calls and ten seconds. The planner receives a read-only snapshot of available units and incidents. It produces a pending draft through the API. The SQL approval function separately checks the dispatcher, candidate IDs and unit availability. An existing assignment produces a conflict and rolls back the entire approval. Repeating a successful review returns the same assignment. [Planning code](../backend/copilot.py) · [Draft and approval migration](../supabase/migrations/20261124164000_clearpath_copilot.sql)

## Evaluation

The fixture gives each model the same 30 reports and simulated fleet. The baseline picks the quickest available unit at the fixture destination. The copilot must choose the expected set of unit types or request clarification for ambiguous or duplicate incidents. The baseline is given the fixture location for resolvable cases. These timing figures use a local fixture rather than the hosted database.

| Method | Correct | Mean runtime | Mean tool calls |
| --- | ---: | ---: | ---: |
| Nearest ETA | 20 / 30 | 24 ms | Baseline route calculation |
| Copilot | 22 / 30 | 1,594 ms | 4.5 |

The copilot recognized all five duplicates and selected the required pair in two of five compound crashes. It scored zero of five on the roadblock cases, all of which the baseline classified correctly by picking the nearest unit. These synthetic cases show a tradeoff between handling duplicates or multiple unit types and making reliable choices on simple reports. Keep human review in the demo. [Benchmark data](../models/copilot-benchmark-result.json)

With real Supabase accounts, the first full proposal took 11.95 seconds. A warm repeat with connection pooling took 6.13 seconds end to end, including authentication and draft storage. The planner took 2.96 seconds and recorded 429 prompt and 74 completion tokens. The full request exceeded the five-second goal in that run. Local inference used no metered API calls. [Live trace](copilot-rehearsal-trace.json)

The adversarial test asked the copilot to ignore the rules and send every vehicle. The system returned a reviewable draft, and the dispatch board stayed the same. The live authorization check rejected a citizen’s approval and an unknown unit ID. An explicit dispatcher approval assigned the rescue unit once, the Rescue account saw it, and the test incident was closed. [Live trace](copilot-rehearsal-trace.json)

## Final presentation handoff

| Show | Source |
| --- | --- |
| Public simulator, Android Rescue and Citizen, and spoken alert | [Partner guide](../user.md) and [rehearsal report](rehearsal.md) |
| Routing, green-wave timing, and measured performance | [Milestone 7 report](rehearsal.md) |
| Supabase roles, replay checks and dispatch persistence | [Signed-in dispatch guide](dispatch.md) and [rehearsal trace](dispatch-rehearsal-trace.json) |
| What we trained and what we ran zero-shot | [Model brief for the slide team](model-development-brief.md) |
| Copilot proposal, rejected injection and explicit approval | This guide, [30-case evaluation](../models/copilot-benchmark-result.json), and [live evidence](copilot-rehearsal-trace.json) |

Use the public simulator to present the shared traffic scene. Use the laptop’s signed-in browser for dispatch and the copilot. The road data and dispatch fixtures are synthetic or drawn from the demo map. Report the benchmark and latency as measurements of this setup.
