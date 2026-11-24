# ClearPath model development brief for the slide team

## What the team built

A dispatcher can paste a free-text report into the local review page. It drafts an incident category, severity, a phrase naming the location, and candidate rescue units. The dispatcher checks the draft before opening an incident. The project also trains a small text classifier so students can compare a learned baseline with a zero-shot language model on the same classification task.

| Model | What we did | What it returns |
| --- | --- | --- |
| TF-IDF with logistic regression | Trained a classifier on ClearPath’s labeled reports. | One of four categories and a score for each category. |
| Qwen3-0.6B | Ran pretrained Qwen weights locally through llama.cpp. We designed the prompt, response schema and verification. The weights were kept as released, with Q8 quantization. | A structured incident draft or an unresolved field. |

For the slides, call this **training a classifier and developing an LLM workflow**. Fine-tuning a language model would update its weights on new data. The ClearPath comparison uses zero-shot inference. [Benchmark code](../models/benchmark.py) · [Model card](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF)

## Data and training

The four labels are accident, fire, medical and roadblock. The training corpus contains 256 synthetic reports made from 32 report phrasings, each combined with eight Manhattan locations. The evaluation uses 32 separately worded synthetic reports, eight per class. It includes overlapping cues such as smoke after a collision and a broken-down vehicle blocking traffic.

The classifier turns words and adjacent word pairs into TF-IDF features. This gives more weight to terms that help distinguish reports from one another. Logistic regression learns a weight for those features for each class. The notebook lets students change a sentence, inspect the class probabilities, and rerun the confusion matrix. The LLM saw the same test reports with the task prompt and schema, without examples from the classifier’s training corpus. [Dataset](../models/reports.py) · [Training notebook](../models/report_comparison.ipynb)

## How the LLM draft gets checked

1. FastAPI accepts the report from an authenticated dispatcher and sends it to the model on the demo laptop. The prompt defines the four labels and the severity scale. Inference uses temperature zero.
2. A JSON schema limits the model to a category, severity from 1 to 5, a location phrase, and candidate unit types. Missing details can be returned as null. FastAPI checks the generated response before displaying it.
3. FastAPI accepts a map location only if the model’s phrase appears in the original report and both point to the same single place in the supported Manhattan catalog. The server snaps the catalog point to the OpenStreetMap driving graph. Unrecognized or ambiguous locations require manual review.
4. The page displays the result as a draft. In the integration check, drafting left the dispatch board unchanged, and a citizen account received `403` when requesting a draft. [Prompt and validation code](../backend/report_extraction.py) · [Model logbook](../logbooks/2026-11-24-hackatonintel-models.md)

A collision near Fifth Avenue and 34th Street gave us the clearest example. The report mentioned a trapped occupant and smoke. The first prompt returned severity **1**. After we specified how immediate danger maps to the scale, the same example returned **5**, and the server matched the location to the road graph. This shows why well-formed JSON alone cannot establish that a suggestion is correct. [Model logbook](../logbooks/2026-11-24-hackatonintel-models.md)

## What the benchmark actually measured

| Model | Correct category | Accuracy | Macro F1 | Median time on Lenovo |
| --- | ---: | ---: | ---: | ---: |
| Trained classifier | 25 of 32 | 78.1% | 0.779 | 0.37 ms |
| Zero-shot Qwen3 | 27 of 32 | 84.4% | 0.852 | 906 ms |

Qwen got two more examples right on this set. It classified all eight accident examples correctly, but confused two fires and two medical reports with accidents. The trained classifier got more medical cases right, seven versus six. Use the counts alongside the percentages so the audience can see the sample size.

The timing compares a local classifier prediction with the LLM’s local HTTP call, generation and validation. Both ran without a per-call API fee. This benchmark scores category only. It does not establish the quality of severity, location or unit suggestions. The reports were generated for the prototype, and an independent set written and labeled by students is the next evaluation step. [Recorded results and confusion matrices](../models/benchmark-result.json)

## Suggested presentation sequence

- **Show the difference between training and inference.** Use one report to show the four-class prediction beside the LLM’s richer draft. Explain where the labeled corpus was used and where the released model was used.
- **Show the result and one failure.** Put 25/32 and 27/32 next to the timing, then tell the severity-1 to severity-5 story. Show why the dispatcher still checks the result before taking action.
- **Give the presenters a small rehearsal.** Change one report in the notebook and explain the prediction. In the review page, use one recognized place and one ambiguous location to show what the system can verify and what needs judgment. [Run the demo](../models/README.md)
