# HackatonIntel development log

The original prompt below records where the log was first filed. The project’s evidence now lives in HackatonIntel’s own logbook.

## User prompt

> new extended docx was updated. Update the AGENTS to reference it (and update the md version for it).
>
> add this section to AGENTS.md - we must start documenting our process:
>
> In `Maagar-meta/logbooks/`, record the user prompt under a level-two heading, followed by level-three headings for decisions, AI contribution, independent checks, and the session result. At each checkpoint, link the relevant evidence to `Maagar-meta/docs/rubric.html`. Keep teacher vetting qualitative.

### Decisions

- The user selected the extended Word document as the source and requested an editable Markdown copy. The [editable specification](../docs/specification.md) remains the place to edit the spec. `HackatonIntel/AGENTS.md` links to both versions. The six learning components in section 6 state what students are expected to demonstrate. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Codex converted the Word headings, lists, tables, Mermaid diagram, and JSON example to Markdown. The overview table names each technology family and uses filled and empty squares so its classifications and scope ratings can be read without color. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Compared the Markdown text with text independently extracted from the Word document. Verified 256 text items outside the Mermaid diagram, exact diagram source, five tables, 75 list items, and valid JSON. Checked that all three project-reference links in `AGENTS.md` resolve and that `git diff --check` passes. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The updated spec and process directions are in HackatonIntel. This entry records the conversion and its checks. Teacher vetting will be recorded as qualitative observations when it takes place. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt

> we just got an updated spec with dev phases
> integrate this to the repo.

### Decisions

- Use `HackatonIntel/docs/specification.md` as the current specification and keep the earlier Word reference linked from `AGENTS.md`. Retain milestones 1–7 and add the Dispatcher Copilot as milestone 8. The expanded section defines the skills and evidence expected for the Copilot. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Codex located the ClearPath document behind the pasted browser wrapper, compared the update with the repository spec, and converted the new material into Markdown. The implementation milestones are project requirements from the source. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Compared normalized text from the rendered source against the updated overview table, section 6.7, and all eight milestones. Verified the training-component count against the seven subsections, checked the links in `AGENTS.md`, and ran `git diff --check`. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The spec now covers the Copilot's six tools, tool-call limit, dispatcher approval, manual fallback, and evaluation against a baseline. Teacher vetting remains qualitative. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Correction to the logbook location

> you dumb fuck. we are working on a different project here - this Hackathon repo is not the same as Maagar. We are running 2 different submissions, one with this Simulator of lights here with the android project of the vehicle that controls the lights, and another which is  Maagar. fix this mess.

The user then asked for this correction to be included in the record.

> and document this stupid error as any other prompt and final response in the logbook.

### Decisions

- HackatonIntel is the ClearPath AI submission for the traffic-light simulator and the Android vehicle project that controls the lights. Maagar is a separate submission. HackatonIntel’s evidence belongs in its own `logbooks/` directory, with links to its own copy of the rubric. [Rubric criterion 4](../docs/rubric.html#c4)

### AI contribution

- **Error.** Codex treated the `Maagar-meta/logbooks/` path in HackatonIntel’s project instructions as the correct destination without reconciling it with the active project. Two HackatonIntel records ended up in Maagar, and Codex reported the digest as complete while linking to the wrong repository. The original final response is quoted below, with the obsolete hyperlink shown as plain text. [Rubric criterion 4](../docs/rubric.html#c4)

  > Added Amit’s ClearPath AI session to the logbook. It preserves all nine prompts in order, summarizes each Claude reply, and traces how the discussion shaped the updated spec.
  >
  > The entry records Claude’s recommendation, Amit’s choice of the Dispatcher Copilot, and the planned comparison against a shortest-ETA rule. I checked the nine prompts against the supplied transcript and verified the spec references and rubric links.

- **Correction.** Codex moved both HackatonIntel records out of Maagar and corrected [HackatonIntel’s project instructions](../AGENTS.md) to identify the submission and its local logbook. The migrated entries link to HackatonIntel’s [specification](../docs/specification.md) and rubric. [Rubric criterion 4](../docs/rubric.html#c4)

### Independent checks

- Compared the moved Amit digest with its original and confirmed that all nine prompts and reply summaries carried over. Checked both entries’ local links and rubric anchors, confirmed the two misplaced files were removed from Maagar, and verified the Maagar kickoff log against its pre-move contents. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Both files are in the HackatonIntel logbook. This entry preserves the error, the user’s correction, the original completion claim, and the final response below. [Rubric criterion 4](../docs/rubric.html#c4)

#### Final response

> I filed two HackatonIntel records in Maagar. I moved both into HackatonIntel’s logbook and corrected the project instructions to identify ClearPath AI as the traffic-light simulator and Android vehicle submission.
>
> The correction entry records the mistake, your prompts, the original response, and this final response. Amit’s digest still contains all nine prompts and reply summaries.

## User prompt · Commit and push

> commit-push

### Decisions

- Include the updated ClearPath AI specification, project instructions, Amit session digest, and development log in one HackatonIntel commit. Use the current branch, which tracks the HackatonIntel repository on GitHub. [Rubric criterion 4](../docs/rubric.html#c4)

### AI contribution

- Review the pending changes, stage the four project files, and publish the documentation commit to the tracked branch. [Rubric criterion 4](../docs/rubric.html#c4)

### Independent checks

- Reviewed the specification diff and confirmed that the logbook files and the project's rubric are in HackatonIntel. The staged diff is checked for whitespace errors before committing. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- This commit records the Dispatcher Copilot requirements and the HackatonIntel development history together. GitHub's branch history provides the publication record. [Rubric criterion 4](../docs/rubric.html#c4)\n