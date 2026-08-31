# PARAMS: Frozen Parameters for Sinter Reproducibility Matrix

**Repository:** `sinter-repro-boundary-s1`  
**Date Frozen:** 2026-08-31  

---

## 1. Circuit Generation Parameters & Tasks

Circuits are generated using the `stim gen` CLI from `stim==1.16.0`:

### Task 1: Rotated Surface Code $d=3$, $r=3$, $p=0.001$
* **Generation Command (Verbatim):**
  ```bash
  stim gen --code surface_code --task rotated_memory_z --distance 3 --rounds 3 \
    --after_clifford_depolarization 0.001 \
    --before_measure_flip_probability 0.001 \
    --after_reset_flip_probability 0.001 \
    --before_round_data_depolarization 0.001 > tasks/surface_code_d3_r3_p0001.stim
  ```
* **File Path:** `tasks/surface_code_d3_r3_p0001.stim`
* **Frozen SHA-256 Digest:** `ec996ccd11005ccc8f7accbbf4c0e676306eee7ade0e27c23d89acf9f61a53b7`

### Task 2: Rotated Surface Code $d=5$, $r=5$, $p=0.001$
* **Generation Command (Verbatim):**
  ```bash
  stim gen --code surface_code --task rotated_memory_z --distance 5 --rounds 5 \
    --after_clifford_depolarization 0.001 \
    --before_measure_flip_probability 0.001 \
    --after_reset_flip_probability 0.001 \
    --before_round_data_depolarization 0.001 > tasks/surface_code_d5_r5_p0001.stim
  ```
* **File Path:** `tasks/surface_code_d5_r5_p0001.stim`
* **Frozen SHA-256 Digest:** `bb946c95d9c146e8c1407b05589994d447e51721255d8073dea916b6256444c7`

---

## 2. Collection & Stopping Parameters

* **Decoder:** `pymatching` (`PyMatching==2.4.0`)
* **Maximum Shots per Circuit (`max_shots`):** `50000`
* **Maximum Errors per Circuit (`max_errors`):** `500`
* **Starting Batch Size (`start_batch_size`):** `100`
* **Maximum Batch Size (`max_batch_size`):** `1000`
* **Seed Parameter:** `NOT EXPOSED BY TOOL` (cf. `PREMISES.md §1`)

---

## 3. Canonical Combination & Sort Specification

* **Combination Step:** Executed via `sinter combine --order metadata` across the raw CSV file.
* **Canonical Sort Key (`canonical_sort_key`):**
  The resulting CSV rows are sorted lexicographically by the tuple:
  `("json_metadata", "decoder", "strong_id")`
  ensuring deterministic, platform-independent row ordering prior to canonical SHA-256 hashing.
