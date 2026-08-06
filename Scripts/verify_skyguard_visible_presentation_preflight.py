from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_SCHEMA = "skyguard.visible-presentation-preflight.report.v1"
VERIFICATION_SCHEMA = "skyguard.visible-presentation-preflight.verification.v1"
EXPECTED_STAGES = (
    ("entry_visible", "/Engine/Maps/Entry"),
    ("m01_visible", "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"),
)
REQUIRED_BINDINGS = {"package_launcher", "package_runtime"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def verify_report(report_path: Path) -> dict[str, Any]:
    report = load_json(report_path)
    issues: list[str] = []
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool, issue: str) -> None:
        checks[name] = bool(condition)
        if not condition:
            issues.append(issue)

    check(
        "schema",
        report.get("schema") == REPORT_SCHEMA,
        f"report schema must be {REPORT_SCHEMA}",
    )
    check(
        "terminal_state",
        report.get("terminal_state") == "EXECUTION_COMPLETE",
        "supervisor terminal_state must be EXECUTION_COMPLETE",
    )
    configuration = report.get("configuration", {})
    check(
        "canonical_configuration",
        isinstance(configuration, dict)
        and configuration.get("visible") is True
        and configuration.get("rhi") == "D3D12"
        and configuration.get("feature_level") == "SM6"
        and configuration.get("resolution") == {"x": 1280, "y": 720}
        and configuration.get("smoke_seconds") == 10
        and configuration.get("stage_timeout_seconds") == 35,
        "configuration must be the canonical visible 1280x720 D3D12/SM6 "
        "10-second smoke with a 35-second stage bound",
    )

    bindings = report.get("bindings")
    binding_labels: set[str] = set()
    binding_hashes_valid = True
    if isinstance(bindings, list):
        for binding in bindings:
            if not isinstance(binding, dict):
                binding_hashes_valid = False
                continue
            label = binding.get("label")
            if isinstance(label, str):
                binding_labels.add(label)
            path_text = binding.get("path")
            try:
                path = Path(path_text)
                binding_hashes_valid = (
                    binding_hashes_valid
                    and path.is_file()
                    and path.stat().st_size == binding.get("bytes")
                    and sha256(path) == binding.get("sha256")
                )
            except (OSError, TypeError):
                binding_hashes_valid = False
    else:
        binding_hashes_valid = False
    check(
        "required_bindings",
        binding_labels == REQUIRED_BINDINGS,
        "exact package_launcher and package_runtime bindings are required",
    )
    check(
        "binding_hashes",
        binding_hashes_valid,
        "one or more package bindings are missing, stale, or hash-invalid",
    )

    driver = report.get("driver", {})
    selected_adapter = driver.get("selected_adapter", {})
    check(
        "driver_query_complete",
        isinstance(driver, dict) and driver.get("query_complete") is True,
        "video-driver identity query did not complete",
    )
    check(
        "driver_identity_present",
        isinstance(selected_adapter, dict)
        and bool(selected_adapter.get("name"))
        and bool(selected_adapter.get("driver_version"))
        and bool(selected_adapter.get("pnp_device_id")),
        "selected GPU driver identity is incomplete",
    )

    firewall = report.get("firewall", {})
    check(
        "firewall_read_only",
        isinstance(firewall, dict)
        and firewall.get("operation") == "READ_ONLY_INSPECTION"
        and firewall.get("mutation_attempted") is False,
        "firewall evidence must come from a read-only inspection",
    )
    check(
        "firewall_query_complete",
        isinstance(firewall, dict) and firewall.get("query_complete") is True,
        "firewall rule query did not complete",
    )
    runtime_binding_path = next(
        (
            str(binding.get("path"))
            for binding in bindings or []
            if isinstance(binding, dict)
            and binding.get("label") == "package_runtime"
        ),
        "",
    )
    check(
        "firewall_exact_runtime",
        isinstance(firewall, dict)
        and bool(runtime_binding_path)
        and str(firewall.get("target_program", "")).casefold()
        == runtime_binding_path.casefold(),
        "firewall query target must be the exact bound packaged runtime",
    )
    enabled_actions: set[str] = set()
    if isinstance(firewall, dict) and isinstance(firewall.get("rules"), list):
        enabled_actions = {
            str(rule.get("action", "")).upper()
            for rule in firewall["rules"]
            if isinstance(rule, dict) and rule.get("enabled") is True
        }
    expected_action_summary = (
        "NO_ENABLED_RULES"
        if not enabled_actions
        else "MIXED"
        if len(enabled_actions) > 1
        else "ALLOW"
        if enabled_actions == {"ALLOW"}
        else "BLOCK"
    )
    check(
        "firewall_action_summary",
        isinstance(firewall, dict)
        and firewall.get("action_summary") == expected_action_summary,
        "firewall action summary does not match the recorded exact rules",
    )
    check(
        "firewall_no_enabled_block",
        not enabled_actions or enabled_actions == {"ALLOW"},
        "enabled firewall rules for the exact packaged runtime must all be Allow",
    )

    stages = report.get("stages")
    stage_sequence_valid = (
        isinstance(stages, list)
        and len(stages) == len(EXPECTED_STAGES)
        and all(
            isinstance(stage, dict)
            and stage.get("name") == expected_name
            and stage.get("map") == expected_map
            for stage, (expected_name, expected_map) in zip(
                stages, EXPECTED_STAGES, strict=True
            )
        )
    )
    check(
        "exact_stage_sequence",
        stage_sequence_valid,
        "exactly entry_visible then m01_visible are required",
    )

    all_receipts_complete = True
    no_gpu_timeouts = True
    no_critical_signatures = True
    overlay_scan_complete = True
    no_overlay_modules = True
    process_cleanup = True
    natural_clean_exit = True
    bounded_duration = True
    stage_verdicts: list[dict[str, Any]] = []
    if isinstance(stages, list):
        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                all_receipts_complete = False
                continue
            expected_name, expected_map = (
                EXPECTED_STAGES[index]
                if index < len(EXPECTED_STAGES)
                else ("unexpected", "unexpected")
            )
            receipt = stage.get("receipt", {})
            signatures = stage.get("signatures", {})
            module_scan = stage.get("module_scan", {})
            cleanup = stage.get("cleanup", {})
            expected_receipt_map = (
                "Entry"
                if expected_map == "/Engine/Maps/Entry"
                else expected_map.rsplit("/", 1)[-1]
            )
            receipt_ok = (
                isinstance(receipt, dict)
                and receipt.get("exists") is True
                and receipt.get("schema") == "skyguard.shipping-startup-smoke.v1"
                and receipt.get("state") == "COMPLETE"
                and receipt.get("map") == expected_receipt_map
            )
            stage_gpu_ok = (
                isinstance(signatures, dict)
                and signatures.get("gpu_timeout_count") == 0
            )
            stage_critical_ok = (
                isinstance(signatures, dict)
                and signatures.get("critical_signature_count") == 0
            )
            module_scan_ok = (
                isinstance(module_scan, dict)
                and module_scan.get("query_complete") is True
                and isinstance(module_scan.get("samples"), int)
                and module_scan.get("samples") > 0
            )
            overlay_modules_ok = (
                module_scan_ok
                and isinstance(module_scan.get("overlay_modules"), list)
                and len(module_scan["overlay_modules"]) == 0
            )
            cleanup_ok = (
                isinstance(cleanup, dict)
                and cleanup.get("success") is True
                and cleanup.get("post_cleanup_process_exists") is False
            )
            exit_ok = (
                stage.get("timed_out") is False
                and stage.get("natural_exit") is True
                and stage.get("exit_code") == 0
            )
            duration_ok = (
                isinstance(stage.get("elapsed_seconds"), (int, float))
                and isinstance(stage.get("supervisor_seconds"), int)
                and stage["supervisor_seconds"] == 35
                and stage["elapsed_seconds"] <= stage["supervisor_seconds"] + 5
            )
            all_receipts_complete &= receipt_ok
            no_gpu_timeouts &= stage_gpu_ok
            no_critical_signatures &= stage_critical_ok
            overlay_scan_complete &= module_scan_ok
            no_overlay_modules &= overlay_modules_ok
            process_cleanup &= cleanup_ok
            natural_clean_exit &= exit_ok
            bounded_duration &= duration_ok
            stage_verdicts.append(
                {
                    "name": expected_name,
                    "receipt_complete": receipt_ok,
                    "no_gpu_timeouts": stage_gpu_ok,
                    "no_critical_signatures": stage_critical_ok,
                    "overlay_scan_complete": module_scan_ok,
                    "no_overlay_modules": overlay_modules_ok,
                    "process_cleanup": cleanup_ok,
                    "natural_clean_exit": exit_ok,
                    "bounded_duration": duration_ok,
                }
            )
    else:
        all_receipts_complete = False
        no_gpu_timeouts = False
        no_critical_signatures = False
        overlay_scan_complete = False
        no_overlay_modules = False
        process_cleanup = False
        natural_clean_exit = False
        bounded_duration = False

    check(
        "all_receipts_complete",
        all_receipts_complete,
        "both visible stages must produce COMPLETE startup-smoke receipts",
    )
    check(
        "no_gpu_timeouts",
        no_gpu_timeouts,
        "one or more visible stages logged a GPU-timeout signature",
    )
    check(
        "no_critical_signatures",
        no_critical_signatures,
        "one or more visible stages logged a critical render/device signature",
    )
    check(
        "overlay_scan_complete",
        overlay_scan_complete,
        "loaded-module sampling did not complete for both visible stages",
    )
    check(
        "no_overlay_modules",
        no_overlay_modules,
        "one or more known overlay/capture modules were loaded",
    )
    check(
        "process_cleanup",
        process_cleanup,
        "one or more exact launched process trees were not confirmed cleaned up",
    )
    check(
        "natural_clean_exit",
        natural_clean_exit,
        "both visible stages must exit naturally with code zero",
    )
    check(
        "bounded_duration",
        bounded_duration,
        "one or more stages exceeded the canonical supervisor bound",
    )

    gate = "PASS" if all(checks.values()) else "FAIL"
    return {
        "schema": VERIFICATION_SCHEMA,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": gate,
        "terminal_state": "VERIFICATION_COMPLETE",
        "report": str(report_path.resolve()),
        "report_sha256": sha256(report_path),
        "checks": checks,
        "issues": issues,
        "stage_verdicts": stage_verdicts,
        "input_combat_gate_authorized": gate == "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the fail-closed Skyguard visible-presentation preflight."
    )
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = verify_report(args.report)
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["gate"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
