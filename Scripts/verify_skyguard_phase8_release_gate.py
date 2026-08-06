"""Independent verifier for Skyguard Phase 8 Windows release attempts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verify_skyguard_phase8_cook_contract import (
    evaluate_packaged_maps,
    evaluate_preflight,
)


CRITICAL_PATTERNS = {
    "fatal": re.compile(r"Fatal error|LowLevelFatalError", re.I),
    "assertion": re.compile(r"Assertion failed", re.I),
    "gpu_crash": re.compile(r"GPU Crash|DXGI_ERROR_DEVICE_(?:REMOVED|HUNG|RESET)", re.I),
    "oom": re.compile(r"Out of video memory|Ran out of memory|OOM detected", re.I),
    "unhandled_exception": re.compile(
        r"Unhandled Exception|EXCEPTION_ACCESS_VIOLATION", re.I
    ),
    "blueprint_or_property": re.compile(
        r"Blueprint Runtime Error|LogBlueprint: Error|LogProperty: Error|"
        r"LogLinker: Error|LogClass: Error",
        re.I,
    ),
}


def read_text(path: str | None) -> str:
    if not path:
        return ""
    candidate = Path(path)
    return (
        candidate.read_text(encoding="utf-8", errors="replace")
        if candidate.is_file()
        else ""
    )


def scan_stage(stage: dict[str, Any]) -> dict[str, Any]:
    text = read_text(stage.get("stdout")) + "\n" + read_text(stage.get("stderr"))
    matches = {
        name: [line.strip() for line in text.splitlines() if pattern.search(line)][:25]
        for name, pattern in CRITICAL_PATTERNS.items()
    }
    return {
        "stage": stage.get("name"),
        "critical_count": sum(len(lines) for lines in matches.values()),
        "samples": matches,
        "uat_success": bool(re.search(r"BUILD SUCCESSFUL|AutomationTool exiting with ExitCode=0", text, re.I)),
        "benchmark_exit": bool(
            re.search(r"RequestExit.*Benchmarking|reason:.*Benchmarking", text, re.I)
        ),
        "shipping_smoke_exit": bool(
            re.search(r"\[SkyguardStartupSmoke\]\s+COMPLETE\b", text, re.I)
        ),
        "map_loaded": bool(re.search(r"LoadMap:|Bringing World .* up for play", text)),
        "d3d12": bool(re.search(r'rhiname="D3D12"|verbatimrhiname="D3D12"', text)),
    }


def process_clean(stage: dict[str, Any]) -> bool:
    if stage.get("timed_out") or stage.get("process_exit_observed") is False:
        return False
    code = stage.get("exit_code")
    return code is None or code == 0


def verify_shipping_smoke_receipt(
    path_value: Any,
    expected_map: str,
) -> dict[str, Any]:
    path = Path(path_value) if isinstance(path_value, str) and path_value else None
    receipt: dict[str, Any] | None = None
    parse_error: str | None = None
    if path and path.is_file():
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            receipt = value if isinstance(value, dict) else None
        except (OSError, json.JSONDecodeError) as exc:
            parse_error = f"{type(exc).__name__}: {exc}"
    expected_short_name = expected_map.rsplit("/", 1)[-1]
    checks = {
        "receipt_exists": bool(path and path.is_file()),
        "schema": bool(
            receipt
            and receipt.get("schema") == "skyguard.shipping-startup-smoke.v1"
        ),
        "state_complete": bool(receipt and receipt.get("state") == "COMPLETE"),
        "exact_map": bool(
            receipt
            and isinstance(receipt.get("map"), str)
            and receipt["map"].endswith(expected_short_name)
        ),
        "d3d12": bool(
            receipt
            and isinstance(receipt.get("rhi"), str)
            and "D3D12" in receipt["rhi"].upper()
        ),
    }
    return {
        "path": str(path) if path else None,
        "parse_error": parse_error,
        "receipt": receipt,
        "checks": checks,
        "pass": all(checks.values()),
    }


def verify_release_tier_receipt(manifest: dict[str, Any]) -> dict[str, Any]:
    """Verify new explicit tier evidence without invalidating historical runs."""
    controls = manifest.get("controls", {})
    declared_tier = controls.get("release_tier")
    declared_exception = controls.get("engineering_audio_exception")
    path_value = manifest.get("release_tier_receipt")
    path = Path(path_value) if isinstance(path_value, str) and path_value else None

    # Phase 8 manifests created before the tier contract remain accepted only as
    # Engineering evidence. This preserves immutable baseline history without
    # upgrading it to AAA, Shipping promotion, or friend-facing distribution.
    if declared_tier is None and path is None:
        return {
            "path": None,
            "explicit_contract": False,
            "historical_implicit_engineering_exception": True,
            "release_tier": "Engineering",
            "audio_shipping_allowed": False,
            "engineering_audio_exception_applied": True,
            "packaging_allowed": True,
            "external_distribution_allowed": False,
            "shipping_promotion_allowed": False,
            "pass": True,
            "limitations": [
                "Historical manifest predates explicit release-tier audio preflight.",
                "Accepted as Engineering baseline only; never AAA or friend-facing.",
            ],
        }

    receipt = None
    parse_error = None
    if path and path.is_file():
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            receipt = value if isinstance(value, dict) else None
        except (OSError, json.JSONDecodeError) as exc:
            parse_error = f"{type(exc).__name__}: {exc}"
    result = receipt.get("result", {}) if receipt else {}
    checks = {
        "receipt_exists": bool(path and path.is_file()),
        "schema": bool(
            receipt
            and receipt.get("schema") == "skyguard.phase8.release-tier-preflight.v1"
        ),
        "tier_matches": bool(
            declared_tier in {"Engineering", "AAA", "FriendFacing"}
            and result.get("release_tier") == declared_tier
        ),
        "exception_matches": bool(
            isinstance(declared_exception, bool)
            and result.get("engineering_audio_exception_requested")
            is declared_exception
        ),
        "packaging_allowed": result.get("packaging_allowed") is True,
    }
    if declared_tier == "Engineering":
        tier_safe = bool(
            result.get("external_distribution_allowed") is False
            and result.get("shipping_promotion_allowed") is False
            and (
                result.get("audio_shipping_allowed") is True
                or (
                    declared_exception is True
                    and result.get("engineering_audio_exception_applied") is True
                    and result.get("effective_audio_state")
                    == "BLOCK_SHIPPING_UNVERIFIED_AUDIO_WITH_ENGINEERING_EXCEPTION"
                )
            )
        )
    else:
        tier_safe = bool(
            declared_exception is False
            and result.get("audio_shipping_allowed") is True
            and result.get("engineering_audio_exception_applied") is False
            and result.get("effective_audio_state")
            == "PASS_SHIPPING_AUDIO_BOUNDARY"
            and result.get("shipping_promotion_allowed") is True
        )
    checks["tier_audio_policy"] = tier_safe
    return {
        "path": str(path) if path else None,
        "parse_error": parse_error,
        "receipt": receipt,
        "checks": checks,
        "explicit_contract": True,
        "historical_implicit_engineering_exception": False,
        "release_tier": declared_tier,
        "audio_shipping_allowed": result.get("audio_shipping_allowed"),
        "engineering_audio_exception_applied": result.get(
            "engineering_audio_exception_applied"
        ),
        "packaging_allowed": result.get("packaging_allowed"),
        "external_distribution_allowed": result.get(
            "external_distribution_allowed"
        ),
        "shipping_promotion_allowed": result.get("shipping_promotion_allowed"),
        "pass": all(checks.values()),
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_package(
    name: str,
    package: dict[str, Any] | None,
    inventory: list[dict[str, Any]],
    expected_maps: list[str],
) -> dict[str, Any]:
    package = package or {}
    exe = Path(package["executable"]) if package.get("executable") else None
    archive_root = (
        Path(package["archive_root"]).resolve()
        if package.get("archive_root")
        else None
    )
    containers = [
        Path(item) for item in package.get("cooked_container_files", [])
    ]
    container_extensions = {path.suffix.lower() for path in containers if path.is_file()}
    archive_files = (
        sorted(
            (path.resolve() for path in archive_root.rglob("*") if path.is_file()),
            key=lambda path: str(path).lower(),
        )
        if archive_root and archive_root.is_dir()
        else []
    )
    matching_inventory = [
        item
        for item in inventory
        if item.get("configuration") == name
    ]
    inventory_paths = [
        Path(item["path"]).resolve()
        for item in matching_inventory
        if item.get("path")
    ]
    archive_path_set = {str(path).lower() for path in archive_files}
    inventory_path_set = {str(path).lower() for path in inventory_paths}
    inventory_complete = bool(archive_files) and (
        len(matching_inventory) == len(inventory_paths)
        == len(inventory_path_set)
        == len(archive_path_set)
        and inventory_path_set == archive_path_set
    )
    hashes_valid = inventory_complete and all(
        Path(item["path"]).is_file()
        and Path(item["path"]).stat().st_size == item.get("bytes")
        and file_sha256(Path(item["path"])) == item.get("sha256")
        for item in matching_inventory
    )
    cooked_registry = (
        Path(package["cooked_asset_registry"])
        if package.get("cooked_asset_registry")
        else Path("__missing_phase8_cooked_asset_registry__")
    )
    packaged_map_contract = evaluate_packaged_maps(
        expected_maps,
        archive_root if archive_root else Path("__missing_phase8_archive__"),
        cooked_registry,
    )
    cooked_registry_hash_valid = bool(
        package.get("cooked_asset_registry_sha256")
        and package.get("cooked_asset_registry_sha256")
        == packaged_map_contract.get("cooked_asset_registry_sha256")
    )
    return {
        "configuration": name,
        "archive_root": package.get("archive_root"),
        "executable": str(exe) if exe else None,
        "executable_exists": bool(exe and exe.is_file()),
        "cooked_container_count": len([item for item in containers if item.is_file()]),
        "container_extensions": sorted(container_extensions),
        "has_pak_or_iostore": bool(container_extensions & {".pak", ".utoc", ".ucas"}),
        "archive_file_count": len(archive_files),
        "inventory_entry_count": len(matching_inventory),
        "inventory_complete": inventory_complete,
        "hashes_valid": hashes_valid,
        "packaged_map_contract": packaged_map_contract,
        "packaged_maps_valid": packaged_map_contract["gate"] == "PASS",
        "cooked_asset_registry_hash_valid": cooked_registry_hash_valid,
        "pass": bool(exe and exe.is_file())
        and bool(container_extensions & {".pak", ".utoc", ".ucas"})
        and inventory_complete
        and hashes_valid
        and cooked_registry_hash_valid
        and packaged_map_contract["gate"] == "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--latest-output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    controls = manifest.get("controls", {})
    validate_only = bool(controls.get("validate_only"))
    stages = manifest.get("stages", [])
    scans = {stage["name"]: scan_stage(stage) for stage in stages}

    matrix_path = Path(manifest["mission_matrix"])
    matrix = (
        json.loads(matrix_path.read_text(encoding="utf-8-sig"))
        if matrix_path.is_file()
        else {"missions": []}
    )
    missions = matrix.get("missions", [])
    expected_maps = [mission.get("map") for mission in missions]
    mission_ids = [mission.get("id") for mission in missions]
    mission_maps_complete = (
        len(missions) == matrix.get("required_mission_count") == 10
        and len(set(mission_ids)) == 10
        and all(mission.get("map") for mission in missions)
        and all(mission.get("status") not in {"NOT_AUTHORED", "BLOCKED"} for mission in missions)
    )
    cook_contract = evaluate_preflight(
        Path(manifest.get("project_root", "")),
        Path(manifest.get("project_root", "")) / "Config" / "DefaultGame.ini",
        matrix_path,
    )

    input_receipt = manifest.get("source_static_receipt", {}).get("input", {})
    input_static_pass = all(input_receipt.get("action_checks", {}).values()) and all(
        input_receipt.get("axis_checks", {}).values()
    )
    save_receipt = manifest.get("source_static_receipt", {}).get("save", {})
    save_static_pass = all(
        save_receipt.get(key, False)
        for key in (
            "save_game_class",
            "builds_save_object",
            "disk_save_call",
            "disk_load_call",
        )
    )
    settings_receipt = manifest.get("source_static_receipt", {}).get("settings", {})
    settings_static_pass = all(settings_receipt.values())

    runtime_receipt_path = manifest.get("runtime_validation_receipt")
    runtime_receipt = None
    if runtime_receipt_path and Path(runtime_receipt_path).is_file():
        runtime_receipt = json.loads(
            Path(runtime_receipt_path).read_text(encoding="utf-8-sig")
        )
    runtime_evidence = runtime_receipt.get("evidence", {}) if runtime_receipt else {}
    receipt_package_hash = (
        runtime_receipt.get("package_executable_sha256") if runtime_receipt else None
    )
    current_executable_hashes = {
        item.get("sha256")
        for item in manifest.get("artifact_inventory", [])
        if item.get("relative_path", "").lower().endswith("skyguard52.exe")
    }
    runtime_validation_pass = bool(
        runtime_receipt
        and runtime_receipt.get("schema")
        == "skyguard.phase8.runtime-validation-receipt.v1"
        and runtime_receipt.get("gate") == "PASS"
        and runtime_receipt.get("package_configuration")
        in {"Development", "Shipping"}
        and receipt_package_hash in current_executable_hashes
        and runtime_receipt.get("input") == "PASS"
        and runtime_receipt.get("save_round_trip") == "PASS"
        and runtime_receipt.get("settings_round_trip") == "PASS"
        and len(runtime_evidence.get("input_cases", [])) >= 8
        and len(runtime_evidence.get("save_cases", [])) >= 4
        and len(runtime_evidence.get("settings_cases", [])) >= 5
        and len(runtime_evidence.get("launches", [])) >= 2
        and all(
            case.get("result") == "PASS"
            for category in ("input_cases", "save_cases", "settings_cases")
            for case in runtime_evidence.get(category, [])
        )
        and all(
            launch.get("timed_out") is False
            and launch.get("exit_code") == 0
            and launch.get("log")
            for launch in runtime_evidence.get("launches", [])
        )
    )

    provenance_path = Path(manifest.get("provenance_ledger", ""))
    provenance = (
        json.loads(provenance_path.read_text(encoding="utf-8-sig"))
        if provenance_path.is_file()
        else None
    )
    provenance_gate = provenance.get("gate") if provenance else "MISSING"
    provenance_pass = provenance_gate in {
        "PASS",
        "COMPLETE",
        "RELEASE_READY",
        "PASS_USED_ASSETS_WITH_ART_BACKLOG",
    }

    shader = manifest.get("source_static_receipt", {}).get("shader_pso", {})
    shipping_package = manifest.get("packages", {}).get("Shipping", {})
    shipping_root = Path(shipping_package.get("archive_root", ""))
    packaged_pso_files = (
        [
            path
            for path in shipping_root.rglob("*")
            if path.is_file()
            and (
                path.suffix.lower() in {".upipelinecache", ".spc"}
                or path.name.lower().endswith(".stablepc.csv")
            )
        ]
        if shipping_root.is_dir()
        else []
    )
    pso_pass = bool(shader.get("enabled_in_config")) and bool(packaged_pso_files)
    release_tier = verify_release_tier_receipt(manifest)

    inventory = manifest.get("artifact_inventory", [])
    development = verify_package(
        "Development",
        manifest.get("packages", {}).get("Development"),
        inventory,
        expected_maps,
    )
    shipping = verify_package(
        "Shipping",
        manifest.get("packages", {}).get("Shipping"),
        inventory,
        expected_maps,
    )
    package_stage_pass = {}
    for configuration in ("development", "shipping"):
        stage = next(
            (item for item in stages if item.get("name") == f"package_{configuration}"),
            None,
        )
        scan = scans.get(f"package_{configuration}", {})
        package_stage_pass[configuration] = bool(
            stage
            and process_clean(stage)
            and scan.get("critical_count") == 0
            and scan.get("uat_success")
        )

    soak_results = []
    for mission in missions:
        stage_name = f"mission_soak_{mission.get('id')}"
        stage = next((item for item in stages if item.get("name") == stage_name), None)
        scan = scans.get(stage_name, {})
        soak_results.append(
            {
                "mission": mission.get("id"),
                "map": mission.get("map"),
                "stage_present": stage is not None,
                "pass": bool(
                    stage
                    and process_clean(stage)
                    and scan.get("critical_count") == 0
                    and scan.get("d3d12")
                    and scan.get("map_loaded")
                    and scan.get("benchmark_exit")
                ),
            }
        )
    mission_soak_pass = (
        mission_maps_complete
        and len(soak_results) == 10
        and all(result["pass"] for result in soak_results)
    )

    shipping_stage = next(
        (item for item in stages if item.get("name") == "shipping_startup_smoke"),
        None,
    )
    shipping_scan = scans.get("shipping_startup_smoke", {})
    shipping_smoke_receipt = verify_shipping_smoke_receipt(
        manifest.get("shipping_smoke_receipt"),
        expected_maps[0] if expected_maps else "",
    )
    shipping_smoke_pass = bool(
        shipping_stage
        and process_clean(shipping_stage)
        and shipping_scan.get("critical_count") == 0
        and shipping_smoke_receipt["pass"]
    )

    before_crashes = set(manifest.get("crash_snapshot_before", []))
    after_crashes = set(manifest.get("crash_snapshot_after", []))
    new_crashes = sorted(after_crashes - before_crashes)
    crash_pass = manifest.get("terminal_state") == "EXECUTION_COMPLETE" and not new_crashes

    checks = {
        "cook_contract_preflight": cook_contract["gate"] == "PASS",
        "development_uat": package_stage_pass.get("development", False),
        "development_is_cooked_package": development["pass"],
        "shipping_uat": package_stage_pass.get("shipping", False),
        "shipping_is_cooked_hashed_package": shipping["pass"],
        "ten_unique_mission_maps": mission_maps_complete,
        "ten_mission_soak": mission_soak_pass,
        "shipping_startup_smoke": shipping_smoke_pass,
        "input_static_contract": input_static_pass,
        "save_static_contract": save_static_pass,
        "settings_static_contract": settings_static_pass,
        "input_save_settings_runtime_round_trip": runtime_validation_pass,
        "shader_pso_cache": pso_pass,
        "no_new_crash_receipts": crash_pass,
        "third_party_provenance_complete": provenance_pass,
        "release_tier_audio_preflight": release_tier["pass"],
    }

    if validate_only:
        gate = "READY_TO_EXECUTE_WITH_BLOCKERS"
    elif manifest.get("terminal_state") == "BLOCKED_ACTIVE_UNREAL_OR_BUILD_PROCESS":
        gate = "BLOCKED_ACTIVE_UNREAL_OR_BUILD_PROCESS"
    elif all(checks.values()):
        gate = "PASS"
    else:
        gate = "FAIL"

    blockers = [name for name, passed in checks.items() if not passed]
    report = {
        "schema": "skyguard.phase8.release-gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": gate,
        "attempt_id": manifest.get("attempt_id"),
        "manifest": str(args.manifest),
        "terminal_state": manifest.get("terminal_state"),
        "harness_failure": manifest.get("failure"),
        "harness_self_checks": manifest.get("harness_self_checks", {}),
        "checks": checks,
        "blockers": blockers,
        "packages": {"Development": development, "Shipping": shipping},
        "cook_contract_preflight": cook_contract,
        "mission_matrix": {
            "path": str(matrix_path),
            "required_count": 10,
            "declared_count": len(missions),
            "maps_complete": mission_maps_complete,
            "missions": missions,
        },
        "mission_soak_results": soak_results,
        "input_save_settings": {
            "source_static_receipt": manifest.get("source_static_receipt"),
            "runtime_receipt_path": runtime_receipt_path,
            "runtime_receipt": runtime_receipt,
        },
        "shader_pso": {
            "source_receipt": shader,
            "packaged_files": [str(path) for path in packaged_pso_files],
        },
        "provenance": {
            "path": str(provenance_path),
            "gate": provenance_gate,
            "pass": provenance_pass,
        },
        "release_tier": release_tier,
        "crash_receipts": {"new": new_crashes, "pass": crash_pass},
        "stage_scans": scans,
        "shipping_smoke_receipt": shipping_smoke_receipt,
        "limitations": [
            "Static input/save/settings discovery is not a runtime round trip; a separate PASS receipt is mandatory.",
            "A Binaries/Win64 Development executable without cooked pak/IoStore containers is never a package.",
            "Development and Shipping promotion require a complete SHA-256 inventory of every archived file and re-verify it from disk.",
            "The current mission matrix intentionally records missing Missions 2-10 instead of treating the Mission 1 vertical slice as a campaign release.",
            "A generated PSO cache is insufficient unless configuration enables its runtime use and the cache ships in the archived package.",
            "Unsigned Windows builds may trigger reputation warnings; code signing is reported separately from functional acceptance.",
            "Historical manifests without a release-tier receipt remain Engineering-only and cannot authorize AAA or friend-facing distribution.",
            "Engineering audio exceptions preserve baseline packaging evidence but never upgrade authentic-audio, Shipping-promotion, or external-distribution state.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.latest_output:
        args.latest_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.output, args.latest_output)
    print(json.dumps({"gate": gate, "blockers": blockers, "report": str(args.output)}, indent=2))
    return 0 if gate in {"PASS", "READY_TO_EXECUTE_WITH_BLOCKERS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
