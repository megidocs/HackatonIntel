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

### Session result

The full [Tel Aviv dispatch rehearsal](../backend/README.md#tel-aviv-dispatch-rehearsal) passed locally. The feature is ready for the Render rollout and hosted verification.
