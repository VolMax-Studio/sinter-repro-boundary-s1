#!/usr/bin/env python3
"""
run_matrix.py — Executes the 4x3 Sinter Reproducibility Matrix according to PREREGISTRATION_v2.md
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


def hash_string(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def canonicalize_csv(raw_csv_path: str, canonical_csv_path: str):
    """
    Combines and deterministically sorts a raw sinter CSV using sinter stats_from_csv_files.
    """
    stats_list = sinter.stats_from_csv_files(raw_csv_path)
    combined_dict = {}
    for s in stats_list:
        key = (json.dumps(s.json_metadata, sort_keys=True), s.decoder, s.strong_id)
        if key not in combined_dict:
            combined_dict[key] = s
        else:
            combined_dict[key] = combined_dict[key] + s

    sorted_keys = sorted(combined_dict.keys())

    with open(canonical_csv_path, "w") as f:
        f.write(sinter.CSV_HEADER + "\n")
        for k in sorted_keys:
            f.write(combined_dict[k].to_csv_line() + "\n")


def generate_schema_representation(canonical_csv_path: str) -> str:
    """
    Generates a deterministic structural representation of the combined CSV,
    abstracting away stochastic numeric quantities (errors, seconds).
    """
    stats_list = sinter.stats_from_csv_files(canonical_csv_path)
    combined_dict = {}
    for s in stats_list:
        key = (json.dumps(s.json_metadata, sort_keys=True), s.decoder, s.strong_id)
        if key not in combined_dict:
            combined_dict[key] = s
        else:
            combined_dict[key] = combined_dict[key] + s

    sorted_keys = sorted(combined_dict.keys())
    schema_lines = [sinter.CSV_HEADER]
    for k in sorted_keys:
        s = combined_dict[k]
        # Abstract stochastic values: errors, seconds
        dummy_stat = sinter.TaskStats(
            strong_id=s.strong_id,
            decoder=s.decoder,
            json_metadata=s.json_metadata,
            shots=s.shots,
            errors=0,
            seconds=0.0
        )
        schema_lines.append(dummy_stat.to_csv_line())
    return "\n".join(schema_lines) + "\n"


def parse_task_breakdown(csv_path: str):
    """
    Parses exact per-task statistics from a CSV file.
    """
    stats_list = sinter.stats_from_csv_files(csv_path)
    task_stats = {}
    for s in stats_list:
        d_val = s.json_metadata.get("d", "unknown")
        task_label = f"d={d_val}"
        if task_label not in task_stats:
            task_stats[task_label] = {"shots": 0, "errors": 0}
        task_stats[task_label]["shots"] += s.shots
        task_stats[task_label]["errors"] += s.errors

    num_rows = sum(1 for _ in open(csv_path)) - 1 if os.path.exists(csv_path) else 0
    total_shots = sum(s["shots"] for s in task_stats.values())
    total_errors = sum(s["errors"] for s in task_stats.values())
    return {
        "num_rows": num_rows,
        "total_shots": total_shots,
        "total_errors": total_errors,
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
    measurement_log = []

    print("================================================================================")
    print("SINTER REPRODUCIBILITY MATRIX v2 (4x3 = 12 RUNS)")
    print("================================================================================")

    for w in workers_list:
        for r in range(1, repetitions + 1):
            config_id = f"w{w}_r{r}"
            raw_path = f"results/raw/run_{config_id}.csv"
            canonical_path = f"results/canonical/run_{config_id}.csv"
            log_path = f"results/raw/run_{config_id}.log"

            if os.path.exists(raw_path):
                os.remove(raw_path)
            if os.path.exists(canonical_path):
                os.remove(canonical_path)

            print(f"\n[RUN] Executing {config_id}: workers={w}, repetition={r}/3 ...")

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

            canonicalize_csv(raw_path, canonical_path)

            raw_sha = hash_file(raw_path)
            canonical_sha = hash_file(canonical_path)
            log_sha = hash_file(log_path)

            schema_repr = generate_schema_representation(canonical_path)
            schema_sha = hash_string(schema_repr)

            raw_stats = parse_task_breakdown(raw_path)
            canonical_stats = parse_task_breakdown(canonical_path)

            entry = {
                "config_id": config_id,
                "num_workers": w,
                "repetition": r,
                "wall_time_seconds": round(wall_time, 3),
                "raw_sha256": raw_sha,
                "canonical_sha256": canonical_sha,
                "canonical_schema_sha256": schema_sha,
                "log_sha256": log_sha,
                "raw_num_rows": raw_stats["num_rows"],
                "canonical_num_rows": canonical_stats["num_rows"],
                "total_shots": canonical_stats["total_shots"],
                "total_errors": canonical_stats["total_errors"],
                "task_breakdown": canonical_stats["task_breakdown"]
            }
            manifest_entries.append(entry)
            measurement_log.append({
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                **entry
            })

            d3_s = canonical_stats["task_breakdown"]["d=3"]["shots"]
            d3_e = canonical_stats["task_breakdown"]["d=3"]["errors"]
            d5_s = canonical_stats["task_breakdown"]["d=5"]["shots"]
            d5_e = canonical_stats["task_breakdown"]["d=5"]["errors"]

            print(f"  Done in {wall_time:.2f}s | Rows: {raw_stats['num_rows']:>2} | d=3: {d3_s} shots ({d3_e} err) | d=5: {d5_s} shots ({d5_e} err) | Schema SHA: {schema_sha[:16]}...")

    # Save manifest
    manifest_data = {
        "experiment": "sinter-repro-boundary-s1",
        "specification_version": "v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runs": manifest_entries
    }
    with open("results/manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)

    # Save history log
    with open("history/measurement_log.json", "w") as f:
        json.dump(measurement_log, f, indent=2)

    # Generate full SHA256SUMS
    with open("results/SHA256SUMS", "w") as f:
        for entry in manifest_entries:
            f.write(f"{entry['raw_sha256']}  results/raw/run_{entry['config_id']}.csv\n")
            f.write(f"{entry['canonical_sha256']}  results/canonical/run_{entry['config_id']}.csv\n")

    print("\n================================================================================")
    print("ALL 12 RUNS COMPLETED. Results written to results/manifest.json and history/measurement_log.json")
    print("================================================================================")


if __name__ == "__main__":
    main()
