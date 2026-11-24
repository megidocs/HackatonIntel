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

## User prompt · Teacher and student guidance

> part of our product must be TeacherAndStudentguidance in C:\Users\LENOVO\Documents\Jupiter Notebooks\HackatonIntel\TeacherAndStudentguidance
>
> התוכן הזה יהווה הנחיות  פדגוגיות למורה.  מלבד התוצר - תהליך הלמידה

The user added this requirement while the guidance was being written:

> התוכן הזה יהווה הנחיות  פדגוגיות למורה.  מלבד התוצר - תהליך הלמידה יכיל את מרכיבים פדגוגיים נוספים (למשל -   התלמיד צריך לשלוט בתהליך פיתוח התוצר ולהבין אותו.   הערכה:  התלמיד חייב  לצרף הדיאלוגים עם  ל AI לקבצי הפרויקט -.)

### Decisions

- Treat the learning process as part of the product. The guidance follows the eight milestones in [specification section 7](../docs/specification.md#7-שלבי-פיתוח-מוצעים-milestones) and adds an opening phase and a defense phase. [Rubric criterion 4](../docs/rubric.html#c4)
- Give every phase the same five parts: core concepts, what AI makes possible, a checkpoint against evidence, a short check without AI, and common mistakes. This maps each phase to rubric criteria 1 to 3. [Rubric criterion 1](../docs/rubric.html#c1)
- Write a graduate profile and a program rubric alongside the project, because the judging rubric scores the alignment between graduate profile, program rubric and model. Teacher feedback during the process stays qualitative; ratings are given at the defense. [Rubric criterion 4](../docs/rubric.html#c4)
- Make mastery of the development process a requirement alongside understanding the product. Students rebuild and run the system from scratch, explain the build order and their Git history, debug, and make a small change without AI. The program rubric gains a fifth dimension for this. [Rubric criterion 1](../docs/rubric.html#c1)
- Make attaching the full AI dialogues to the project files a submission threshold. Dialogues go in `ai-dialogues/` weekly and unedited, with only secrets and personal data masked. Each AI log entry links to its dialogue, and the teacher samples dialogues against the log. [Rubric criterion 4](../docs/rubric.html#c4)
- Write the guidance in Hebrew, matching the specification and the judging rubric.

### AI contribution

- Claude drafted five Hebrew documents in [TeacherAndStudentguidance](../TeacherAndStudentguidance/README.md): an index, a [teacher guide](../TeacherAndStudentguidance/teacher-guide.md), a [student guide](../TeacherAndStudentguidance/student-guide.md), a [graduate profile and program rubric](../TeacherAndStudentguidance/assessment-rubric.md) with a bank of no-AI questions, and [templates](../TeacherAndStudentguidance/templates.md) for the AI log, checkpoints, decisions, weekly reflection and the `ai-dialogues/` folder. The checkpoints and questions draw on sections 6.1 to 6.7 of the specification. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Checked that every relative link in the new documents resolves to an existing file and every in-page anchor matches a heading. Teacher review of the pedagogical content is still pending. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- HackatonIntel now includes teacher and student guidance on the learning process, with process mastery, attached AI dialogues as a submission threshold, a graduate profile, a program rubric, and an alignment table linking both to the project and the judging rubric. Nothing is committed yet. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Core-knowledge assessment skills

> Create SKIILS that will be used to  assess the CORE knowledge of the student. Use the design spec documents in this project.

### Decisions

- Build the assessment as Claude Code skills in `.claude/skills/`. One entry skill and a shared protocol serve eight topic skills. Seven follow the specification's core learning components (sections 6.1 to 6.7), and one covers routing, green wave and Geofence (sections 3.1 to 3.3). [Rubric criterion 1](../docs/rubric.html#c1)
- Reconcile an AI examiner with the rubric's requirement that core knowledge is checked without AI. In assessment mode the skill only asks and records. It gives no hints, chooses new numbers and scenarios each session, and asks "why" after "what". Its rating is a suggestion; the teacher decides, and confirms formal assessments with a short oral follow-up. [Rubric criterion 1](../docs/rubric.html#c1)
- Each session writes an evidence report to `assessments/<student>/`, and the student attaches the conversation to `ai-dialogues/`. This links the skills to the attached-dialogue threshold. [Rubric criterion 4](../docs/rubric.html#c4)

### AI contribution

- Claude wrote the [shared protocol](../.claude/skills/assess-core-knowledge/protocol.md), the [entry skill](../.claude/skills/assess-core-knowledge/SKILL.md), and eight topic skills. Each topic skill lists core concepts and gives a question bank across five question types, with what a good answer includes, common misconceptions, and topic-specific rating levels. The teacher guide and the guidance index now link to the skills. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Claude Code registered all nine skills in this session. Every relative link and in-page anchor in the skills and guidance resolves. No assessment session has been run with a student yet, and the technical answer keys await teacher review. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Teachers and students can run `/assess-core-knowledge` in practice or assessment mode for eight core topics. Nothing is committed yet. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Slide deck and the T model

> create 3 slides presentation deck with
> מדריך פדגוגי למורה
> פרופיל הבוגר ומחוון המגמה
> תבניות

> FIX THE SLIDES to format RightToLeft

> ATTCHED file with "T model"  .  Learn it.  Add additional slide that shows how this model is implemented in our project.

### Decisions

- Present the guidance as a Hebrew deck: one slide each for the teacher guide, the graduate profile and program rubric, and the templates. [ClearPath AI pedagogical deck](https://claude.ai/artifact/3L7NETeH58eRGv3aj2tF8r) [Rubric criterion 4](../docs/rubric.html#c4)
- Make right-to-left explicit, because the Slides format drops `direction: rtl`. Text is right-aligned and wrapped in Unicode right-to-left embedding marks, rows and grids list their children right to left, and list markers became badges on the right.
- Map the T model, from the PDF the user supplied, onto ClearPath AI in a fourth slide. The core pillar A is the computer-science core in specification section 6, tested without AI as a pass threshold. Arm B is the in-field work AI makes possible: the Manhattan simulator, the Android green-wave app, and the LLM and dispatcher agent, each verified by measurement or baseline. Arm C brings in traffic engineering, emergency medicine and GPS physics. The X deep dive is one component per student, with the green wave as the example across technological, scientific, ethical and historical facets. The weights follow the model document's proposed rubric. [Rubric criterion 2](../docs/rubric.html#c2)

### AI contribution

- Claude built and published the deck, rewrote it for right-to-left, read the T-model PDF, and added the T-model slide with speaker notes. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- In a local preview, measured element positions on every slide: the order runs right to left, the T-model boxes sit B right, A centre, C left and X under A, and no content passes the slide's lower margin. The deck has not been viewed on claude.ai, because the built-in browser required a sign-in. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The deck has four slides, the last showing how the T model is implemented in ClearPath AI. The deck is private until the user shares it. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Align the guidance with the T model

> Yes, align guidance

### Decisions

- Rebuild the program rubric on the T model's five components and four-level scale: A, domain knowledge without AI (35%); X, deep dive (20%); B, in-field knowledge with AI (25%); C, out-of-field knowledge with AI (10%); and transparency (10%). The weights are the model document's proposal. [Rubric criterion 1](../docs/rubric.html#c1)
- Fold the earlier dimensions into the T components. Development-process mastery joins A, because it is tested without AI. Critical checking of AI output joins B, and ownership and documentation join transparency. [Rubric criterion 3](../docs/rubric.html#c3)
- Add a second threshold alongside the attached dialogues: a score of 1 on A fails the project, as the T model requires. X and C become required for every student, chosen at the opening phase, where the judging rubric treats them as bonuses. [Rubric criterion 4](../docs/rubric.html#c4)
- Keep a copy of the T-model document in this repository at [docs/T-model-STEM-final-project.pdf](../docs/T-model-STEM-final-project.pdf), so the guidance can link to it.

### AI contribution

- Claude rewrote the [graduate profile and program rubric](../TeacherAndStudentguidance/assessment-rubric.md), and added a T-model overview, deep-dive examples and the exam checks to the [teacher guide](../TeacherAndStudentguidance/teacher-guide.md). It added a T-model self-check to the [student guide](../TeacherAndStudentguidance/student-guide.md), a deep-dive template to the [templates](../TeacherAndStudentguidance/templates.md), and the model to the guidance index. The assessment skills now suggest an A rating from 1 to 4, and deck slide 2 shows the T-model rubric. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Checked that every relative link and anchor in the guidance and skills resolves, and that no reference to the old five-dimension, 1–5 rubric remains. Teacher review of the new level descriptors is pending. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The guidance, skills and deck now assess the project by the T model. Nothing is committed yet. [Rubric criterion 4](../docs/rubric.html#c4)

## User prompt · Commit message and logbook review

> prepare a short commit message. make sure logbooks are containing all this work process we did here

### Decisions

- Prepare one commit for the session's work: the guidance folder, the assessment skills, the T-model reference copy and this logbook. The T-model PDF is a third-party document, so including it is left to the user. [Rubric criterion 4](../docs/rubric.html#c4)

### AI contribution

- Claude checked that every prompt in this session has its own entry: the guidance and its mid-task additions, the assessment skills, the deck with its right-to-left fix and T-model slide, and the T-model alignment. It drafted the commit message. While adding the guidance entry, Claude also removed a stray literal `\n` left at the end of this file by an earlier edit. [Rubric criterion 4](../docs/rubric.html#c4)

### Independent checks

- Compared the logbook's prompt headings with the session's prompts, and found each one recorded with decisions, AI contribution, checks and result. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The logbook records the full session. The commit waits for the user's approval. [Rubric criterion 4](../docs/rubric.html#c4)
