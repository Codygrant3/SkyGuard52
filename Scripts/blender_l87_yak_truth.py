import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


SOURCE = Path(
    os.environ.get(
        "SKYGUARD_YAK_SOURCE",
        r"D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame"
        r"\yak52-detail-kit-blender.glb",
    )
)
OUT_DIR = Path(
    os.environ.get(
        "SKYGUARD_YAK_OUT_DIR",
        r"D:\Skyguard52\Saved\Screenshots\AAA_L87_Blender",
    )
)
EXPORT = Path(
    os.environ.get(
        "SKYGUARD_YAK_EXPORT",
        r"D:\Skyguard52\Content\Skyguard\Meshes\Source\processed"
        r"\yak52_assembled_l87.glb",
    )
)
REPORT = OUT_DIR / "BLENDER_L87_REPORT.json"


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat(
        "-Z",
        "Y",
    ).to_euler()


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("import produced no mesh bounds")
    minimum = Vector(
        (
            min(point.x for point in points),
            min(point.y for point in points),
            min(point.z for point in points),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in points),
            max(point.y for point in points),
            max(point.z for point in points),
        )
    )
    return minimum, maximum


def add_area(name, location, energy, size, color, target):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name=name, object_data=data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def add_camera(name, location, target, lens):
    data = bpy.data.cameras.new(name=name)
    data.lens = lens
    data.sensor_width = 36.0
    data.dof.use_dof = False
    obj = bpy.data.objects.new(name=name, object_data=data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def configure_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.engine = "BLENDER_EEVEE"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("L87_StudioWorld")
    scene.world.color = (0.018, 0.025, 0.04)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.055, 0.075, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.32
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def main():
    if not SOURCE.is_file():
        raise RuntimeError(f"source GLB missing: {SOURCE}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    configure_render()
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))

    imported = list(bpy.context.scene.objects)
    mesh_objects = [obj for obj in imported if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("source GLB imported zero mesh objects")
    minimum, maximum = world_bounds(mesh_objects)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum

    root = bpy.data.objects.new("Yak52_L87_AssemblyRoot", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in list(bpy.context.scene.objects):
        if obj == root or obj.parent is not None:
            continue
        matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = matrix
    root.location -= center
    bpy.context.view_layer.update()

    minimum, maximum = world_bounds(mesh_objects)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    span = max(dimensions.x, dimensions.y, dimensions.z)
    if span <= 0.01:
        raise RuntimeError(f"invalid imported bounds: {tuple(dimensions)}")

    # Export only the reconstructed source hierarchy before adding validation
    # floor, lights, and cameras.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in imported:
        obj.select_set(True)
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(EXPORT),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )

    floor_z = minimum.z - max(0.01, dimensions.z * 0.015)
    bpy.ops.mesh.primitive_plane_add(
        size=span * 6.0,
        location=(center.x, center.y, floor_z),
    )
    floor = bpy.context.object
    floor.name = "L87_StudioFloor"
    floor_material = bpy.data.materials.new("L87_StudioFloor_Mat")
    floor_material.diffuse_color = (0.075, 0.085, 0.105, 1.0)
    floor_material.roughness = 0.68
    floor.data.materials.append(floor_material)

    target = center + Vector((0.0, 0.0, dimensions.z * 0.08))
    add_area(
        "L87_Key",
        center + Vector((span * 1.25, -span * 1.05, span * 1.15)),
        26000.0,
        span * 0.75,
        (1.0, 0.78, 0.58),
        target,
    )
    add_area(
        "L87_Fill",
        center + Vector((-span * 1.0, -span * 0.25, span * 0.65)),
        17000.0,
        span * 0.95,
        (0.48, 0.67, 1.0),
        target,
    )
    add_area(
        "L87_Rim",
        center + Vector((0.0, span * 1.3, span * 1.05)),
        22000.0,
        span * 0.7,
        (0.7, 0.82, 1.0),
        target,
    )

    camera_specs = (
        (
            "YakSide",
            center + Vector((span * 1.55, 0.0, span * 0.34)),
            target,
            55.0,
        ),
        (
            "YakFrontThreeQuarter",
            center + Vector((span * 1.1, -span * 1.45, span * 0.5)),
            target,
            58.0,
        ),
        (
            "YakRearThreeQuarter",
            center + Vector((-span * 1.0, span * 1.4, span * 0.55)),
            target,
            58.0,
        ),
        (
            "CockpitProbe",
            center
            + Vector(
                (
                    dimensions.x * 0.28,
                    dimensions.y * 0.12,
                    dimensions.z * 0.55,
                )
            ),
            center
            + Vector(
                (
                    0.0,
                    -dimensions.y * 0.16,
                    dimensions.z * 0.14,
                )
            ),
            42.0,
        ),
    )

    renders = []
    for name, location, aim, lens in camera_specs:
        camera = add_camera("L87_" + name, location, aim, lens)
        bpy.context.scene.camera = camera
        output = OUT_DIR / f"AAA_Cam_L87_{name}_FINAL.png"
        bpy.context.scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        if not output.is_file() or output.stat().st_size < 1000:
            raise RuntimeError(f"render failed: {output}")
        renders.append(
            {
                "camera": name,
                "path": str(output),
                "bytes": output.stat().st_size,
            }
        )

    report = {
        "source": str(SOURCE),
        "export": str(EXPORT),
        "mesh_objects": len(mesh_objects),
        "materials": len(bpy.data.materials),
        "bounds_min": list(minimum),
        "bounds_max": list(maximum),
        "dimensions": list(dimensions),
        "renders": renders,
        "gate": "visual_probe_not_promotion",
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("[SkyguardAAA] L87 Blender truth complete")
    print(json.dumps(report))


main()
