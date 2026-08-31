#!/usr/bin/env python3
"""
run_matrix.py — Executes the 4x3 Sinter Reproducibility Matrix according to PREREGISTRATION.md
"""

import os
import sys
import time
import subprocess
import json
import hashlib
from datetime import datetime, timezone
import stim
import sinter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def hash_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def canonicalize_csv(raw_csv_path: str, canonical_csv_path: str):
    """
    Combines and deterministically sorts a raw sinter CSV using sinter combine API / stats_from_csv_files.
    """
    stats_list = sinter.stats_from_csv_files(raw_csv_path)
    # Combine stats by task
    combined_dict = {}
    for s in stats_list:
        key = (json.dumps(s.json_metadata, sort_keys=True), s.decoder, s.strong_id)
        if key not in combined_dict:
            combined_dict[key] = s
        else:
            combined_dict[key] = combined_dict[key] + s

    # Sort combined stats deterministically by metadata key
    sorted_keys = sorted(combined_dict.keys())

    # Write out canonical CSV
    with open(canonical_csv_path, "w") as f:
        f.write(sinter.CSV_HEADER + "\n")
        for k in sorted_keys:
            f.write(combined_dict[k].to_csv_line() + "\n")


def parse_csv_stats(csv_path: str):
    """
    Parses total shots, total errors, and task breakdown from a sinter CSV.
    """
    stats_list = sinter.stats_from_csv_files(csv_path)
    total_shots = sum(s.shots for s in stats_list)
    total_errors = sum(s.errors for s in stats_list)
    task_stats = {}
    for s in stats_list:
        meta_str = json.dumps(s.json_metadata, sort_keys=True)
        if meta_str not in task_stats:
            task_stats[meta_str] = {"shots": 0, "errors": 0}
        task_stats[meta_str]["shots"] += s.shots
        task_stats[meta_str]["errors"] += s.errors

    num_rows = sum(1 for _ in open(csv_path)) - 1 if os.path.exists(csv_path) else 0
    return {
        "total_shots": total_shots,
        "total_errors": total_errors,
        "num_rows": num_rows,
        "task_breakdown": task_stats
    }


def main():
    os.chdir(REPO_ROOT)
    os.makedirs("results/raw", exist_ok=True)
    os.makedirs("results/canonical", exist_ok=True)
    os.makedirs("history", exist_ok=True)

    task_files = [
        ("tasks/surface_code_d3_r3_p0001.stim", {"d": 3, "r": 3, "p": 0.001}),
        ("tasks/surface_code_d5_r5_p0001.stim", {"d": 5, "r": 5, "p": 0.001})
    ]
    for tf, _ in task_files:
        if not os.path.exists(tf):
            raise FileNotFoundError(f"Missing task file: {tf}")

    workers_list = [1, 2, 4, 8]
    repetitions = 3

    manifest_entries = []

    print("================================================================================")
    print("SINTER REPRODUCIBILITY MATRIX EXECUTION (4x3 = 12 RUNS)")
    print("================================================================================")

    for w in workers_list:
        for r in range(1, repetitions + 1):
            config_id = f"w{w}_r{r}"
            raw_path = f"results/raw/run_{config_id}.csv"
            canonical_path = f"results/canonical/run_{config_id}.csv"
            log_path = f"results/raw/run_{config_id}.log"

            # Remove previous if re-running
            if os.path.exists(raw_path):
                os.remove(raw_path)
            if os.path.exists(canonical_path):
                os.remove(canonical_path)

            print(f"\n[RUN] Executing {config_id}: workers={w}, repetition={r}/3 ...")

            # Construct Sinter Tasks
            sinter_tasks = [
                sinter.Task(
                    circuit=stim.Circuit.from_file(tf),
                    decoder="pymatching",
                    json_metadata=meta
                )
                for tf, meta in task_files
            ]

            start_t = time.time()
            collected_stats = sinter.collect(
                num_workers=w,
                tasks=sinter_tasks,
                max_shots=50000,
                max_errors=500,
                start_batch_size=100,
                max_batch_size=1000,
                save_resume_filepath=raw_path,
                print_progress=False
            )
            wall_time = time.time() - start_t

            with open(log_path, "w") as f:
                f.write(f"Execution finished in {wall_time:.3f} seconds\n")
                f.write(f"Collected {len(collected_stats)} TaskStats entries\n")

            # Canonicalize
            canonicalize_csv(raw_path, canonical_path)

            raw_sha = hash_file(raw_path)
            canonical_sha = hash_file(canonical_path)
            log_sha = hash_file(log_path)

            raw_stats = parse_csv_stats(raw_path)
            canonical_stats = parse_csv_stats(canonical_path)

            entry = {
                "config_id": config_id,
                "num_workers": w,
                "repetition": r,
                "wall_time_seconds": round(wall_time, 3),
                "raw_sha256": raw_sha,
                "canonical_sha256": canonical_sha,
                "log_sha256": log_sha,
                "raw_num_rows": raw_stats["num_rows"],
                "canonical_num_rows": canonical_stats["num_rows"],
                "total_shots": canonical_stats["total_shots"],
                "total_errors": canonical_stats["total_errors"],
                "task_breakdown": canonical_stats["task_breakdown"]
            }
            manifest_entries.append(entry)

            print(f"  Done in {wall_time:.2f}s | RAW SHA: {raw_sha[:16]}... (rows: {raw_stats['num_rows']}) | CANONICAL SHA: {canonical_sha[:16]}... | Total shots: {canonical_stats['total_shots']} | Total errors: {canonical_stats['total_errors']}")

    # Save manifest
    manifest_data = {
        "experiment": "sinter-repro-boundary-s1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runs": manifest_entries
    }
    with open("results/manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)

    # Generate SHA256SUMS
    with open("results/SHA256SUMS", "w") as f:
        for entry in manifest_entries:
            f.write(f"{entry['raw_sha256']}  results/raw/run_{entry['config_id']}.csv\n")
            f.write(f"{entry['canonical_sha256']}  results/canonical/run_{entry['config_id']}.csv\n")

    print("\n================================================================================")
    print("ALL 12 RUNS COMPLETED. Results saved to results/manifest.json and results/SHA256SUMS")
    print("================================================================================")


if __name__ == "__main__":
    main()
