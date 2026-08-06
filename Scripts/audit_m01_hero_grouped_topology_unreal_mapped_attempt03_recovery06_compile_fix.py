"""Offline Recovery06 compile-bridge audit; never invokes UBT or Unreal."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_COMPILE_FIX_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_COMPILE_FIX_READINESS.json"
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


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []

    failed = contract["failed_build_evidence"]
    add(
        checks,
        "failed_build_evidence_bound",
        exact(failed["build_log"])
        and exact(failed["recovery05_design_contract"]),
        "failed build log and Recovery05 design contract exact",
    )
    log = resolve(failed["build_log"]["path"]).read_text(encoding="utf-8-sig")
    add(
        checks,
        "exact_compiler_failures_present",
        log.count("error C2027: use of undefined type 'USkyLightComponent'") == 2
        and log.count(
            "error C2039: 'GetDirectionalLightComponent': "
            "is not a member of 'ADirectionalLight'"
        )
        == 1,
        "C2027 occurs twice and C2039 occurs once",
    )

    frozen = contract["frozen_recovery05_source"]
    add(
        checks,
        "recovery05_source_frozen_exact",
        exact(frozen)
        and frozen["must_remain_byte_identical"]
        and frozen["direct_edit_forbidden"],
        f'{frozen["path"]} remains byte-identical',
    )
    frozen_source = resolve(frozen["path"]).read_text(encoding="utf-8-sig")
    add(
        checks,
        "frozen_failure_surface_preserved",
        frozen_source.count("GetDirectionalLightComponent()") == 1
        and '#include "Components/SkyLightComponent.h"' not in frozen_source,
        "the evidenced failure surface remains unchanged in Recovery05",
    )

    ue = contract["ue58_api_evidence"]
    add(
        checks,
        "ue58_evidence_hash_bound",
        all(exact(record) for record in ue.values()),
        "installed UBT and five UE 5.8 API headers exact",
    )
    module_rules = resolve(ue["module_rules"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    sky_actor = resolve(ue["sky_light_actor_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    directional_actor = resolve(
        ue["directional_light_actor_header"]["path"]
    ).read_text(encoding="utf-8-sig")
    light_actor = resolve(ue["light_actor_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    directional_component = resolve(
        ue["directional_light_component_header"]["path"]
    ).read_text(encoding="utf-8-sig")
    add(
        checks,
        "ue58_api_signatures_verified",
        "public List<string> ForceIncludeFiles { get; } = [];" in module_rules
        and "USkyLightComponent* GetLightComponent() const" in sky_actor
        and "ULightComponent* GetLightComponent() const" in light_actor
        and "UDirectionalLightComponent* GetComponent() const" in directional_actor
        and "#if WITH_EDITORONLY_DATA" in directional_actor
        and "void SetAtmosphereSunLight(bool bNewValue)" in directional_component,
        "forced include supported; runtime base getter and typed cast required",
    )

    bridge = contract["recovery06_compile_bridge"]
    bridge_records = (
        bridge["forced_include_header"],
        bridge["runtime_cast_source"],
        bridge["module_rules_file"],
    )
    add(
        checks,
        "recovery06_bridge_hash_bound",
        all(exact(record) for record in bridge_records),
        "bridge header, helper source, and module rules exact",
    )
    bridge_header = resolve(bridge["forced_include_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    helper_source = resolve(bridge["runtime_cast_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    build_rules = resolve(bridge["module_rules_file"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "sky_light_type_completed_by_bridge",
        '#include "Components/SkyLightComponent.h"' in bridge_header,
        "forced header completes USkyLightComponent",
    )
    add(
        checks,
        "directional_runtime_cast_checked",
        "Cast<UDirectionalLightComponent>(" in helper_source
        and "Light ? Light->GetLightComponent() : nullptr" in helper_source
        and "checkf(" in helper_source
        and "Light->GetComponent()" not in helper_source,
        "helper uses runtime-safe base getter, typed cast, and checkf",
    )
    add(
        checks,
        "forced_include_registered",
        "using System.IO;" in build_rules
        and "ForceIncludeFiles.Add(Path.Combine(" in build_rules
        and '"SkyguardM01GroupedTopologyRecovery06CompileFix.h"' in build_rules,
        "Skyguard52 module force-includes the Recovery06 bridge",
    )
    add(
        checks,
        "macro_is_narrow_and_source_collision_free",
        bridge_header.count("#define GetDirectionalLightComponent()") == 1
        and bridge_header.count("SkyguardRecovery06RequireDirectionalLight(Key)")
        == 1
        and frozen_source.count("GetDirectionalLightComponent()") == 1
        and all(
            "GetDirectionalLightComponent()" not in path.read_text(
                encoding="utf-8-sig"
            )
            for path in (ROOT / "Source/Skyguard52").glob("*")
            if path.suffix in {".h", ".cpp"}
            and path
            not in {
                resolve(frozen["path"]),
                resolve(bridge["forced_include_header"]["path"]),
            }
        ),
        "one macro definition, one frozen call site, no other project call sites",
    )

    future_output = ROOT / contract["future_execution_output"]
    add(
        checks,
        "future_namespace_absent",
        not future_output.exists(),
        str(future_output),
    )
    future = contract["future_build"]
    add(
        checks,
        "build_and_launch_not_authorized",
        future["requires_separate_authorization"]
        and future["unreal_launch_allowed"] is False
        and future["post_build_dll_hash_must_be_bound_before_execution"]
        and future["root_must_wait_for_final_execution_handoff"]
        and contract["native_build_authorized"] is False
        and contract["native_build_executed"] is False
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False,
        "separate build, DLL rebind, then separate execution handoff",
    )
    add(
        checks,
        "never_promotes_or_closes",
        contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "compile bridge readiness only",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery06-compile-bridge-readiness.v1"
        ),
        "gate": (
            "PASS_OFFLINE_RECOVERY06_COMPILE_BRIDGE_READY_"
            "AWAITING_SEPARATE_BUILD_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY06_COMPILE_BRIDGE_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "native_build_executed": False,
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
