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

## User follow-up · Restart the report app on port 8003

> Can you restart the server on port 8003 with the updated app so I can choose Tel Aviv at the same /dispatch/reports URL I’ve been using? I think I already chose (I had the dropdown) but still got this stupid unrelated message "Which single supported Manhattan location should this report use?" a few seconds after clicking the `propose dispatch`

### Decisions

- The user authorized restarting port 8003. Codex replaced the existing loopback listener and reused the configured dispatch database, Redis, and local report model.

### AI contribution

- Identified the old listener by its executable and app arguments. Started the current checkout at the same URL and checked the report form through Playwright.

### Independent checks

- Before restart, port 8003 returned 404 for the signed-in Tel Aviv map. After restart, Playwright confirmed `city: tel-aviv` in the submitted proposal, received a Jaffa Road proposal listing an ambulance from Nahmani, and opened the returned map URL. The test draft was rejected without assigning a vehicle. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

The updated [signed-in report app](http://127.0.0.1:8003/dispatch/reports) is available at the original localhost URL.
