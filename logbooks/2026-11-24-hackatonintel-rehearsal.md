# HackatonIntel · Milestone 7 measurements and rehearsal

## User prompt · Sync the model phase and continue

> if the phase and dev-process docs are ready, commit and sync, and continue to the next phase.

### Decisions

- Verify the model workflow, benchmark, and presentation brief on GitHub, then follow milestone 7 in the specification. Measure the public simulator read-only and use a disposable laptop instance for tests that change shared traffic. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Reviewed the pending presenter-code log. It documents the user prompt, the location of the environment variable, and the presenter controls without disclosing the value. Included it in the sync checkpoint. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- Confirmed local and remote main matched and contained the model code, benchmark, presenter brief, and milestone log. The private environment file remained ignored. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- Model development and its documentation were already committed. The presenter-code follow-up was the remaining process entry in this checkout. Milestone 7 now proceeds with performance measurements and rehearsal evidence. [Rubric criterion 4](../docs/rubric.html#c4)

## User follow-up · Pause and merge outgoing and incoming work

> you must pause a bit and merge the outgoing and incomming again.

### Decisions

- Pause milestone 7 after saving the current measurements. Sync the outgoing rehearsal changes and the incoming slide updates. Preserve both sets of entries in the shared Lenovo logbook. [Rubric criterion 1](../docs/rubric.html#c1)

### AI contribution

- Saved the reproducible [performance probe](../backend/measure_demo.py), the [preliminary measurements](../docs/rehearsal-measurements.json), the optional browser frame meter, and the [signed-in rehearsal script](../backend/rehearse_dispatch.py). Synced these alongside the incoming deck changes. [Rubric criterion 2](../docs/rubric.html#c2)

### Independent checks

- The 100-pair routing sample measured 39.84 ms p95 for a single-road detour. The foreground desktop browser recorded 60.0 FPS and 16.8 ms p95 frame time with 500 vehicles. A background-tab sample was discarded after browser throttling limited it to 1 FPS. HTTPS and both WSS roles responded on Render. The signed-in rehearsal reached priority auditing, then the initial citizen position returned `409`. Its cleanup marked the rescue arrival and closed the synthetic incident. The cause of the position response remains to be checked. [Rubric criterion 3](../docs/rubric.html#c3)

### Session result

- The saved measurements and scripts are a milestone 7 checkpoint. The full rehearsal, position-rejection diagnosis, and presentation performance report remain pending after the sync. [Rubric criterion 4](../docs/rubric.html#c4)
