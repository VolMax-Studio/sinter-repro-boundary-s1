# sinter-repro-boundary-s1: Boundaries of Sinter Execution Reproducibility

**Instance ID:** `sinter-repro-boundary-s1`  
**Classification:** Positive Control & Reproducibility Boundary Evaluation (Quantum Error Correction Benchmarking)  
**Specification Document:** [`PREREGISTRATION_v2.md`](PREREGISTRATION_v2.md) *(v1 preserved in [`PREREGISTRATION_v1_INAPPLICABLE.md`](PREREGISTRATION_v1_INAPPLICABLE.md))*  
**Status:** `SPREMNO ZA GEJT`  

---

## 1. Central Claim Under Test

> Under unseeded stochastic sampling, does `sinter collect` preserve exact total sampling budgets per task across worker concurrency levels, and how does worker count ($w \in \{1, 2, 4, 8\}$) affect the batch row structure, fragmentation, and canonical combined schema of the output artifact?

*(Note: As documented in [`PREMISES.md`](PREMISES.md), `sinter collect` does not expose an external global seed parameter. This investigation evaluates output artifact stability and batch fragmentation under worker scaling $w \in \{1, 2, 4, 8\}$ across triplicate runs, accompanied by a 10-run single-worker control in [`results/w1_ten_run_control/`](results/w1_ten_run_control/)).*

---

## 2. What Would Falsify It / Decision Outcomes

Evaluation follows the hierarchical decision rules pre-registered in [`PREREGISTRATION_v2.md`](PREREGISTRATION_v2.md):
* **R1 (Verified Structural Fragmentation):** Per-task total shots are exactly $50,000$ for $d=3$ and $50,000$ for $d=5$ across all 12 runs, raw batch row count at $w=1$ is invariant at 4 rows, raw row count varies across multi-worker configurations with non-overlapping ranges ($w=2$: 10–12; $w=4$: 21–25; $w=8$: 43–60), and the canonical schema hash is 100% byte-identical.
* **R2 (Sampling Budget Worker-Dependent):** Total shots differ across worker counts.
* **R3 (Non-Monotonic Batch Dispatch at Single Worker):** Row count at $w=1$ varies across runs.
* **R4 (Canonical Schema Mutation):** Canonical schema hash differs across runs.

---

## 3. Limitations & Epistemic Boundaries

See [`LIMITATIONS.md`](LIMITATIONS.md) for explicit non-claims:
* Positive control on the measurement instrument, not an audit of third-party scientific correctness.
* Data generated and evaluated in the same environment.
* **Statistical resolution limit on $d=5$:** Observed errors are in the single digits (2–12 per run); this repository MUST NOT be used to derive logical error rate estimates for $d=5$.

---

## 4. Operational Status

`SPREMNO ZA GEJT` (Pending Gate Review & Ratification)

---

## 5. Deterministic Reproduction

Execute the standalone single-entry reproduction harness:
```bash
pip install -r requirements.lock
python3 reproduce.py
```
