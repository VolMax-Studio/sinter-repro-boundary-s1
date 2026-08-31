#!/usr/bin/env python3
"""
reproduce.py — Single-entry point reproduction harness for sinter-repro-boundary-s1 (v2)
"""

import os
import sys
import subprocess
import json
import hashlib

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = sys.executable


def print_env():
    import platform
    print("================================================================================")
    print("REPRODUCTION ENVIRONMENT")
    print("================================================================================")
    print(f"Python:       {platform.python_version()} ({platform.python_build()})")
    print(f"System:       {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Processor:    {platform.processor()}")
    try:
        import stim, sinter, pymatching, numpy
        print(f"stim:         {stim.__version__}")
        print(f"sinter:       {sinter.__version__}")
        print(f"pymatching:   {pymatching.__version__}")
        print(f"numpy:        {numpy.__version__}")
    except ImportError as e:
        print(f"Warning: missing dependencies ({e}). Run: pip install -r requirements.lock")
    print("================================================================================\n")


def evaluate_decision_rules_v2(manifest_path: str):
    with open(manifest_path) as f:
        data = json.load(f)

    runs = data.get("runs", [])
    if len(runs) != 12:
        return "ERROR: Incomplete run matrix (expected 12 runs)"

    w1_runs = [r for r in runs if r["num_workers"] == 1]
    w2_runs = [r for r in runs if r["num_workers"] == 2]
    w4_runs = [r for r in runs if r["num_workers"] == 4]
    w8_runs = [r for r in runs if r["num_workers"] == 8]

    # Print Full Table
    print("==================================================================================================================")
    print("REPRODUCTION EXECUTION RESULTS TABLE (PREREGISTRATION v2)")
    print("==================================================================================================================")
    print(f"{'Config':<8} | {'Workers':<7} | {'Rep':<3} | {'RAW Rows':<8} | {'d=3 Shots':<9} | {'d=3 Err':<7} | {'d=5 Shots':<9} | {'d=5 Err':<7} | {'Canonical Schema SHA (prefix)':<30}")
    print("-" * 114)
    for r in runs:
        d3_s = r["task_breakdown"]["d=3"]["shots"]
        d3_e = r["task_breakdown"]["d=3"]["errors"]
        d5_s = r["task_breakdown"]["d=5"]["shots"]
        d5_e = r["task_breakdown"]["d=5"]["errors"]
        schema_sha = r["canonical_schema_sha256"][:24]
        print(f"{r['config_id']:<8} | {r['num_workers']:<7} | {r['repetition']:<3} | {r['raw_num_rows']:<8} | {d3_s:<9} | {d3_e:<7} | {d5_s:<9} | {d5_e:<7} | {schema_sha:<30}...")
    print("=" * 114)

    # 1. Evaluate Task Sampling Invariance
    all_d3_shots = {r["task_breakdown"]["d=3"]["shots"] for r in runs}
    all_d5_shots = {r["task_breakdown"]["d=5"]["shots"] for r in runs}
    sampling_invariant = (all_d3_shots == {50000} and all_d5_shots == {50000})

    # 2. Evaluate Worker 1 Row Invariance
    w1_rows = [r["raw_num_rows"] for r in w1_runs]
    w1_rows_invariant = (len(set(w1_rows)) == 1 and w1_rows[0] == 4)

    # 3. Evaluate Monotonic Scaling of Multi-Worker Fragmentation
    w2_rows_min = min(r["raw_num_rows"] for r in w2_runs)
    w4_rows_min = min(r["raw_num_rows"] for r in w4_runs)
    w8_rows_min = min(r["raw_num_rows"] for r in w8_runs)
    fragmentation_scaled = (w2_rows_min > 4 and w4_rows_min > 4 and w8_rows_min > 4)

    # 4. Evaluate Canonical Schema Byte-Identity
    all_schema_hashes = {r["canonical_schema_sha256"] for r in runs}
    schema_invariant = (len(all_schema_hashes) == 1)

    if not sampling_invariant:
        return "R2: SAMPLING_BUDGET_IS_WORKER_COUNT_DEPENDENT"
    if not w1_rows_invariant:
        return "R3: NON_MONOTONIC_BATCH_DISPATCH_AT_SINGLE_WORKER"
    if not schema_invariant:
        return "R4: CANONICAL_SCHEMA_MUTATION_UNDER_CONCURRENCY"

    if sampling_invariant and w1_rows_invariant and fragmentation_scaled and schema_invariant:
        return "R1: STRUCTURAL_FRAGMENTATION_WITH_TOTAL_SAMPLING_INVARIANCE"

    return "UNCLASSIFIED_OUTCOME"


def main():
    os.chdir(REPO_ROOT)
    print_env()

    # Run matrix
    run_script = os.path.join(REPO_ROOT, "src", "run_matrix.py")
    res = subprocess.run([PYTHON_BIN, run_script], check=True)

    manifest_path = os.path.join(REPO_ROOT, "results", "manifest.json")
    verdict = evaluate_decision_rules_v2(manifest_path)

    print("\n==================================================================================================================")
    print(f"FORMAL DECISION OUTCOME (v2): {verdict}")
    print("==================================================================================================================")


if __name__ == "__main__":
    main()
