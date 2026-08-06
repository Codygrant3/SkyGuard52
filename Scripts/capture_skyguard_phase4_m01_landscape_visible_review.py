"""Capture governed baseline/candidate Landscape review evidence.

Required command-line switches:
  -SkyguardReviewMode=baseline|candidate
  -SkyguardReviewMap=/Game/...
  -SkyguardReviewOutput=D:/.../captures/baseline

The loaded map is never saved. PCG generation is never invoked.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


EXPECTED_RHI_VALIDATION = "D3D12|SM6"
REPAIRED_CONTRACT_IDS = {
    "P4.5-M01-LANDSCAPE-VISIBLE-005",
    "P4.5-M01-LANDSCAPE-VISIBLE-006",
}
CAPTURE_EVIDENCE: dict[str, dict] = {}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf"(?:^|\s)-{re.escape(name)}=(?:\"([^\"]+)\"|(\S+))",
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Missing required -" + name + " command-line switch")
    return match.group(1) or match.group(2)


def require_d3d12_sm6() -> str:
    validation = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if validation != EXPECTED_RHI_VALIDATION:
        raise RuntimeError(
            "Governed capture requires active D3D12 SM6 before screenshots; "
            f"Unreal reported {validation!r}"
        )
    unreal.log(
        "[SkyguardP45LandscapeCapture][RHI_VALIDATED] " + validation
    )
    return validation


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Capture is not a valid PNG: " + str(path))
    return struct.unpack(">II", data[16:24])


def ensure_render_target(width: int, height: int):
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = unreal.RenderingLibrary.create_render_target2d(
        world,
        width,
        height,
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    if target is None:
        raise RuntimeError(
            "Could not create initialized transient review render target"
        )
    target.set_editor_property(
        "clear_color", unreal.LinearColor(0.0, 0.0, 0.0, 1.0)
    )
    return target


def find_candidate_camera(camera_id: str):
    label = "M01_P45_Camera_" + camera_id
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.CameraActor) and actor.get_actor_label() == label:
            return actor
    return None


def find_governed_landscape(contract: dict):
    expected_label = contract["candidate"]["landscape_actor_label"]
    expected_tag = unreal.Name(contract["candidate"]["landscape_actor_tag"])
    matches = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_class().get_name() not in {
            "Landscape",
            "LandscapeStreamingProxy",
        }:
            continue
        tags = list(actor.get_editor_property("tags") or [])
        if actor.get_actor_label() == expected_label and expected_tag in tags:
            matches.append(actor)
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one governed Landscape; found "
            + str(len(matches))
        )
    return matches[0]


def camera_transform(spec: dict) -> tuple:
    rotation = spec["rotation_degrees"]
    return (
        unreal.Vector(*spec["location_cm"]),
        unreal.Rotator(
            pitch=rotation["pitch"],
            yaw=rotation["yaw"],
            roll=rotation["roll"],
        ),
    )


def camera_proof_by_id(contract: dict) -> dict[str, dict]:
    if contract["contract_id"] != "P4.5-M01-LANDSCAPE-VISIBLE-006":
        return {}
    from phase4_m01_landscape_attempt06_camera_math import build_proof

    return {
        item["id"]: item
        for item in build_proof()["camera_results"]
    }


def record_capture_evidence(
    path: Path,
    spec: dict,
    contract: dict,
    configured=None,
    material_audit=None,
) -> None:
    proof = camera_proof_by_id(contract).get(spec["id"], {})
    CAPTURE_EVIDENCE[str(path)] = {
        "camera_id": spec["id"],
        "exact_location_cm": list(spec["location_cm"]),
        "exact_rotation_degrees": dict(spec["rotation_degrees"]),
        "camera_transform_authority": "contract_only",
        "forward_ray_intersects_bounds": proof.get(
            "forward_ray_intersects_landscape_bounds"
        ),
        "projected_top_surface_fraction": proof.get(
            "projected_top_surface_fraction"
        ),
        "show_only_component_count": (
            int(configured.show_only_landscape_component_count)
            if configured is not None
            else 0
        ),
        "generated_material_instance_count": (
            int(
                configured.generated_material_instance_ready_component_count
            )
            if configured is not None
            else (
                int(
                    material_audit
                    .generated_material_instance_ready_component_count
                )
                if material_audit is not None
                else 0
            )
        ),
        "material_parent_match_count": (
            int(configured.diagnostic_material_parent_match_component_count)
            if configured is not None
            else (
                int(
                    material_audit
                    .governed_material_parent_match_component_count
                )
                if material_audit is not None
                else 0
            )
        ),
        "render_thread_synchronization_complete": (
            bool(configured.render_thread_synchronized)
            if configured is not None
            else contract["contract_id"]
            != "P4.5-M01-LANDSCAPE-VISIBLE-006"
        ),
    }


def capture_lit_views(
    contract: dict, mode: str, output_dir: Path, width: int, height: int
) -> list[Path]:
    target = ensure_render_target(width, height)
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if capture is None:
        raise RuntimeError("Could not spawn transient SceneCapture2D")
    capture.set_actor_label("M01_P45_TransientReviewCapture")
    component = capture.capture_component2d
    component.set_editor_property("texture_target", target)
    component.set_editor_property(
        "capture_source",
        unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR,
    )
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    configured = None
    if contract["contract_id"] in REPAIRED_CONTRACT_IDS:
        authoring = (
            unreal.SkyguardMission01EnvironmentAuthoringLibrary
        )
        configured = authoring.configure_landscape_scene_capture_diagnostic(
            component,
            None,
            unreal.SkyguardLandscapeCaptureDiagnosticMode.LIT,
        )
        if not bool(configured.success):
            raise RuntimeError(
                "Could not configure governed lit SceneCapture: "
                + str(configured.error)
            )
    outputs = []
    for spec in contract["capture"]["cameras"]:
        location, rotation = camera_transform(spec)
        candidate_camera = (
            find_candidate_camera(spec["id"])
            if mode == "candidate"
            and contract["contract_id"]
            != "P4.5-M01-LANDSCAPE-VISIBLE-006"
            else None
        )
        if candidate_camera is not None:
            location = candidate_camera.get_actor_location()
            rotation = candidate_camera.get_actor_rotation()
        capture.set_actor_location(location, False, False)
        capture.set_actor_rotation(rotation, False)
        component.capture_scene()
        filename = f"{mode}_lit_{spec['id']}"
        unreal.RenderingLibrary.export_render_target(
            unreal.EditorLevelLibrary.get_editor_world(),
            target,
            str(output_dir),
            filename + ".png",
        )
        output = output_dir / (filename + ".png")
        outputs.append(output)
        record_capture_evidence(
            output,
            spec,
            contract,
            configured=configured,
        )
    unreal.EditorLevelLibrary.destroy_actor(capture)
    return outputs


def capture_diagnostic(
    spec: dict,
    output: Path,
    before_commands: list[str],
    width: int,
    height: int,
) -> None:
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = ensure_render_target(width, height)
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if capture is None:
        raise RuntimeError("Could not spawn transient diagnostic capture")
    component = capture.capture_component2d
    component.set_editor_property("texture_target", target)
    component.set_editor_property(
        "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
    )
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    location, rotation = camera_transform(spec)
    capture.set_actor_location(location, False, False)
    capture.set_actor_rotation(rotation, False)
    for command in before_commands:
        unreal.SystemLibrary.execute_console_command(world, command)
    component.capture_scene()
    unreal.RenderingLibrary.export_render_target(
        world, target, str(output.parent), output.name
    )
    unreal.EditorLevelLibrary.destroy_actor(capture)


def capture_candidate_diagnostics(
    contract: dict, output_dir: Path, width: int, height: int
) -> list[Path]:
    specs = {item["id"]: item for item in contract["capture"]["cameras"]}
    outputs = [
        output_dir / "candidate_diagnostic_landscape_lod_C05.png",
        output_dir / "candidate_diagnostic_shader_complexity_C04.png",
        output_dir / "candidate_diagnostic_component_boundary_C05.png",
    ]
    capture_diagnostic(
        specs["C05_COVERAGE_HIGH"],
        outputs[0],
        ["viewmode lit", "Landscape.DebugViewMode 5"],
        width,
        height,
    )
    capture_diagnostic(
        specs["C04_INLAND_CLOSE"],
        outputs[1],
        ["Landscape.DebugViewMode 0", "viewmode shadercomplexity"],
        width,
        height,
    )
    capture_diagnostic(
        specs["C05_COVERAGE_HIGH"],
        outputs[2],
        ["viewmode lit", "Landscape.DebugViewMode 6"],
        width,
        height,
    )
    unreal.SystemLibrary.execute_console_command(
        unreal.EditorLevelLibrary.get_editor_world(), "Landscape.DebugViewMode 0"
    )
    unreal.SystemLibrary.execute_console_command(
        unreal.EditorLevelLibrary.get_editor_world(), "viewmode lit"
    )
    return outputs


def capture_native_diagnostic(
    contract: dict,
    spec: dict,
    output: Path,
    width: int,
    height: int,
    landscape,
    mode,
    material_audit=None,
) -> None:
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = ensure_render_target(width, height)
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if capture is None:
        raise RuntimeError("Could not spawn native diagnostic SceneCapture")
    try:
        component = capture.capture_component2d
        component.set_editor_property("texture_target", target)
        configured = (
            unreal.SkyguardMission01EnvironmentAuthoringLibrary
            .configure_landscape_scene_capture_diagnostic(
                component, landscape, mode
            )
        )
        if not bool(configured.success):
            raise RuntimeError(
                "Native SceneCapture diagnostic configuration failed: "
                + str(configured.error)
            )
        if contract["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-006":
            if not bool(configured.render_thread_synchronized):
                raise RuntimeError(
                    "Attempt06 native capture was not render-thread synchronized"
                )
            if mode in {
                unreal.SkyguardLandscapeCaptureDiagnosticMode.LANDSCAPE_COVERAGE,
                unreal.SkyguardLandscapeCaptureDiagnosticMode.COMPONENT_BOUNDARY,
            } and (
                int(configured.show_only_landscape_component_count) != 16
                or int(
                    configured
                    .generated_material_instance_ready_component_count
                )
                != 16
                or int(
                    configured
                    .diagnostic_material_parent_match_component_count
                )
                != 16
            ):
                raise RuntimeError(
                    "Attempt06 explicit 16-component diagnostic audit failed"
                )
        location, rotation = camera_transform(spec)
        capture.set_actor_location(location, False, False)
        capture.set_actor_rotation(rotation, False)
        component.capture_scene()
        unreal.RenderingLibrary.export_render_target(
            world, target, str(output.parent), output.name
        )
        record_capture_evidence(
            output,
            spec,
            contract,
            configured=configured,
            material_audit=material_audit,
        )
    finally:
        unreal.EditorLevelLibrary.destroy_actor(capture)


def apply_transient_material(contract: dict, authoring, landscape, material):
    if contract["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-006":
        audit = (
            authoring.set_transient_landscape_diagnostic_material_synchronized(
                landscape, material
            )
        )
        if (
            not bool(audit.success)
            or int(audit.landscape_component_count) != 16
            or int(
                audit.generated_material_instance_ready_component_count
            )
            != 16
            or int(
                audit.governed_material_parent_match_component_count
            )
            != 16
        ):
            raise RuntimeError(
                "Attempt06 synchronized diagnostic material audit failed: "
                + str(audit.error)
            )
        return audit
    if not authoring.set_transient_landscape_diagnostic_material(
        landscape, material
    ):
        raise RuntimeError("Could not apply transient Landscape material")
    return None


def capture_repaired_candidate_diagnostics(
    contract: dict, output_dir: Path, width: int, height: int
) -> list[Path]:
    authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
    modes = unreal.SkyguardLandscapeCaptureDiagnosticMode
    landscape = find_governed_landscape(contract)
    governed_material = unreal.load_asset(
        contract["candidate"]["landscape_material"]
    )
    repair_outputs = contract["repair"]["future_immutable_outputs"]
    coverage_material = unreal.load_asset(
        repair_outputs["coverage_material"]
    )
    component_material = unreal.load_asset(
        repair_outputs["component_id_material"]
    )
    if not governed_material or not coverage_material or not component_material:
        raise RuntimeError("Attempt05 diagnostic material set is incomplete")
    outputs = []
    specs = {item["id"]: item for item in contract["capture"]["cameras"]}
    try:
        coverage_audit = apply_transient_material(
            contract, authoring, landscape, coverage_material
        )
        for spec in contract["capture"]["cameras"]:
            output = (
                output_dir
                / f"candidate_diagnostic_landscape_coverage_{spec['id']}.png"
            )
            capture_native_diagnostic(
                contract,
                spec,
                output,
                width,
                height,
                landscape,
                modes.LANDSCAPE_COVERAGE,
                coverage_audit,
            )
            outputs.append(output)
        component_audit = apply_transient_material(
            contract, authoring, landscape, component_material
        )
        component_output = (
            output_dir
            / "candidate_diagnostic_component_boundary_C05.png"
        )
        capture_native_diagnostic(
            contract,
            specs["C05_COVERAGE_HIGH"],
            component_output,
            width,
            height,
            landscape,
            modes.COMPONENT_BOUNDARY,
            component_audit,
        )
        outputs.append(component_output)
        governed_audit = apply_transient_material(
            contract, authoring, landscape, governed_material
        )
        complexity_output = (
            output_dir
            / "candidate_diagnostic_shader_complexity_C04.png"
        )
        capture_native_diagnostic(
            contract,
            specs["C04_INLAND_CLOSE"],
            complexity_output,
            width,
            height,
            landscape,
            modes.SHADER_COMPLEXITY,
            governed_audit,
        )
        outputs.append(complexity_output)
    finally:
        apply_transient_material(
            contract, authoring, landscape, governed_material
        )
        restored = authoring.audit_landscape_visible_readiness(
            landscape, governed_material
        )
        if not bool(restored.success):
            raise RuntimeError(
                "Landscape failed live readiness after diagnostic restore: "
                + str(restored.error)
            )
    return outputs


def main() -> None:
    CAPTURE_EVIDENCE.clear()
    contract = load_effective_contract()
    rhi_validation = require_d3d12_sm6()
    mode = parse_switch("SkyguardReviewMode").lower()
    map_path = parse_switch("SkyguardReviewMap")
    output_dir = Path(parse_switch("SkyguardReviewOutput"))
    if mode not in {"baseline", "candidate"}:
        raise RuntimeError("Review mode must be baseline or candidate")
    expected_map = (
        contract["baseline"]["immutable_map"]
        if mode == "baseline"
        else contract["candidate"]["immutable_map"]
    )
    if map_path != expected_map:
        raise RuntimeError("Review map does not match governed contract")
    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        raise RuntimeError("Review map does not exist: " + map_path)

    baseline_file = ROOT / contract["baseline"]["file"]
    baseline_hash_before = sha256_file(baseline_file)
    if baseline_hash_before != contract["baseline"]["sha256"]:
        raise RuntimeError("Immutable baseline hash failed before capture")
    output_dir.mkdir(parents=True, exist_ok=False)
    if not unreal.EditorLevelLibrary.load_level(map_path):
        raise RuntimeError("Could not load review map")

    width, height = contract["capture"]["resolution"]
    lit = capture_lit_views(contract, mode, output_dir, width, height)
    if mode == "candidate":
        diagnostics = (
            capture_repaired_candidate_diagnostics(
                contract, output_dir, width, height
            )
            if contract["contract_id"] in REPAIRED_CONTRACT_IDS
            else capture_candidate_diagnostics(
                contract, output_dir, width, height
            )
        )
    else:
        diagnostics = []
    all_files = lit + diagnostics

    # HighResShot requests may finish at the end of the next editor frame.
    # The supervisor additionally polls every required path before acceptance.
    existing = [path for path in all_files if path.is_file() and path.stat().st_size]
    records = []
    for path in existing:
        dimensions = png_dimensions(path)
        records.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "dimensions": list(dimensions),
                **CAPTURE_EVIDENCE.get(str(path), {}),
            }
        )

    pcg_components = [
        actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if actor.get_class().get_name() == "PCGWorldActor"
    ]
    baseline_hash_after = sha256_file(baseline_file)
    report = {
        "schema": "skyguard.phase4.m01-landscape-capture-manifest.v1",
        "contract_id": contract["contract_id"],
        "mode": mode,
        "map": map_path,
        "resolution": [width, height],
        "rhi_validation": rhi_validation,
        "rhi_name": "D3D12",
        "feature_level": "SM6",
        "baseline_sha256_before": baseline_hash_before,
        "baseline_sha256_after": baseline_hash_after,
        "requested_lit_count": 5,
        "requested_diagnostic_count": (
            7
            if mode == "candidate"
            and contract["contract_id"] in REPAIRED_CONTRACT_IDS
            else (3 if mode == "candidate" else 0)
        ),
        "files_complete_at_script_exit": len(existing) == len(all_files),
        "files": records,
        "generated_pcg_world_actor_count": len(pcg_components),
        "pcg_generation_invoked": False,
        "world_saved": False,
        "camera_transform_authority": (
            "contract_only"
            if contract["contract_id"]
            == "P4.5-M01-LANDSCAPE-VISIBLE-006"
            else "legacy_contract_or_serialized_actor"
        ),
        "serialized_camera_actor_fallback_used": False,
    }
    manifest_path = output_dir / "capture_manifest.json"
    manifest_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[SkyguardP45LandscapeCapture] " + json.dumps(report))
    if baseline_hash_before != baseline_hash_after:
        raise RuntimeError("Immutable baseline changed during capture")
    expected_diagnostic_count = (
        7
        if mode == "candidate"
        and contract["contract_id"] in REPAIRED_CONTRACT_IDS
        else (3 if mode == "candidate" else 0)
    )
    if len(lit) != 5 or len(diagnostics) != expected_diagnostic_count:
        raise RuntimeError("Governed capture request count mismatch")


if __name__ == "__main__":
    main()
