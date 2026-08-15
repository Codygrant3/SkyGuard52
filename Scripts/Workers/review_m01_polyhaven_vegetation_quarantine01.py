import bpy
import json
import math
import os
import sys
from pathlib import Path


QUARANTINE = Path(r"D:\Skyguard52\Saved\SourceQuarantine\M01_POLYHAVEN_VEGETATION_QUARANTINE01")
ASSETS = ["fir_sapling", "pine_sapling_small", "shrub_02", "shrub_04", "grass_medium_02"]


def arg_value(name: str) -> str:
    if "--" not in sys.argv:
        raise RuntimeError("Missing Blender script delimiter")
    args = sys.argv[sys.argv.index("--") + 1 :]
    if name not in args:
        raise RuntimeError(f"Missing {name}")
    return args[args.index(name) + 1]


OUTPUT = Path(arg_value("--output"))
OUTPUT.mkdir(parents=True, exist_ok=False)
(OUTPUT / "renders").mkdir()


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def import_asset(asset_id: str, x: float):
    gltf = QUARANTINE / asset_id / f"{asset_id}_2k.gltf"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(gltf), import_shading="NORMALS")
    imported = [obj for obj in bpy.data.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"No mesh imported for {asset_id}")
    parent = bpy.data.objects.new(f"SRC_{asset_id}", None)
    bpy.context.scene.collection.objects.link(parent)
    for obj in imported:
        if obj.parent is None:
            obj.parent = parent
    parent.location.x = x
    parent["source_asset_id"] = asset_id
    parent["source_license"] = "CC0-1.0"
    return parent, meshes


def world_bounds(objects):
    corners = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        corners.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    if not corners:
        return None
    mins = [min(v[i] for v in corners) for i in range(3)]
    maxs = [max(v[i] for v in corners) for i in range(3)]
    return mins, maxs


from mathutils import Vector


clear_scene()

records = []
x_positions = [-6.0, -3.0, 0.0, 2.8, 5.2]
for asset_id, x in zip(ASSETS, x_positions):
    parent, meshes = import_asset(asset_id, x)
    triangles = sum(sum(len(p.vertices) - 2 for p in obj.data.polygons) for obj in meshes)
    vertices = sum(len(obj.data.vertices) for obj in meshes)
    materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
    records.append({
        "asset_id": asset_id,
        "object_count": len(meshes),
        "vertices": vertices,
        "triangles": triangles,
        "materials": materials,
        "source_path": str(QUARANTINE / asset_id / f"{asset_id}_2k.gltf"),
    })

# Neutral ground, never exported or interpreted as an asset.
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, -0.02))
ground = bpy.context.object
ground.name = "REVIEW_Ground_NotForExport"
mat = bpy.data.materials.new("MAT_ReviewGround")
mat.diffuse_color = (0.12, 0.14, 0.13, 1.0)
ground.data.materials.append(mat)

world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.05, 0.065, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4

def add_area(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    direction = Vector((0, 0, 1.3)) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return obj

add_area("Key", (3, -7, 8), 1700, 6, (1.0, 0.86, 0.72))
add_area("Fill", (-7, -1, 4), 900, 5, (0.62, 0.78, 1.0))

camera_data = bpy.data.cameras.new("ReviewCamera")
camera = bpy.data.objects.new("ReviewCamera", camera_data)
bpy.context.scene.collection.objects.link(camera)
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

views = [
    ("01_group_front_daylight", (10.5, -18.0, 6.0), (0, 0, 1.5)),
    ("02_group_oblique_daylight", (-13.0, -13.0, 7.0), (0, 0, 1.4)),
    ("03_group_overcast", (1.0, -20.0, 4.5), (0, 0, 1.25)),
    ("04_conifers", (-4.5, -10.0, 4.0), (-4.5, 0, 1.7)),
    ("05_groundcover", (2.5, -7.5, 2.0), (2.5, 0, 0.6)),
]

for index, (name, loc, target) in enumerate(views):
    if index == 2:
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.17, 0.2, 0.23, 1)
        world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    camera.location = loc
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 52 if index < 3 else 65
    scene.render.filepath = str(OUTPUT / "renders" / f"{name}.png")
    bpy.ops.render.render(write_still=True)

blend_path = OUTPUT / "M01_PolyHaven_Vegetation_Quarantine01_Review01.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

receipt = {
    "schema": "skyguard.m01-polyhaven-vegetation-quarantine01-blender-review01-receipt.v1",
    "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW",
    "source_mutated": False,
    "assets": records,
    "render_count": len(views),
    "renders": [str(OUTPUT / "renders" / f"{v[0]}.png") for v in views],
    "blend": str(blend_path),
    "unreal_imported": False,
    "runtime_promoted": False,
}
(OUTPUT / "review_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps(receipt, separators=(",", ":")))
