# PREREGISTRATION: Positive Control on Sinter Execution Reproducibility Boundaries

**Instance:** `sinter-repro-boundary-s1`  
**Date Frozen:** 2026-08-31  
**Software Version Lock:** `stim==1.16.0`, `sinter==1.16.0`, `PyMatching==2.4.0`  

---

## 1. Claim Under Test (Verbatim)

> For a fixed task, software version, seed, and execution environment, does `sinter` produce a byte-identical output artifact when worker count is changed across the pre-registered configurations?

*(Note on Tool Seeding: As established in `PREMISES.md`, `sinter collect` does not expose a global seed parameter to external callers; random sampling states are generated internally per worker process. This investigation explicitly measures the resulting artifact stability under varying worker concurrency).*

---

## 2. Unit of Observation

The output artifact, identified by SHA-256 digest. Two artifacts are hashed and recorded per run:
1. **RAW**: The exact CSV file written directly by `sinter collect`, unmodified.
2. **CANONICAL**: The combined and sorted CSV file produced by applying `sinter combine` over the RAW artifact, followed by sorting rows lexicographically by the pre-registered key (`PARAMS.md §canonical_sort_key`).

---

## 3. Manipulated Variable

* **Worker Concurrency (`num_workers` / `--processes`):** Evaluated across $w \in \{1, 2, 4, 8\}$.

---

## 4. Held Constant (Invariants)

* **Circuit Tasks:** Fixed Stim rotated surface code memory_z circuits (`d=3, r=3, p=0.001` and `d=5, r=5, p=0.001`), frozen with exact SHA-256 digests in `tasks/`.
* **Decoder:** `pymatching` (`PyMatching==2.4.0`).
* **Stopping Criteria:** `max_shots = 50000`, `max_errors = 500`.
* **Batch Sizing Parameters:** `start_batch_size = 100`, `max_batch_size = 1000`.
* **Environment:** Same physical host machine (12th Gen Intel Core i7-1255U, x86_64, Linux 7.0.0-28-generic, AVX2 SIMD), same Python binary (`Python 3.12.3`), and identical pinned `requirements.lock`.

---

## 5. Pre-Registered Run Matrix ($4 \times 3 = 12$ Runs)

| Configuration ID | `num_workers` | Repetition Index | Output RAW Path | Output Canonical Path |
|---|---|---|---|---|
| `w1_r1` | 1 | 1 | `results/raw/run_w1_r1.csv` | `results/canonical/run_w1_r1.csv` |
| `w1_r2` | 1 | 2 | `results/raw/run_w1_r2.csv` | `results/canonical/run_w1_r2.csv` |
| `w1_r3` | 1 | 3 | `results/raw/run_w1_r3.csv` | `results/canonical/run_w1_r3.csv` |
| `w2_r1` | 2 | 1 | `results/raw/run_w2_r1.csv` | `results/canonical/run_w2_r1.csv` |
| `w2_r2` | 2 | 2 | `results/raw/run_w2_r2.csv` | `results/canonical/run_w2_r2.csv` |
| `w2_r3` | 2 | 3 | `results/raw/run_w2_r3.csv` | `results/canonical/run_w2_r3.csv` |
| `w4_r1` | 4 | 1 | `results/raw/run_w4_r1.csv` | `results/canonical/run_w4_r1.csv` |
| `w4_r2` | 4 | 2 | `results/raw/run_w4_r2.csv` | `results/canonical/run_w4_r2.csv` |
| `w4_r3` | 4 | 3 | `results/raw/run_w4_r3.csv` | `results/canonical/run_w4_r3.csv` |
| `w8_r1` | 8 | 1 | `results/raw/run_w8_r1.csv` | `results/canonical/run_w8_r1.csv` |
| `w8_r2` | 8 | 2 | `results/raw/run_w8_r2.csv` | `results/canonical/run_w8_r2.csv` |
| `w8_r3` | 8 | 3 | `results/raw/run_w8_r3.csv` | `results/canonical/run_w8_r3.csv` |

*Triplicate repetitions at each worker level ($n=3$) are mandatory to distinguish run-to-run stochasticity from worker-count scaling effects.*

---

## 6. Recorded Metrics per Run

For each of the 12 execution runs, the harness records:
1. `sha256_raw`: SHA-256 digest of raw sinter CSV output.
2. `sha256_canonical`: SHA-256 digest of combined, sorted canonical CSV.
3. `shots_per_case`: Total collected shots for each task ($d=3$ and $d=5$).
4. `errors_per_case`: Total observed logical errors for each task.
5. `num_rows_raw`: Number of lines in the raw CSV.
6. `wall_time_seconds`: Total execution wall time.
7. `stdout_stderr_sha256`: Digest of run console telemetry.

---

## 7. Pre-Frozen Decision Rules

Evaluation follows strict hierarchical precedence:

```
D5: Any difference (in shots, errors, or canonical content) is already present
    within the workers=1 repetitions (w1_r1 vs w1_r2 vs w1_r3)
    → RUN-TO-RUN NONDETERMINISM (Tool exhibits unseeded stochasticity across
      repeated invocations; worker-count comparison is confounded by run-to-run variance).

D1: RAW is byte-identical across all 12 runs AND CANONICAL is byte-identical
    across all 12 runs
    → BYTE-IDENTICAL UNDER TESTED CONFIGURATIONS

D2: RAW differs, CANONICAL is byte-identical across all 12 runs, AND shots-per-case
    is identical across all runs
    → ROW-ORDER VARIATION ONLY (Artifact line ordering is subject to worker process
      completion timing; semantic content and sampling totals are stable).

D3: CANONICAL differs across worker counts, BUT shots-per-case is identical
    → CONTENT VARIATION AT EQUAL SAMPLING

D4: shots-per-case differs across worker counts (with stable workers=1 baselines)
    → SAMPLING ALLOCATION IS WORKER-COUNT DEPENDENT (Adaptive batch aggregation
      yields differing total collected shots as concurrency scales).
```

*Rule Precedence: D5 must be evaluated first. If D5 triggers, D1–D4 are not asserted.*
