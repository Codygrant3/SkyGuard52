from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def move_to_collection(obj: Any, collection: Any) -> Any:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def activate(obj: Any) -> None:
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def finish_mesh(
    obj: Any,
    collection: Any,
    materials: Iterable[Any],
    *,
    bevel: float = 0.0,
    bevel_segments: int = 3,
    smooth: bool = True,
) -> Any:
    import bpy

    obj = move_to_collection(obj, collection)
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if obj.type == "MESH" and not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UV0")
    for material in materials:
        if material is not None:
            obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new(name="BEVEL_Production", type="BEVEL")
        modifier.width = bevel
        modifier.segments = bevel_segments
        modifier.limit_method = "ANGLE"
    if smooth and obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    collection: Any,
    material: Any,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.01,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish_mesh(obj, collection, [material], bevel=bevel)


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    collection: Any,
    material: Any,
    *,
    axis: str = "X",
    vertices: int = 48,
    bevel: float = 0.002,
) -> Any:
    import bpy

    rotation = {
        "X": (0.0, math.pi / 2.0, 0.0),
        "Y": (math.pi / 2.0, 0.0, 0.0),
        "Z": (0.0, 0.0, 0.0),
    }[axis]
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, collection, [material], bevel=bevel)


def add_cylinder_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    collection: Any,
    material: Any,
    *,
    vertices: int = 40,
    bevel: float = 0.002,
) -> Any:
    import bpy
    from mathutils import Vector

    a = Vector(start)
    b = Vector(end)
    direction = b - a
    midpoint = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=direction.length,
        location=midpoint,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    obj.rotation_mode = "XYZ"
    return finish_mesh(obj, collection, [material], bevel=bevel)


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    collection: Any,
    material: Any,
    *,
    segments: int = 48,
    rings: int = 24,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return finish_mesh(obj, collection, [material], bevel=0.0)


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    collection: Any,
    material: Any,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=48,
        minor_segments=12,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, collection, [material], bevel=0.0)


def add_curve(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    collection: Any,
    material: Any,
) -> Any:
    import bpy

    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    curve_data.materials.append(material)
    return obj


def pbr_material(
    name: str,
    base_color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    *,
    micro_scale: float = 0.0,
    micro_strength: float = 0.0,
    transmission: float = 0.0,
    alpha: float = 1.0,
) -> Any:
    import bpy

    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*base_color[:3], alpha)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    if "Transmission Weight" in principled.inputs:
        principled.inputs["Transmission Weight"].default_value = transmission
    if "Alpha" in principled.inputs:
        principled.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        material.surface_render_method = "DITHERED"
    if micro_scale > 0.0 and micro_strength > 0.0:
        texcoord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        bump = nodes.new("ShaderNodeBump")
        noise.inputs["Scale"].default_value = micro_scale
        noise.inputs["Detail"].default_value = 5.0
        noise.inputs["Roughness"].default_value = 0.7
        bump.inputs["Strength"].default_value = micro_strength
        bump.inputs["Distance"].default_value = 0.002
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def add_socket(name: str, location: tuple[float, float, float], collection: Any) -> Any:
    import bpy

    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.035
    obj.location = location
    collection.objects.link(obj)
    return obj


def add_collision_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    collection: Any,
    material: Any,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    obj = add_box(
        name,
        location,
        dimensions,
        collection,
        material,
        rotation=rotation,
        bevel=0.002,
    )
    obj.hide_render = True
    obj["SKG_Collision"] = True
    return obj


def render_fixed_views(
    sdk: Any,
    asset_collection: Any,
    output: Path,
    views: list[dict[str, Any]],
) -> list[Path]:
    import bpy
    from mathutils import Vector

    _review, camera = sdk.add_review_stage(asset_collection)
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for view in views:
        bpy.context.scene.frame_set(int(view.get("frame", 1)))
        camera.location = Vector(view["camera"])
        target = Vector(view["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = float(view.get("lens", 55.0))
        path = render_dir / f"{view['name']}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def scene_inventory(collection: Any) -> dict[str, Any]:
    import bpy

    meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
    armatures = [obj for obj in collection.all_objects if obj.type == "ARMATURE"]
    materials = sorted(
        {
            slot.material.name
            for obj in meshes
            for slot in obj.material_slots
            if slot.material
        }
    )
    return {
        "object_count": len(collection.all_objects),
        "mesh_count": len(meshes),
        "armature_count": len(armatures),
        "mesh_objects": [
            {
                "name": obj.name,
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "uv_layers": [layer.name for layer in obj.data.uv_layers],
                "materials": [
                    slot.material.name for slot in obj.material_slots if slot.material
                ],
                "modifiers": [modifier.type for modifier in obj.modifiers],
            }
            for obj in sorted(meshes, key=lambda item: item.name)
        ],
        "armatures": [
            {
                "name": obj.name,
                "bones": sorted(bone.name for bone in obj.data.bones),
            }
            for obj in armatures
        ],
        "actions": sorted(action.name for action in bpy.data.actions),
        "materials": materials,
        "sockets": sorted(
            obj.name
            for obj in collection.all_objects
            if obj.type == "EMPTY" and obj.name.startswith("SOCKET_")
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_production_receipt(
    output: Path,
    asset_id: str,
    collection: Any,
    source_records: list[dict[str, Any]],
    validations: dict[str, Any],
) -> Path:
    artifacts = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        if path.name == "production_receipt.json":
            continue
        artifacts.append(
            {
                "relative_path": str(path.relative_to(output)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    receipt = {
        "schema": "skyguard.asset-production-receipt.v1",
        "asset_id": asset_id,
        "sources": source_records,
        "scene_inventory": scene_inventory(collection),
        "validations": validations,
        "artifacts": artifacts,
    }
    path = output / "production_receipt.json"
    write_json(path, receipt)
    return path

