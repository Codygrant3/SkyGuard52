"""Offline Recovery10 compile-compat audit; never invokes UBT or Unreal."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY10_COMPILE_FIX_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY10_COMPILE_FIX_READINESS.json"
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


def line_sites(
    root: Path,
    line_number: int,
    token: str,
    suffixes: frozenset[str] = frozenset({".h", ".cpp"}),
) -> list[str]:
    sites: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in suffixes:
            continue
        lines = path.read_text(
            encoding="utf-8-sig", errors="replace"
        ).splitlines()
        if len(lines) >= line_number and token in lines[line_number - 1]:
            sites.append(path.as_posix())
    return sites


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []

    failed = contract["failed_build_evidence"]
    evidence_records = (
        failed["compile_receipt"],
        failed["build_stdout"],
        failed["build_stderr"],
        failed["source_inventory"],
    )
    add(
        checks,
        "failed_build_evidence_hash_bound",
        all(exact(record) for record in evidence_records),
        "receipt, stdout, empty stderr, and source inventory remain exact",
    )
    receipt = json.loads(
        resolve(failed["compile_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    stdout = resolve(failed["build_stdout"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "receipt_is_terminal_recovery09_compile_fail",
        receipt["gate"] == failed["gate"]
        and receipt["build_exit_code"] == failed["exit_code"]
        and receipt["timed_out"] == failed["timed_out"]
        and failed["retry_same_build_namespace_forbidden"],
        "exit 6 terminal compile failure; same namespace cannot be retried",
    )
    add(
        checks,
        "exact_three_compiler_errors_bound",
        stdout.count("error C") == 3
        and stdout.count("error C7595:") == 1
        and stdout.count("error C2511:") == 2
        and "Recovery09Capture.cpp(378,4)" in stdout
        and "Recovery09Capture.cpp(783,47)" in stdout
        and "Recovery09Capture.cpp(853,52)" in stdout,
        "one checked-format and two member-signature errors only",
    )

    frozen = contract["frozen_recovery09"]
    frozen_records = tuple(
        record
        for key, record in frozen.items()
        if isinstance(record, dict) and "path" in record
    )
    add(
        checks,
        "recovery09_artifacts_remain_frozen_exact",
        all(exact(record) for record in frozen_records)
        and frozen["must_remain_byte_identical"]
        and frozen["direct_edit_forbidden"],
        f"{len(frozen_records)} Recovery09 artifacts remain exact",
    )
    header = resolve(frozen["header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    source = resolve(frozen["source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "frozen_signature_mismatch_preserved",
        header.count("TArrayView64<const FColor> Colors") == 3
        and source.count("const TArray<FColor>& Colors) const") == 2
        and "LexToString(GMaxRHIFeatureLevel));" in source.splitlines()[379],
        "Recovery09 mismatch and line-380 FString call remain unedited",
    )

    inventory = json.loads(
        resolve(failed["source_inventory"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    inventory_by_path = {
        record["file"]: record for record in inventory["files"]
    }
    old = contract["failed_inventory_inputs"]
    add(
        checks,
        "failed_inventory_binds_original_inputs",
        inventory_by_path["Source/Skyguard52/Skyguard52.Build.cs"]["bytes"]
        == old["module_rules"]["bytes"]
        and inventory_by_path[
            "Source/Skyguard52/Skyguard52.Build.cs"
        ]["sha256"]
        == old["module_rules"]["sha256"]
        and inventory_by_path[
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery08CompileFix.h"
        ]["sha256"]
        == old["recovery08_bridge"]["sha256"]
        and inventory_by_path[
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery09Capture.cpp"
        ]["sha256"]
        == frozen["source"]["sha256"]
        and inventory_by_path[
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery09Capture.h"
        ]["sha256"]
        == frozen["header"]["sha256"],
        "failed inventory preserves original rules, R08 bridge, and R09",
    )
    add(
        checks,
        "recovery08_bridge_remains_exact",
        exact(old["recovery08_bridge"])
        and old["recovery08_bridge"]["remains_byte_identical"],
        "Recovery08 bridge is unchanged",
    )

    correction = contract["recovery10_correction"]
    add(
        checks,
        "recovery10_correction_hash_bound",
        exact(correction["forced_include_header"])
        and exact(correction["module_rules"]),
        "Recovery10 bridge and superseding module rules are exact",
    )
    bridge = resolve(correction["forced_include_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    rules = resolve(correction["module_rules"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "forced_include_order_is_exact",
        rules.count("ForceIncludeFiles.Add(Path.Combine(") == 3
        and rules.index("Recovery06CompileFix.h")
        < rules.index("Recovery08CompileFix.h")
        < rules.index("Recovery10CompileFix.h"),
        "Recovery10 is registered after Recovery06 and Recovery08",
    )
    add(
        checks,
        "member_declaration_bridge_is_scoped",
        bridge.count("#define BuildRecord(...)") == 1
        and bridge.count("#define WritePng(...)") == 1
        and bridge.index("#define BuildRecord")
        < bridge.index(
            '#include "SkyguardM01GroupedTopologyRecovery09Capture.h"'
        )
        < bridge.index("#undef WritePng")
        < bridge.index("#undef BuildRecord")
        and bridge.count("const TArray<FColor>& Colors") == 2,
        "only the frozen header declarations are rewritten, then macros end",
    )
    add(
        checks,
        "feature_level_proxy_extends_only_line_380",
        bridge.count(
            "TSkyguardRecovery08FeatureLevelAtLine<380>"
        )
        == 1
        and "#undef GMaxRHIFeatureLevel" in bridge
        and bridge.count("#define GMaxRHIFeatureLevel") == 1
        and "FSkyguardRecovery08PrintfFeatureLevel Get()" in bridge
        and "#define LexToString" not in bridge,
        "existing checked-format proxy is extended only at line 380",
    )

    project_sites = line_sites(
        ROOT / "Source", 380, "GMaxRHIFeatureLevel"
    )
    engine_sites = line_sites(
        Path(r"D:\UE_5.8\Engine\Source"),
        380,
        "GMaxRHIFeatureLevel",
        frozenset({".h"}),
    )
    expected_owner = correction["project_target_line_owner"]
    project_relative = [
        Path(path).relative_to(ROOT).as_posix() for path in project_sites
    ]
    add(
        checks,
        "line_380_collision_scan_exact",
        project_relative == [expected_owner]
        and len(engine_sites)
        == correction["installed_ue_header_target_line_collision_count"],
        f"project={project_relative}; engine_count={len(engine_sites)}",
    )
    forbidden = (
        "PRAGMA_DISABLE",
        "DISABLE_FORMAT",
        "#define LexToString",
    )
    add(
        checks,
        "no_validation_suppression_or_global_stringifier_macro",
        all(token not in bridge for token in forbidden)
        and correction["format_validation_suppression_forbidden"]
        and correction["global_lex_to_string_macro_forbidden"],
        "checked-format validation remains active",
    )

    future = contract["future_build"]
    add(
        checks,
        "build_and_launch_remain_unauthorized",
        future["requires_separate_authorization"]
        and future["unreal_launch_allowed"] is False
        and future["new_immutable_build_namespace_required"]
        and contract["native_build_authorized"] is False
        and contract["native_build_executed"] is False
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False
        and contract["blender_launched"] is False,
        "offline compile correction only",
    )
    add(
        checks,
        "never_promotes_or_closes",
        contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "compile readiness cannot promote evidence or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery10-compile-compat-readiness.v1"
        ),
        "gate": (
            "PASS_OFFLINE_RECOVERY10_COMPILE_COMPAT_READY_"
            "AWAITING_SEPARATE_FULL_MODULE_BUILD_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY10_COMPILE_COMPAT_NOT_READY"
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
