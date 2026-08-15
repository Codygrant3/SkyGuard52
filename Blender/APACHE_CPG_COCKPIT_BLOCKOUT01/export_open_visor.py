"""Open CPG visor for the Play camera. No glass, seat, floor, or horizon."""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"D:\Skyguard52\Blender\APACHE_CPG_COCKPIT_BLOCKOUT01")
GLB = ROOT / "exports" / "apache_cpg_open_visor.glb"
EYE = Vector((0.0, 0.0, 1.18))


def nuke():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def mat(name, color, metallic=0.15, roughness=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def box(name, loc, size, material, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def cyl(name, loc, radius, depth, material, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=loc, rotation=rot, vertices=20
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def build():
    nuke()
    (ROOT / "exports").mkdir(parents=True, exist_ok=True)

    olive = mat("M_InteriorOlive", (0.18, 0.20, 0.12), roughness=0.7)
    dark = mat("M_Bezel", (0.04, 0.045, 0.05), metallic=0.35, roughness=0.35)
    stick = mat("M_Grip", (0.03, 0.03, 0.03), roughness=0.55)

    # Instruments stay below the eyepoint so the coast stays open.
    box("GEO_Dash", (0.50, 0.0, 0.72), (0.18, 0.76, 0.08), olive)
    box("GEO_GlareShield", (0.58, 0.0, 0.84), (0.16, 0.78, 0.015), dark)
    box("GEO_TEDAC_Bezel", (0.46, 0.0, 0.74), (0.04, 0.16, 0.16), dark)
    box("GEO_MPD_L_Bezel", (0.47, 0.24, 0.76), (0.035, 0.18, 0.15), dark)
    box("GEO_MPD_R_Bezel", (0.47, -0.24, 0.76), (0.035, 0.18, 0.15), dark)
    box("GEO_EUFD_Bezel", (0.50, 0.0, 0.90), (0.03, 0.36, 0.035), dark)
    box("GEO_Console_L", (0.08, 0.36, 0.62), (0.55, 0.10, 0.16), olive)
    box("GEO_Console_R", (0.08, -0.36, 0.62), (0.55, 0.10, 0.16), olive)
    cyl("GEO_Collective", (0.05, 0.30, 0.70), 0.022, 0.28, stick, (0.0, 1.15, 0.2))
    box("GEO_CollectiveHead", (0.16, 0.30, 0.78), (0.07, 0.04, 0.05), stick)
    cyl("GEO_Cyclic", (0.18, -0.16, 0.62), 0.018, 0.34, stick, (0.25, 0.0, 0.0))
    box("GEO_CyclicHead", (0.18, -0.16, 0.80), (0.05, 0.035, 0.07), stick)
    box("GEO_BowFrame", (0.82, 0.0, 1.05), (0.02, 0.80, 0.03), dark)

    geos = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in geos:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = geos[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = "SM_ApacheCPG_OpenVisor"

    bpy.context.scene.cursor.location = EYE
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    joined.location = (0.0, 0.0, 0.0)

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


if __name__ == "__main__":
    build()
