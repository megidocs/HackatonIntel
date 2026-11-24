# ClearPath AI · Tel Aviv simulator

## User prompt

> if you could have an option where the simulator is in Tel-Aviv we will be much more oriented and could understand where to propose events.
>
> Other alternative - playwright cli or defined set of clicks that work. right now we are not there.

The user clarified, “(i.e. in tel aviv map).”

### Decisions

- The user requested Tel Aviv geography for orienting the team and proposing events. The team also wanted a repeatable way to rehearse.
- Codex chose central Tel Aviv and a default simulated trip from Ichilov Hospital to Rabin Square. It added Dizengoff Square, Habima Square, and Sarona Market as selectable incident sites. The map uses Hebrew landmark labels.
- Codex gave each desktop city its own scenario state. Tel Aviv uses manual map and landmark placement. The Android and dispatch/copilot workflow is served by the Manhattan scenario.

### AI contribution

- Added the desktop city switch, bilingual incident choices, and city-specific map, playback, and closure requests.
- Prepared and bundled an OpenStreetMap driving graph from Geofabrik. The import retained 5,146 nodes, 7,992 directed edges, 6,798 physical road segments, and 722 signal nodes. The map background outline follows the road envelope.
- Wrote a [click walkthrough](../backend/README.md#tel-aviv-rehearsal) and a [Playwright rehearsal](../backend/check_tel_aviv_browser.py). These are evidence for the project team's [core knowledge](../docs/rubric.html#c1) and [critical checking](../docs/rubric.html#c3) checkpoints.

### Independent checks

- Built the Tel Aviv graph, validated its SHA-256, and computed open routes from Ichilov to all four landmarks.
- The Playwright-managed Chromium binary on this machine was missing for the installed version. Ran the rehearsal with installed Chrome via Playwright and passed it on both open and presenter-protected local instances.
- Visually inspected the rendered map and clicked a Tel Aviv road on the highlighted route. The browser showed a closure and rerouting, and reopening restored the original line. Also verified the same behavior via the city API.
- Passed the local public-preview smoke check with anonymous control rejection for both cities, Manhattan routing and simulation checks, the paired priority check, the mobile stream check, JavaScript syntax, and `git diff --check`.
- The host has no Docker CLI. The Render container build and hosted rollout remain unverified. Teacher vetting is pending.

### Session result

The [local Tel Aviv simulator](http://127.0.0.1:8017/simulator/tel-aviv) is running. The rehearsal starts from **Reset**, selects **Habima Square**, clicks **Set incident**, then starts, pauses, and resets the simulation. The [rehearsal](../backend/README.md#tel-aviv-rehearsal) can be reproduced by a team member for the [judging checkpoint](../docs/rubric.html#c3).

## User prompt

> when you think you got real progress commit-push so we can take a look on Render

### Decisions

- The user authorized committing and pushing the completed Tel Aviv simulator. Codex chose the current `main` branch because the Render preview tracks it after CI passes.
- The commit covers the Tel Aviv feature, walkthrough, check, graph bundle, and this log. A pre-existing local edit to the Copilot log has its own history.

### AI contribution

- Reviewed the feature diff and the Render check configuration. The hosted check exercises both city maps, both city scenarios, and presenter access.
- Scoped the release commit to the verified Tel Aviv work and its [judging evidence](../docs/rubric.html#c3).

### Independent checks

- Confirmed that local and remote `main` matched before committing, and that `git diff --check` passed.
- The [container preview and regressions](https://github.com/megidocs/HackatonIntel/actions/runs/45442493753) and [dispatch regression](https://github.com/megidocs/HackatonIntel/actions/runs/45442493748) passed.
- The [live health endpoint](https://clearpath-hackatonintel.onrender.com/health) reported release `d46512be425d8a0e2b97b83478868282256b03ec`. The hosted smoke test verified both maps and presenter authorization. Playwright opened the deployed Tel Aviv map in Chrome and confirmed the Habima label, Rabin Square default destination, and locked public-viewer controls. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

Feature commit `d46512b` is on GitHub `main` and live on [Render](https://clearpath-hackatonintel.onrender.com/simulator/tel-aviv). Presenters can unlock the controls to run the walkthrough. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Vehicle availability for different incident locations

> another user question. The tel-aviv map looks great. what if I create a new dispatcher report that is in a somewhat different area. will there be an available vehicle for it? asking because the simulator shows origin and destination for the simulated event (as I understand it). it does not tell me which other rescue vehicles are available to dispatch. this puts me as a demonstrator and creator of dispatch events - facing a wall. or maybe I'm missing something in the big picture.

### Decisions

- The user asked how the current demonstration works and pointed out the lack of fleet visibility before writing a report. Codex checked the deployed simulator and the local dispatcher board to answer the question.

### AI contribution

- Traced the origin and destination on the Tel Aviv desktop map, the report candidate list, and the Copilot eligibility rules for matching unassigned unit types, supported depots, distance, and route availability. [Rubric criterion 1](../docs/rubric.html#c1)

### Independent checks

- Render reported standalone mode for Tel Aviv and returned HTTP 404 for the dispatcher report page. The Lenovo rehearsal on port 8004 reported dispatch mode and served its report page.
- The authenticated dispatcher board showed one medical unit available. The default modeled medical depot is Bellevue Hospital. The check read the board without creating or changing an incident or an assignment. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The Tel Aviv desktop map shows one simulated rescue trip. The local Manhattan dispatcher chooses from the connected fleet after a report is proposed. The checked fleet had one ambulance and could cover another supported, reachable location while the ambulance was free. A pre-report fleet view and Tel Aviv dispatch integration are open product gaps.
