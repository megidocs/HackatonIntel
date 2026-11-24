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
