# PREMISES: Documented Capabilities and Determinism Boundaries of Pinned Tools

**Repository:** `sinter-repro-boundary-s1`  
**Date of Access:** 2026-08-31  
**Pinned Versions:** `stim==1.16.0`, `sinter==1.16.0`, `PyMatching==2.4.0`  

---

## 1. Sinter Seed Parameter Exposure
* **Query:** Does `sinter collect` (CLI / Python API) expose a global or per-worker random seed parameter?
* **Documentation Source:** `sinter==1.16.0` package metadata, public docstrings (`sinter.collect.__doc__`), and CLI specification (`sinter collect --help`).
* **Verbatim Findings:**
  * In `sinter collect` CLI arguments:
    * Supported arguments: `--circuits`, `--decoders`, `--max_shots`, `--max_errors`, `--processes`, `--save_resume_filepath`, `--start_batch_size`, `--max_batch_size`, `--max_batch_seconds`, `--postselect_detectors_with_non_zero_4th_coord`, `--count_observable_error_combos`, `--count_detection_events`, `--quiet`, `--custom_error_count_key`, `--allowed_cpu_affinity_ids`, `--also_print_results_to_stdout`, `--existing_data_filepaths`, `--metadata_func`.
    * **No `--seed` argument is exposed on the `sinter collect` CLI.**
  * In `sinter.collect` Python API:
    * `sinter.collect(num_workers, tasks, existing_data_filepaths=(), save_resume_filepath=None, progress_callback=None, max_shots=None, max_errors=None, count_observable_error_combos=False, count_detection_events=False, decoders=None, max_batch_seconds=None, max_batch_size=None, start_batch_size=None, print_progress=False, hint_num_tasks=None, custom_decoders=None, custom_error_count_key=None, allowed_cpu_affinity_ids=None)`
    * **No `seed` parameter is exposed in `sinter.collect()`.**
* **Finding Status:** `SEED NOT EXPOSED BY SINTER COLLECT`. `sinter` manages random sampling internally across worker processes.

---

## 2. Relationship between Seeding and Worker Parallelism
* **Documentation Source:** `sinter==1.16.0` and `stim==1.16.0` documentation.
* **Finding:** Because `sinter collect` does not expose an external seed parameter to callers, worker processes spawn independent pseudo-random number generators. The exact interleaving and dispatch order of batches across `num_workers` processes is subject to operating system process scheduling.

---

## 3. Adaptive Batch Sampling and Termination Conditions
* **Documentation Source:** `sinter collect --help`, `sinter.collect` docstrings.
* **Verbatim Findings:**
  * `--start_batch_size START_BATCH_SIZE`: *"Initial number of samples to batch together into one job. Starting small prevents over-sampling of circuits above threshold. The allowed batch size increases exponentially from this starting point."*
  * `--max_batch_size MAX_BATCH_SIZE`: *"Maximum number of samples to batch together into one job. Bigger values increase the delay between jobs finishing. Smaller values decrease the amount of aggregation of results, increasing the amount of output information."*
  * `--max_shots MAX_SHOTS`: *"Sampling of a circuit will stop if this many shots have been taken."*
  * `--max_errors MAX_ERRORS`: *"Sampling of a circuit will stop if this many errors have been seen."*
* **Termination Rule:** Sampling for a given task terminates when either `max_shots` or `max_errors` is reached. In multi-worker environments, batches already dispatched to worker processes may complete after the threshold is crossed, potentially causing total collected shots to exceed the minimum threshold depending on worker concurrency.

---

## 4. Canonical Combination (`sinter combine`)
* **Documentation Source:** `sinter combine --help`.
* **Verbatim Findings:**
  * `sinter combine` accepts paths to CSV files containing sample statistics and combines rows belonging to the same task and decoder.
  * Options:
    * `--order {preserve,metadata,error}`: *"Determines the order of output rows. metadata (default): sort ascending by metadata. preserve: match order of input rows. error: sort ascending by error rate"*
    * `--strip_custom_counts`: *"Removes custom counts from the output."*
* **Finding:** `sinter combine` provides an official, deterministic row-combination mechanism that aggregates multi-row CSV outputs into a single consolidated row per task/decoder.

---

## 5. Stim Determinism & Platform Reproducibility Boundaries
* **Documentation Source:** `stim==1.16.0` API Reference and documentation.
* **Verbatim Findings:**
  * `stim.Circuit.compile_sampler(..., seed=Optional[int])` and `compile_detector_sampler(..., seed=Optional[int])` accept an explicit integer seed.
  * Stim's internal SIMD-accelerated stabilizer tableau sampling guarantees bit-level reproducibility **only when running the exact same version of Stim on the same CPU architecture / SIMD instruction set with the same sequence of method calls.**
  * Stim does not promise cross-architecture or cross-SIMD bit-identical output across differing vector extensions (e.g., SSE2 vs AVX2 vs AVX-512) or across major version upgrades.
