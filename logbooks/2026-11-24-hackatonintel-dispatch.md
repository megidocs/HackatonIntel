# HackatonIntel · Milestone 5 database and security

## User prompt · Continue next phase

> continue next phase.

### Decisions

- Continue with milestone 5 in the [specification](../docs/specification.md) using the existing Hackathon-supa Free project and local Redis. The agent chose a least-privilege direct PostgreSQL connection and Supabase Auth token verification. Dispatch configuration is optional for the standalone simulator. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added the [schema migration](../supabase/migrations/20261124154000_clearpath_dispatch.sql), dispatch lifecycle and role checks, priority-request audit, temporary position validation in Redis, and an integration check. The [runbook](../docs/dispatch.md) includes the ERD, SQL queries, and threat checks. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Ran the integration check with actual PostgreSQL and Redis instances in WSL and a stubbed Supabase Auth response. The check enforced private roles, rejected duplicate active assignments across concurrent requests, persisted one priority audit per request, and rejected stale, repeated and implausible positions. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Dispatch and security behavior verified locally. Hosted schema and Auth setup have a separate verification checkpoint. [Rubric criterion 4](../docs/rubric.html#c4)

## Milestone checkpoint · Apply and verify the hosted schema

### Decisions

- Apply the versioned migration manually in the existing Hackathon-supa project and keep production auto-deploy off. Leave the restricted database role without login until the administrator provisions its credential. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Applied the [migration](../supabase/migrations/20261124154000_clearpath_dispatch.sql) in the Supabase SQL Editor. Started the Redis demo instance on the laptop and documented the Free session-pooler settings and the remaining credential and demo-enrollment steps. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Supabase reported six private tables with row-level security, no schema access for public API roles, and a disabled login for `clearpath_app`. The project had no Auth accounts or ClearPath enrollments. Verified the pooler's TLS hostname and chain with the CA downloaded from Supabase, and verified Windows can reach Redis on `127.0.0.1:6379`. Both [dispatch CI](https://github.com/megidocs/HackatonIntel/actions/runs/45406634142) and [simulator CI](https://github.com/megidocs/HackatonIntel/actions/runs/45406634269) passed. Public HTTPS served revision `8705fc2`. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The private schema is in place on Supabase Free with production auto-deploy off. The public simulator remains available. A hosted end-to-end dispatch rehearsal still requires the database credential and enrolled demo Auth accounts. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Test vehicle authentication from the emulator

> is there a way to test security vehicle user's auth from the Emulator, towards the production simulator? or do you need to [@Computer](plugin://computer-use@openai-bundled) to implement additional setup?

### Decisions

- Distinguish the existing public presenter authorization check from a Supabase rescue-account test. Use an emulator browser against the configured FastAPI dispatch API before adding a native Android sign-in screen. Keep the public simulator available for the presentation. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Inspected the Android rescue client, the dispatch API, and the signed-in Supabase Auth dashboard using Computer Use. Identified the required database login and demo roles, and the additional runtime configuration required if the test targets the public Render service itself. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Render returned `200` for health with release `8705fc2`, `403` for an anonymous empty presenter command, and `503` for `/dispatch/me` with dispatch storage disabled. The Auth dashboard displayed no signed-up users. The Android client currently sends the presenter header and has no Supabase sign-in flow. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Presenter authorization can be rehearsed from Android against Render today. Testing a vehicle user's JWT and active assignment requires provisioning the restricted database login and enrolling demo accounts. The local FastAPI setup can verify real Supabase identities without enabling dispatch on the public demo. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Provision demo accounts and keep the local environment private

> you can create a few demo accounts. leave that env file out of repo (updated .gitignore) but tell us where it is locally in user.md
> commit-push and continue to next phase.
>
> tell me the login command and I'll sign-in to the cli. if cli is not installed install it.
>
> we are now logged it.

### Decisions

- The user approved demo-account creation and signed in with `npx.cmd --yes supabase login`. The agent targeted only Hackathon-supa and provisioned dispatcher, rescue, and citizen identities. The signed-in rehearsal uses FastAPI on the laptop. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Enrolled the three accounts, added one rescue unit, enabled the restricted database login, and saved only the demo credentials and runtime settings in the ignored `.env.dispatch.local` file. The [partner guide](../user.md) records its path without credentials, and the [dispatch guide](../docs/dispatch.md) documents the emulator and laptop setup. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Verified a TLS-checked login to PostgreSQL as `clearpath_app` and obtained real Supabase JWTs for each demo account. The dispatcher opened and assigned a synthetic incident, the assigned rescue request was accepted, the citizen and arrived rescue requests returned `403`, and the event was closed. Confirmed Git ignores `.env.dispatch.local`. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The hosted authentication and dispatch checks now pass from the demo laptop using Supabase Free. Render continues to serve the public simulator. Milestone 6 proceeds in the report-models workspace. [Rubric criterion 4](../docs/rubric.html#c4)
