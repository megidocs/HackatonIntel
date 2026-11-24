# HackatonIntel · Milestone 6 incident report models

## User prompt · Continue to the next phase after account provisioning

> commit-push and continue to next phase.

### Decisions

- Follow the specification's model comparison milestone. Use a free local Qwen3 model for structured suggestions and a TF-IDF logistic-regression baseline on four incident classes. The authenticated report page presents a draft for review and leaves incident creation to the dispatcher. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Added the [schema and prompt](../backend/report_extraction.py), dispatcher-only endpoint and review page, [dataset](../models/reports.py), [benchmark](../models/benchmark.py) and [notebook](../models/report_comparison.ipynb). The server checks the location phrase against the report and the bundled Manhattan graph. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Compared the two models on the same 32 synthetic reports. The LLM classified 27 correctly and the baseline 25. Initial extraction rated a trapped occupant with smoke as severity 1. After adding the explicit rubric, the same case returned severity 5 and the graph matched Fifth Avenue and 34th Street. Tested a real Supabase dispatcher JWT, a rejected citizen JWT, rejection of an invented or ambiguous location, and an unchanged dispatch board. The browser form showed the intended message for an invalid token. [Benchmark evidence](../models/benchmark-result.json) · [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Report drafting and the classifier comparison are reproducible using the [model guide](../models/README.md). The current scores use AI-authored synthetic examples and measure incident category. Student-authored evaluation and separate checks for severity, unit suggestions and location are still needed. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Explain model development for the presentation team

> LLM training and dev, as was done merits a side doc explaining in some details, so that the guys generating the slides to present give it some time and focus

### Decisions

- Write a standalone briefing for the slide team. Explain the actual classifier training and LLM development, and include the benchmark's scope and an example presenters can rehearse. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Wrote the [model development brief](../docs/model-development-brief.md) and linked it from the partner guide. It covers training data, inference, validation, comparison, a severity failure and correction, and a suggested presentation sequence. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Cross-checked the report counts, category errors, timing, and macro F1 against the [benchmark JSON](../models/benchmark-result.json), and checked the workflow against the source and the actual dispatcher and citizen rehearsals. The documented PowerShell sign-in returned a real demo access token. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The slide team has a dedicated source for the comparison, one reproducible demo, and limitations to explain. [Rubric criterion 4](../docs/rubric.html#c4)
