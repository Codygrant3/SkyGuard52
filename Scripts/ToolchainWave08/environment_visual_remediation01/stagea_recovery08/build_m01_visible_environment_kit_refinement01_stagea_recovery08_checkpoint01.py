from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY08_CHECKPOINT01"
RECOVERY07_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\build_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01.py"
RECOVERY07_WORKER_BYTES = 12591
RECOVERY07_WORKER_SHA256 = "86133a4e47057cbfd015538f888569e682eea920ce52035ae46bff0b7160713c"
RECOVERY07_GATE_TOKEN = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01"'
RECOVERY08_GATE_TOKEN = f'GATE = "{GATE}"'


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
                    black_adjustment = 1.0 if metrics["black_fraction_linear_0_01"] > 0.70 else 0.0
                    adjustment = min(5.5, max(0.5, mean_adjustment, black_adjustment))
                    new_exposure = min(7.0, current_exposure + adjustment)
                    require(new_exposure > current_exposure, f"Night calibration could not raise exposure: {camera_id}")
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
            require(metrics["mean_luma_linear"] >= minimum_luma, f"Checkpoint is too dark after bounded calibration: {condition}_{camera_id}")
            require(metrics["black_fraction_linear_0_01"] <= maximum_black, f"Checkpoint is excessively black after bounded calibration: {condition}_{camera_id}")
            results.append({
                "condition": condition,
                "camera": camera_id,
                "path": str(path),
                "metrics": metrics,
                "exposure": float(scene.view_settings.exposure),
                "calibration_passes": calibration_passes,
                "passed": True,
            })
    require(len(results) == 9, "Checkpoint render count is not exactly nine")
    return results
'''.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_recovery07_module():
    if not RECOVERY07_WORKER.is_file():
        raise RuntimeError(f"Frozen Recovery07 worker is missing: {RECOVERY07_WORKER}")
    if RECOVERY07_WORKER.stat().st_size != RECOVERY07_WORKER_BYTES:
        raise RuntimeError("Frozen Recovery07 worker byte count changed")
    digest = sha256_file(RECOVERY07_WORKER)
    if digest != RECOVERY07_WORKER_SHA256:
        raise RuntimeError(f"Frozen Recovery07 worker hash changed: {digest}")
    spec = importlib.util.spec_from_file_location("skyguard_recovery07_frozen_worker", RECOVERY07_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create a module specification for the frozen Recovery07 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_top_level_function(source: str, function_name: str, replacement: str) -> str:
    tree = ast.parse(source)
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function_name]
    if len(matches) != 1:
        raise RuntimeError(f"Top-level function cardinality for {function_name} is {len(matches)}, expected one")
    node = matches[0]
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[: node.lineno - 1])
    end = sum(len(line) for line in lines[: node.end_lineno])
    suffix = "\n" if source[start:end].endswith("\n") else ""
    return source[:start] + replacement + suffix + source[end:]


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} token cardinality is {count}, expected one")
    return source.replace(old, new, 1)


def static_named_call_graph(source: str) -> dict[str, object]:
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
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)
    called = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    unresolved = sorted(called - (set(dir(builtins)) | definitions | imports | assigned))
    return {
        "function_and_class_definition_count": len(definitions),
        "named_call_count": len(called),
        "unresolved_named_calls": unresolved,
        "passed": not unresolved,
    }


def load_recovery08_source() -> tuple[str, dict[str, object]]:
    module = load_recovery07_module()
    source, recovery07_receipt = module.load_recovery07_source()
    source = replace_once(source, RECOVERY07_GATE_TOKEN, RECOVERY08_GATE_TOKEN, "Recovery07 gate")
    source = replace_top_level_function(source, "render_checkpoints", RENDER_CHECKPOINTS_IMPLEMENTATION)
    graph = static_named_call_graph(source)
    if not graph["passed"]:
        raise RuntimeError(f"Generated Recovery08 source has unresolved named calls: {graph['unresolved_named_calls']}")
    for token in (
        RECOVERY08_GATE_TOKEN,
        '"night_lighting_calibration"',
        "for calibration_index in range(2):",
        "new_exposure = min(7.0",
        'require(len(results) == 9, "Checkpoint render count is not exactly nine")',
        '"finalization_authorized":False',
    ):
        if token not in source:
            raise RuntimeError(f"Required Recovery08 token is absent: {token}")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery08-checkpoint01.in-memory-correction.v1",
        "gate": GATE,
        "recovery07_worker": str(RECOVERY07_WORKER),
        "recovery07_worker_bytes": RECOVERY07_WORKER_BYTES,
        "recovery07_worker_sha256": RECOVERY07_WORKER_SHA256,
        "recovery07_design_receipt": recovery07_receipt,
        "bounded_correction": "NIGHT_LIGHTING_ADAPTIVE_EXPOSURE_CALIBRATION",
        "generated_call_graph": graph,
        "night_calibration_max_passes_per_camera": 2,
        "night_exposure_hard_ceiling": 7.0,
        "recovery07_attempt_or_output_reused": False,
        "checkpoint_only": True,
        "checkpoint_count": 9,
        "final_render_count": 0,
        "texture_count": 0,
        "glb_count": 0,
        "finalization_authorized": False,
        "passed": True,
    }
    return source, receipt


def main() -> int:
    corrected, receipt = load_recovery08_source()
    print(json.dumps(receipt, sort_keys=True), flush=True)
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery08_checkpoint01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery08 checkpoint embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    raise SystemExit(main())
