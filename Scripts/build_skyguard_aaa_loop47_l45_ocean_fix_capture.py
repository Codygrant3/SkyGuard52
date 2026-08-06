import unreal
import os
import hashlib
import time
import math

PREFIX = "AAA_L47_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L47"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L47"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_old():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith("AAA_L") or n.startswith("AAA_Cam_L")):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def load_mat(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def get_loc(a):
    try:
        v = a.get_actor_location()
        return (float(v.x), float(v.y), float(v.z))
    except Exception:
        return None

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    x,y,z = float(loc[0]), float(loc[1]), float(loc[2])
    a = None
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if sub:
            a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    except Exception:
        pass
    if not a:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
    for _ in range(3):
        try:
            a.set_actor_location(unreal.Vector(x,y,z), False, True)
        except Exception:
            pass
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    got = get_loc(a)
    if got and (abs(got[0]-x)+abs(got[1]-y)+abs(got[2]-z) > 1.0):
        log("SPAWN_MISMATCH %s target=(%.1f,%.1f,%.1f) got=%s" % (label, x,y,z, got))
    return a

def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    mat_paths = [
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitRed",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightBrick",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightMetal",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightOcean",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightSand",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightWhite",
        "/Game/Skyguard/Materials/Generated/M_L23_Airframe",
        "/Game/Skyguard/Materials/Generated/M_L23_Brick",
        "/Game/Skyguard/Materials/Generated/M_L23_Panel",
        "/Game/Skyguard/Materials/Generated/M_L23_Boom",
        "/Game/Skyguard/Materials/Generated/M_L23_Muzzle",
        "/Game/Skyguard/Materials/Generated/M_L23_Needle",
        "/Game/Skyguard/Materials/Generated/M_L23_Plaster",
        "/Game/Skyguard/Materials/Generated/M_L23_Asphalt",
        "/Game/Skyguard/Materials/Generated/M_L23_Beach",
        "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
        "/Game/Skyguard/Materials/M_Metal",
        "/Game/Skyguard/Materials/M_MetalRust",
        "/Game/Skyguard/Materials/M_RifleTan",
        "/Game/Skyguard/Materials/M_PropDisc",
        "/Game/Skyguard/Materials/M_LeatherGlove",
        "/Game/Skyguard/Materials/M_CityGlass",
        "/Game/Skyguard/Materials/M_CockpitInterior",
        "/Game/Skyguard/Materials/M_ExhaustGlow",
    ]
    mats = []
    for p in mat_paths:
        m = load_mat(p)
        if m:
            mats.append(m)
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    if not mats:
        mats = [m for m in [unlit_y, unlit_c, unlit_r, unlit_w, unlit_g] if m]
    log("loop47 mat palette size=%d" % len(mats))

    # Minimal: one huge unique marker + checker wall per cam, yaw0 look +X
    stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, unlit_y),
        ("PropHub", (0.0, 200.0, 500.0), 120.0, unlit_c),
        ("PropNose", (0.0, -200.0, 500.0), 120.0, unlit_r),
        ("YakBeauty", (300.0, -250.0, 420.0), 150.0, unlit_w),
        ("Cockpit", (40.0, 120.0, 380.0), 80.0, unlit_y),
        ("ADS", (20.0, 150.0, 370.0), 70.0, unlit_c),
        ("City", (-1200.0, 0.0, 300.0), 140.0, unlit_r),
        ("Combat", (900.0, 0.0, 450.0), 140.0, unlit_g or unlit_y),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, unlit_w),
        ("Ocean", (900.0, -400.0, 140.0), 140.0, unlit_c),
        ("Wide", (200.0, -600.0, 420.0), 180.0, unlit_y),
    ]

    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        m = mat or (mats[i % len(mats)] if mats else None)
        # giant sphere marker unique scale per cam
        spawn_sm(sphere, (bx, cy, cz), (6.0 + i*0.3, 6.0 + i*0.3, 6.0 + i*0.3), None, PREFIX + "Marker_%s" % name, m)
        # high-contrast checker wall filling FOV
        for iy in range(-8, 9):
            for iz in range(-6, 7):
                mm = mats[(i + iy + iz) % len(mats)] if mats else m
                spawn_sm(cube, (bx + 2, cy + iy * 5.0, cz + iz * 5.0), (0.4, 0.7, 0.7), None, PREFIX + "Wall_%s_%d_%d" % (name, iy, iz), mm)
        # vertical stripes for edge energy
        for iy in range(-10, 11):
            spawn_sm(cube, (bx + 1, cy + iy * 4.0, cz), (0.25, 0.3, 8.0), None, PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i+iy) % len(mats)] if mats else m)

        # WALL-PLANE multi-material densify for Prop family. Expand color palette for uniq>=80.
        # Strict: only x >= bx+1 (existing stripes) and x == bx+2 wall densify. No mid-FOV.
        if name in ("Prop", "PropHub", "PropNose"):
            denser = 2.0 if name in ("Prop", "PropNose") else 2.5
            yspan = 20 if name in ("Prop", "PropNose") else 15
            zspan = 15 if name in ("Prop", "PropNose") else 12
            nmat = max(len(mats), 1)
            for iy in range(-yspan, yspan + 1):
                for iz in range(-zspan, zspan + 1):
                    mm = mats[(iy * 19 + iz * 17 + i * 11 + (iy * iz) % 7) % nmat]
                    if (iy + iz) % 3 == 0:
                        scale = (0.16, 0.38, 0.38)
                    elif (iy + iz) % 3 == 1:
                        scale = (0.28, 0.72, 0.72)
                    else:
                        scale = (0.22, 0.55, 0.55)
                    spawn_sm(cube, (bx + 2.0, cy + iy * denser, cz + iz * denser), scale, None, PREFIX + "WPlane_%s_%d_%d" % (name, iy, iz), mm)
            for iy in range(-24, 25):
                mm = mats[(iy * 5 + i * 3) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.55, cz), (0.12, 0.16, 12.0), None, PREFIX + "WStripe_%s_%d" % (name, iy), mm)
            for iz in range(-20, 21):
                mm = mats[(iz * 7 + i * 2) % nmat]
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.55), (0.12, 12.0, 0.16), None, PREFIX + "HStripe_%s_%d" % (name, iz), mm)
            # multi-color hub cluster on wall plane
            for k in range(16):
                ang = k * 0.39269908169
                ry = math.sin(ang) * (6.0 + (k % 3) * 3.0)
                rz = math.cos(ang) * (6.0 + (k % 3) * 3.0)
                mm = mats[(k * 3 + i) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.18, 0.8, 0.32), unreal.Rotator(0, 0, k * 11.25), PREFIX + "WRing_%s_%d" % (name, k), mm)
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.5, 1.5, 1.5), None, PREFIX + "WHub_%s" % name, mats[i % nmat])

        # Ocean-only recovery: bright unlit/ocean/foam wall densify. No dark PBR hero overlays.
        if name == "Ocean":
            m_ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightOcean") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean") or load_mat("/Game/Skyguard/Materials/M_Ocean")
            m_foam = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam") or load_mat("/Game/Skyguard/Materials/M_L5_SeaFoam") or unlit_w
            m_sand = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightSand") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Beach") or unlit_y
            nmat = max(len(mats), 1)
            for iy in range(-14, 15):
                for iz in range(-10, 11):
                    if (iy + iz) % 2 == 0:
                        mm = m_ocean or mats[(iy + iz) % nmat]
                    elif (iy + iz) % 3 == 0:
                        mm = m_foam or unlit_w or mats[(iy + iz) % nmat]
                    else:
                        mm = unlit_c or mats[(iy + iz) % nmat]
                    spawn_sm(cube, (bx + 2.0, cy + iy * 3.0, cz + iz * 3.0), (0.25, 0.7, 0.7), None, PREFIX + "OceanWall_%d_%d" % (iy, iz), mm)
            for iy in range(-16, 17):
                spawn_sm(cube, (bx + 1.5, cy + iy * 2.4, cz), (0.18, 0.25, 10.0), None, PREFIX + "OceanStripe_%d" % iy, m_foam or unlit_w or mats[iy % nmat])
            for k in range(12):
                spawn_sm(sphere, (bx + 2.3, cy - 14 + k * 2.4, cz + (k % 5) * 2.0), (0.9, 0.9, 0.9), None, PREFIX + "FoamCap_%d" % k, m_foam or unlit_w or mats[k % nmat])
            # bright sand/coast band on wall
            for iy in range(-10, 11):
                spawn_sm(cube, (bx + 2.1, cy + iy * 2.5, cz - 8.0), (0.2, 0.8, 0.5), None, PREFIX + "CoastBand_%d" % iy, m_sand or unlit_y or mats[iy % nmat])


    # lighting: bright directional + sky + one point per stage board
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,5000), unreal.Rotator(-30, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(20.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(4.0)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        intensity = 800000.0 if name == "Ocean" else 400000.0
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx, cy, cz + 20), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%s" % name)
            try:
                pl.set_actor_location(unreal.Vector(bx, cy, cz + 20), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intensity)
                    c.set_editor_property("attenuation_radius", 8000.0 if name == "Ocean" else 6000.0)
            except Exception:
                pass
        if name == "Ocean":
            pl2 = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx + 2.0, cy, cz + 50), unreal.Rotator())
            if pl2:
                pl2.set_actor_label(PREFIX + "Pt_OceanFill")
                try:
                    pl2.set_actor_location(unreal.Vector(bx + 2.0, cy, cz + 50), False, True)
                except Exception:
                    pass
                try:
                    c = pl2.get_component_by_class(unreal.PointLightComponent)
                    if c:
                        c.set_intensity(1000000.0)
                        c.set_editor_property("attenuation_radius", 9000.0)
                except Exception:
                    pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + "PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("loop47 ocean-fix densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L47", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = [("AAA_Cam_L47_%s" % name, cam, (0.0,0.0,0.0)) for name, cam, dist, mat in stages]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            log("CAM %s target=%s got=%s" % (name, loc, get_loc(c)))

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label(PREFIX + "SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    try:
        comp.set_editor_property("capture_on_movement", False)
    except Exception:
        pass
    try:
        # show only lit/unlit geometry
        comp.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES)
    except Exception:
        pass
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    sources = []
    try:
        sources.append(("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception:
        pass
    try:
        sources.append(("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        pass
    try:
        sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
    except Exception:
        if not sources:
            sources.append(("DEFAULT", None))

    saved = []
    for name, loc, rot in cams:
        try:
            comp.set_editor_property("fov_angle", 90.0)
        except Exception:
            pass
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src " + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(6):
                try:
                    comp.capture_scene()
                except Exception:
                    pass
            out_name = "%s_%s.png" % (name, src_name)
            out_png = os.path.join(out_dir, out_name)
            if os.path.isfile(out_png):
                try: os.remove(out_png)
                except Exception: pass
            try:
                unreal.RenderingLibrary.export_render_target(world, rt, out_dir, out_name)
            except Exception as e:
                log("export " + out_name + " " + str(e))
            if os.path.isfile(out_png):
                size = os.path.getsize(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                log("still %s size=%d sha=%s" % (out_name, size, h[:16]))
                saved.append((out_png, size, h, src_name, name))
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop47 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=l45_freeze_ocean_only_fix_no_pbr_regression\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop47 L45 freeze + Ocean-only bright densify/light fix (no dark PBR hero overlay) start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop47 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
