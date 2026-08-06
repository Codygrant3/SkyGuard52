"""Offline, fail-closed readiness for Attempt07 Recovery01."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
UE_ROOT = Path(r"D:\UE_5.8")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY01_CONTRACT.json"
)
OUTPUT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY01_READINESS.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-01"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_files(root: Path, items: dict) -> bool:
    return all(
        (root / item["file"]).is_file()
        and sha256_file(root / item["file"]) == item["sha256"]
        and (
            "bytes" not in item
            or (root / item["file"]).stat().st_size == item["bytes"]
        )
        for item in items.values()
    )


def python_syntax_exact(paths: list[Path]) -> bool:
    try:
        for path in paths:
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"))
        return True
    except (SyntaxError, UnicodeError):
        return False


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery01 contract ID mismatch")

    failed = contract["immutable_failed_attempt07"]
    failed_root = ROOT / failed["root"]
    failed_manifest = json.loads(
        (failed_root / "run_manifest.json").read_text(
            encoding="utf-8-sig"
        )
    )
    predecessor = contract["immutable_predecessor"]
    predecessor_root = ROOT / predecessor["root"]
    predecessor_gate = json.loads(
        (predecessor_root / "gate_report.json").read_text(
            encoding="utf-8-sig"
        )
    )

    implementation_paths = {
        name: ROOT / item["file"]
        for name, item in contract["implementation_files"].items()
    }
    implementation_sources = {
        name: path.read_text(encoding="utf-8")
        for name, path in implementation_paths.items()
        if path.suffix in {".h", ".cpp", ".py", ".ps1"}
    }
    native_header = implementation_sources["native_header"]
    native_cpp = implementation_sources["native_implementation"]
    builder = implementation_sources["diagnostic_builder"]
    author = implementation_sources["recovery01_author"]
    proof = implementation_sources["recovery01_tiny_proof"]
    proof_helpers = implementation_sources["attempt07_proof_helpers"]
    supervisor = implementation_sources["recovery01_supervisor"]
    launcher = implementation_sources["recovery01_launcher"]

    source_evidence = contract["ue58_source_evidence"]
    interface_header_path = (
        UE_ROOT / source_evidence["material_interface_header"]["file"]
    )
    interface_header = interface_header_path.read_text(
        encoding="utf-8", errors="replace"
    )
    landscape_roots = [
        UE_ROOT / item
        for item in source_evidence["landscape_module_search"]["roots"]
    ]
    landscape_source_files = []
    for root in landscape_roots:
        if root.exists():
            landscape_source_files.extend(root.rglob("*.h"))
            landscape_source_files.extend(root.rglob("*.cpp"))
    landscape_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in landscape_source_files
    )

    outputs = contract["new_immutable_outputs"]
    execution_root = ROOT / contract["tiny_live_proof"]["execution_root"]
    module = ROOT / contract["compiled_module_before_recovery"]["file"]
    set_transient = native_cpp.split(
        "SetTransientLandscapeDiagnosticMaterialSynchronized(", 1
    )[1]
    capture_helper = proof_helpers.split("def capture_one(", 1)[1].split(
        "\ndef coverage_analysis", 1
    )[0]
    checks = {
        "contract_is_offline_pending_authorization": (
            contract["status"]
            == "OFFLINE_IMPLEMENTED_PENDING_EXPLICIT_AUTHORIZATION"
            and all(
                contract["execution_authorization"][field] is False
                for field in (
                    "unreal_launch_allowed",
                    "native_build_allowed",
                    "author_new_diagnostic_assets_allowed",
                    "tiny_live_proof_allowed",
                    "full_capture_allowed",
                    "profile_allowed",
                    "automatic_retry_allowed",
                    "network_allowed",
                    "promotion_allowed",
                )
            )
        ),
        "failed_attempt07_inventory_exact": exact_files(
            failed_root, failed["files"]
        ),
        "failed_attempt07_terminal_boundary_exact": (
            failed_manifest.get("terminal_state")
            == failed["terminal_state_required"]
            and len(failed_manifest.get("stages", []))
            == failed["stage_count_required"]
            and failed["failure_required"]
            in failed_manifest.get("errors", [])
            and failed_manifest.get("full_capture_invoked")
            is failed["full_capture_invoked_required"]
            and failed_manifest.get("profile_invoked")
            is failed["profile_invoked_required"]
        ),
        "failed_attempt07_saved_no_material_assets": all(
            not (ROOT / item["file"]).exists()
            for item in (
                {
                    "file": (
                        "Content/Skyguard/Materials/Diagnostics/"
                        "M_P45_LandscapeCoverage_Unlit_v3_attempt07.uasset"
                    )
                },
                {
                    "file": (
                        "Content/Skyguard/Materials/Diagnostics/"
                        "M_P45_LandscapeComponentId_Unlit_v3_attempt07.uasset"
                    )
                },
            )
        ),
        "recovery02_predecessor_exact_and_failed": (
            exact_files(predecessor_root, predecessor["files"])
            and predecessor_gate.get("gate")
            == predecessor["required_gate"]
            and predecessor_gate.get("technical_gate")
            == predecessor["required_technical_gate"]
        ),
        "locked_production_packages_exact": exact_files(
            ROOT, contract["locked_production_packages"]
        ),
        "pre_recovery_compiled_module_exact": (
            module.is_file()
            and sha256_file(module)
            == contract["compiled_module_before_recovery"]["sha256"]
        ),
        "ue58_source_hashes_exact": all(
            (
                UE_ROOT / source_evidence[name]["file"]
            ).is_file()
            and sha256_file(
                UE_ROOT / source_evidence[name]["file"]
            )
            == source_evidence[name]["sha256"]
            for name in (
                "material_interface_header",
                "material_header",
                "material_implementation",
            )
        ),
        "ue58_has_no_landscape_material_usage_flag": (
            "MATUSAGE_Landscape" not in interface_header
            and "MATUSAGE_Landscape" not in landscape_sources
        ),
        "implementation_hashes_exact": exact_files(
            ROOT, contract["implementation_files"]
        ),
        "python_syntax_exact": python_syntax_exact(
            list(implementation_paths.values())
        ),
        "invalid_usage_flag_paths_absent_from_recovery": all(
            token not in "\n".join(
                (
                    native_header,
                    native_cpp,
                    builder,
                    author,
                    proof,
                )
            )
            for token in (
                "MATUSAGE_Landscape",
                "used_with_landscape",
                "ensure_landscape_material_usage",
                "audit_landscape_material_usage",
            )
        ),
        "builder_recompiles_completed_graph_before_save": (
            "MaterialEditingLibrary" in builder
            and "mel.recompile_material(material)" in builder
            and "save_loaded_asset(material, False)" in builder
            and builder.index("mel.recompile_material(material)")
            < builder.index("save_loaded_asset(material, False)")
        ),
        "native_bridge_waits_and_audits_all_generated_resources": all(
            token in native_cpp
            for token in (
                "FAssetCompilingManager::Get().FinishAllCompilation()",
                "GShaderCompilingManager->FinishAllCompilation()",
                "Resource->FinishCompilation()",
                "Resource->IsCompilationFinished()",
                "Resource->GetGameThreadShaderMap()",
                "ShaderMap->IsValidForRendering()",
                "Result.LandscapeComponentCount == 16",
                "Result.ValidShaderMapResourceCount == 16",
            )
        ),
        "compilation_finishes_before_render_state_recreation": (
            set_transient.index(
                "Landscape->UpdateAllComponentMaterialInstances(true)"
            )
            < set_transient.index(
                "FinishLandscapeMaterialCompilation(Landscape, Material)"
            )
            < set_transient.index("Component->RecreateRenderState_Concurrent()")
            < set_transient.index("FlushRenderingCommands()")
        ),
        "camera_transform_precedes_configuration_and_flush": (
            capture_helper.index("capture.set_actor_location")
            < capture_helper.index(
                "configure_landscape_scene_capture_diagnostic"
            )
            and capture_helper.index("capture.set_actor_rotation")
            < capture_helper.index(
                "configure_landscape_scene_capture_diagnostic"
            )
            and '"transform_applied_before_configuration": True'
            in capture_helper
        ),
        "proof_requires_exact_compile_and_visual_gates": all(
            token in proof
            for token in (
                '"native_compilation_audits_exact"',
                '"coverage_c05_visible_white"',
                '"coverage_c04_visible_white"',
                '"all_16_component_ids_visible"',
                '"governed_material_restored"',
                '"locked_production_packages_unchanged"',
            )
        ),
        "supervisor_is_bounded_build_author_proof_only": (
            supervisor.index('"build_native_landscape_usage_bridge"')
            < supervisor.index('"author_recovery01_diagnostic_materials"')
            < supervisor.index('"recovery01_tiny_live_proof_d3d12_sm6"')
            and '"full_capture_allowed": False' in supervisor
            and '"profile_allowed": False' in supervisor
            and '"automatic_retry_allowed": False' in supervisor
            and '"promotion_allowed": False' in supervisor
            and "capture_skyguard_phase4" not in supervisor
            and "ProfileWarmupSeconds" not in supervisor
        ),
        "launcher_requires_exact_authorization_switch": (
            "if (-not $AuthorizeSingleRecoveryTinyProof)" in launcher
            and "--authorize-single-recovery-tiny-proof" in launcher
        ),
        "new_recovery_assets_absent": all(
            not (ROOT / outputs[name]["file"]).exists()
            for name in ("coverage_material", "component_id_material")
        ),
        "new_recovery_execution_root_absent": not execution_root.exists(),
    }
    ready = all(checks.values())
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery01-readiness.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": (
            "PASS_ATTEMPT07_RECOVERY01_OFFLINE_IMPLEMENTATION_READY_"
            "PENDING_AUTHORIZATION"
            if ready
            else "FAIL_ATTEMPT07_RECOVERY01_OFFLINE_NOT_READY"
        ),
        "corrected_diagnosis": contract["formal_diagnosis"],
        "checks": checks,
        "unreal_launched": False,
        "native_build_invoked": False,
        "failed_attempt07_mutated": False,
        "attempt06_or_recovery02_mutated": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
        "future_authorized_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt07_recovery01.ps1\" "
            "-AuthorizeSingleRecoveryTinyProof"
            if ready
            else None
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
