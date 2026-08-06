"""Offline Recovery08 compile-fix audit; never invokes UBT, Unreal, or Blender."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY08_COMPILE_FIX_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY08_COMPILE_FIX_READINESS.json"
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


def project_sites_at_line(line_number: int, token: str) -> list[str]:
    sites: list[str] = []
    source_root = ROOT / "Source"
    for path in sorted(source_root.rglob("*")):
        if path.suffix.lower() not in {".h", ".cpp"}:
            continue
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if len(lines) >= line_number and token in lines[line_number - 1]:
            sites.append(path.relative_to(ROOT).as_posix())
    return sites


def engine_header_sites_at_line(line_number: int, token: str) -> list[str]:
    sites: list[str] = []
    engine_source = Path(r"D:\UE_5.8\Engine\Source")
    for path in sorted(engine_source.rglob("*.h")):
        lines = path.read_text(
            encoding="utf-8-sig", errors="replace"
        ).splitlines()
        if len(lines) >= line_number and token in lines[line_number - 1]:
            sites.append(path.as_posix())
    return sites


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []

    evidence = contract["failed_build_evidence"]
    evidence_records = (
        evidence["compile_receipt"],
        evidence["build_stdout"],
        evidence["build_stderr"],
        evidence["source_inventory"],
    )
    add(
        checks,
        "failed_build_evidence_hash_bound",
        all(exact(record) for record in evidence_records),
        "receipt, stdout, empty stderr, and source inventory remain exact",
    )
    receipt = json.loads(
        resolve(evidence["compile_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    stdout = resolve(evidence["build_stdout"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "receipt_is_terminal_recovery07_compile_fail",
        receipt["gate"] == evidence["receipt_gate"]
        and receipt["build_exit_code"] == evidence["receipt_exit_code"]
        and receipt["timed_out"] is False,
        "exit 6, terminal compile failure, not a timeout",
    )
    add(
        checks,
        "sole_c7595_failure_bound",
        stdout.count("error C7595:") == 1
        and stdout.count("SNeedsDereferencedWideString") == 2
        and stdout.count("error C") == 1
        and "SkyguardM01GroupedTopologyRecovery07Capture.cpp(347,4)"
        in stdout,
        "one compiler error: C7595 at format expression line 347",
    )

    frozen = contract["frozen_recovery07"]
    add(
        checks,
        "recovery07_files_remain_frozen_exact",
        exact(frozen["source"])
        and exact(frozen["header"])
        and frozen["must_remain_byte_identical"]
        and frozen["direct_edit_forbidden"],
        "Recovery07 source and header remain byte-identical",
    )
    frozen_source = resolve(frozen["source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    frozen_lines = frozen_source.splitlines()
    add(
        checks,
        "frozen_failure_expression_preserved",
        len(frozen_lines) >= 349
        and 'TEXT("active_rhi_not_d3d12_sm6:%s|%s")'
        in frozen_lines[346]
        and "LexToString(GMaxRHIFeatureLevel)" in frozen_lines[348]
        and "*LexToString(GMaxRHIFeatureLevel)" not in frozen_lines[348],
        "line 349 remains the evidenced invalid FString argument",
    )

    ue = contract["ue58_api_evidence"]
    add(
        checks,
        "ue58_rhi_api_evidence_exact",
        exact(ue["rhi_strings"]) and exact(ue["rhi_feature_level"]),
        "installed UE 5.8 RHI evidence remains exact",
    )
    rhi_strings = resolve(ue["rhi_strings"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    rhi_feature = resolve(ue["rhi_feature_level"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "ue58_signatures_confirm_root_cause",
        ue["rhi_strings"]["required_signature"] in rhi_strings
        and ue["rhi_feature_level"]["required_signature"] in rhi_feature,
        "feature-level LexToString returns FString; global is enum Type",
    )

    correction = contract["recovery08_correction"]
    add(
        checks,
        "recovery08_files_hash_bound",
        exact(correction["forced_include_header"])
        and exact(correction["module_rules"]),
        "Recovery08 bridge and module rules are exact",
    )
    bridge = resolve(correction["forced_include_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    rules = resolve(correction["module_rules"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "forced_include_registered_after_recovery06",
        rules.count("ForceIncludeFiles.Add(Path.Combine(") == 2
        and rules.index("SkyguardM01GroupedTopologyRecovery06CompileFix.h")
        < rules.index("SkyguardM01GroupedTopologyRecovery08CompileFix.h"),
        "Recovery08 is the second registered force include",
    )
    add(
        checks,
        "line_scoped_type_correction_is_exact",
        "TSkyguardRecovery08FeatureLevelAtLine<349>" in bridge
        and "#define GMaxRHIFeatureLevel" in bridge
        and "TSkyguardRecovery08FeatureLevelAtLine<__LINE__>::Get()" in bridge
        and "FORCEINLINE const TCHAR* LexToString(" in bridge
        and "StableValue = ::LexToString(FeatureLevel.Value);" in bridge,
        "only source line 349 selects the const TCHAR pointer proxy",
    )
    add(
        checks,
        "default_path_preserves_enum_type",
        "static ERHIFeatureLevel::Type Get()" in bridge
        and "return GMaxRHIFeatureLevel;" in bridge,
        "all non-349 uses retain ERHIFeatureLevel::Type",
    )
    forbidden = (
        "#define LexToString",
        "SNeedsDereferencedWideString",
        "DISABLE_FORMAT",
        "PRAGMA_DISABLE",
    )
    add(
        checks,
        "no_global_stringifier_or_validator_suppression",
        all(token not in bridge for token in forbidden),
        "no LexToString macro and no checked-format suppression",
    )

    target_sites = project_sites_at_line(
        correction["target_line"], "GMaxRHIFeatureLevel"
    )
    add(
        checks,
        "target_line_collision_scan_exact",
        len(target_sites) == correction["target_line_project_collision_count"]
        and target_sites
        == [correction["target_line_project_collision_owner"]],
        f"line 349 owner set: {target_sites}",
    )
    engine_target_sites = engine_header_sites_at_line(
        correction["target_line"], "GMaxRHIFeatureLevel"
    )
    add(
        checks,
        "installed_ue_header_target_line_collision_free",
        len(engine_target_sites)
        == correction["target_line_installed_ue_header_collision_count"],
        f"installed UE header line 349 owner set: {engine_target_sites}",
    )

    supersession = contract["supersession"]
    add(
        checks,
        "supersession_is_compile_boundary_only",
        "compiler-compatibility boundary"
        in supersession["compile_implementation"]
        and "immutable runtime implementation"
        in supersession["runtime_capture_implementation"]
        and supersession["recovery07_failed_module_must_not_be_reused"]
        and supersession["recovery07_evidence_remains_terminal_fail"],
        "Recovery08 fixes compilation; Recovery07 capture behavior is retained",
    )

    future_output = ROOT / contract["future_execution_output"]
    add(
        checks,
        "future_recovery08_namespace_absent",
        not future_output.exists(),
        str(future_output),
    )
    future = contract["future_build"]
    add(
        checks,
        "build_and_launch_remain_unauthorized",
        future["requires_separate_authorization"]
        and future["success_receipt_and_new_dll_hash_required"]
        and future["unreal_launch_allowed"] is False
        and contract["native_build_authorized"] is False
        and contract["native_build_executed"] is False
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False
        and contract["blender_launch_authorized"] is False
        and contract["blender_launched"] is False,
        "offline correction only; build and execution require later handoffs",
    )
    add(
        checks,
        "never_promotes_or_closes",
        contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "readiness cannot promote evidence or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery08-compile-fix-readiness.v1"
        ),
        "gate": (
            "PASS_OFFLINE_RECOVERY08_COMPILE_FIX_READY_"
            "AWAITING_SEPARATE_BUILD_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY08_COMPILE_FIX_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "native_build_executed": False,
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
