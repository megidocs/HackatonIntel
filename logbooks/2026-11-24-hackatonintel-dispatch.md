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
