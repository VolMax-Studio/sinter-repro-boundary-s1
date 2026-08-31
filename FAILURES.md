# FAILURES.md: Anomaly and Defect Ledger for sinter-repro-boundary-s1

---

### Failure Entry #001 — Omission of Seed Exposure in Sinter Collect API
- **Date / Event:** 2026-08-31 (Pre-Flight Analysis)
- **Component:** `sinter.collect` CLI / Python API.
- **Observation:** Verified via package metadata and docstrings that `sinter collect` does not provide an external seed parameter, leaving sampling pseudo-randomization to internal worker state generation.
- **Classification:** Tool Premise Clarification (Recorded in `PREMISES.md` prior to execution).
- **Remediation:** Explicitly pre-registered decision rule D5 to assess baseline unseeded run-to-run variation at $w=1$ before evaluating multi-worker concurrency.

---

### Failure Entry #002 — Inapplicable Determinism Rule D5 Executed Against Unseeded Tool
- **Date / Event:** 2026-08-31 (Gate Review Round 1 — `sinter-repro-boundary-s1`)
- **Component:** `PREREGISTRATION.md` and `reproduce.py` (v1).
- **Root Cause (General Class):** Premise-Specification Inversion & Mismatched Decision Logic. Although Step 0 (`PREMISES.md`) explicitly discovered that `sinter` does not expose an external random seed, `PREREGISTRATION.md` retained rule D5 assuming that unseeded stochastic variance across $w=1$ runs constituted an invalidating defect ("Run-to-Run Nondeterminism") rather than the expected behavior of independent pseudo-random sampling.
- **Measurable Impact:** The harness reported `D5: RUN-TO-RUN NONDETERMINISM`, failing to assert the primary structural finding: that total sampling remained perfectly invariant ($100,000$ shots) while batch fragmentation / row count scaled systematically from $4$ ($w=1$) to $56$ ($w=8$).
- **Remediation:** Registered this failure. Preserved `PREREGISTRATION.md` as v1 (`PREREGISTRATION_v1_INAPPLICABLE.md`), and formulated `PREREGISTRATION_v2.md` defining decision rules around structural fragmentation, task-level shot invariants, and schema canonicalization.
