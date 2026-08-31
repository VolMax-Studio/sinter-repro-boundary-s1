# Exploratory Single-Worker Control (w=1, n=10)

POST-HOC CONTROL. Added in response to a gate finding (G-4) after the
pre-registered 4x3 matrix was executed. Not covered by
PREREGISTRATION_v2.md. Exploratory; carries no verdict.

## Summary of Findings
Across 10 independent sequential repetitions with num_workers=1 using
the exact frozen parameters in PARAMS.md (start_batch_size=100, max_batch_size=1000,
max_shots=50000, max_errors=500 per circuit across d=3 and d=5):
- Total CSV row count was strictly invariant: 4 rows in all 10 runs (unique set: {4}).
- Total shots collected was strictly invariant: 100,000 shots in all 10 runs (unique set: {100000}).
- Observed logical errors exhibited expected Poisson variation across runs (33–53 total errors).

Note on Execution History:
The runs recorded in this directory were executed during Gate Review Round 4. An earlier
exploratory verification executed in scratch/ was not persisted to git.
