# HackatonIntel · Milestone 8 dispatcher copilot

## User prompt · Complete the final phase

> continue to last phase and completion.

### Decisions

- Follow milestone 8. Reuse the local model, the verified Manhattan catalog, the existing dispatch board, and the A* engine. Gate assignments behind human review and write the selected assignments in one database transaction. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added the bounded [planning loop](../backend/copilot.py), a role-gated draft review, and a [Supabase migration](../supabase/migrations/20261124164000_clearpath_copilot.sql) for pending proposals and traces. Applied the migration in Hackathon-supa. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The local Qwen model produced a five-tool pending plan on a fixture. Supabase completed the additive draft migration. JavaScript syntax and Python compilation passed. Live review and the 30-case evaluation follow this checkpoint. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Copilot code and draft storage are in place. The presentation and verification checkpoint will document the live workflow and results. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Check Google OAuth and Rescue enrollment

> do we have oauth properly setup so we can sign it with Google? I want to designate a few users who are rescue.

### Decisions

- Verify Google sign-in directly on the existing project. Keep identity authentication and the decision to grant the Rescue role independent. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Queried Supabase Auth's provider settings, checked the exact project callback, and asked for the selected Google accounts and whether there was already a ClearPath OAuth client. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Hackathon-supa reports Google disabled and email enabled. ClearPath reads roles from the database and requires an active rescue assignment before accepting a priority request. [Dispatch guide](../docs/dispatch.md) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Google sign-in and the individual enrollments await the Google OAuth client setup and the selected accounts. The existing demo sign-in is available for the final-phase rehearsal. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Use email/password for Amit’s demo

> I did not define this project on google at all. there is no way to open this stuff on supabase without the google setup?
> I don't want to setup a new google project just for this hackathon. can we do something else or should we go back to email/pw sign-in?
>
> so give me the way Amit should login to demonstrate.

### Decisions

- Use the existing Supabase email/password provider and pre-enrolled Rescue account for the hackathon. The user supplied two addresses for later named enrollment and indicated that a new Google project is out of scope. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added direct email/password sign-in to the laptop page, a Rescue assignment view, and a read-only preview for enrolling verified accounts. Documented the [steps Amit can use](../docs/rescue-accounts.md) and the separate Android viewer and presenter behavior. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The enrollment preview found neither requested address as a verified Supabase account. The local sign-in endpoint configuration, Supabase password exchange, Rescue role, and existing unit passed with the demo account. The [live copilot trace](../docs/copilot-rehearsal-trace.json) verifies approval and the assigned Rescue unit. The dispatch regression covers rollback on unavailable units. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Amit has a documented demonstration path with the existing demo Rescue login. An administrator can grant the two individual roles after account verification. [Rubric criterion 4](../docs/rubric.html#c4)

## Final milestone checkpoint · Verify the copilot and presentation handoff

### Decisions

- Keep the copilot on the authenticated laptop service and use a bounded local PostgreSQL connection pool to reduce repeated remote connection setup. Use measured latency and the model’s weak categories in the presentation. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Completed the [copilot rehearsal and handoff](../docs/copilot.md), including the model-selected tool loop, candidate review, manual fallback, and instructions for the demo Rescue account. The browser falls back after a ten-second proposal timeout. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Across 30 synthetic scenarios, the copilot scored 22 correct and the nearest-ETA baseline 20. The copilot flagged five duplicates, selected the expected pair in two compound cases, and missed all five roadblocks. A live injection request left the dispatch board unchanged. An explicit dispatcher approval created one assignment, the Rescue account saw it, and a retry returned the same record. The test incident was closed. With a warm pool, the observed full proposal improved from 11.95 to 6.13 seconds, with 2.96 seconds in the planner. [Benchmark](../models/copilot-benchmark-result.json) · [Live trace](../docs/copilot-rehearsal-trace.json) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The final phase is ready for the local hackathon rehearsal with the pre-enrolled accounts. The five-second end-to-end proposal goal and the independent student-authored evaluation remain follow-up measurements. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-ups · Shorten and provision the Rescue demo login

> shorten the CLEARPATH_DEMO_RESCUE_PASSWORD to an easy to type short pw (lower security, I know), and same for the email.
>
> and provision these updated creds

### Decisions

- Shorten the credentials for the existing synthetic Rescue account for the live presentation. Use a short reserved-domain alias and an eight-character password under the existing Supabase password rules. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Updated the same Supabase Auth identity and replaced the two Rescue credential values in the Git-ignored `.env.dispatch.local`. The [partner instructions](../docs/rescue-accounts.md) use that file for the sign-in values. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Verified a password exchange with the replacement credentials, the same Supabase user ID and Rescue role, and the same medical unit ID. The old email/password combination was rejected. Git reports the credential file as ignored. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Amit can sign in to the laptop demo with the short Rescue alias and the password in the private configuration file. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Commit and sync

> commit, sync,

### Decisions

- Include the pending Android installation records in this sync. The Rescue credential rotation was already on GitHub in `197044c`. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Reviewed the pending [Android installation log](2026-11-24-hackatonintel-mobile.md) for the Samsung and Xiaomi demo phones. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Confirmed `main` and `origin/main` were aligned before committing. The [dispatch checks](https://github.com/megidocs/HackatonIntel/actions/runs/45419875272) and [preview checks](https://github.com/megidocs/HackatonIntel/actions/runs/45419875312) passed for the final application changes. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- This documentation commit captures the outstanding Android installation evidence and the requested sync. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Identify where the Rescue credentials are used

> tell me about this user password pair - are they used for the simulator or more on the android or both?

### Decisions

- Explain the existing login and presenter controls for each demo surface. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Checked the [dispatch sign-in guide](../docs/rescue-accounts.md) and [Android connection instructions](../mobile/README.md) against the [Android source](../mobile/lib/main.dart). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The laptop dispatch page returned HTTP 200. The public Render dispatch URL returned HTTP 404. The Android app connects to the simulation feeds with its chosen Rescue or Citizen view and uses a separate presenter code for protected priority changes. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The email and password are for the signed-in Rescue assignment view on the demo laptop. The public simulator and Android viewing flows are open. On Render, the presenter code unlocks browser controls and lets Android change priority. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Clarify what runs on Lenovo

> i want to understand we have a live simulator on Render. is the lenovo local used for a 3rd functionality?

### Decisions

- Describe the public simulation, the Android view of that same simulation, and the signed-in dispatch workflow on Lenovo. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Checked the [partner guide](../user.md), the [copilot demo steps](../docs/copilot.md), and the [Render configuration](../render.yaml). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Both simulator URLs returned HTTP 200. Each FastAPI process initializes its own live simulation state. The separate laptop dispatch rehearsal uses Supabase for accounts and assignments and runs the copilot model locally. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Lenovo adds the dispatch and copilot demo and can also host a separate copy of the traffic simulator for rehearsal. An approved laptop dispatch assignment appears in the signed-in Rescue browser view. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Walk through the dispatcher page

> I signed in to the dispatcher but I'm not sure what do I do from there? [@Computer](plugin://computer-use@openai-bundled) on your browser on the right

### Decisions

- Inspect the open tab and keep the existing Rescue session available for the second half of the rehearsal. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Matched the visible role and available unit with the controls in the [copilot walkthrough](../docs/copilot.md#run-the-demo). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Computer Use showed **Signed in as rescue** and an available medical unit. Confirmed the dispatcher form labels and the dispatcher credential variable names. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The walkthrough uses a second browser tab for the dispatcher to propose and approve a synthetic incident. The existing Rescue tab can then refresh the assignment. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Provide a report to paste

> what dispatch text can I paste in ? I'm now logged.

### Decisions

- Reuse the synthetic Bellevue Hospital report from the dispatcher rehearsal. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Provided the report text and the next button to click. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Checked the exact sample and **Propose dispatch** label against the [rehearsal instructions](../docs/copilot.md#run-the-demo). [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The dispatcher can paste the Bellevue Hospital report into **Incident report**, propose a response, and review it before approval. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Find the approved assignment

> do we expect to see something on the simulator or on the phone signed is as rescue? my current android app does not have a user password for logging as rescue

### Decisions

- Clarify what the approved assignment changes and correct the ambiguous wording about mobile sign-in in the demo guide. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Updated the [copilot guide](../docs/copilot.md) to identify the laptop Rescue browser view and describe the Android simulator feed. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Read the [Rescue assignment rendering](../frontend/public/dispatch-sign-in.js), [approval endpoint](../backend/dispatch.py), and [Android stream connection](../mobile/lib/main.dart). The browser shows the unit state, and Android connects to the simulation feed. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Refreshing the signed-in Rescue browser view shows **Active assignment** after approval. The Render simulator and native Android app continue displaying their selected simulation scenario. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Test dispatch through the Rescue view and emulator

> test this an reach a working end to end between the dispatch and what I see on the emulator or if I have to look at the simulator - tell me.

### Decisions

- Use the existing active demo assignment to check both roles and preserve the user's rehearsal state. Check the native app on the Android emulator separately. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Started the Medium Phone emulator, connected the installed app to Render in Rescue mode, and forwarded emulator port 8003 to Lenovo's dispatch service using ADB reverse. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The dispatcher and Rescue boards returned the same open medical incident and active medical assignment. The signed-in Rescue webpage displayed **Active assignment** at a phone-sized viewport. The emulator retrieved that same dispatch page over its loopback port with HTTP 200. Chrome was at its first-run screen, so the signed-in browser check was performed on Lenovo, using a phone viewport. [Rubric criterion 3](../docs/rubric.html#c3)
- The native app on the emulator showed **Connected · Paused** and the Render route at 3.16 km and 4.7 modeled minutes while the dispatch assignment was active. [Android demo guide](../mobile/README.md) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The verified dispatch flow ends at **Active assignment** in Lenovo's signed-in Rescue browser. The emulator can reach that webpage and use it after browser setup. The native app and public simulator show the separate traffic simulation. The existing assignment was preserved. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Identify the audience-facing gap after approval

> look. nothing visual happens after I click the dispatch browser is here on the right. this looks sad. not sure we see eye to eye on this. What is the audience expected to see on the simulator or on a Resquer's phone once we click Approve selected units?

### Decisions

- Explain the visible behavior of the current demo and the missing connection from approval to the shared traffic scene. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Inspected the open dispatcher tab and traced the [approval endpoint](../backend/dispatch.py) alongside the [simulator controls](../backend/app.py). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The right-hand browser showed a successful approval for one medical unit and a modeled ETA of zero seconds for the Bellevue Hospital proposal. The approval stores the assignment. The simulator's traffic state is separate. The signed-in Rescue browser can refresh to see the unit status. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Today the audience sees an approval message and can refresh the Rescue web status. The proposed audience sequence is an incident marker, a moving rescue unit on a new route, and the same route and ETA on the phone. It requires a connection between confirmed dispatch and the shared simulator, plus a scenario with different start and incident locations. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Reset the duplicate-blocked rehearsal

> now if I try again with the same text `Medical emergency at Bellevue Hospital. One adult is having a seizure. Ambulance needed.` it tells me A similar incident is already open nearby. Is this a separate event?
>
> and I cannot override and send it. so I Cannot test.

### Decisions

- Complete and close the exact approved Bellevue rehearsal to free the only medical unit and let the user repeat the report. Preserve its history and the duplicate check. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Used the existing authorized arrival and close endpoints for the known test incident. Updated the [rehearsal guide](../docs/copilot.md#run-the-demo) with the reset sequence and Times Square as a sample with a nonzero ETA. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Verified the earlier incident was closed and the demo medical unit was available. Bellevue Hospital and Times Square both returned reviewable proposals. The modeled ETAs were 0 and 284.2 seconds respectively. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The verification drafts were rejected so the demo unit stays available. The dispatcher can run the same Bellevue report again or try Times Square. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Pick a dispatch route with traffic lights

> I need a text for another dispatch that will cross some lights. probably a different location.

### Decisions

- Use Bryant Park as a different recognized incident location while keeping the demo ambulance at its Bellevue Hospital base. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Provided a synthetic medical report and calculated the route using the project’s [place catalog](../backend/report_extraction.py) and [A* router](../backend/routing.py). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- With no closures, the Bellevue Hospital to Bryant Park route is 2.56 km and 229.2 modeled seconds. It passes 14 graph points marked with traffic signals, excluding the endpoints. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The report can be pasted into dispatch. To show the lights changing, set Bryant Park as the simulator destination and run the route with the green wave enabled. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Add both sample reports to the partner guide

> add both this new text and the older `Medical emergency at Bellevue Hospital. One adult is having a seizure. Ambulance needed.` to user.md

### Decisions

- Put both reports in one copy-ready section of the partner guide. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added the [Bellevue Hospital and Bryant Park reports](../user.md#dispatch-rehearsal-reports) with the expected dispatcher, Rescue browser, and simulator behavior. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Compared both report strings against the conversation and checked the Markdown diff. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Partners can copy either example from the guide and see which steps show the assignment or traffic lights. [Rubric criterion 4](../docs/rubric.html#c4)
