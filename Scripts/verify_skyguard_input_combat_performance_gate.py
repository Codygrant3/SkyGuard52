"""Fail-closed verifier for the input-driven combat performance capture plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    contract_path = Path(manifest["contract"]["path"])
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    contract_hash_ok = sha256(contract_path) == manifest["contract"]["sha256"]

    trace_channels = {
        item.lower() for item in manifest["requested_profile"]["trace_channels"]
    }
    required_trace = {
        item.lower() for item in contract["required_trace_channels"]
    }
    csv_categories = set(manifest["requested_profile"]["csv_categories"])
    required_csv = set(contract["required_csv_categories"])
    arguments = manifest["requested_profile"]["runtime_arguments"]
    joined_arguments = " ".join(arguments)
    source_coverage = manifest["source_instrumentation"]
    missing_source = [
        item["literal"]
        for item in source_coverage
        if not item.get("found", False)
    ]

    static_checks = {
        "manifest_schema": manifest.get("schema")
        == "skyguard.input-combat-performance.run.v1",
        "contract_schema": contract.get("schema")
        == "skyguard.input-combat-performance.contract.v1",
        "contract_hash": contract_hash_ok,
        "memory_trace_channel": "memory" in trace_channels,
        "all_trace_channels": required_trace.issubset(trace_channels),
        "all_csv_categories": required_csv.issubset(csv_categories),
        "d3d12_sm6": "-d3d12" in arguments and "-sm6" in arguments,
        "full_hd": "-ResX=1920" in arguments and "-ResY=1080" in arguments,
        "csv_gpu_stats": "-csvGpuStats" in arguments,
        "csv_named_events": "-csvNamedEvents" in arguments,
        "trace_file_bound": "-tracefile=" in joined_arguments,
        "nvidia_sampling_declared": manifest["requested_profile"][
            "external_gpu_telemetry"
        ]["provider"]
        == "nvidia-smi",
        "five_context_windows": len(contract["required_windows"]) == 5,
    }
    contract_gate = "PASS" if all(static_checks.values()) else "FAIL"

    controls = manifest.get("controls", {})
    validate_only = controls.get("validate_only", False)
    prerequisite = manifest.get("prerequisite", {})
    prerequisite_pass = prerequisite.get("gate") == "PASS"
    runtime_bookmarks_ready = not missing_source
    execution = manifest.get("execution", {})

    artifacts = {}
    for name, raw_path in manifest.get("artifacts", {}).items():
        if not isinstance(raw_path, str):
            continue
        path = Path(raw_path)
        artifacts[name] = {
            "path": str(path),
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else 0,
            "sha256": sha256(path) if path.is_file() else None,
        }

    if contract_gate == "FAIL":
        gate = "FAIL_STATIC_CONTRACT"
    elif validate_only and not runtime_bookmarks_ready:
        gate = "VALIDATED_CONTRACT_BLOCKED_RUNTIME_BOOKMARKS"
    elif validate_only and not prerequisite_pass:
        gate = "VALIDATED_CONTRACT_BLOCKED_PREREQUISITE"
    elif validate_only:
        gate = "VALIDATED_NOT_EXECUTED"
    elif not prerequisite_pass:
        gate = "BLOCKED_PREREQUISITE"
    elif not runtime_bookmarks_ready:
        gate = "BLOCKED_RUNTIME_BOOKMARKS"
    elif execution.get("terminal_state") != "CAPTURE_COMPLETE":
        gate = "FAIL_CAPTURE"
    else:
        # Raw capture is intentionally not promoted. Contextual Insights exports,
        # three-repeat aggregation, and the soak stability calculation remain
        # separate acceptance artifacts.
        gate = "CAPTURE_COMPLETE_REVIEW_REQUIRED"

    requirements = {
        "P1.4": "INSUFFICIENT_EVIDENCE",
        "P1.5": "NOT_EXECUTED" if validate_only else "INSUFFICIENT_EVIDENCE",
        "P8.10": "NOT_EXECUTED" if validate_only else "INSUFFICIENT_EVIDENCE",
        "P8.11": "NOT_EXECUTED" if validate_only else "INSUFFICIENT_EVIDENCE",
        "P8.12": "NOT_EXECUTED" if validate_only else "INSUFFICIENT_EVIDENCE",
    }
    blockers = []
    if not prerequisite_pass:
        blockers.append(
            "Visible D3D12 capture is blocked until the Windows Security/NVIDIA "
            "prerequisite receipt returns gate=PASS."
        )
    if missing_source:
        blockers.append(
            "Runtime code does not yet contain all required trace region/bookmark "
            "literals; measured interaction windows cannot be proven."
        )
    blockers.extend(
        [
            "P8.10 requires three accepted 1080p combat captures.",
            "P1.5/P8.11 require one accepted 20-minute input-driven combat soak.",
            "P8.12 requires contextual first-use shader/PSO review inside the "
            "player-triggered windows.",
        ]
    )

    return {
        "schema": "skyguard.input-combat-performance.gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "attempt_id": manifest.get("attempt_id"),
        "gate": gate,
        "contract_gate": contract_gate,
        "static_checks": static_checks,
        "prerequisite": prerequisite,
        "runtime_bookmark_coverage": {
            "ready": runtime_bookmarks_ready,
            "required_literal_count": len(source_coverage),
            "found_literal_count": sum(
                1 for item in source_coverage if item.get("found", False)
            ),
            "missing_literals": missing_source,
            "evidence": source_coverage,
        },
        "requested_profile": manifest["requested_profile"],
        "execution": execution,
        "artifacts": artifacts,
        "requirement_disposition": requirements,
        "blockers": blockers,
        "limitations": [
            "Validate-only mode never launches Unreal.",
            "External nvidia-smi samples measure the adapter globally; the in-engine "
            "GPUUsage/Memory CSV counter is required for process-relative context.",
            "Raw artifacts never satisfy the repeated-capture, soak, or contextual "
            "Insights acceptance gates by themselves.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--latest-output", type=Path)
    args = parser.parse_args()
    report = verify(args.manifest.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.latest_output:
        args.latest_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.output, args.latest_output)
    print(json.dumps({"gate": report["gate"], "report": str(args.output)}, indent=2))
    return 1 if report["gate"].startswith("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
