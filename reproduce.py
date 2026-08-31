#!/usr/bin/env python3
"""
reproduce.py — Single-entry point reproduction harness for sinter-repro-boundary-s1
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


def evaluate_decision_rules(manifest_path: str):
    with open(manifest_path) as f:
        data = json.load(f)

    runs = data.get("runs", [])
    if len(runs) != 12:
        return "ERROR: Incomplete run matrix (expected 12 runs)"

    # Extract groups
    w1_runs = [r for r in runs if r["num_workers"] == 1]
    w2_runs = [r for r in runs if r["num_workers"] == 2]
    w4_runs = [r for r in runs if r["num_workers"] == 4]
    w8_runs = [r for r in runs if r["num_workers"] == 8]

    # Print Table
    print("================================================================================")
    print("REPRODUCTION EXECUTION RESULTS TABLE")
    print("================================================================================")
    print(f"{'Config':<8} | {'Workers':<7} | {'Rep':<3} | {'RAW SHA256 (prefix)':<20} | {'CANONICAL SHA (prefix)':<22} | {'Shots':<8} | {'Errors':<6} | {'Rows':<4}")
    print("-" * 90)
    for r in runs:
        print(f"{r['config_id']:<8} | {r['num_workers']:<7} | {r['repetition']:<3} | {r['raw_sha256'][:16]}... | {r['canonical_sha256'][:16]}...   | {r['total_shots']:<8} | {r['total_errors']:<6} | {r['raw_num_rows']:<4}")
    print("=" * 90)

    # 1. Evaluate D5 (Differences present already within workers=1)
    w1_raw_hashes = {r["raw_sha256"] for r in w1_runs}
    w1_canonical_hashes = {r["canonical_sha256"] for r in w1_runs}
    w1_shots = {r["total_shots"] for r in w1_runs}
    w1_errors = {r["total_errors"] for r in w1_runs}

    if len(w1_raw_hashes) > 1 or len(w1_canonical_hashes) > 1 or len(w1_shots) > 1 or len(w1_errors) > 1:
        return "D5: RUN-TO-RUN NONDETERMINISM (Tool exhibits unseeded stochasticity across repeated invocations; worker-count comparison is confounded by run-to-run variance)"

    # 2. Evaluate D1 (Byte-identical across all 12 runs)
    all_raw_hashes = {r["raw_sha256"] for r in runs}
    all_canonical_hashes = {r["canonical_sha256"] for r in runs}
    all_shots = {r["total_shots"] for r in runs}

    if len(all_raw_hashes) == 1 and len(all_canonical_hashes) == 1:
        return "D1: BYTE-IDENTICAL UNDER TESTED CONFIGURATIONS"

    # 3. Evaluate D2 (RAW differs, CANONICAL identical, shots identical)
    if len(all_canonical_hashes) == 1 and len(all_shots) == 1:
        return "D2: ROW-ORDER VARIATION ONLY (Artifact line ordering is subject to worker process completion timing; semantic content and sampling totals are stable)"

    # 4. Evaluate D3 (CANONICAL differs, shots identical)
    if len(all_canonical_hashes) > 1 and len(all_shots) == 1:
        return "D3: CONTENT VARIATION AT EQUAL SAMPLING"

    # 5. Evaluate D4 (Shots vary across worker counts with stable w=1)
    if len(all_shots) > 1:
        return "D4: SAMPLING ALLOCATION IS WORKER-COUNT DEPENDENT (Adaptive batch aggregation yields differing total collected shots as concurrency scales)"

    return "UNCLASSIFIED_OUTCOME"


def main():
    os.chdir(REPO_ROOT)
    print_env()

    # Run matrix
    run_script = os.path.join(REPO_ROOT, "src", "run_matrix.py")
    res = subprocess.run([PYTHON_BIN, run_script], check=True)

    manifest_path = os.path.join(REPO_ROOT, "results", "manifest.json")
    verdict = evaluate_decision_rules(manifest_path)

    print("\n================================================================================")
    print(f"FORMAL DECISION OUTCOME: {verdict}")
    print("================================================================================")


if __name__ == "__main__":
    main()
