# HackatonIntel agent instructions

## Permissions

Agents have full local permissions within this repository. They may read, create, edit, move, and delete project files as needed for the task. They may install project dependencies, run scripts, build and test the project, start local services, open browsers, and use network access for project work.

Agents may use local Git operations in this repository, including staging, committing, and creating or switching branches, when the task calls for them. Keep unrelated user changes intact. Ask before destructive Git operations that would discard existing work. Remote Git changes require explicit authorization.

Permissions outside this repository follow the user's workspace instructions.

## Project references

- [Extended ClearPath AI specification (Word)](docs/ClearPath_AI_%D7%90%D7%A4%D7%99%D7%95%D7%9F_%D7%9E%D7%95%D7%A8%D7%97%D7%91%20%281%29.docx) is the reference for the expanded requirements.
- [ClearPath AI specification (Markdown)](docs/specification.md) is the editable version.
- [Hackathon judging rubric (מחוון)](docs/rubric.html) is the reference used to evaluate the project. Consult it when planning features, checking project readiness, or preparing the demo and submission.

## Process documentation

In `Maagar-meta/logbooks/`, record the user prompt under a level-two heading, followed by level-three headings for decisions, AI contribution, independent checks, and the session result. At each checkpoint, link the relevant evidence to `Maagar-meta/docs/rubric.html`. Keep teacher vetting qualitative.
