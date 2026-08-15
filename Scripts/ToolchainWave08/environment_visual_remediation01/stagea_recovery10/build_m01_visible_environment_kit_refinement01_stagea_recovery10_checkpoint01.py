from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01"
R09_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery09\build_m01_visible_environment_kit_refinement01_stagea_recovery09_checkpoint01.py"
R09_WORKER_BYTES = 11322
R09_WORKER_SHA256 = "0b8baf2524a1f864acdc84bb6c1ab83da45432d42fa84d8ad300fdb9aea30cab"
R09_GATE_TOKEN = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01"'
R10_GATE_TOKEN = f'GATE = "{GATE}"'


RENDER_CHECKPOINTS_IMPLEMENTATION = r'''
def render_checkpoints(scene: bpy.types.Scene, rig: dict[str, Any], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = (1920, 1080)
    cameras = {
        "coastal_route": ((50.0, -54.0, 22.0), (50.0, 54.0, 7.0), 52.0),
        "street_close": ((24.0, 39.0, 9.5), (31.0, 72.0, 8.0), 58.0),
        "district_aerial": ((50.0, -42.0, 44.0), (50.0, 52.0, 7.0), 50.0),
    }
    results: list[dict[str, Any]] = []
    for condition in ("daylight", "night", "storm"):
        configure_condition(scene, rig, condition, materials)
        for camera_id, (location, target, lens) in cameras.items():
            point_camera(rig["camera"], location, target, lens)
            if condition == "night":
                target_vector = Vector(target)
                view_direction = (Vector(location) - target_vector).normalized()
                rig["sun"].data.energy = 0.45
                rig["sun"].data.color = (0.18, 0.30, 0.60)
                rig["fill"].location = target_vector + view_direction * 20.0 + Vector((0.0, 0.0, 14.0))
                rig["fill"].rotation_euler = (target_vector - rig["fill"].location).to_track_quat("-Z", "Y").to_euler()
                rig["fill"].data.energy = 2500.0
                rig["fill"].data.color = (0.20, 0.36, 0.72)
                rig["moon"].location = target_vector + view_direction * 30.0 + Vector((14.0, 0.0, 30.0))
                rig["moon"].rotation_euler = (target_vector - rig["moon"].location).to_track_quat("-Z", "Y").to_euler()
                rig["moon"].data.energy = 2500.0
                rig["moon"].data.color = (0.15, 0.28, 0.65)
                scene.view_settings.exposure = 1.5
                trace_phase(
                    "night_review_lighting_aimed",
                    camera=camera_id,
                    fill_energy=2500.0,
                    moon_energy=2500.0,
                    sun_energy=0.45,
                    base_exposure=1.5,
                )
            elif condition == "storm":
                target_vector = Vector(target)
                view_direction = (Vector(location) - target_vector).normalized()
                rig["sun"].data.energy = 1.10
                rig["sun"].data.color = (0.42, 0.52, 0.64)
                rig["fill"].location = target_vector + view_direction * 20.0 + Vector((0.0, 0.0, 14.0))
                rig["fill"].rotation_euler = (target_vector - rig["fill"].location).to_track_quat("-Z", "Y").to_euler()
                rig["fill"].data.energy = 2800.0
                rig["fill"].data.color = (0.42, 0.50, 0.58)
                rig["moon"].location = target_vector + view_direction * 30.0 + Vector((14.0, 0.0, 30.0))
                rig["moon"].rotation_euler = (target_vector - rig["moon"].location).to_track_quat("-Z", "Y").to_euler()
                rig["moon"].data.energy = 2400.0
                rig["moon"].data.color = (0.30, 0.38, 0.48)
                scene.view_settings.exposure = 1.0
                trace_phase(
                    "storm_review_lighting_aimed",
                    camera=camera_id,
                    fill_energy=2800.0,
                    moon_energy=2400.0,
                    sun_energy=1.10,
                    base_exposure=1.0,
                )
            path = output / "renders" / "checkpoints" / f"{condition}_{camera_id}.png"
            trace_phase("checkpoint_render_start", condition=condition, camera=camera_id)
            metrics = render_and_measure(scene, path)
            calibration_passes: list[dict[str, float]] = []
            if condition in ("night", "storm"):
                target_mean = 0.012 if condition == "night" else 0.024
                target_black = 0.65 if condition == "night" else 0.55
                for calibration_index in range(2):
                    if metrics["mean_luma_linear"] >= target_mean and metrics["black_fraction_linear_0_01"] <= target_black:
                        break
                    current_exposure = float(scene.view_settings.exposure)
                    mean_adjustment = math.log2(target_mean / max(metrics["mean_luma_linear"], 1e-6))
                    black_adjustment = 1.0 if metrics["black_fraction_linear_0_01"] > target_black else 0.0
                    adjustment = min(5.5, max(0.5, mean_adjustment, black_adjustment))
                    new_exposure = min(7.0, current_exposure + adjustment)
                    if new_exposure <= current_exposure + 1e-6:
                        break
                    calibration_passes.append({
                        "pass": float(calibration_index + 1),
                        "previous_exposure": current_exposure,
                        "adjustment_stops": adjustment,
                        "new_exposure": new_exposure,
                        "previous_mean_luma_linear": metrics["mean_luma_linear"],
                        "previous_black_fraction_linear_0_01": metrics["black_fraction_linear_0_01"],
                    })
                    trace_phase(
                        f"{condition}_lighting_calibration",
                        camera=camera_id,
                        calibration_pass=calibration_index + 1,
                        previous_exposure=current_exposure,
                        adjustment_stops=adjustment,
                        new_exposure=new_exposure,
                        previous_mean_luma=metrics["mean_luma_linear"],
                        previous_black_fraction=metrics["black_fraction_linear_0_01"],
                    )
                    scene.view_settings.exposure = new_exposure
                    metrics = render_and_measure(scene, path)
            trace_phase(
                "checkpoint_render_complete",
                condition=condition,
                camera=camera_id,
                mean_luma=metrics["mean_luma_linear"],
                black_fraction=metrics["black_fraction_linear_0_01"],
                exposure=float(scene.view_settings.exposure),
                calibration_pass_count=len(calibration_passes),
            )
            require((metrics["width"], metrics["height"]) == (1920, 1080), f"Checkpoint resolution failed: {condition}_{camera_id}")
            minimum_luma = 0.008 if condition == "night" else 0.018 if condition == "storm" else 0.030
            maximum_black = 0.70 if condition == "night" else 0.58 if condition == "storm" else 0.35
            require(metrics["mean_luma_linear"] >= minimum_luma, f"Checkpoint is too dark after targeted review lighting: {condition}_{camera_id}")
            require(metrics["black_fraction_linear_0_01"] <= maximum_black, f"Checkpoint is excessively black after targeted review lighting: {condition}_{camera_id}")
            results.append({
                "condition": condition,
                "camera": camera_id,
                "path": str(path),
                "metrics": metrics,
                "exposure": float(scene.view_settings.exposure),
                "calibration_passes": calibration_passes,
                "night_review_lighting_aimed": condition == "night",
                "storm_review_lighting_aimed": condition == "storm",
                "passed": True,
            })
    require(len(results) == 9, "Checkpoint render count is not exactly nine")
    return results
'''.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_r09_module():
    if (
        not R09_WORKER.is_file()
        or R09_WORKER.stat().st_size != R09_WORKER_BYTES
        or sha256_file(R09_WORKER) != R09_WORKER_SHA256
    ):
        raise RuntimeError("Frozen Recovery09 worker authority changed")
    spec = importlib.util.spec_from_file_location("skyguard_r09_frozen_worker", R09_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the frozen Recovery09 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_recovery10_source() -> tuple[str, dict[str, object]]:
    module = load_r09_module()
    source, r09_receipt = module.load_recovery09_source()
    if source.count(R09_GATE_TOKEN) != 1:
        raise RuntimeError("Recovery09 gate token cardinality changed")
    source = source.replace(R09_GATE_TOKEN, R10_GATE_TOKEN, 1)
    source = module.replace_top_level_function(source, "render_checkpoints", RENDER_CHECKPOINTS_IMPLEMENTATION)
    graph = module.static_graph(source)
    if not graph["passed"]:
        raise RuntimeError(f"Recovery10 generated source has unresolved calls: {graph['unresolved_named_calls']}")
    required = (
        R10_GATE_TOKEN,
        '"night_review_lighting_aimed"',
        '"storm_review_lighting_aimed"',
        "fill_energy=2800.0",
        'if condition in ("night", "storm"):',
        'require(len(results) == 9, "Checkpoint render count is not exactly nine")',
        '"finalization_authorized":False',
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"Required Recovery10 token is absent: {token}")
    return source, {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery10-checkpoint01.in-memory-correction.v1",
        "gate": GATE,
        "recovery09_worker": str(R09_WORKER),
        "recovery09_worker_bytes": R09_WORKER_BYTES,
        "recovery09_worker_sha256": R09_WORKER_SHA256,
        "recovery09_design_receipt": r09_receipt,
        "bounded_correction": "CAMERA_TARGETED_STORM_REVIEW_LIGHTING_WITH_EXPOSURE_GUARD",
        "selected_night_probe_candidate": "A",
        "selected_storm_probe_candidate": "B",
        "generated_call_graph": graph,
        "recovery09_attempt_or_output_reused": False,
        "checkpoint_count": 9,
        "glb_count": 0,
        "texture_count": 0,
        "finalization_authorized": False,
        "passed": True,
    }


def main() -> int:
    source, receipt = load_recovery10_source()
    print(json.dumps(receipt, sort_keys=True), flush=True)
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery10_checkpoint01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(source, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery10 embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    raise SystemExit(main())
