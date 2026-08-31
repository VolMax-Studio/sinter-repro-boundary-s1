# PREREGISTRATION v2: Structural Invariance and Batch Fragmentation under Sinter Worker Concurrency

**Instance:** `sinter-repro-boundary-s1`  
**Specification Version:** v2  
**Date Frozen:** 2026-08-31  
**Software Lock:** `stim==1.16.0`, `sinter==1.16.0`, `PyMatching==2.4.0`  

---

## 1. Context and Claim Under Test

In `PREMISES.md`, it was established that `sinter collect` operates without an external global seed parameter, utilizing internal pseudo-random generators per worker. Consequently, individual shot samples and observed error counts are inherently stochastic across repeated runs.

**The Central Pre-Registered Question (v2):**
> Under unseeded stochastic sampling, does `sinter collect` preserve exact total sampling budgets per task across worker concurrency levels, and how does worker count ($w \in \{1, 2, 4, 8\}$) affect the batch row structure, fragmentation, and canonical combined schema of the output artifact?

---

## 2. Units of Observation & Metrics

For each run $i \in \{1, \dots, 12\}$ in the $4 \times 3$ matrix ($w \in \{1, 2, 4, 8\}$, repetitions $r \in \{1, 2, 3\}$):
1. **Per-Task Total Shots:** Exact number of shots collected for Task 1 ($d=3$) and Task 2 ($d=5$).
2. **Per-Task Total Errors:** Observed logical errors for Task 1 ($d=3$) and Task 2 ($d=5$).
3. **Raw Batch Fragmentation (`num_rows_raw`):** Total CSV rows written to disk prior to combination.
4. **Canonical Combined Schema Hash (`sha256_canonical_schema`):** The SHA-256 digest of the combined CSV with stochastic numerical values (`shots`, `errors`, `discards`, `seconds`, `custom_counts`) replaced with constant structural placeholders, testing exact schema and metadata stability.
5. **Full Raw Artifact SHA-256 (`sha256_raw`) & Canonical Artifact SHA-256 (`sha256_canonical`).**

---

## 3. Invariants & Fixed Parameters

* **Circuit 1:** `tasks/surface_code_d3_r3_p0001.stim` (SHA-256: `ec996ccd11005ccc8f7accbbf4c0e676306eee7ade0e27c23d89acf9f61a53b7`).
* **Circuit 2:** `tasks/surface_code_d5_r5_p0001.stim` (SHA-256: `bb946c95d9c146e8c1407b05589994d447e51721255d8073dea916b6256444c7`).
* **Stopping Criteria:** `max_shots = 50000` per circuit (Total expected: $100,000$), `max_errors = 500`.
* **Batch Sizing:** `start_batch_size = 100`, `max_batch_size = 1000`.
* **Decoder:** `pymatching`.
* **Host Platform:** Fixed CPU/SIMD/OS specifications pinned in `ENVIRONMENT.md`.

---

## 4. Pre-Frozen Decision Rules (v2)

Evaluation follows strict hierarchical evaluation across the 12-run matrix:

```
R1: Per-task total shots are exactly 50,000 for d=3 and 50,000 for d=5 across all 12 runs,
    AND RAW batch row count at w=1 is invariant (w1_r1 == w1_r2 == w1_r3 == 4 rows),
    AND RAW batch row count varies within multi-worker configurations with non-overlapping ranges (w=2: 10–12; w=4: 21–25; w=8: 43–60),
    AND Canonical combined schema hash is byte-identical across all 12 runs
    → STRUCTURAL_FRAGMENTATION_WITH_TOTAL_SAMPLING_INVARIANCE
      (The artifact's row count was invariant at 4 for w=1 across three repetitions,
       and varied within each multi-worker configuration with non-overlapping ranges;
       the total sampling allocation and canonical schema are strictly invariant).

R2: Per-task total shots differ across worker counts (e.g. shots(w=8) != shots(w=1))
    → SAMPLING_BUDGET_IS_WORKER_COUNT_DEPENDENT
      (Adaptive batch termination permits overshoot under higher concurrency).

R3: RAW batch row count at w=1 varies across repetitions (w1_r1 != w1_r2 != w1_r3)
    → NON_MONOTONIC_BATCH_DISPATCH_AT_SINGLE_WORKER

## 5. Cross-Machine Replication Outcomes (Pre-Registered)

When the reproduction package (`reproduce.py`) is executed on an independent secondary host (Machine B):

```
CM-0: requirements.lock cannot be satisfied on the target platform
      → PACKAGE_PORTABILITY_LIMIT
        (The declared environment is not installable on the secondary host
         due to wheel or platform availability; logged, no schema comparison is attempted).

CM-1: Schema Hash Match (Hash(B) == Hash(A))
      AND shots-per-case invariant (50,000 for d=3, 50,000 for d=5)
      → CROSS_MACHINE_INVARIANCE_OF_CANONICAL_SCHEMA
        (The execution artifact's canonical structure and task sampling
         budgets are invariant across differing host environments).

CM-2: Schema Hash Differs (Hash(B) != Hash(A))
      AND Environment differs in declared dimension (e.g. library versions [stim, sinter, pymatching, numpy], CPU architecture, SIMD width, OS)
      → REPRODUCTION_BOUNDARY_LOCATED
        (Discrepancy mapped to specific environmental or library dependency dimension).

CM-3: Schema Hash Differs (Hash(B) != Hash(A))
      AND Environment and library versions are identical in declared dimensions
      → UNEXPLAINED_DISCREPANCY
        (Instance execution halts; discrepancy recorded in FAILURES.md).
```

