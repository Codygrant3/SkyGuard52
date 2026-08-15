"""Join CPG GEO into one mesh with origin at the eye for Unreal attach."""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"D:\Skyguard52\Blender\APACHE_CPG_COCKPIT_BLOCKOUT01")
BLEND = ROOT / "apache_cpg_cockpit_blockout01.blend"
GLB = ROOT / "exports" / "apache_cpg_cockpit_unreal.glb"
EYE = Vector((0.0, 0.0, 1.18))

bpy.ops.wm.open_mainfile(filepath=str(BLEND))

skip = {"GEO_HorizonCard"}
geos = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.name.startswith("GEO_") and obj.name not in skip
]
if not geos:
    raise RuntimeError("no GEO_ meshes")

bpy.ops.object.select_all(action="DESELECT")
for obj in geos:
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True)
bpy.context.view_layer.objects.active = geos[0]
bpy.ops.object.join()
joined = bpy.context.active_object
joined.name = "SM_ApacheCPG_Cockpit"

bpy.context.scene.cursor.location = EYE
bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
joined.location = (0.0, 0.0, 0.0)

(ROOT / "exports").mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
joined.select_set(True)
bpy.context.view_layer.objects.active = joined
bpy.ops.export_scene.gltf(
    filepath=str(GLB),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
print("WROTE", GLB)
print("origin_at_eye")
