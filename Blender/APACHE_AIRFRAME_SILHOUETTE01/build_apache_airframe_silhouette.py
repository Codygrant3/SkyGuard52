"""AH-64 silhouette blockout. Public layout. Meters. +X forward, +Z up."""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"D:\Skyguard52\Blender\APACHE_AIRFRAME_SILHOUETTE01")
BLEND = ROOT / "apache_airframe_silhouette01.blend"
GLB = ROOT / "exports" / "apache_airframe_silhouette01.glb"
RENDERS = ROOT / "renders"


def nuke():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def mat(name, color, metallic=0.12, roughness=0.62, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
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


def cyl(name, loc, radius, depth, material, rot=(0.0, 0.0, 0.0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=loc, rotation=rot, vertices=verts
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def sph(name, loc, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=20, ring_count=12)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def empty(name, loc):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.empty_display_size = 0.12
    return obj


def camera(name, loc, aim):
    data = bpy.data.cameras.new(name)
    data.lens = 35.0
    data.clip_start = 0.05
    data.clip_end = 80.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    direction = Vector(aim) - Vector(loc)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return obj


def render_cam(cam, filename):
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)


def build():
    nuke()
    (ROOT / "exports").mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)

    green = mat("M_Olive", (0.07, 0.09, 0.055), roughness=0.7)
    dark = mat("M_OliveDark", (0.045, 0.055, 0.04), roughness=0.68)
    metal = mat("M_Metal", (0.12, 0.12, 0.11), metallic=0.55, roughness=0.38)
    rotor = mat("M_Rotor", (0.04, 0.04, 0.04), roughness=0.5)
    glass = mat("M_Glass", (0.18, 0.22, 0.26), roughness=0.08, alpha=0.22)
    frame = mat("M_Frame", (0.03, 0.03, 0.03), roughness=0.45)
    store = mat("M_Store", (0.13, 0.13, 0.12), roughness=0.55)

    empty("SO_Origin", (0.0, 0.0, 0.0))
    empty("SO_FrontGunnerSeat", (1.68, 0.0, 1.18))
    empty("SO_RearPilotSeat", (0.48, 0.0, 1.18))
    empty("SO_FrontEye", (1.76, 0.0, 1.46))
    empty("SO_GunnerSensorTurret", (2.36, 0.0, 0.28))
    empty("SO_ChinWeapon", (2.70, 0.0, -0.48))
    empty("SO_RotorHub", (0.30, 0.0, 2.58))

    # Fuselage — stepped so it reads Apache, not one gold brick.
    box("GEO_FuselageMid", (-0.40, 0.0, 0.78), (3.4, 1.05, 0.95), green)
    box("GEO_FuselageAft", (-2.40, 0.0, 0.86), (2.2, 0.92, 0.82), green)
    box("GEO_Belly", (0.20, 0.0, 0.28), (2.6, 0.78, 0.28), dark)
    box("GEO_Nose", (2.55, 0.0, 0.42), (1.7, 0.72, 0.42), dark, rot=(0.0, 0.18, 0.0))

    # Tandem greenhouses. CPG forward, pilot aft.
    box("GEO_CPG_Tub", (1.55, 0.0, 0.92), (1.35, 0.88, 0.38), dark)
    box("GEO_CPG_Glass", (1.62, 0.0, 1.38), (1.15, 0.78, 0.62), glass)
    box("GEO_CPG_Frame", (1.62, 0.0, 1.38), (1.22, 0.84, 0.06), frame)
    box("GEO_Pilot_Glass", (0.42, 0.0, 1.36), (1.05, 0.76, 0.58), glass)
    box("GEO_Pilot_Frame", (0.42, 0.0, 1.36), (1.12, 0.82, 0.06), frame)

    # TADS under the nose + lens snout.
    sph("GEO_TADS_Ball", (2.36, 0.0, 0.28), 0.24, metal)
    cyl("GEO_TADS_Lens", (2.58, 0.0, 0.28), 0.09, 0.22, metal, rot=(0.0, 1.5708, 0.0))

    # M230 hangs below the chin.
    box("GEO_M230_Receiver", (2.70, 0.0, -0.48), (0.42, 0.26, 0.32), metal)
    cyl("GEO_M230_Barrel", (3.18, 0.0, -0.54), 0.045, 0.95, metal, rot=(0.12, 1.5708, 0.0))
    box("GEO_M230_Mount", (2.55, 0.0, -0.18), (0.16, 0.12, 0.42), dark)

    # Stub wings, pylons, stores.
    box("GEO_Wing_L", (0.40, -1.55, 0.70), (0.95, 2.15, 0.10), dark)
    box("GEO_Wing_R", (0.40, 1.55, 0.70), (0.95, 2.15, 0.10), dark)
    box("GEO_Pylon_L", (0.40, -1.70, 0.42), (0.18, 0.10, 0.48), dark)
    box("GEO_Pylon_R", (0.40, 1.70, 0.42), (0.18, 0.10, 0.48), dark)
    cyl("GEO_Hydra_L", (0.40, -2.00, 0.28), 0.14, 1.15, store, rot=(0.0, 1.5708, 0.0))
    cyl("GEO_Hydra_R", (0.40, 2.00, 0.28), 0.14, 1.15, store, rot=(0.0, 1.5708, 0.0))
    box("GEO_Hellfire_L", (0.36, -1.28, 0.32), (1.05, 0.20, 0.14), store)
    box("GEO_Hellfire_R", (0.36, 1.28, 0.32), (1.05, 0.20, 0.14), store)

    # Twin engines.
    cyl("GEO_Engine_L", (-0.90, -0.82, 1.08), 0.24, 1.55, dark, rot=(0.0, 1.5708, 0.0))
    cyl("GEO_Engine_R", (-0.90, 0.82, 1.08), 0.24, 1.55, dark, rot=(0.0, 1.5708, 0.0))
    cyl("GEO_Exhaust_L", (-1.70, -0.82, 1.08), 0.18, 0.35, metal, rot=(0.0, 1.5708, 0.0))
    cyl("GEO_Exhaust_R", (-1.70, 0.82, 1.08), 0.18, 0.35, metal, rot=(0.0, 1.5708, 0.0))

    # Tail.
    box("GEO_TailBoom", (-4.40, 0.0, 0.96), (4.4, 0.28, 0.26), green)
    box("GEO_VerticalTail", (-6.85, 0.0, 1.70), (0.55, 0.14, 1.55), dark)
    box("GEO_HorizTail", (-6.85, 0.0, 1.18), (0.42, 2.20, 0.08), dark)
    cyl("GEO_TailRotor", (-6.95, 0.42, 1.78), 0.78, 0.05, rotor, rot=(1.5708, 0.0, 0.0))

    # Main rotor + Longbow-style dome.
    cyl("GEO_RotorMast", (0.30, 0.0, 1.95), 0.11, 1.05, metal)
    sph("GEO_RadarDome", (0.30, 0.0, 2.92), 0.22, metal)
    box("GEO_Blade_A", (0.30, 0.0, 2.58), (14.5, 0.18, 0.05), rotor)
    box("GEO_Blade_B", (0.30, 0.0, 2.58), (14.5, 0.18, 0.05), rotor, rot=(0.0, 0.0, 1.5708))

    # Gear.
    cyl("GEO_Gear_Nose", (2.00, 0.0, -0.28), 0.06, 0.70, metal, rot=(0.32, 0.0, 0.0))
    sph("GEO_Wheel_Nose", (2.10, 0.0, -0.62), 0.14, rotor)
    cyl("GEO_Gear_L", (-0.20, -0.70, -0.18), 0.06, 0.72, metal)
    cyl("GEO_Gear_R", (-0.20, 0.70, -0.18), 0.06, 0.72, metal)
    sph("GEO_Wheel_L", (-0.20, -0.70, -0.55), 0.16, rotor)
    sph("GEO_Wheel_R", (-0.20, 0.70, -0.55), 0.16, rotor)

    # Studio.
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.42, 0.50, 0.56, 1.0)
        bg.inputs[1].default_value = 0.9
    box(
        "GEO_GroundCard",
        (0.0, 0.0, -1.2),
        (40.0, 40.0, 0.04),
        mat("M_Ground", (0.28, 0.30, 0.24), roughness=0.9),
    )

    key = bpy.data.lights.new("L_Key", "AREA")
    key.energy = 900
    key.size = 6.0
    key_obj = bpy.data.objects.new("L_Key", key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (6.0, -8.0, 7.0)

    fill = bpy.data.lights.new("L_Fill", "AREA")
    fill.energy = 280
    fill.size = 8.0
    fill_obj = bpy.data.objects.new("L_Fill", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-4.0, 6.0, 4.0)

    cam_side = camera("CAM_Side", (-1.2, -17.5, 2.1), (-1.0, 0.0, 1.15))
    cam_side.data.lens = 32.0
    cam_q = camera("CAM_ThreeQuarter", (8.5, -9.5, 3.2), (0.2, 0.0, 1.0))
    cam_front = camera("CAM_Front", (12.0, 0.0, 1.4), (0.5, 0.0, 1.1))
    cam_down = camera("CAM_CPG_Down", (2.32, 0.0, 1.50), (2.95, 0.0, -0.40))
    cam_down.data.lens = 22.0

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.film_transparent = False

    render_cam(cam_side, "side.png")
    render_cam(cam_q, "three_quarter.png")
    render_cam(cam_front, "front.png")
    render_cam(cam_down, "cpg_down.png")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.name.startswith("GEO_") or obj.name.startswith("SO_"):
            if obj.name != "GEO_GroundCard":
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
    print("WROTE renders")


if __name__ == "__main__":
    build()
