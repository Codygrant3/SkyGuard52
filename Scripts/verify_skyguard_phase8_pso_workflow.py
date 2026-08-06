"""Fail-closed offline verifier for the Skyguard Phase 8 PSO workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


PHASES = ("PREFLIGHT", "CAPTURED", "STABILIZED", "PACKAGED", "CONSUMED")
CRITICAL_RE = re.compile(
    r"Fatal error|Assertion failed|GPU Crash|DXGI_ERROR_DEVICE_|"
    r"Out of video memory|Unhandled Exception|EXCEPTION_ACCESS_VIOLATION",
    re.I,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record_valid(record: dict[str, Any]) -> bool:
    path = Path(record.get("path", ""))
    return bool(
        path.is_file()
        and path.stat().st_size > 0
        and record.get("bytes") == path.stat().st_size
        and record.get("sha256") == sha256_file(path)
    )


def evaluate(manifest: dict[str, Any]) -> dict[str, Any]:
    phase = manifest.get("phase")
    config_path = Path(manifest.get("config", ""))
    config_text = (
        config_path.read_text(encoding="utf-8", errors="replace")
        if config_path.is_file()
        else ""
    )
    checks: dict[str, bool] = {
        "known_phase": phase in PHASES,
        "stable_keys_enabled": bool(
            re.search(r"(?m)^\s*NeedsShaderStableKeys\s*=\s*True\s*$", config_text)
        ),
        "runtime_cache_enabled": bool(
            re.search(
                r"(?m)^\s*r\.ShaderPipelineCache\.Enabled\s*=\s*1\s*$",
                config_text,
            )
        ),
        "pso_precaching_enabled": bool(
            re.search(r"(?m)^\s*r\.PSOPrecaching\s*=\s*1\s*$", config_text)
        ),
        "bound_package_executable": file_record_valid(
            manifest.get("package_executable", {})
        ),
        "bound_mission_matrix": file_record_valid(
            manifest.get("mission_matrix", {})
        ),
    }

    if phase in PHASES[1:]:
        captures = manifest.get("captures", [])
        mission_ids = [item.get("mission") for item in captures]
        checks.update(
            {
                "ten_unique_capture_receipts": (
                    len(captures) == 10 and len(set(mission_ids)) == 10
                ),
                "all_capture_files_hash_valid": bool(captures)
                and all(file_record_valid(item.get("cache", {})) for item in captures),
                "all_capture_stages_clean": bool(captures)
                and all(
                    item.get("exit_code") == 0
                    and item.get("timed_out") is False
                    and Path(item.get("log", "")).is_file()
                    and not CRITICAL_RE.search(
                        Path(item["log"]).read_text(
                            encoding="utf-8", errors="replace"
                        )
                    )
                    for item in captures
                ),
            }
        )

    if phase in PHASES[2:]:
        stable = manifest.get("stable_cache", {})
        stable_keys = manifest.get("stable_keys", [])
        mode = manifest.get("stabilization_mode", "recorded_graphics_binary_spc")
        common_stable_checks = {
            "known_stabilization_mode": mode
            in (
                "recorded_graphics_binary_spc",
                "raw_recorded_binary_merge",
                "cook_native_compute_fallback",
            ),
            "stable_keys_present_and_hash_valid": bool(stable_keys)
            and all(file_record_valid(item) for item in stable_keys),
            "stable_keys_are_sm6": bool(stable_keys)
            and all(
                re.search(r"PCD3D_SM6\.shk$", item.get("path", ""), re.I)
                for item in stable_keys
            ),
        }
        checks.update(common_stable_checks)
        if mode == "recorded_graphics_binary_spc":
            checks.update({
                "stable_cache_hash_valid": file_record_valid(stable),
                "stable_cache_is_binary_sm6_spc": bool(
                    re.search(r"PCD3D_SM6\.spc$", stable.get("path", ""), re.I)
                ),
                "stabilize_stage_clean": (
                    manifest.get("stabilize_stage", {}).get("exit_code") == 0
                    and manifest.get("stabilize_stage", {}).get("timed_out") is False
                ),
            })
        elif mode == "raw_recorded_binary_merge":
            stage = manifest.get("stabilize_stage", {})
            steps = stage.get("merge_steps", [])
            dump = stage.get("dump_stage", {})
            dump_log = Path(stage.get("dump_log", {}).get("path", ""))
            dump_text = (
                dump_log.read_text(encoding="utf-8", errors="replace")
                if dump_log.is_file()
                else ""
            )
            checks.update({
                "stable_cache_hash_valid": file_record_valid(stable),
                "stable_cache_is_runtime_sm6_seed": bool(
                    re.search(
                        r"Skyguard52_PCD3D_SM6\.stable\.upipelinecache$",
                        stable.get("path", ""),
                        re.I,
                    )
                ),
                "nine_raw_merge_steps_clean": len(steps) == 9
                and all(
                    item.get("stage", {}).get("exit_code") == 0
                    and item.get("stage", {}).get("timed_out") is False
                    and file_record_valid(item.get("output", {}))
                    for item in steps
                ),
                "validated_merge_matches_accepted_seed": (
                    file_record_valid(stage.get("validated_merge_output", {}))
                    and stage.get("validated_merge_output", {}).get("sha256")
                    == stable.get("sha256")
                ),
                "raw_merge_dump_clean": (
                    dump.get("exit_code") == 0
                    and dump.get("timed_out") is False
                    and file_record_valid(stage.get("dump_log", {}))
                    and not CRITICAL_RE.search(dump_text)
                    and bool(re.search(r"Total PSOs logged:\s*[1-9]\d*", dump_text))
                    and stage.get("total_pso_count", 0) > 0
                ),
            })
        elif mode == "cook_native_compute_fallback":
            stage = manifest.get("stabilize_stage", {})
            evidence = stage.get("engine_defect_evidence", [])
            checks.update({
                "recorded_graphics_cache_absent": stable in ({}, None),
                "fallback_mode_explicit": (
                    stage.get("mode") == "cook_native_compute_fallback"
                    and stage.get("recorded_graphics_cache_status")
                    == "BLOCKED_UE58_BINARY_LOADER_DEFECT"
                    and stage.get("cook_generated_cache_required") is True
                ),
                "engine_defect_reproduced_and_hash_valid": len(evidence) >= 2
                and all(file_record_valid(item) for item in evidence),
            })

    if phase in PHASES[3:]:
        packaged = manifest.get("packaged_cache", {})
        package_mode = packaged.get("mode", "iostore_cooked_cache")
        shipping_root = Path(packaged.get("shipping_root", ""))
        utocs = sorted(shipping_root.rglob("*.utoc")) if shipping_root.is_dir() else []
        expected_name = packaged.get("expected_name", "")
        checks.update({
            "known_package_mode": package_mode
            in ("iostore_cooked_cache", "loose_nonufs_runtime_seed"),
            "shipping_executable_hash_valid": file_record_valid(
                packaged.get("shipping_executable", {})
            ),
            "shipping_utoc_hashes_valid": bool(packaged.get("shipping_utocs"))
            and all(
                file_record_valid(item)
                for item in packaged.get("shipping_utocs", [])
            ),
        })
        if package_mode == "loose_nonufs_runtime_seed":
            source = packaged.get("source_cache", {})
            development_cache = packaged.get("development_cache", {})
            shipping_cache = packaged.get("packaged_cache", {})
            checks.update({
                "development_executable_hash_valid": file_record_valid(
                    packaged.get("development_executable", {})
                ),
                "source_cache_hash_valid": file_record_valid(source),
                "development_cache_hash_valid": file_record_valid(
                    development_cache
                ),
                "shipping_cache_hash_valid": file_record_valid(shipping_cache),
                "packaged_cache_hashes_match_source": bool(source.get("sha256"))
                and source.get("sha256") == development_cache.get("sha256")
                and source.get("sha256") == shipping_cache.get("sha256"),
                "stable_cache_loose_staged_at_runtime_path": bool(expected_name)
                and Path(shipping_cache.get("path", "")).name == expected_name
                and "Content/PipelineCaches/Windows/" in Path(
                    shipping_cache.get("path", "")
                ).as_posix(),
            })
        else:
            checks.update({
                "cooked_cache_hash_valid": file_record_valid(
                    packaged.get("cooked_cache", {})
                ),
                "stable_cache_indexed_in_shipping": bool(expected_name)
                and bool(utocs)
                and any(
                    expected_name.encode("utf-8") in path.read_bytes()
                    for path in utocs
                ),
            })

    if phase == "CONSUMED":
        consumption = manifest.get("consumption", {})
        log = Path(consumption.get("log", ""))
        text = (
            log.read_text(encoding="utf-8", errors="replace")
            if log.is_file()
            else ""
        )
        checks.update(
            {
                "consumption_stage_clean": (
                    consumption.get("exit_code") == 0
                    and consumption.get("timed_out") is False
                    and log.is_file()
                    and not CRITICAL_RE.search(text)
                ),
                "bundled_cache_opened": bool(
                    re.search(
                        r"Opened FPipelineCacheFile: .*"
                        r"Skyguard52_PCD3D_SM6\.stable\.upipelinecache|"
                        r"FPipelineCacheFile\[Skyguard52\] opened Skyguard52",
                        text,
                        re.I,
                    )
                ),
                "precompile_completed": bool(
                    re.search(
                        r"FShaderPipelineCache .* completed \d+ tasks", text, re.I
                    )
                ),
                "no_missing_shaders": bool(
                    re.search(r"0 had missing shaders", text, re.I)
                ),
                "no_cache_open_failure": not bool(
                    re.search(r"Could not open FPipelineCacheFile", text, re.I)
                ),
            }
        )

    gate = "PASS" if checks and all(checks.values()) else "FAIL"
    return {
        "schema": "skyguard.phase8.pso-workflow-verification.v1",
        "phase": phase,
        "gate": gate,
        "checks": checks,
        "blockers": [name for name, passed in checks.items() if not passed],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    report = evaluate(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
