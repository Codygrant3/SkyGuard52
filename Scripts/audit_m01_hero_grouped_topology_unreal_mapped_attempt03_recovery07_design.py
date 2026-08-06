"""Offline Recovery07 design audit; never invokes UBT or Unreal."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_DESIGN_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_DESIGN_READINESS.json"
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
    failed = contract["recovery06_failure_evidence"]
    add(
        checks,
        "recovery06_failure_preserved_exact",
        all(exact(record) for record in failed.values()),
        f"{len(failed)} failed-attempt artifacts exact",
    )
    log = resolve(failed["unreal_engine_log"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    supervisor = json.loads(
        resolve(failed["supervisor_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "resolution_root_cause_exact",
        'systemresolution.resx="888"' in log
        and 'systemresolution.resy="500"' in log
        and "-ResX=2048" in log
        and "-ResY=2048" in log
        and "-RenderOffscreen" in log
        and "Using Forced RHI: D3D12" in log
        and "Using Forced Feature Level in Editor: SM6" in log
        and supervisor["gate"] == "FAIL_CLOSED_RECOVERY06_NATIVE_NOT_ACCEPTED"
        and supervisor["promotion_allowed"] is False,
        "live offscreen viewport was 888x500 despite requested 2048",
    )

    ue = contract["ue58_api_evidence"]
    add(
        checks,
        "ue58_resolution_api_evidence_bound",
        all(exact(record) for record in ue.values()),
        f"{len(ue)} installed UE 5.8 implementation files exact",
    )
    highres_h = resolve(ue["highres_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    highres_cpp = resolve(ue["highres_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    client_cpp = resolve(ue["unreal_client_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    viewport_h = resolve(ue["game_viewport_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    viewport_cpp = resolve(ue["game_viewport_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    game_engine_cpp = resolve(ue["game_engine_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "ue58_highres_path_verified",
        "bool SetResolution(" in highres_h
        and "GScreenshotResolutionX = (ResolutionX * ResolutionScale);"
        in highres_cpp
        and "DummyViewport->SetInitialSize(FIntPoint(" in client_cpp
        and "bool FViewport::TakeHighResScreenShot()" in client_cpp
        and "ScreenshotCapturedDelegate.Broadcast(Size.X, Size.Y, Bitmap);"
        in viewport_cpp
        and "FSceneViewport* GetGameViewport();" in viewport_h
        and 'TEXT("ForceRes")' in game_engine_cpp,
        "dummy viewport guarantees configured pixels; callback supplies dimensions",
    )

    native = contract["native_sources"]
    add(
        checks,
        "recovery07_sources_hash_bound",
        all(exact(record) for record in native.values()),
        "new Recovery07 header and source exact",
    )
    source = resolve(native["implementation"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    header = resolve(native["header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "capture_independent_of_live_viewport_dimensions",
        "IsWorldRenderable" in header
        and "live_viewport_has_no_renderable_extent" in source
        and "Viewport is not exact 2048x2048" not in source
        and "HighRes.SetResolution(RequiredWidth, RequiredHeight, 1.0f)"
        in source
        and "SceneViewport->TakeHighResScreenShot()" in source
        and "Width != RequiredWidth || Height != RequiredHeight" in source,
        "live viewport only needs nonzero extent; callback must be exact 2048",
    )
    add(
        checks,
        "bounded_observable_wait_states",
        "WorldReadinessTimeoutSeconds = 45.0" in source
        and "ScreenshotTimeoutSeconds = 30.0" in source
        and "AbsoluteSessionTimeoutSeconds = 300.0" in source
        and "DiagnosticIntervalSeconds = 2.0" in source
        and "[RECOVERY07][STATE]" in source
        and "[RECOVERY07][FAIL]" in source
        and "IFileManager::Get().MakeDirectory(*OutputRoot, true);" in source
        and "RequestExitWithStatus" in source,
        "periodic state logs plus receipt-bearing self-failure",
    )
    add(
        checks,
        "runtime_api_compile_surface_safe",
        '#include "Components/SkyLightComponent.h"' in source
        and "Cast<UDirectionalLightComponent>(Key->GetLightComponent())"
        in source
        and "GetDirectionalLightComponent()" not in source,
        "Recovery07 does not repeat Recovery05 compile failures",
    )

    wrapper = contract["future_execution_wrapper"]
    add(
        checks,
        "future_wrapper_hash_bound_and_post_build_gated",
        exact(wrapper)
        and contract["future_build"]["full_module_compile_required"]
        and contract["future_build"]["post_build_execution_contract_required"]
        and not (
            ROOT
            / contract["future_build"]["post_build_execution_contract_path"]
        ).exists(),
        "wrapper exists but cannot run before DLL rebind contract",
    )
    wrapper_text = resolve(wrapper["path"]).read_text(encoding="utf-8-sig")
    add(
        checks,
        "future_wrapper_has_resolution_and_timeout_guards",
        "AuthorizeSingleRecovery07Run" in wrapper_text
        and "ExpectedExecutionContractSha256" in wrapper_text
        and '"-ForceRes", "-ResX=2048", "-ResY=2048"' in wrapper_text
        and "Stop-OwnedProcessTree" in wrapper_text
        and "PASS_RECOVERY07_HIGHRES_CAPTURE_AWAITING_OFFLINE_AUDIT"
        in wrapper_text
        and "[RECOVERY07\\]\\[STATE" in wrapper_text,
        "startup ForceRes defense plus highres receipt and diagnostics",
    )

    output = ROOT / contract["future_output"]["attempt_root"]
    add(
        checks,
        "new_output_namespace_absent",
        not output.exists(),
        str(output),
    )
    add(
        checks,
        "offline_only_never_promotes",
        contract["native_build_authorized"] is False
        and contract["native_build_executed"] is False
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False
        and contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "design/readiness only",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-attempt03."
            "recovery07-design-readiness.v1"
        ),
        "gate": (
            "PASS_RECOVERY07_OFFLINE_DESIGN_READY_"
            "AWAITING_SEPARATE_FULL_MODULE_COMPILE_AUTHORIZATION"
            if not failures
            else "FAIL_CLOSED_RECOVERY07_OFFLINE_DESIGN_NOT_READY"
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
