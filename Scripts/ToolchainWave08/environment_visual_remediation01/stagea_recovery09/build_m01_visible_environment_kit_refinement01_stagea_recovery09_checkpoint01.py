from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01"
R08_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery08\build_m01_visible_environment_kit_refinement01_stagea_recovery08_checkpoint01.py"
R08_WORKER_BYTES = 10929
R08_WORKER_SHA256 = "0e7a1ffa28477a3dd94b326e1c31a56833e37bd2952df8b5eb87145f4b2193dc"
R08_GATE_TOKEN = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY08_CHECKPOINT01"'
R09_GATE_TOKEN = f'GATE = "{GATE}"'


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
            path = output / "renders" / "checkpoints" / f"{condition}_{camera_id}.png"
            trace_phase("checkpoint_render_start", condition=condition, camera=camera_id)
            metrics = render_and_measure(scene, path)
            calibration_passes: list[dict[str, float]] = []
            if condition == "night":
                for calibration_index in range(2):
                    if metrics["mean_luma_linear"] >= 0.010 and metrics["black_fraction_linear_0_01"] <= 0.65:
                        break
                    current_exposure = float(scene.view_settings.exposure)
                    mean_adjustment = math.log2(0.012 / max(metrics["mean_luma_linear"], 1e-6))
                    black_adjustment = 1.0 if metrics["black_fraction_linear_0_01"] > 0.65 else 0.0
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
                        "night_lighting_calibration",
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
                "passed": True,
            })
    require(len(results) == 9, "Checkpoint render count is not exactly nine")
    return results
'''.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_r08_module():
    if not R08_WORKER.is_file() or R08_WORKER.stat().st_size != R08_WORKER_BYTES or sha256_file(R08_WORKER) != R08_WORKER_SHA256:
        raise RuntimeError("Frozen Recovery08 worker authority changed")
    spec = importlib.util.spec_from_file_location("skyguard_r08_frozen_worker", R08_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the frozen Recovery08 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_top_level_function(source: str, name: str, replacement: str) -> str:
    tree = ast.parse(source)
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"Top-level function cardinality for {name} is {len(matches)}")
    node = matches[0]
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[: node.lineno - 1])
    end = sum(len(line) for line in lines[: node.end_lineno])
    suffix = "\n" if source[start:end].endswith("\n") else ""
    return source[:start] + replacement + suffix + source[end:]


def static_graph(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    definitions = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    imports: set[str] = set()
    assigned: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Assign):
            assigned.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)
    called = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    unresolved = sorted(called - (set(dir(builtins)) | definitions | imports | assigned))
    return {"function_and_class_definition_count":len(definitions),"named_call_count":len(called),"unresolved_named_calls":unresolved,"passed":not unresolved}


def load_recovery09_source() -> tuple[str, dict[str, object]]:
    module = load_r08_module()
    source, r08_receipt = module.load_recovery08_source()
    if source.count(R08_GATE_TOKEN) != 1:
        raise RuntimeError("Recovery08 gate token cardinality changed")
    source = source.replace(R08_GATE_TOKEN, R09_GATE_TOKEN, 1)
    source = replace_top_level_function(source, "render_checkpoints", RENDER_CHECKPOINTS_IMPLEMENTATION)
    graph = static_graph(source)
    if not graph["passed"]:
        raise RuntimeError(f"Recovery09 generated source has unresolved calls: {graph['unresolved_named_calls']}")
    for token in (R09_GATE_TOKEN, '"night_review_lighting_aimed"', "fill_energy=2500.0", "for calibration_index in range(2):", 'require(len(results) == 9, "Checkpoint render count is not exactly nine")', '"finalization_authorized":False'):
        if token not in source:
            raise RuntimeError(f"Required Recovery09 token is absent: {token}")
    return source, {
        "schema":"skyguard.m01-visible-environment-kit-refinement01-stagea-recovery09-checkpoint01.in-memory-correction.v1",
        "gate":GATE,
        "recovery08_worker":str(R08_WORKER),
        "recovery08_worker_bytes":R08_WORKER_BYTES,
        "recovery08_worker_sha256":R08_WORKER_SHA256,
        "recovery08_design_receipt":r08_receipt,
        "bounded_correction":"CAMERA_TARGETED_NIGHT_REVIEW_LIGHTING_WITH_EXPOSURE_GUARD",
        "selected_probe_candidate":"A",
        "generated_call_graph":graph,
        "recovery08_attempt_or_output_reused":False,
        "checkpoint_count":9,
        "glb_count":0,
        "texture_count":0,
        "finalization_authorized":False,
        "passed":True,
    }


def main() -> int:
    source, receipt = load_recovery09_source()
    print(json.dumps(receipt, sort_keys=True), flush=True)
    namespace: dict[str, object] = {"__name__":"skyguard_stagea_recovery09_checkpoint01_embedded","__file__":str(Path(__file__).resolve()),"__package__":None}
    exec(compile(source, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery09 embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    raise SystemExit(main())
