"""Offline Recovery07-runtime/Recovery08-compile execution audit."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_EXECUTION_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_RUNTIME_RECOVERY08_EXECUTION_READINESS.json"
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


def inventory_records(inventory: dict) -> dict[str, dict]:
    return {record["file"]: record for record in inventory["files"]}


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []
    bound = contract["bound_files"]

    add(
        checks,
        "all_execution_inputs_hash_bound",
        all(exact(record) for record in bound.values()),
        f"{len(bound)} execution inputs remain exact",
    )

    receipt = json.loads(
        resolve(bound["compile_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    activation = json.loads(
        resolve(bound["compile_activation"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "full_module_receipt_is_success",
        receipt["gate"] == "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        and receipt["build_exit_code"] == 0
        and receipt["timed_out"] is False
        and receipt["target"] == "Skyguard52Editor"
        and receipt["platform"] == "Win64"
        and receipt["configuration"] == "Development",
        "fresh full Skyguard52Editor Win64 Development build passed",
    )
    add(
        checks,
        "activation_matches_receipt",
        activation["gate"] == receipt["gate"]
        and activation["target"] == receipt["target"]
        and activation["platform"] == receipt["platform"]
        and activation["configuration"] == receipt["configuration"]
        and activation["build_exit_code"] == receipt["build_exit_code"]
        and activation["compiled_module"]["sha256"]
        == receipt["compiled_module_sha256"]
        and activation["source_inventory"]["sha256"]
        == bound["source_inventory"]["sha256"],
        "activation, receipt, source inventory, and module identity agree",
    )
    add(
        checks,
        "compiled_module_matches_receipt",
        exact(bound["compiled_module"])
        and receipt["compiled_module_bytes"]
        == bound["compiled_module"]["bytes"]
        and receipt["compiled_module_sha256"]
        == bound["compiled_module"]["sha256"],
        "current UnrealEditor-Skyguard52.dll is the receipt-bound module",
    )

    stdout = resolve(bound["build_stdout"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "build_log_proves_recovery07_compiled_and_linked",
        "[42/96] Compile [x64] SkyguardM01GroupedTopologyRecovery07Capture.cpp"
        in stdout
        and "[95/96] Link [x64] UnrealEditor-Skyguard52.dll" in stdout
        and "Result: Succeeded" in stdout
        and "error C" not in stdout,
        "Recovery07 compiled and the Skyguard52 DLL linked without errors",
    )

    inventory = json.loads(
        resolve(bound["source_inventory"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    records = inventory_records(inventory)
    expected_inventory = {
        "Source/Skyguard52/Skyguard52.Build.cs": bound["module_rules"],
        (
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery07Capture.cpp"
        ): bound["recovery07_source"],
        (
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery07Capture.h"
        ): bound["recovery07_header"],
        (
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery08CompileFix.h"
        ): bound["recovery08_compile_bridge"],
    }
    add(
        checks,
        "source_inventory_contains_exact_recovery07_08_inputs",
        all(
            path in records
            and records[path]["bytes"] == expected["bytes"]
            and records[path]["sha256"] == expected["sha256"]
            for path, expected in expected_inventory.items()
        ),
        "inventory binds Recovery07, Recovery08, and module rules",
    )

    disclosure = contract["generic_supervisor_contract_id_disclosure"]
    add(
        checks,
        "generic_contract_id_mismatch_explicit_and_non_authorizing",
        receipt["contract_id"] == disclosure["receipt_contract_id"]
        and disclosure["exact_match"] is False
        and disclosure["violates_recovery08_execution_contract"] is False
        and disclosure["fail_closed_due_to_mismatch"] is False
        and disclosure["disposition"]
        == "ACCEPTED_NON_GATING_GENERIC_SUPERVISOR_PROVENANCE_LABEL"
        and "grants no execution authorization" in disclosure["rationale"],
        "generic supervisor label mismatch disclosed and non-gating",
    )

    wrapper = resolve(bound["powershell_supervisor"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "wrapper_is_hash_bound_and_fail_closed",
        exact(bound["powershell_supervisor"])
        and "ExpectedExecutionContractSha256" in wrapper
        and "AuthorizeSingleRecovery07Run" in wrapper
        and "Recovery07 execution contract hash mismatch" in wrapper
        and "Immutable Recovery07 output exists" in wrapper,
        "wrapper requires explicit switch, exact contract hash, and empty output",
    )

    source = resolve(bound["recovery07_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    native = contract["native_runtime"]
    add(
        checks,
        "runtime_contract_id_matches_immutable_source",
        f'TEXT("{native["required_contract_id"]}")' in source
        and "ContractId == RequiredContractId" in source,
        "runtime remains inert without exact Recovery07 contract ID",
    )

    outputs = contract["outputs"]
    output_paths = (
        resolve(outputs["attempt_root"]),
        resolve(outputs["capture_root"]),
        resolve(outputs["supervisor_receipt"]),
    )
    add(
        checks,
        "recovery07_output_namespace_absent",
        all(not path.exists() for path in output_paths)
        and outputs["must_be_absent_before_execution"]
        and outputs["overwrite_or_retry_in_same_namespace"] is False,
        f"absent namespace: {output_paths[0]}",
    )

    activation_contract = contract["compile_activation"]
    add(
        checks,
        "post_build_activation_is_bound",
        contract["post_build_activation_bound"]
        and activation_contract["post_build_activation_bound"]
        and activation_contract["recovery07_translation_unit_compiled"]
        and activation_contract[
            "recovery08_forced_include_present_in_source_inventory"
        ]
        and activation_contract["compiled_module_hash_matches_receipt"],
        "successful module is bound to Recovery07 runtime plus Recovery08 fix",
    )

    add(
        checks,
        "launch_remains_unauthorized",
        contract["native_build_executed"]
        and contract["native_build_gate"]
        == "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False
        and contract["blender_launched"] is False,
        "build is complete; no runtime or Blender process is authorized",
    )
    add(
        checks,
        "never_promotes_or_closes",
        contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "execution readiness cannot promote evidence or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery07-runtime-recovery08-execution-readiness.v1"
        ),
        "gate": (
            "PASS_RECOVERY07_RUNTIME_RECOVERY08_EXECUTION_CONTRACT_"
            "HASH_READY_AWAITING_EXPLICIT_SINGLE_RUN_AUTHORIZATION"
            if not failures
            else "FAIL_CLOSED_RECOVERY07_RUNTIME_RECOVERY08_EXECUTION_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "unreal_launched": False,
        "blender_launched": False,
    }
    if write_report:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


if __name__ == "__main__":
    result = audit(write_report=True)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["failure_count"] == 0 else 1)
