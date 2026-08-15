from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m01-litter-bin-export-recovery01\attempt_20260811T120000000000Z\output"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_LitterBin_Production01_ExportRecovery01.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_LitterBin_Production01_ExportRecovery01.glb"
MESH_NAME = "SM_M01_Promenade_LitterBin_A"
SOCKET_NAME = "SOCKET_LitterBin_Origin"
COLLISION_NAME = "UCX_SM_M01_Promenade_LitterBin_A_00"
MATERIALS = [
    "M_M01_LitterBin_PowderCoat",
    "M_M01_LitterBin_DarkAperture",
    "M_M01_LitterBin_StainlessTrim",
]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return minimum, maximum


def unhide_layer(layer):
    layer.exclude = False
    layer.hide_viewport = False
    for child in layer.children:
        unhide_layer(child)


def read_glb(path):
    with open(path, "rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2 and total == path.stat().st_size, "Invalid recovery GLB header")
        length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "Recovery GLB JSON chunk is absent")
        return json.loads(stream.read(length).decode("utf-8").rstrip("\x00 \t\r\n"))


for directory in (OUTPUT, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

required = [MESH_NAME, SOCKET_NAME, COLLISION_NAME]
for name in required:
    require(bpy.data.objects.get(name) is not None, f"Accepted blend is missing {name}")
mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
require(mesh.type == "MESH" and socket.type == "EMPTY" and collision.type == "MESH", "Accepted governed object type changed")
require(mesh.data.uv_layers.get("UVMap") is not None, "Accepted mesh lost UVMap")
minimum, maximum = bounds(mesh)
dimensions = maximum - minimum
require(0.48 <= dimensions.x <= 0.62 and 0.42 <= dimensions.y <= 0.55 and 0.90 <= dimensions.z <= 1.10, f"Accepted dimensions changed: {tuple(dimensions)}")
require(-0.025 <= minimum.z <= 0.025, f"Accepted grounding changed: {minimum.z}")
require({slot.material.name for slot in mesh.material_slots if slot.material} == set(MATERIALS), "Accepted material identities changed")
socket.empty_display_type = "PLAIN_AXES"

unhide_layer(bpy.context.view_layer.layer_collection)
for collection in bpy.data.collections:
    collection.hide_viewport = False
    collection.hide_render = False
for obj in (mesh, socket, collision):
    obj.hide_viewport = False
    obj.hide_render = False
    obj.hide_set(False)

bpy.ops.object.select_all(action="DESELECT")
for obj in (mesh, socket, collision):
    obj.select_set(True)
bpy.context.view_layer.objects.active = mesh
bpy.ops.export_scene.gltf(
    filepath=str(FINAL_GLB),
    export_format="GLB",
    use_selection=True,
    use_visible=False,
    use_renderable=False,
    export_yup=True,
    export_apply=True,
    export_extras=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)

document = read_glb(FINAL_GLB)
nodes = [str(row.get("name", "")) for row in document.get("nodes", [])]
meshes = [str(row.get("name", "")) for row in document.get("meshes", [])]
materials = [str(row.get("name", "")) for row in document.get("materials", [])]
require(set(required).issubset(nodes), f"Recovery GLB still lacks governed nodes: {nodes}")
require(len(meshes) == 2, f"Recovery GLB must contain render and collision meshes: {meshes}")
require(materials == MATERIALS, f"Recovery GLB materials changed: {materials}")

collision.hide_render = True
socket.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

report = {
    "schema": "skyguard.m01-litter-bin.export-recovery01.report.v1",
    "classification": "PASSED_GLTF_STRUCTURE_READY_FOR_UNREAL_STAGING",
    "geometry_changed": False,
    "dimensions_m": list(dimensions),
    "vertices": len(mesh.data.vertices),
    "polygons": len(mesh.data.polygons),
    "nodes": nodes,
    "meshes": meshes,
    "materials": materials,
    "blend": str(FINAL_BLEND),
    "glb": str(FINAL_GLB),
}
write_json(OUTPUT / "export_recovery_report.json", report)
write_json(RECEIPTS / "glb_structure_receipt.json", report)
inventory = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": inventory})
print("PASSED_GLTF_STRUCTURE_READY_FOR_UNREAL_STAGING")
