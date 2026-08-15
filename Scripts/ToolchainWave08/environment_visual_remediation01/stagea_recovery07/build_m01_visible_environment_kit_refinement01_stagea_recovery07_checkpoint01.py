from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01"
RECOVERY06_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\build_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py"
RECOVERY06_WORKER_BYTES = 7427
RECOVERY06_WORKER_SHA256 = "a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399"
RECOVERY06_GATE_TOKEN = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01"'
RECOVERY07_GATE_TOKEN = f'GATE = "{GATE}"'


FAST_BOX_IMPLEMENTATION = r'''
_FAST_BOX_MESH_CACHE: dict[tuple[object, ...], bpy.types.Mesh] = {}


def _fast_box_mesh(
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    bevel: float,
) -> bpy.types.Mesh:
    dimensions = tuple(float(value) for value in dimensions)
    key = tuple(round(value, 5) for value in dimensions) + (round(float(bevel), 5), material.name)
    cached = _FAST_BOX_MESH_CACHE.get(key)
    if cached is not None:
        return cached
    mesh = bpy.data.meshes.new("FASTBOX_" + hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:16])
    bm = bmesh.new()
    try:
        bmesh.ops.create_cube(bm, size=1.0)
        sx, sy, sz = dimensions
        for vertex in bm.verts:
            vertex.co.x *= sx
            vertex.co.y *= sy
            vertex.co.z *= sz
        safe_bevel = min(max(0.0, float(bevel)), min(dimensions) * 0.24)
        if safe_bevel > 0.0:
            bmesh.ops.bevel(
                bm,
                geom=list(bm.edges),
                offset=safe_bevel,
                segments=2,
                affect="EDGES",
            )
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.materials.append(material)
    mesh.update(calc_edges=True)
    uv0 = mesh.uv_layers.new(name="UV0")
    sx, sy, sz = (max(value, 1e-6) for value in dimensions)
    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(normal.z) >= abs(normal.x) and abs(normal.z) >= abs(normal.y):
                uv = (coordinate.x / sx + 0.5, coordinate.y / sy + 0.5)
            elif abs(normal.x) >= abs(normal.y):
                uv = (coordinate.y / sy + 0.5, coordinate.z / sz + 0.5)
            else:
                uv = (coordinate.x / sx + 0.5, coordinate.z / sz + 0.5)
            uv0.data[loop_index].uv = uv
    uv1 = mesh.uv_layers.new(name="UV1")
    for loop_index, loop in enumerate(uv0.data):
        uv1.data[loop_index].uv = loop.uv
    _FAST_BOX_MESH_CACHE[key] = mesh
    return mesh


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    bevel: float = 0.04,
    rotation_z: float = 0.0,
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, _fast_box_mesh(dimensions, material, bevel))
    obj.location = location
    obj.rotation_euler[2] = rotation_z
    target.objects.link(obj)
    return obj
'''.strip()


TRACE_IMPLEMENTATION = r'''
def trace_phase(phase: str, **fields: object) -> None:
    payload = {"skyguard_phase": phase, "utc": utc_now()}
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True), flush=True)
'''.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_recovery06_module():
    if not RECOVERY06_WORKER.is_file():
        raise RuntimeError(f"Frozen Recovery06 worker is missing: {RECOVERY06_WORKER}")
    if RECOVERY06_WORKER.stat().st_size != RECOVERY06_WORKER_BYTES:
        raise RuntimeError("Frozen Recovery06 worker byte count changed")
    digest = sha256_file(RECOVERY06_WORKER)
    if digest != RECOVERY06_WORKER_SHA256:
        raise RuntimeError(f"Frozen Recovery06 worker hash changed: {digest}")
    spec = importlib.util.spec_from_file_location("skyguard_recovery06_frozen_worker", RECOVERY06_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create a module specification for the frozen Recovery06 worker")
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


def static_named_call_graph(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    definitions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
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
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    allowed = set(dir(builtins)) | definitions | imports | assigned
    unresolved = sorted(called - allowed)
    return {
        "function_and_class_definition_count": len(definitions),
        "named_call_count": len(called),
        "unresolved_named_calls": unresolved,
        "passed": not unresolved,
    }


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} token cardinality is {count}, expected one")
    return source.replace(old, new, 1)


def load_recovery07_source() -> tuple[str, dict[str, object]]:
    module = load_recovery06_module()
    source, recovery06_receipt = module.load_recovery06_source()
    source = replace_once(source, RECOVERY06_GATE_TOKEN, RECOVERY07_GATE_TOKEN, "Recovery06 gate")
    source = replace_once(source, "import bpy\n", "import bpy\nimport bmesh\n", "bmesh import")
    source = replace_top_level_function(source, "add_box", FAST_BOX_IMPLEMENTATION)
    require_token = 'def require(condition: bool, message: str) -> None:\n    if not condition:\n        raise BuildError(message)\n'
    source = replace_once(source, require_token, require_token + "\n\n" + TRACE_IMPLEMENTATION + "\n", "trace insertion")
    source = replace_once(
        source,
        "    output.mkdir(parents=True)\n\n    scene = reset_scene()",
        '    output.mkdir(parents=True)\n    trace_phase("output_namespace_created", output=str(output))\n\n    scene = reset_scene()\n    trace_phase("scene_reset")',
        "output telemetry",
    )
    source = replace_once(
        source,
        "    materials = build_materials()\n    build_shore_and_street(materials, district, collision, sockets)",
        '    materials = build_materials()\n    trace_phase("materials_built", material_count=len(materials))\n    build_shore_and_street(materials, district, collision, sockets)\n    trace_phase("shore_and_street_built", object_count=len(bpy.data.objects))',
        "scene telemetry",
    )
    source = replace_once(
        source,
        '        build_midrise(f"SM_M01_STAGEA_R05_Midrise_{style}_{index:02d}", center_x, floors, style, materials, district, collision, sockets)',
        '        trace_phase("building_start", index=index, style=style, floors=floors, object_count=len(bpy.data.objects))\n        build_midrise(f"SM_M01_STAGEA_R05_Midrise_{style}_{index:02d}", center_x, floors, style, materials, district, collision, sockets)\n        trace_phase("building_complete", index=index, style=style, object_count=len(bpy.data.objects), cached_box_meshes=len(_FAST_BOX_MESH_CACHE))',
        "building telemetry",
    )
    source = replace_once(
        source,
        "    rig = add_review_rig(scene)\n    checkpoints = render_checkpoints(scene, rig, output, materials)",
        '    rig = add_review_rig(scene)\n    trace_phase("review_rig_built", object_count=len(bpy.data.objects), cached_box_meshes=len(_FAST_BOX_MESH_CACHE))\n    checkpoints = render_checkpoints(scene, rig, output, materials)\n    trace_phase("checkpoint_renders_complete", checkpoint_count=len(checkpoints))',
        "render telemetry",
    )
    source = replace_once(
        source,
        '            path = output / "renders" / "checkpoints" / f"{condition}_{camera_id}.png"\n            metrics = render_and_measure(scene, path)',
        '            path = output / "renders" / "checkpoints" / f"{condition}_{camera_id}.png"\n            trace_phase("checkpoint_render_start", condition=condition, camera=camera_id)\n            metrics = render_and_measure(scene, path)\n            trace_phase("checkpoint_render_complete", condition=condition, camera=camera_id, mean_luma=metrics["mean_luma_linear"])',
        "checkpoint telemetry",
    )
    source = replace_once(
        source,
        '    print(json.dumps({"gate":GATE,"status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW","output":str(output)}))',
        '    print(json.dumps({"gate":GATE,"status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW","output":str(output)}), flush=True)',
        "terminal flush",
    )
    graph = static_named_call_graph(source)
    if not graph["passed"]:
        raise RuntimeError(f"Generated Recovery07 source has unresolved named calls: {graph['unresolved_named_calls']}")
    required = (
        RECOVERY07_GATE_TOKEN,
        "def _fast_box_mesh(",
        "def trace_phase(",
        'trace_phase("building_complete"',
        'trace_phase("checkpoint_render_start"',
        'require(len(results) == 9, "Checkpoint render count is not exactly nine")',
        '"finalization_authorized":False',
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"Required Recovery07 token is absent: {token}")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery07-checkpoint01.in-memory-correction.v1",
        "gate": GATE,
        "recovery06_worker": str(RECOVERY06_WORKER),
        "recovery06_worker_bytes": RECOVERY06_WORKER_BYTES,
        "recovery06_worker_sha256": RECOVERY06_WORKER_SHA256,
        "recovery06_design_receipt": recovery06_receipt,
        "bounded_correction": "CACHED_DIRECT_BOX_MESH_AND_FLUSHED_PHASE_TELEMETRY",
        "generated_call_graph": graph,
        "box_mesh_cache": True,
        "per_object_box_bpy_ops": False,
        "recovery06_attempt_or_output_reused": False,
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
    corrected, receipt = load_recovery07_source()
    print(json.dumps(receipt, sort_keys=True), flush=True)
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery07_checkpoint01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery07 checkpoint embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    raise SystemExit(main())
