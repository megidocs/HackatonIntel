# ClearPath AI · Tel Aviv dispatch rehearsal

## User prompt

> yes, please add a fleet panel so I can see which rescue vehicles are available and where they’re based before writing a report, and connect dispatch to the Tel Aviv map so we can demo the whole flow there. and the vehicles should be available in some locations in TLV that are (for example in פנקס, ז'בוטינסקי, בן יהודה, נחמני, דרך יפו וספורטק

### Decisions

- The user requested fleet visibility before report creation and suggested six Tel Aviv bases. Codex chose to use all six and seed two ambulances, two fire engines, and two police cars with positions verified against the bundled Tel Aviv driving graph.
- Codex integrated a structured report, proposal, approval, and simulated arrival into a Tel Aviv dispatch page. The rehearsal uses the shared presenter code and handles one active trip at a time. The fleet is simulated and lives in the server process. [Core knowledge checkpoint](../docs/rubric.html#c1)

### AI contribution

- Built the fleet list and Hebrew base markers, selected compatible reachable vehicles using the existing router and road closures, and wired approved reports to the vehicle and route shown on the Tel Aviv map.
- Made approval recheck compatibility, route, and availability under the simulation lock. The fleet panel shows the status changes through arrival. [Rehearsal guide](../backend/README.md#tel-aviv-dispatch-rehearsal) · [Judging checkpoint](../docs/rubric.html#c3)

### Independent checks

- Checked routes from each unit type to all six requested bases and to Habima Square. Chrome Playwright verified the fleet before entry, a Hebrew report for Jaffa Road, selected Ambulance 2 at Nahmani, watched the route run, and saw the ambulance become available on arrival. A screenshot confirmed the six fleet rows and base markers on the map.
- Local API checks rejected anonymous proposals and approvals, an incompatible unit, and simultaneous approval attempts. They confirmed that preview leaves availability intact, reset frees the fleet, and the two Tel Aviv modes have independent state.
- The standalone Tel Aviv Playwright check, hosted-style smoke check, Manhattan routing and simulation regressions, JavaScript syntax, and diff whitespace check passed locally. [Critical checking checkpoint](../docs/rubric.html#c3)
- The [container preview](https://github.com/megidocs/HackatonIntel/actions/runs/45450321197) and [dispatch regression](https://github.com/megidocs/HackatonIntel/actions/runs/45450321066) passed. Render served release `7ab68c6e79847d30799b92ae7f464a81d2c35ebc`. Chrome confirmed six fleet rows and map markers and verified the public viewer's disabled report controls.

### Session result

The full [Tel Aviv dispatch rehearsal](../backend/README.md#tel-aviv-dispatch-rehearsal) passed locally, and [Tel Aviv dispatch](https://clearpath-hackatonintel.onrender.com/simulator/tel-aviv/dispatch) is live on Render. The hosted check used viewer access. A presenter can unlock the report and approval controls to run the rehearsal.

## User follow-up · Keep the team demo guide current

> keep adding user relevant info to user.md so that all  the team can demo and use the product.

### Decisions

- The user designated `user.md` as the ongoing guide for product use and demos. Codex placed the presenters' Tel Aviv steps before local setup and kept the signed-in Manhattan and Android rehearsal links.

### AI contribution

- Added the live and local Tel Aviv entry points, viewer and presenter instructions, the fleet bases, the Hebrew Jaffa Road report, expected statuses, reset instructions, and a quick standalone road-closure walkthrough. [Team demo guide](../user.md#demo-tel-aviv-on-render)

### Independent checks

- Verified the deployed release, both city maps, fleet listing, and viewer permissions through the hosted smoke check. Checked that the guide's repository-relative links resolve and that Git reports clean diff whitespace. [Judging checkpoint](../docs/rubric.html#c3)

### Session result

The team's [user guide](../user.md) now includes both Tel Aviv rehearsals and the pre-demo checks.

## User follow-up · Local URLs and a full hosted rehearsal

> 1. On my client - running to localhost:8003 (maybe it's old?) [`http://127.0.0.1:8003/dispatch/reports`](http://127.0.0.1:8003/dispatch/reports) I get "Which single supported Manhattan location should this report use". is there a different url for TLV?
> 2. can you run the whole Tel Aviv dispatch demo on Render with Playwright, from unlocking presenter access to the ambulance arriving, and update user.md if any steps are missing?
>
> I'm not sure a get it - the launch switches on the dispatch localhost determine if it's TLV or new-york? (while on simulator is by URL termination) ? ? ??

### Decisions

- The user asked how the URL and startup configuration relate and requested an authorized hosted rehearsal. Codex used the Jaffa Road ambulance example at the running demo defaults and paused the hosted scene on arrival.

### AI contribution

- Traced the Manhattan Copilot, Manhattan dispatch-mode switch, and dedicated Tel Aviv paths. Started an additional loopback-only process on port 8005 for the current Tel Aviv page.
- Added a local URL reference, the clean starting state, the arrival indicator, and the pause and reset choices. [Team guide](../user.md) · [Judging checkpoint](../docs/rubric.html#c3)

### Independent checks

- The existing process on port 8003 returned 404 for the Tel Aviv dispatch page. The fresh process on port 8005 returned 200 and reported six available vehicles and local controls.
- Playwright unlocked the deployed presenter UI, selected the Hebrew Jaffa Road report, and reviewed both ambulance choices. Ambulance 2 at Nahmani showed an 84-second modeled drive estimate. Approval showed the running trip, one dispatched ambulance, and five available units. Arrival was displayed at 1 minute 31 seconds of simulated time, and the panel returned to six available units.

### Session result

The [Render demo](https://clearpath-hackatonintel.onrender.com/simulator/tel-aviv/dispatch) was paused on the completed Jaffa Road dispatch. The [updated guide](../user.md#which-local-url-should-i-use) explains how to open the Tel Aviv workflow locally.
