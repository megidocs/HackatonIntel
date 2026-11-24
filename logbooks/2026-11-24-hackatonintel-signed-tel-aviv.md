# ClearPath AI · Signed-in Tel Aviv dispatch

## User prompt

> Add Tel Aviv support to the standalone localhost /dispatch/reports app, so I can create and approve events there and see the ambulance dispatched on the Tel Aviv simulator?

### Decisions

- The user requested Tel Aviv support in the existing signed-in report app. Codex added an explicit report city and a separate Tel Aviv view for approved, stored assignments. The same attached demo fleet and database approval rules apply in both report cities.
- The signed-in Tel Aviv ambulance uses a modeled base at Nahmani. Tel Aviv report resolution uses a single supported location named in the report, including Hebrew spellings with attached prepositions. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Reused report extraction, candidate selection, approval, and simulation launch logic with the selected city’s road graph, location catalog, and modeled depots.
- Added a city selector, a link to the correct local map after approval, and the [team walkthrough](../user.md#signed-in-tel-aviv-dispatch). The approved Tel Aviv trip starts playing automatically. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The local Qwen model and Tel Aviv planner produced reviewable Jaffa Road proposals in English and Hebrew with a fixture fleet.
- In Chrome Playwright, signed into the fresh local server on port 8006, drafted a Hebrew report for Jaffa Road, proposed the registered ambulance at Nahmani, approved the stored assignment, and opened the Tel Aviv map from the approval. Verified that the vehicle appeared, traveled, and arrived. Recorded the test arrival and closed only the rehearsal incident, freeing the ambulance. The separate Tel Aviv simulated-fleet scene remained idle during the check.
- The [disposable database CI regression](https://github.com/megidocs/HackatonIntel/actions/runs/45455811978) passed, including city selection, regional route launch, and scene isolation. A local no-storage check also confirmed the standalone Tel Aviv demo remains available. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

The [signed-in report app](http://127.0.0.1:8006/dispatch/reports) and its [Tel Aviv approved dispatch map](http://127.0.0.1:8006/simulator/tel-aviv/reports) passed the local rehearsal. Feature commit `32aabf2` was pushed to `main`.
