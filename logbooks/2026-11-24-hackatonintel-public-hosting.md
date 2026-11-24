# HackatonIntel · Public simulator hosting

## User prompt · Propose the missing public hosting infrastructure

> I don't get it. is our spec not taking into about the server frontend? is supabase incapable of this? what have we done here?
>
> is there a missing brick in the infra plan? if so, what do you propose? I have accounts on netlify and render. can open on railway too

### Decisions

- Recommend one Render Free Python web service serving both FastAPI and the existing frontend over HTTPS. Keep the laptop deployment and use Supabase Free for persistent PostgreSQL when the database milestone is implemented. Public hosting remains a proposal pending the user's decision. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Mapped the existing spec to the live code. The missing public component is an application host and deployment pipeline. Proposed building with the pinned prepared graph, testing before deploy, and smoke-testing the public routes. The current state is shared across browsers, so public access also needs a presenter-controlled session or isolated visitor sessions. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Confirmed that §4 specifies the frontend and FastAPI on the laptop, with the public endpoint deferred. Inspected FastAPI's static routes and single in-memory simulator. The saved graph is about 7.1 MB, and a local state response at the default density was 26,558 bytes before compression. Reviewed the provider docs for Render's limits, Netlify Server's Node runtime, Railway's recurring free credit and Supabase Edge Functions. [Render limits](https://render.com/docs/free) · [Netlify Server runtime](https://docs.netlify.com/build/server/get-started/) · [Railway Free](https://docs.railway.com/pricing/free-plan) · [Supabase Edge Functions](https://supabase.com/docs/guides/functions) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The proposed Render preview needs a Linux memory and bandwidth check on the free instance, a $0 usage configuration, and a deployment smoke test. The simulator and Supabase settings were unchanged by the review. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Prepare the public Render Free deployment

> go ahead with Render Free for FastAPI and the frontend. set up CI/CD, verify the public simulator URL, update the spec and user.md, log everything and commit-push. keep Supabase on Free with auto-deploy off. I'll approve where needed.
>
> I signed us in to Render. you can add this critical missing brick and continue.
> keep documenting the progress, committing and syncing
>
> we need to add render to github like we did with supabase. tell me what URL Amit (the owner) should open.

### Decisions

- Use a single Render Free Docker web service for the simulator and API with deploys after CI checks pass. The prepared Manhattan graph is bundled at build time. Anonymous viewers have read-only access to the shared simulation, and only presenters can edit it. Keep the existing Supabase project on Free with auto-deploy off. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added the Docker build, Render service definition, GitHub CI checks, a public HTTPS smoke check, and presenter controls. Compressed the responses and slowed polling while paused. The deployment packages the attributed OpenStreetMap graph with a checksum. Updated the [spec](../docs/specification.md), [partner guide](../user.md), and [deployment guide](../deploy/README.md). [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Ran the hosted-mode smoke test on the laptop and verified public read-only mode, protected writes, and identical compressed and uncompressed map responses. Presenter-authorized routing, simulation, and green-wave regression checks all passed. Render’s signed-in GitHub picker showed no HackatonIntel result. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The CI and deployment files are ready for the Linux CI run. Gave the user the [Render GitHub App installer](https://github.com/apps/render/installations/new) for Amit to grant access only to HackatonIntel. The public URL is pending service creation and verification. [Rubric criterion 4](../docs/rubric.html#c4)
