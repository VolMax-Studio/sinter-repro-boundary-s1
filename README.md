# sinter-repro-boundary-s1: Boundaries of Sinter Execution Reproducibility

**Instance ID:** `sinter-repro-boundary-s1`  
**Classification:** Positive Control & Reproducibility Boundary Evaluation (Quantum Error Correction Benchmarking)  
**Status:** `SPREMNO ZA GEJT`  

---

## 1. Central Claim Under Test

> For a fixed task, software version, seed, and execution environment, does `sinter` produce a byte-identical output artifact when worker count is changed across the pre-registered configurations?

*(Note: As documented in `PREMISES.md`, `sinter collect` does not expose an external global seed parameter. This investigation evaluates output artifact stability under worker scaling $w \in \{1, 2, 4, 8\}$ across triplicate runs).*

---

## 2. What Would Falsify It / Decision Outcomes

Evaluation follows the hierarchical decision rules pre-registered in `PREREGISTRATION.md`:
* **D5 (Run-to-Run Nondeterminism):** Variation is present already across repetitions at $w=1$.
* **D1 (Byte-Identical):** RAW and CANONICAL artifacts are byte-identical across all 12 runs.
* **D2 (Row-Order Variation Only):** RAW differs, CANONICAL is byte-identical across all 12 runs, and total shots-per-case are identical.
* **D3 (Content Variation at Equal Sampling):** CANONICAL differs across worker counts while shots-per-case remain identical.
* **D4 (Sampling Allocation Worker-Dependent):** Total shots-per-case vary as worker concurrency scales.

---

## 3. Limitations & Boundaries

See [`LIMITATIONS.md`](LIMITATIONS.md) for explicit non-claims:
* Positive control on the measurement instrument, not an audit of third-party scientific correctness.
* Data generated and evaluated in the same environment.

---

## 4. Operational Status

`SPREMNO ZA GEJT` (Pending Gate Review & Execution Verification)

---

## 5. Deterministic Reproduction

Execute the standalone single-entry reproduction harness:
```bash
pip install -r requirements.lock
python3 reproduce.py
```
