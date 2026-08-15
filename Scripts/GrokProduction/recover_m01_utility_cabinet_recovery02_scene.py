from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


PROJECT = Path(r"D:\Skyguard52")
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-deterministic-recovery02" / "attempt_20260811T093000000000Z"
OUTPUT = ATTEMPT / "output"
CHECKPOINT = OUTPUT / "checkpoint"
RECEIPTS = OUTPUT / "receipts"
EXPORTS = OUTPUT / "exports"
BUILD_SOURCE = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-grok-mcp-recovery01" / "attempt_20260811T091500000000Z" / "output" / "scripts" / "rebuild_utility_cabinet_recovery01.py"
RENDER_SOURCE = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-grok-mcp-recovery01" / "attempt_20260811T091500000000Z" / "output" / "scripts" / "render_utility_cabinet_checkpoints.py"
FINAL_BLEND = OUTPUT / "M01_Promenade_UtilityCabinet_Recovery02.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_UtilityCabinet_Recovery02.glb"
MESH_NAME = "SM_M01_Promenade_UtilityCabinet_A"
SOCKET_NAME = "SOCKET_UtilityCabinet_Origin"
COLLISION_PREFIX = "UCX_SM_M01_Promenade_UtilityCabinet_A_"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def world_bounds(obj):
    corners = [obj.matrix_world @ v.co for v in obj.data.vertices]
    minimum = tuple(min(v[i] for v in corners) for i in range(3))
    maximum = tuple(max(v[i] for v in corners) for i in range(3))
    return minimum, maximum


def configure_build_module(module) -> None:
    module.OUTPUT = OUTPUT
    module.CHECKPOINT = CHECKPOINT
    module.RECEIPTS = RECEIPTS

    original_vent_bank = module.vent_bank
    original_make_hinge = module.make_hinge
    original_create_materials = module.create_materials

    def corrected_vent_bank(name, side):
        obj = original_vent_bank(name, side)
        obj.location.x += -0.018 if side == "left" else 0.018
        module.apply_transforms(obj, location=True)
        return obj

    def corrected_make_hinge(name, location, side):
        obj = original_make_hinge(name, location, side)
        obj.location.y -= 0.030
        module.apply_transforms(obj, location=True)
        return obj

    def corrected_create_materials():
        materials = original_create_materials()
        paint = materials["M_M01_UtilCab_PaintSteel"]
        ramps = [node for node in paint.node_tree.nodes if node.type == "VALTORGB"]
        if not ramps:
            raise RuntimeError("Paint material lacks governed color ramp")
        ramps[0].color_ramp.elements[0].color = (0.045, 0.075, 0.050, 1.0)
        ramps[0].color_ramp.elements[1].color = (0.155, 0.205, 0.145, 1.0)
        hardware = materials["M_M01_UtilCab_Hardware"]
        hardware_bsdf = next((node for node in hardware.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        if hardware_bsdf is not None:
            hardware_bsdf.inputs["Base Color"].default_value = (0.16, 0.17, 0.18, 1.0)
            hardware_bsdf.inputs["Roughness"].default_value = 0.42
        return materials

    module.vent_bank = corrected_vent_bank
    module.make_hinge = corrected_make_hinge
    module.create_materials = corrected_create_materials


def configure_render_module(module) -> None:
    module.OUTPUT = OUTPUT
    module.CHECKPOINT = CHECKPOINT
    module.RECEIPTS = RECEIPTS
    module.SHOTS = [
        ("01_front_full_daylight.png", (0.0, -4.1, 1.05), "daylight", 50.0, (0.0, 0.0, 0.72)),
        ("02_front_threequarter_daylight.png", (-2.5, -3.5, 1.25), "daylight", 52.0, (0.0, 0.0, 0.72)),
        ("03_rear_threequarter_overcast.png", (2.5, 3.5, 1.2), "overcast", 52.0, (0.0, 0.0, 0.72)),
        ("04_left_side_vents.png", (-3.8, -0.45, 1.0), "overcast", 52.0, (0.0, 0.0, 0.72)),
        ("05_right_side_vents.png", (3.8, -0.45, 1.0), "overcast", 52.0, (0.0, 0.0, 0.72)),
        ("06_door_latch_hinges_close.png", (1.15, -3.0, 1.05), "daylight", 62.0, (0.12, -0.20, 0.94)),
        ("07_plinth_and_door_gap_wet.png", (-0.8, -2.7, 0.42), "wet", 58.0, (0.0, -0.16, 0.25)),
        ("08_eye_level_context.png", (2.7, -4.8, 1.45), "daylight", 48.0, (0.0, 0.0, 0.70)),
    ]
    original_setup_lights = module.setup_lights

    def corrected_setup_lights(mode):
        original_setup_lights(mode)
        bpy.context.scene.view_settings.exposure -= 0.55

    module.setup_lights = corrected_setup_lights


def export_asset(mesh, collisions) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for name in [MESH_NAME, SOCKET_NAME] + collisions:
        item = bpy.data.objects.get(name)
        if item is not None:
            item.hide_set(False)
            item.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.export_scene.gltf(
        filepath=str(FINAL_GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )


def main() -> None:
    for directory in (OUTPUT, CHECKPOINT, RECEIPTS, EXPORTS):
        directory.mkdir(parents=True, exist_ok=True)

    build = load_module(BUILD_SOURCE, "skyguard_utility_cabinet_recovery01_build_authority")
    configure_build_module(build)
    construction = build.main()

    mesh = bpy.data.objects.get(MESH_NAME)
    if mesh is None or mesh.type != "MESH":
        raise RuntimeError("Corrected cabinet mesh is missing")
    left_vent = bpy.data.objects.get("SRC_UtilityCabinet_Vent_Left")
    right_vent = bpy.data.objects.get("SRC_UtilityCabinet_Vent_Right")
    if left_vent is None or right_vent is None:
        raise RuntimeError("Corrected vent sources are missing")
    left_min, left_max = world_bounds(left_vent)
    right_min, right_max = world_bounds(right_vent)
    if left_min[0] >= -0.500:
        raise RuntimeError(f"Left vent remains concealed: min X {left_min[0]:.6f}")
    if right_max[0] <= 0.500:
        raise RuntimeError(f"Right vent remains concealed: max X {right_max[0]:.6f}")

    render = load_module(RENDER_SOURCE, "skyguard_utility_cabinet_recovery01_render_authority")
    configure_render_module(render)
    render_receipt = render.main()

    mesh.hide_render = False
    collisions = sorted(item.name for item in bpy.data.objects if item.name.startswith(COLLISION_PREFIX))
    if not 1 <= len(collisions) <= 3:
        raise RuntimeError(f"Expected one to three collision objects, found {len(collisions)}")
    bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
    export_asset(mesh, collisions)
    if not FINAL_GLB.is_file() or FINAL_GLB.stat().st_size < 4096:
        raise RuntimeError("GLB export is missing or empty")

    minimum, maximum = world_bounds(mesh)
    dimensions = [maximum[i] - minimum[i] for i in range(3)]
    report = {
        "schema": "skyguard.m01-utility-cabinet.deterministic-recovery02.report.v1",
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW",
        "corrections": {
            "vent_bank_outward_translation_m": 0.018,
            "hinge_front_translation_m": 0.030,
            "paint_response": "darker olive-green calibrated ramp",
            "review_cameras": "widened to show full asset and both side assemblies",
        },
        "mesh": MESH_NAME,
        "socket": SOCKET_NAME,
        "collision": collisions,
        "dimensions_m": dimensions,
        "bounds_min_m": list(minimum),
        "bounds_max_m": list(maximum),
        "vertices": len(mesh.data.vertices),
        "polygons": len(mesh.data.polygons),
        "construction": construction,
        "renders": render_receipt["shots"],
        "final_blend": str(FINAL_BLEND),
        "glb": str(FINAL_GLB),
        "limitations": [
            "Direct review of all eight original renders is mandatory before Unreal import",
            "Candidate is scoped to mid-distance Mission 1 promenade use",
        ],
    }
    write_json(OUTPUT / "implementation_report.json", report)
    artifacts = [record(path) for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json")]
    write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})
    print("PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW")


if __name__ == "__main__":
    main()
