# FAILURES.md: Anomaly and Defect Ledger for sinter-repro-boundary-s1

---

### Failure Entry #001 — Omission of Seed Exposure in Sinter Collect API
- **Date / Event:** 2026-08-31 (Pre-Flight Analysis)
- **Component:** `sinter.collect` CLI / Python API.
- **Observation:** Verified via package metadata and docstrings that `sinter collect` does not provide an external seed parameter, leaving sampling pseudo-randomization to internal worker state generation.
- **Classification:** Tool Premise Clarification (Recorded in `PREMISES.md` prior to execution).
- **Remediation:** Explicitly pre-registered decision rule D5 to assess baseline unseeded run-to-run variation at $w=1$ before evaluating multi-worker concurrency.
