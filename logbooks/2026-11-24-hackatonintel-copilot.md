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

- Queried Supabase Auth's provider settings and prepared the [Google OAuth and Rescue enrollment guide](../docs/google-rescue-enrollment.md) with the exact project callback. Asked for the selected Google accounts and whether there is already a ClearPath OAuth client. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Hackathon-supa reports Google disabled and email enabled. ClearPath reads roles from the database and requires an active rescue assignment before accepting a priority request. [Dispatch guide](../docs/dispatch.md) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Google sign-in and the individual enrollments await the Google OAuth client setup and the selected accounts. The existing demo sign-in is available for the final-phase rehearsal. [Rubric criterion 4](../docs/rubric.html#c4)
