import json
from pathlib import Path

import bpy
from mathutils import Vector


ATTEMPT = Path(r"D:\Skyguard52\Production\Attempts\m01-radar-post-grok-mcp-correction02\attempt_20260811T045000000000Z")
OUTPUT = ATTEMPT / "output"
BLEND = OUTPUT / "M01_RadarPost_GrokMCP_Production_R02.blend"
GLB = OUTPUT / "exports" / "M01_RadarPost_GrokMCP_Production_R02.glb"
REPORT = OUTPUT / "grok_implementation_report.json"
RECEIPT = OUTPUT / "receipts" / "scene_serialization_receipt.json"

VISIBLE = [
    "SM_M01_RadarPost_Bunker_A",
    "SM_M01_RadarPost_MastDrive_A",
    "SM_M01_RadarPost_DishAssembly_A",
    "SM_M01_RadarPost_ServiceDetails_A",
]
SOCKETS = [
    "SOCKET_RadarPost_Origin",
    "SOCKET_RadarPost_DishPivot",
    "SOCKET_RadarPost_ObjectiveMarker",
    "SOCKET_RadarPost_DamageFX",
]


def record_mesh(obj):
    mesh = obj.data
    return {
        "name": obj.name,
        "vertices": len(mesh.vertices),
        "polygons": len(mesh.polygons),
        "uv_layers": [layer.name for layer in mesh.uv_layers],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "dimensions_m": [round(float(value), 6) for value in obj.dimensions],
    }


def combined_bounds(objects):
    points = []
    for obj in objects:
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum, maximum - minimum


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    GLB.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)

    missing_visible = [name for name in VISIBLE if bpy.data.objects.get(name) is None]
    missing_sockets = [name for name in SOCKETS if bpy.data.objects.get(name) is None]
    visible_objects = [bpy.data.objects.get(name) for name in VISIBLE if bpy.data.objects.get(name)]
    collision_objects = sorted(
        [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith("UCX_SM_M01_RadarPost_")],
        key=lambda item: item.name,
    )
    errors = []
    if missing_visible:
        errors.append(f"missing visible meshes: {missing_visible}")
    if missing_sockets:
        errors.append(f"missing sockets: {missing_sockets}")
    if not 4 <= len(collision_objects) <= 12:
        errors.append(f"collision count {len(collision_objects)} is outside 4..12")
    for obj in visible_objects:
        if obj.type != "MESH":
            errors.append(f"{obj.name} is not a mesh")
        elif len(obj.data.uv_layers) < 1:
            errors.append(f"{obj.name} has no UV layer")
        elif len(obj.material_slots) < 1:
            errors.append(f"{obj.name} has no material slot")

    if errors:
        raise RuntimeError("; ".join(errors))

    minimum, maximum, dimensions = combined_bounds(visible_objects)
    if not (8.0 <= dimensions.x <= 13.0 and 6.0 <= dimensions.y <= 11.0 and 16.0 <= dimensions.z <= 24.5):
        raise RuntimeError(f"combined bounds outside radar authority: {tuple(round(v, 4) for v in dimensions)}")

    implementation = {
        "schema": "skyguard.m01-radar-post.grok-mcp.production-correction02-implementation.v1",
        "classification": "PASSED_STRUCTURAL_PENDING_VISUAL",
        "source_scene": r"D:\Skyguard52\Production\Attempts\m01-radar-post-grok-mcp\attempt_20260811T040000000000Z\output\checkpoint\M01_RadarPost_GrokMCP_Checkpoint_A.blend",
        "visible_meshes": [record_mesh(obj) for obj in visible_objects],
        "sockets": SOCKETS,
        "collision_meshes": [obj.name for obj in collision_objects],
        "combined_min_m": [round(float(v), 6) for v in minimum],
        "combined_max_m": [round(float(v), 6) for v in maximum],
        "combined_dimensions_m": [round(float(v), 6) for v in dimensions],
        "total_vertices": sum(len(obj.data.vertices) for obj in visible_objects),
        "total_polygons": sum(len(obj.data.polygons) for obj in visible_objects),
        "generated_by": "Codex-supervised deterministic postflight after Grok OAuth Blender-MCP production",
    }
    REPORT.write_text(json.dumps(implementation, indent=2) + "\n", encoding="utf-8")

    bpy.context.scene["skyguard_asset_id"] = "m01-radar-post"
    bpy.context.scene["skyguard_classification"] = "PASSED_STRUCTURAL_PENDING_VISUAL"
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), check_existing=False)

    bpy.ops.object.select_all(action="DESELECT")
    export_objects = visible_objects + [bpy.data.objects[name] for name in SOCKETS] + collision_objects
    for obj in export_objects:
        obj.hide_viewport = False
        obj.hide_render = obj.name.startswith("UCX_") or obj.name.startswith("SOCKET_")
        obj.select_set(True)
    bpy.context.view_layer.objects.active = visible_objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
    )

    receipt = {
        "schema": "skyguard.m01-radar-post.production-correction02.scene-serialization-receipt.v1",
        "classification": "PASSED_STRUCTURAL_PENDING_VISUAL",
        "blend": str(BLEND),
        "glb": str(GLB),
        "implementation_report": str(REPORT),
        "visible_mesh_count": len(visible_objects),
        "socket_count": len(SOCKETS),
        "collision_count": len(collision_objects),
        "combined_dimensions_m": implementation["combined_dimensions_m"],
        "total_vertices": implementation["total_vertices"],
        "total_polygons": implementation["total_polygons"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("SKYGUARD_RADAR_FINALIZE_PASS")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
