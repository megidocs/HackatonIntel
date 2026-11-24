# ClearPath incident-report models

The report review page asks a local language model to draft an incident type, severity, location phrase and candidate units. FastAPI validates the response against a strict schema. It accepts a map location only when the report contains one supported Manhattan place, the model quotes it, and the place snaps to the bundled road graph. Confirm the severity, location and units before opening an incident.

## Run the laptop demo

- Obtain the [llama.cpp CPU release](https://github.com/ggml-org/llama.cpp/releases/tag/b12676) and the [Qwen3-0.6B GGUF weights](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/23749fefcc72300e3a2ad315e1317431b06b590a). These are already available on Lenovo in `C:\Temp\clearpath-llama-b12676` and `C:\Temp\clearpath-models`.
- Start the local model server from PowerShell.

```powershell
& 'C:/Temp/clearpath-llama-b12676/llama-server.exe' -m 'C:/Temp/clearpath-models/Qwen3-0.6B-Q8_0.gguf' --host 127.0.0.1 --port 8011 --ctx-size 2048 --threads 6 --parallel 1 --reasoning off
```

- In the PowerShell terminal that starts the [dispatch rehearsal](../docs/dispatch.md#start-with-the-private-local-file), set `$env:CLEARPATH_MODEL_URL = 'http://127.0.0.1:8011'` before running Uvicorn. Open [Report review](http://127.0.0.1:8003/dispatch/reports). Use a dispatcher access token from [Supabase password sign-in](https://supabase.com/docs/reference/javascript/auth-signinwithpassword) for the designated demo account.
- Try a report mentioning a catalog landmark, then one with an unknown or ambiguous location. Try the citizen account and verify that the draft is denied. Drafting leaves the dispatch board and simulation state unchanged.

## Compare the models

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r models/requirements.txt
.\.venv\Scripts\python.exe -m models.benchmark --model-url http://127.0.0.1:8011
```

The [notebook](report_comparison.ipynb) explains the train/test split, shows a classifier prediction, and prints the confusion matrices. The training set has 256 reports generated from 32 text families and eight location variants. The test set has 32 separately worded examples, eight per category. Both sets were written for this prototype and the test set is a smoke benchmark.

| Model | Correct | Accuracy | Macro F1 | Median on Lenovo | External inference fee |
| --- | ---: | ---: | ---: | ---: | ---: |
| TF-IDF + logistic regression | 25/32 | 78.1% | 0.779 | 0.37 ms | $0 |
| Qwen3-0.6B Q8 zero-shot | 27/32 | 84.4% | 0.852 | 906 ms | $0 |

The baseline timing covers classifier prediction and the LLM timing covers localhost HTTP, generation and validation. The [machine-readable results](benchmark-result.json) contain both confusion matrices and the response-validation count. The benchmark scores incident category only. Severity, units and location accuracy need separate reviewed examples. In the first rehearsal, the LLM under-rated a collision with a trapped occupant. An explicit severity rubric improved that example, and the draft still requires review. Use an independent, student-authored test set before drawing broader conclusions.
