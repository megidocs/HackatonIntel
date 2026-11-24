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
