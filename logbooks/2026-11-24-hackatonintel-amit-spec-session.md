# HackatonIntel logbook · Amit’s ClearPath AI specification session

Recorded 24 November 2026. The nine prompts below preserve Amit’s wording, with list markers and whitespace adapted to Markdown. Each Claude reply is summarized alongside its prompt. The shared snapshot is the source for the exchange. [Amit’s shared Claude session](https://claude.ai/share/745edb7e-6839-427e-9783-875fec181007)

## User prompt

> this is the session Amit held to reach our updated spec. It's essential that the logbook will document this thought process (prompts and anwers). digest and document this.

### Decisions

- **Keep the capstone broad and make each topic demonstrable.** Amit first asked for projects spanning the mobile app, server, device sensors, camera, operating systems, networking, security, an ML model students train, and a language-model interface. Once his team had chosen ClearPath AI, he brought its existing spec and named six areas to deepen. He stated a preference for a language model and left room for a classifier. Claude turned each area into requirements and a deliverable students could explain in their defense. [Rubric criterion 1](../docs/rubric.html#c1)
- **Make the coverage visible.** Amit carried the color-coded overview from the five-project comparison into the ClearPath spec. Claude’s scope ratings were estimates of how central each area was. Its repeated concern about the workload led it to suggest teams of two or three or a simpler 2D simulator. The exchange leaves team size, simulator scope, and the platform decision open. [Rubric criterion 1](../docs/rubric.html#c1)
- **Choose the dispatcher copilot.** Amit asked to see five agent concepts before adding one, then chose option 2. Claude had favored the simulator testing agent, alone or together with the copilot. Amit gave no further rationale in the snapshot. Claude had identified continuity with the existing report-parsing feature in §6.6 as a strength of the copilot. The resulting §6.7 gives the copilot proposal and draft permissions and keeps dispatch under the human dispatcher’s approval. [Rubric criterion 4](../docs/rubric.html#c4)

### AI contribution

#### 1. Explore five capstone ideas

> הצע לי 5  הצעות פרויקט שהוא "האמא" של כל הפרויקטים.  הפרויקט מכיל:
> אפליקציה לטלפון
> שרתים
> חיישנים כגון gps, מצפן, ועוד.
> מצלמה
> כמו כן מכיל את נושאי הלימוד האלה:
> מערכת הפעלה
> תקשטרת אינטרנט ו פרוטוקלים כדוגמת http json
> security/cyber
> אימון מודל ( ml)
> ממשק למודל שפה

**Claude’s reply.** It proposed an orienteering game with anti-cheat, a field infrastructure inspector, a hiking companion with SOS, an orchard plant-disease detector, and an indoor navigation assistant for visually impaired users. It highlighted a different constraint for each, including GPS cheating, dataset collection, connectivity, real-world image quality, and safety. It recommended a required core of app, server, camera, and trained model, with smaller modules for the remaining topics. It also proposed making HTTP, JSON, and authentication visible through a student-built server and asking students to justify both models.

#### 2. Turn the concepts into a shareable document

> סדר לי את כל הפרויקטים במסמך מעוצב הניתן לשיתוף.  בפתיח, ציין את כל הנושאים הטכנולוגים הבאים לידי ביטוי

**Claude’s reply.** It reported preparing an editable document with an opening table of nine technology topics, guiding principles, five proposal sections, and a closing comparison. It described the ratings as its own judgment. [Five capstone proposals document](https://claude.ai/artifact/EZZSMy5FB5PQbWqirP8PAy)

#### 3. Add a visual system

> השתמש בשפה עיצובית.  צבעים שונים

**Claude’s reply.** It used blue for app and device topics, green for infrastructure, red for security, and purple for AI. It used traffic-light colors for difficulty and orange for risk. It reported that the editor limited color to table cells and seven palette choices.

#### 4. Package the proposals as an artifact

> צור כארטיפקט הניתן לשיתוף

**Claude’s reply.** It created a page with a topic-by-project grid, one card per proposal, and comparison bars for build difficulty, security depth, and ML difficulty. It described the artifact as private at the time and said it had yet to preview it in a browser. [Capstone proposals artifact](https://claude.ai/artifact/HW9WTtn7r7moZze7Fo1ksZ)

#### 5. Expand the chosen ClearPath AI spec

> אני מצרף מסמך אפיון של הפרויקט שבחרנו:
> אני רוצה שתרחיב את האפיון כך שיכיל גם את רכיבי ליבה האלה :
> SECURITY
> התיחסות לנושא PEFORMANCE
> מבנה המחשב
> הבנה של עקרונות בסיסיים של  "בסיס נתונים"
> תקשורת -  בין מחשבים, ותקשרות ב אינטרנט.
> מרכיב של הבנה של עקרונות פעולה של מודל שפה
> או  מודל סיווג (עדיף שפה), דרך שילוב שימוש ב מודל שפה, אולי גם בנייה של מודל סיווג.

**Claude’s reply.** It reported adding §6.1–§6.6 and a defense deliverable for each area. The new material included a threat model and location privacy, measurable performance targets, choices involving CPU and GPU, threads and memory, a relational database alongside Redis, and the roles of HTTP, WebSocket, TCP, UDP, and push. For AI, it proposed extracting structured data from free-text incident reports and comparing that LLM with a student-trained classifier. It moved milestones to §7 and added stages 5–7. It also flagged background notification delivery, the workload, the risk of testing on LLM-written examples, and the possible jump from Android/Java to React Native or Flutter.

#### 6. Apply the overview design to ClearPath

> בדומה ל 5 ההצעות שנתת קודם,  הוסף תקציר (צבעוני) בתחילת המסמך - שמראה איזה תחומי ליבה טכנולוגים הפרויקט מכסה

**Claude’s reply.** It reported adding an opening table covering 11 technology areas across five color families, including a new algorithms family. Each row described the contribution, identified a spec section, and rated the area’s centrality on a 1–3 scale. Claude again raised the workload concern.

#### 7. Compare five ways to include an agent

> הוסף  עוד מרכיב לאפיון - שימוש בסוכן או סוכנים (AI) כחלק מהתוצר.  הציע לי קודם 5 אפשרויות.

**Claude’s reply.** It defined the proposed agent as a tool-using loop with state and a stopping condition. It set the agent outside the 200 ms update loop and reserved dispatch and signal control for other actors. Its five proposals were simulator testing, a dispatcher copilot, post-incident review, security monitoring, and multiple agents for simultaneous incidents. It weighed measurable simulator outcomes, automation bias in dispatch, read-only access for review, untrusted log input in monitoring, and the need to justify multi-agent complexity against a standard assignment algorithm.

#### 8. Add Amit’s selected dispatcher copilot

> בחרתי ב 2.  הוסף למסמך האפיון.

**Claude’s reply.** It reported adding §6.7, a twelfth overview row, and milestone 8. The copilot uses a five-step workflow, six tool definitions, and a maximum of eight tool calls. It presents a recommendation and two alternatives. The dispatcher can approve, edit, or reject, and the manual workflow remains available on failure. The spec sets a five-second target for proposals and calls for 30 scenarios against a rule that picks the available vehicle with the shortest ETA. Claude named mixed vehicle needs and duplicate reports as cases to test for added value. It explicitly allowed the student to conclude that the simple rule performed as well. [Rubric criterion 2](../docs/rubric.html#c2)

#### 9. Move the revised spec into Claude Docs and report conversion changes

> Open this in Claude Docs, copied word for word with your edits, and tell me anything that didn’t carry over, like a header or footer.

**Claude’s reply.** It reported carrying over the text, tables, and lists, including §6.1–§6.7 and the new milestones. It said the Word file had no headers, footers, page numbers, or footnotes. It identified changes to colors, scope squares, fonts, the A-star formula, the diagram and JSON formatting, and an automatically added title line. It also flagged two spacing defects copied from the source. [ClearPath AI in Claude Docs](https://claude.ai/artifact/3uLydZgU4w82z4HZ9jk8ST)

### Independent checks

- **For this logbook.** Counted nine prompt and reply pairs in the supplied HTML and retained their order. Cross-checked the design outcomes against the project’s editable specification, [editable specification](../docs/specification.md). It contains the 12-area overview, sections 6.1–6.7, and eight milestones. Section 6.7 confirms the six tool definitions, eight-call limit, human approval, five-second proposal target, ten-second manual fallback, and 30-scenario comparison. Claude’s claims about Word-to-Docs fidelity are recorded as its report. [Rubric criterion 3](../docs/rubric.html#c3)
- **Checks specified for the build.** Section 6.6 calls for comparing both models on the same held-out set, including human-written incident reports, and measuring accuracy, latency, and cost. Section 6.7 calls for scenarios with expected dispatch decisions set in advance and a comparison against the shortest-ETA rule. These are test plans. The session records no implementation measurements or teacher vetting. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The session produced an expanded design for ClearPath AI, with requirements the student can demonstrate, a dispatcher-approved agent, and a development milestone for building and evaluating it. Amit’s explicit choices and Claude’s design proposals are captured in the turns above. The repo’s format conversion and integration are documented in a separate entry. [Repository integration log](2026-11-24-lenovo-hackatonintel.md) · [Rubric criterion 4](../docs/rubric.html#c4)
