"""
AH-64 CPG first-person cockpit blockout.
Public layout only. Meters. +X forward, +Z up.
"""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"D:\Skyguard52\Blender\APACHE_CPG_COCKPIT_BLOCKOUT01")
BLEND = ROOT / "apache_cpg_cockpit_blockout01.blend"
GLB = ROOT / "exports" / "apache_cpg_cockpit_blockout01.glb"
RENDER = ROOT / "renders" / "cpg_eyepoint.png"

EYE = Vector((0.0, 0.0, 1.18))


def nuke():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def mat(name, color, metallic=0.15, roughness=0.55, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = emit
    if alpha < 1.0:
        m.blend_method = "BLEND"
        bsdf.inputs["Alpha"].default_value = alpha
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
        radius=radius, depth=depth, location=loc, rotation=rot, vertices=24
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def empty(name, loc):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.empty_display_size = 0.08
    return obj


def build():
    nuke()
    (ROOT / "exports").mkdir(parents=True, exist_ok=True)
    (ROOT / "renders").mkdir(parents=True, exist_ok=True)

    olive = mat("M_InteriorOlive", (0.18, 0.20, 0.12), roughness=0.7)
    dark = mat("M_Bezel", (0.04, 0.045, 0.05), metallic=0.35, roughness=0.35)
    seat = mat("M_Seat", (0.08, 0.07, 0.05), roughness=0.8)
    tedac = mat("M_TEDAC", (0.05, 0.18, 0.08), roughness=0.25, emit=1.8)
    mpd = mat("M_MPD", (0.04, 0.12, 0.16), roughness=0.25, emit=1.4)
    eufd = mat("M_EUFD", (0.15, 0.22, 0.08), roughness=0.3, emit=0.9)
    stick = mat("M_Grip", (0.03, 0.03, 0.03), roughness=0.55)
    glass = mat("M_CanopyGlass", (0.25, 0.35, 0.4), roughness=0.05, alpha=0.12)
    rail = mat("M_CanopyRail", (0.12, 0.13, 0.1), metallic=0.4, roughness=0.4)

    empty("SO_CPG_Eye", EYE)
    empty("SO_TEDAC", (0.40, 0.0, 0.90))
    empty("SO_MPD_L", (0.40, 0.23, 0.92))
    empty("SO_MPD_R", (0.40, -0.23, 0.92))

    # Armored bucket seat behind the eye
    box("GEO_SeatPan", (-0.12, 0.0, 0.58), (0.38, 0.42, 0.08), seat)
    box("GEO_SeatBack", (-0.28, 0.0, 0.95), (0.08, 0.42, 0.70), seat)
    box("GEO_Headrest", (-0.26, 0.0, 1.32), (0.07, 0.22, 0.12), seat)

    # Floor / tub
    box("GEO_Floor", (0.10, 0.0, 0.36), (0.90, 0.78, 0.04), olive)
    box("GEO_Kick", (0.48, 0.0, 0.50), (0.06, 0.70, 0.28), olive)

    # Dash sits low so the CPG looks *over* the instruments at the world.
    box("GEO_Dash", (0.50, 0.0, 0.72), (0.18, 0.76, 0.08), olive)
    box("GEO_GlareShield", (0.58, 0.0, 0.86), (0.20, 0.78, 0.02), dark)

    # TEDAC 5x5 inch ~ 0.127m, lower-center of the CPG view
    box("GEO_TEDAC_Bezel", (0.46, 0.0, 0.74), (0.04, 0.16, 0.16), dark)
    box("GEO_TEDAC_Screen", (0.482, 0.0, 0.74), (0.008, 0.127, 0.127), tedac)
    cyl("GEO_TEDAC_Grip_L", (0.44, 0.12, 0.64), 0.018, 0.11, stick, (1.2, 0, 0))
    cyl("GEO_TEDAC_Grip_R", (0.44, -0.12, 0.64), 0.018, 0.11, stick, (-1.2, 0, 0))

    box("GEO_MPD_L_Bezel", (0.47, 0.24, 0.76), (0.035, 0.18, 0.15), dark)
    box("GEO_MPD_L_Screen", (0.490, 0.24, 0.76), (0.006, 0.16, 0.13), mpd)
    box("GEO_MPD_R_Bezel", (0.47, -0.24, 0.76), (0.035, 0.18, 0.15), dark)
    box("GEO_MPD_R_Screen", (0.490, -0.24, 0.76), (0.006, 0.16, 0.13), mpd)
    box("GEO_EUFD", (0.50, 0.0, 0.90), (0.03, 0.34, 0.03), eufd)

    # Side consoles
    box("GEO_Console_L", (0.08, 0.36, 0.62), (0.55, 0.10, 0.16), olive)
    box("GEO_Console_R", (0.08, -0.36, 0.62), (0.55, 0.10, 0.16), olive)

    # HOCAS — collective left, cyclic right
    cyl("GEO_Collective", (0.05, 0.30, 0.70), 0.022, 0.28, stick, (0.0, 1.15, 0.2))
    box("GEO_CollectiveHead", (0.16, 0.30, 0.78), (0.07, 0.04, 0.05), stick)
    cyl("GEO_Cyclic", (0.18, -0.16, 0.62), 0.018, 0.34, stick, (0.25, 0.0, 0.0))
    box("GEO_CyclicHead", (0.18, -0.16, 0.80), (0.05, 0.035, 0.07), stick)

    # Narrow greenhouse: side rails + bow only. No roof slab in the eyepoint.
    box("GEO_Rail_L", (0.25, 0.42, 1.20), (1.20, 0.025, 0.035), rail)
    box("GEO_Rail_R", (0.25, -0.42, 1.20), (1.20, 0.025, 0.035), rail)
    box("GEO_BowFrame", (0.82, 0.0, 1.12), (0.03, 0.86, 0.05), rail)
    box("GEO_AftFrame", (-0.32, 0.0, 1.28), (0.03, 0.82, 0.04), rail)
    box("GEO_Glass_L", (0.30, 0.41, 1.18), (1.10, 0.008, 0.42), glass)
    box("GEO_Glass_R", (0.30, -0.41, 1.18), (1.10, 0.008, 0.42), glass)
    box("GEO_IHADSS_Frame", (0.06, 0.0, 1.20), (0.008, 0.14, 0.07), dark)

    cam_data = bpy.data.cameras.new("CAM_CPG_Eye")
    cam_data.lens = 24.0
    cam_data.clip_start = 0.03
    cam = bpy.data.objects.new("CAM_CPG_Eye", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = EYE + Vector((0.03, 0.0, 0.0))
    aim = Vector((1.6, 0.0, 0.58)) - cam.location
    cam.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()

    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.42, 0.52, 0.62, 1.0)
        bg.inputs[1].default_value = 1.2
    box("GEO_HorizonCard", (8.0, 0.0, 0.4), (0.2, 18.0, 6.0),
        mat("M_Horizon", (0.35, 0.42, 0.28), roughness=0.9, emit=0.15))

    overview_data = bpy.data.cameras.new("CAM_Overview")
    overview_data.lens = 35.0
    overview = bpy.data.objects.new("CAM_Overview", overview_data)
    bpy.context.collection.objects.link(overview)
    overview.location = (1.6, -1.8, 1.7)
    o_aim = Vector((0.2, 0.0, 0.85)) - overview.location
    overview.rotation_euler = o_aim.to_track_quat("-Z", "Y").to_euler()

    key = bpy.data.lights.new("L_Key", "AREA")
    key.energy = 80
    key.size = 0.6
    key_obj = bpy.data.objects.new("L_Key", key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (0.4, 0.5, 1.8)

    fill = bpy.data.lights.new("L_Fill", "AREA")
    fill.energy = 25
    fill.size = 0.8
    fill_obj = bpy.data.objects.new("L_Fill", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (0.2, -0.6, 1.5)

    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    if hasattr(bpy.context.scene, "eevee"):
        bpy.context.scene.eevee.taa_render_samples = 16
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 900
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = str(RENDER)
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = overview
    bpy.context.scene.render.filepath = str(ROOT / "renders" / "cpg_overview.png")
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = cam

    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.name.startswith("GEO_") or obj.name.startswith("SO_"):
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("WROTE", BLEND)
    print("WROTE", GLB)
    print("WROTE", RENDER)


if __name__ == "__main__":
    build()
