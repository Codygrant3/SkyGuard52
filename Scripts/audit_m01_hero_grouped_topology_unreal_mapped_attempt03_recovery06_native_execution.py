"""Offline readiness audit for activation-bound Recovery06 native execution."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_NATIVE_EXECUTION_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_NATIVE_EXECUTION_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def exact(record: dict) -> bool:
    path = resolve(record["path"])
    return (
        path.is_file()
        and path.stat().st_size == record["bytes"]
        and sha256_file(path) == record["sha256"]
    )


def add(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def current_source_inventory() -> list[dict]:
    records = []
    for path in sorted((ROOT / "Source").rglob("*")):
        if path.is_file():
            records.append(
                {
                    "file": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return records


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []
    bound = contract["bound_files"]

    add(
        checks,
        "all_execution_inputs_hash_bound",
        all(exact(record) for record in bound.values()),
        f"{len(bound)} immutable files exact",
    )

    activation = json.loads(
        resolve(bound["compile_activation"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    receipt = json.loads(
        resolve(bound["compile_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "compile_activation_pass_and_dll_exact",
        activation["gate"] == "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        and activation["build_exit_code"] == 0
        and activation["target"] == "Skyguard52Editor"
        and activation["platform"] == "Win64"
        and activation["configuration"] == "Development"
        and activation["compiled_module"]["sha256"]
        == bound["compiled_module"]["sha256"]
        and activation["compiled_module"]["bytes"]
        == bound["compiled_module"]["bytes"]
        and receipt["gate"] == "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        and receipt["build_exit_code"] == 0
        and receipt["timed_out"] is False
        and receipt["source_inventory_unchanged"] is True
        and receipt["compiled_module_sha256"]
        == bound["compiled_module"]["sha256"],
        "full Development Editor compile succeeded with unchanged source",
    )

    build_log = resolve(bound["build_stdout"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "recovery05_and_recovery06_compiled",
        "Compile [x64] SkyguardM01GroupedTopologyRecovery05Capture.cpp"
        in build_log
        and "Compile [x64] SkyguardM01GroupedTopologyRecovery06CompileFix.cpp"
        in build_log
        and "Result: Succeeded" in build_log,
        "build output names both required translation units",
    )

    inventory = json.loads(
        resolve(bound["source_inventory"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "complete_source_inventory_unchanged",
        inventory["files"] == current_source_inventory(),
        f'{len(inventory["files"])} source files exact',
    )
    inventory_by_path = {
        record["file"]: record for record in inventory["files"]
    }
    required_source_records = (
        bound["recovery05_header"],
        bound["recovery05_source"],
        bound["recovery06_header"],
        bound["recovery06_source"],
        bound["module_rules"],
    )
    add(
        checks,
        "native_and_bridge_sources_match_activation",
        all(
            inventory_by_path.get(record["path"]) == {
                "file": record["path"],
                "bytes": record["bytes"],
                "sha256": record["sha256"],
            }
            for record in required_source_records
        ),
        "native capture, bridge, and module rules match compile inventory",
    )

    native_source = resolve(bound["recovery05_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "native_capture_inert_and_frame_driven",
        'TEXT("M01-HERO-GROUPED-TOPOLOGY-ATTEMPT03-RECOVERY05")'
        in native_source
        and "UTickableWorldSubsystem" in resolve(
            bound["recovery05_header"]["path"]
        ).read_text(encoding="utf-8-sig")
        and "FScreenshotRequest::RequestScreenshot(" in native_source
        and "RequestExitWithStatus" in native_source,
        "exact contract id, real game frames, viewport screenshot, bounded exit",
    )

    wrapper = resolve(bound["powershell_supervisor"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "wrapper_has_explicit_single_run_interlock",
        "AuthorizeSingleRecovery06NativeRun" in wrapper
        and "ExpectedExecutionContractSha256" in wrapper
        and "Assert-SourceInventory" in wrapper
        and "Stop-OwnedProcessTree" in wrapper
        and "PASS_RECOVERY05_NATIVE_CAPTURE_AWAITING_OFFLINE_AUDIT"
        in wrapper
        and "PASS_RECOVERY06_NATIVE_EXECUTION_" in wrapper
        and "Select-Object -Unique" in wrapper,
        "hash pin, source pin, owned timeout cleanup, and exact output gates",
    )

    attempt_root = ROOT / contract["outputs"]["attempt_root"]
    add(
        checks,
        "immutable_recovery06_namespace_absent",
        not attempt_root.exists(),
        str(attempt_root),
    )
    add(
        checks,
        "execution_requires_new_authorization",
        contract["authorization"]["explicit_authorization_required"]
        and contract["authorization"]["unreal_process_count"] == 1
        and contract["unreal_launch_authorized"] is False
        and contract["native_build_executed"] is True
        and contract["native_build_gate"]
        == "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE",
        "compile is accepted; Unreal remains separately unauthorized",
    )
    add(
        checks,
        "preserves_failures_and_never_promotes",
        contract["immutability"]["all_failed_attempts_preserved"]
        and contract["immutability"]["overwrite_or_retry_in_same_namespace"]
        is False
        and contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "new namespace only; review remains open",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery06-native-execution-readiness.v1"
        ),
        "gate": (
            "PASS_RECOVERY06_NATIVE_EXECUTION_READY_"
            "AWAITING_EXPLICIT_SINGLE_RUN_AUTHORIZATION"
            if not failures
            else "FAIL_CLOSED_RECOVERY06_NATIVE_EXECUTION_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "native_build_executed": True,
        "unreal_launched": False,
        "content_packages_created_or_modified": 0,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    if write_report:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    return report


if __name__ == "__main__":
    result = audit(write_report=True)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not result["failures"] else 1)
