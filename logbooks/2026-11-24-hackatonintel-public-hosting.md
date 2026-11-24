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

## User prompt · Connect Render to HackatonIntel and publish the simulator

> we need to add render to github like we did with supabase. tell me what URL Amit (the owner) should open.

### Decisions

- Directed Amit to the [Render GitHub App installer](https://github.com/apps/render/installations/new) to select only HackatonIntel. When `megidocs/HackatonIntel` appeared in Render’s GitHub picker, used the existing access and deployed one Docker web service on Free in Frankfurt. Supabase remained on Free with automatic production deployment off. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Deployed the `ClearPath` Blueprint on `main`. Set the Render build filter to match the GitHub Actions paths after a logbook-only push appeared in Render’s deployment queue with a skipped Supabase check and no ClearPath CI check. This keeps routine documentation syncs from starting application builds. [Render build filters](https://render.com/docs/monorepo-support#setting-build-filters) · [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Verified the Hobby workspace had no card on file and the service dashboard showed Docker, Free, `After CI Checks Pass`, and `/health`. The [first ClearPath Actions run](https://github.com/megidocs/HackatonIntel/actions/runs/45400201821) passed the container, resource-limit, hosted API, routing, simulation, and signal-priority checks. The initial Blueprint deployed `8cff368`, which changes teaching material after `114ac28` and leaves the verified application files intact. An external HTTPS smoke test confirmed that revision, compressed responses, and viewer controls enforced by the API. The browser loaded the Manhattan map, showed Bellevue Hospital → Times Square at 3.16 km, and disabled Start for anonymous viewers. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The [public simulator](https://clearpath-hackatonintel.onrender.com/simulator) is live. [The partner guide](../user.md) and [spec](../docs/specification.md) record the URL and presentation access. The initial access blocker cleared once the repository appeared in Render. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Record the successful deployment and update the partner test brief

> seems like render deploy worked and is here https://clearpath-hackatonintel.onrender.com/simulator
> document this success, add the url to the user.md, and indicate how to run the project locally too.
> write there **an updated brief of what we should test** now.
> commit-push

### Decisions

- Use the bundled Manhattan graph for the local quick start so partners can rehearse against the same road data as Render. Include a public two-browser rehearsal and local tests for routing, closures, signal timing and priority. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Updated [user.md](../user.md) with the public URL, PowerShell setup and startup commands, the test brief, and links to the detailed checks and hosting log. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Started a separate local FastAPI instance with `CLEARPATH_GRAPH_PATH` pointing to the bundled compressed graph. The simulator, map asset reference, simulation state and health check responded with 4,671 nodes and 9,962 directed edges. [GitHub Actions](https://github.com/megidocs/HackatonIntel/actions/runs/45401112767) passed for `fc605e5`. Render’s deploy history showed an automatic deploy, and the public HTTPS smoke check verified `fc605e5`, compressed responses and anonymous write protection. The Supabase dashboard still displayed Free, `megidocs/HackatonIntel` and production auto-deploy off. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The public URL and local steps are ready for partners. The two-browser rehearsal in the test brief is the presenter’s manual check. The deployed revision and anonymous viewer behavior have been verified. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Confirm who signs in when connecting Render

> you said Amit should open the [Render GitHub App installer](https://github.com/apps/render/installations/new) while signed in as `megidocs`, choose **Only select repositories**, select **HackatonIntel**, and install or save.
> But now when adding render it expects us to put the render credentials... (which are mine and require me to enter through my github 3rd party auth). should I add them there on Amit's computer? I trust amit. we are only connecting this one project.

### Decisions

- The user specified that the installation should cover only HackatonIntel. The assistant advised having Amit verify that selection on GitHub as `megidocs` and having the user complete Render sign-in on their own computer. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Explained that the GitHub repository selection scopes the app installation, while signing in opens the user's Render account. If the repository stays missing from Render, check access for the GitHub account Render uses for deployments. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Checked GitHub's installation and verification instructions and Render's login and Git deployment credential rules. The installer itself blocked automated web access, so the exact screen Amit saw was unverified. [GitHub App settings](https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps) · [Render login settings](https://render.com/docs/login-settings) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Provided the account handoff steps. GitHub App access and the Render repository picker still need confirmation before the public deployment can proceed. [Rubric criterion 4](../docs/rubric.html#c4)
