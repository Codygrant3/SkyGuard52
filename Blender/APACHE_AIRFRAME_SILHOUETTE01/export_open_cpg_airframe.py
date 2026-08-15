"""Join silhouette GEO for Unreal. Drop nose/CPG glass so the Play lens stays open."""
from pathlib import Path

import bpy

ROOT = Path(r"D:\Skyguard52\Blender\APACHE_AIRFRAME_SILHOUETTE01")
BLEND = ROOT / "apache_airframe_silhouette01.blend"
GLB = ROOT / "exports" / "apache_airframe_open_cpg.glb"

SKIP = {
    "GEO_GroundCard",
    "GEO_Nose",
    "GEO_CPG_Glass",
    "GEO_CPG_Frame",
}

bpy.ops.wm.open_mainfile(filepath=str(BLEND))

geos = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.name.startswith("GEO_") and obj.name not in SKIP
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
joined.name = "SM_ApacheAirframe_Silhouette"
bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

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
print("WROTE", GLB)
