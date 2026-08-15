import json
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


ATTEMPT = Path(r"D:\Skyguard52\Production\Attempts\m01-pathfinder-boss-grok-mcp\attempt_20260811T052000000000Z")
OUTPUT = ATTEMPT / "output"
BLEND = OUTPUT / "M01_PathfinderBoss_GrokMCP_Production_A.blend"
GLB = OUTPUT / "exports" / "M01_PathfinderBoss_GrokMCP_Production_A.glb"
FBX = OUTPUT / "exports" / "M01_PathfinderBoss_GrokMCP_Production_A.fbx"
REPORT = OUTPUT / "implementation_report.json"
RECEIPT = OUTPUT / "receipts" / "scene_serialization_receipt.json"
CAMERA_RECEIPT = OUTPUT / "receipts" / "camera_framing_receipt.json"
CHECKPOINT_RECEIPT = OUTPUT / "receipts" / "checkpoint_review.json"

INTACT = [
    "SM_Boss_Pathfinder_Body",
    "SM_Boss_Pathfinder_CommandAntenna",
    "SM_Boss_Pathfinder_NoseCamera",
    "SM_Boss_Pathfinder_Engine",
    "SM_Boss_Pathfinder_ControlLinkage",
]
DAMAGED = "SM_Boss_Pathfinder_Body_Damaged"
DEBRIS = [
    "SM_Boss_Pathfinder_BreakChunk_L",
    "SM_Boss_Pathfinder_BreakChunk_Engine",
    "SM_Boss_Pathfinder_BreakChunk_R",
    "SM_Boss_Pathfinder_BreakChunk_Spine_AAA",
]
SOCKETS = {
    "SOCKET_Pathfinder_Origin": (0.00, 0.00, 0.00),
    "SOCKET_Pathfinder_CommandAntenna": (0.20, 0.00, 0.65),
    "SOCKET_Pathfinder_NoseCamera": (1.55, 0.00, -0.05),
    "SOCKET_Pathfinder_Engine": (-1.45, 0.00, 0.05),
    "SOCKET_Pathfinder_ControlLinkage": (-0.45, 0.00, 0.20),
    "SOCKET_Pathfinder_DamageFX": None,
    "SOCKET_Pathfinder_IglaLock": None,
}
CAMERAS = [
    "CAM_Pathfinder_01_DaylightFront",
    "CAM_Pathfinder_02_DaylightRear",
    "CAM_Pathfinder_03_OvercastTop",
    "CAM_Pathfinder_04_WetStormUnderside",
    "CAM_Pathfinder_05_NightOperational",
    "CAM_Pathfinder_06_AntennaCameraClose",
    "CAM_Pathfinder_07_EngineLinkageClose",
    "CAM_Pathfinder_08_DamagedFlyby",
]


def mesh_record(obj):
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "location_m": [round(float(value), 6) for value in obj.location],
        "dimensions_m": [round(float(value), 6) for value in obj.dimensions],
    }


def combined_bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum, maximum - minimum


def projected_bounds(scene, camera, objects):
    points = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner)))
    xs = [point.x for point in points]
    ys = [point.y for point in points]
    zs = [point.z for point in points]
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "min_depth": min(zs),
        "width_occupancy": max(xs) - min(xs),
        "height_occupancy": max(ys) - min(ys),
    }


def require_file(path, label):
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    GLB.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)

    errors = []
    required_mesh_names = INTACT + [DAMAGED] + DEBRIS
    missing_meshes = [name for name in required_mesh_names if bpy.data.objects.get(name) is None]
    missing_sockets = [name for name in SOCKETS if bpy.data.objects.get(name) is None]
    missing_cameras = [name for name in CAMERAS if bpy.data.objects.get(name) is None]
    if missing_meshes:
        errors.append(f"missing governed meshes: {missing_meshes}")
    if missing_sockets:
        errors.append(f"missing sockets: {missing_sockets}")
    if missing_cameras:
        errors.append(f"missing cameras: {missing_cameras}")

    meshes = [bpy.data.objects.get(name) for name in required_mesh_names if bpy.data.objects.get(name)]
    for obj in meshes:
        if obj.type != "MESH":
            errors.append(f"{obj.name} is not a mesh")
            continue
        if len(obj.data.uv_layers) < 1:
            errors.append(f"{obj.name} has no UV layer")
        if len(obj.material_slots) < 1:
            errors.append(f"{obj.name} has no material slot")
        if min(obj.dimensions) <= 0.002:
            errors.append(f"{obj.name} has paper-thin dimensions {tuple(obj.dimensions)}")

    if errors:
        raise RuntimeError("; ".join(errors))

    intact_objects = [bpy.data.objects[name] for name in INTACT]
    damaged_object = bpy.data.objects[DAMAGED]
    debris_objects = [bpy.data.objects[name] for name in DEBRIS]
    collision_objects = sorted(
        [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith("UCX_SM_Boss_Pathfinder_")],
        key=lambda item: item.name,
    )
    if not 7 <= len(collision_objects) <= 20:
        raise RuntimeError(f"collision count {len(collision_objects)} is outside 7..20")

    minimum, maximum, dimensions = combined_bounds(intact_objects)
    if not (4.5 <= dimensions.x <= 5.5 and 5.7 <= dimensions.y <= 6.5 and 0.75 <= dimensions.z <= 1.40):
        raise RuntimeError(f"intact bounds outside Pathfinder authority: {tuple(round(v, 4) for v in dimensions)}")

    body_polygons = len(bpy.data.objects[INTACT[0]].data.polygons)
    damaged_polygons = len(damaged_object.data.polygons)
    intact_polygons = sum(len(obj.data.polygons) for obj in intact_objects)
    if body_polygons < 12000:
        raise RuntimeError(f"body polygon count {body_polygons} is below 12000")
    if damaged_polygons < 10000:
        raise RuntimeError(f"damaged body polygon count {damaged_polygons} is below 10000")
    if not 45000 <= intact_polygons <= 180000:
        raise RuntimeError(f"intact polygon count {intact_polygons} is outside 45000..180000")
    for obj in debris_objects:
        if len(obj.data.polygons) < 120:
            raise RuntimeError(f"{obj.name} remains a placeholder with only {len(obj.data.polygons)} polygons")

    material_names = sorted({slot.material.name for obj in intact_objects for slot in obj.material_slots if slot.material})
    if len(material_names) < 6:
        raise RuntimeError(f"only {len(material_names)} distinct intact material families found")

    socket_errors = []
    for name, expected in SOCKETS.items():
        obj = bpy.data.objects[name]
        if obj.type != "EMPTY":
            socket_errors.append(f"{name} is {obj.type}, not EMPTY")
        if expected is not None:
            delta = (obj.location - Vector(expected)).length
            if delta > 0.05:
                socket_errors.append(f"{name} is {delta:.4f} m from authority")
    if socket_errors:
        raise RuntimeError("; ".join(socket_errors))

    checkpoint = json.loads(CHECKPOINT_RECEIPT.read_text(encoding="utf-8")) if CHECKPOINT_RECEIPT.is_file() else {}
    if checkpoint.get("classification") != "PASSED_TO_FINAL_RENDERS":
        raise RuntimeError("checkpoint review receipt is missing or not PASSED_TO_FINAL_RENDERS")
    checkpoint_pngs = sorted((OUTPUT / "checkpoint_renders").glob("*.png"))
    if len(checkpoint_pngs) != 3:
        raise RuntimeError(f"expected 3 checkpoint PNGs, found {len(checkpoint_pngs)}")

    scene = bpy.context.scene
    framing = []
    for index, camera_name in enumerate(CAMERAS, start=1):
        camera = bpy.data.objects[camera_name]
        if camera.type != "CAMERA":
            raise RuntimeError(f"{camera_name} is not a camera")
        if index <= 5:
            targets = intact_objects
            minimum_occupancy, maximum_occupancy = 0.45, 0.75
            check_axis = "height_occupancy"
        elif index == 6:
            targets = [bpy.data.objects["SM_Boss_Pathfinder_CommandAntenna"], bpy.data.objects["SM_Boss_Pathfinder_NoseCamera"]]
            minimum_occupancy, maximum_occupancy = 0.55, 0.90
            check_axis = "max_axis"
        elif index == 7:
            targets = [bpy.data.objects["SM_Boss_Pathfinder_Engine"], bpy.data.objects["SM_Boss_Pathfinder_ControlLinkage"]]
            minimum_occupancy, maximum_occupancy = 0.55, 0.90
            check_axis = "max_axis"
        else:
            targets = [damaged_object]
            minimum_occupancy, maximum_occupancy = 0.45, 0.75
            check_axis = "height_occupancy"
        bounds = projected_bounds(scene, camera, targets)
        occupancy = max(bounds["width_occupancy"], bounds["height_occupancy"]) if check_axis == "max_axis" else bounds[check_axis]
        passed = (
            bounds["min_x"] >= 0.05
            and bounds["max_x"] <= 0.95
            and bounds["min_y"] >= 0.05
            and bounds["max_y"] <= 0.95
            and bounds["min_depth"] > 0
            and minimum_occupancy <= occupancy <= maximum_occupancy
        )
        framing.append({
            "camera": camera_name,
            "targets": [obj.name for obj in targets],
            "bounds": {key: round(float(value), 6) for key, value in bounds.items()},
            "evaluated_occupancy": round(float(occupancy), 6),
            "required_range": [minimum_occupancy, maximum_occupancy],
            "passed": passed,
        })
        if not passed:
            raise RuntimeError(f"camera framing failed for {camera_name}: {framing[-1]}")

    CAMERA_RECEIPT.write_text(json.dumps({
        "schema": "skyguard.m01-pathfinder.camera-framing.v1",
        "classification": "PASS",
        "cameras": framing,
    }, indent=2) + "\n", encoding="utf-8")

    for path, label in [
        (OUTPUT / "grok_build_report.json", "Grok build report"),
        (OUTPUT / "renders" / "01_daylight_front_intact.png", "render 01"),
        (OUTPUT / "renders" / "02_daylight_rear_intact.png", "render 02"),
        (OUTPUT / "renders" / "03_overcast_top_weakpoints.png", "render 03"),
        (OUTPUT / "renders" / "04_wet_storm_underside_engine.png", "render 04"),
        (OUTPUT / "renders" / "05_night_operational_intact.png", "render 05"),
        (OUTPUT / "renders" / "06_close_antenna_camera.png", "render 06"),
        (OUTPUT / "renders" / "07_close_engine_linkage.png", "render 07"),
        (OUTPUT / "renders" / "08_damaged_gameplay_flyby.png", "render 08"),
    ]:
        require_file(path, label)

    implementation = {
        "schema": "skyguard.m01-pathfinder.grok-mcp.production-attempt01-implementation.v1",
        "classification": "PASSED_STRUCTURAL_PENDING_VISUAL",
        "source_scene": r"D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\HeroGroupedTopology_008\BLD_M01_HERO_GROUPED_TOPOLOGY_008_MASTER.blend",
        "intact_meshes": [mesh_record(obj) for obj in intact_objects],
        "damaged_mesh": mesh_record(damaged_object),
        "debris_meshes": [mesh_record(obj) for obj in debris_objects],
        "sockets": {name: [round(float(value), 6) for value in bpy.data.objects[name].location] for name in SOCKETS},
        "collision_meshes": [obj.name for obj in collision_objects],
        "combined_min_m": [round(float(v), 6) for v in minimum],
        "combined_max_m": [round(float(v), 6) for v in maximum],
        "combined_dimensions_m": [round(float(v), 6) for v in dimensions],
        "intact_vertices": sum(len(obj.data.vertices) for obj in intact_objects),
        "intact_polygons": intact_polygons,
        "material_families": material_names,
        "camera_framing_receipt": str(CAMERA_RECEIPT),
        "checkpoint_review_receipt": str(CHECKPOINT_RECEIPT),
        "generated_by": "Codex-supervised deterministic postflight after Grok OAuth Blender-MCP production",
    }
    REPORT.write_text(json.dumps(implementation, indent=2) + "\n", encoding="utf-8")

    scene["skyguard_asset_id"] = "m01-pathfinder-boss"
    scene["skyguard_classification"] = "PASSED_STRUCTURAL_PENDING_VISUAL"
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), check_existing=False)

    bpy.ops.object.select_all(action="DESELECT")
    export_objects = intact_objects + [damaged_object] + debris_objects + [bpy.data.objects[name] for name in SOCKETS] + collision_objects
    for obj in export_objects:
        obj.hide_viewport = False
        obj.hide_render = obj.name.startswith("UCX_") or obj.name.startswith("SOCKET_") or obj.name == DAMAGED or obj.name in DEBRIS
        obj.select_set(True)
    bpy.context.view_layer.objects.active = intact_objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
    )
    bpy.ops.export_scene.fbx(
        filepath=str(FBX),
        use_selection=True,
        object_types={"MESH", "EMPTY"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Y",
        axis_up="Z",
        bake_anim=False,
        add_leaf_bones=False,
    )

    receipt = {
        "schema": "skyguard.m01-pathfinder.production-attempt01.scene-serialization-receipt.v1",
        "classification": "PASSED_STRUCTURAL_PENDING_VISUAL",
        "blend": str(BLEND),
        "glb": str(GLB),
        "fbx": str(FBX),
        "implementation_report": str(REPORT),
        "camera_framing_receipt": str(CAMERA_RECEIPT),
        "checkpoint_review_receipt": str(CHECKPOINT_RECEIPT),
        "intact_mesh_count": len(intact_objects),
        "damaged_mesh_count": 1,
        "debris_mesh_count": len(debris_objects),
        "socket_count": len(SOCKETS),
        "collision_count": len(collision_objects),
        "combined_dimensions_m": implementation["combined_dimensions_m"],
        "intact_vertices": implementation["intact_vertices"],
        "intact_polygons": intact_polygons,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("SKYGUARD_PATHFINDER_FINALIZE_PASS")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

