import unreal
import os
import hashlib
import time
import math

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
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

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    return a

def rebuild_bright_lit(name, color, metallic=0.2, roughness=0.35):
    ensure_dir("/Game/Skyguard/Materials/Generated")
    path = "/Game/Skyguard/Materials/Generated/" + name
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials/Generated", unreal.Material, unreal.MaterialFactoryNew()
        )
    if not mat:
        return None
    try:
        mel.delete_all_material_expressions(mat)
        bc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, -80)
        bc.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
        mel.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
        # modest emissive so capture never pure black even if lights fail
        em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 40)
        em.set_editor_property("constant", unreal.LinearColor(color[0]*0.35, color[1]*0.35, color[2]*0.35, 1.0))
        mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 140)
        r.set_editor_property("r", float(roughness))
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        m = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
        m.set_editor_property("r", float(metallic))
        mel.connect_material_property(m, "", unreal.MaterialProperty.MP_METALLIC)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        log("bright lit mat " + name)
    except Exception as e:
        log("mat fail " + name + " " + str(e))
    return mat

def forward_from_rot(pitch, yaw):
    # UE: pitch/yaw/roll degrees -> forward vector
    p = math.radians(pitch)
    y = math.radians(yaw)
    x = math.cos(p) * math.cos(y)
    yy = math.cos(p) * math.sin(y)
    z = math.sin(p)
    return (x, yy, z)

def place_in_front_of_cam(name, cam_loc, cam_rot, mesh, mats, distance=400.0, scale=(8,8,8)):
    fx, fy, fz = forward_from_rot(cam_rot[0], cam_rot[1])
    # place a stack of objects along look vector
    placed = 0
    for i in range(8):
        d = distance + i * 120.0
        loc = (cam_loc[0] + fx * d, cam_loc[1] + fy * d, cam_loc[2] + fz * d)
        mat = mats[i % len(mats)]
        sc = (scale[0] * (1.0 - i*0.05), scale[1] * (1.0 - i*0.05), scale[2] * (1.0 - i*0.05))
        spawn_sm(mesh, loc, sc, unreal.Rotator(0, cam_rot[1], 0), "AAA_L21_%s_Near_%d" % (name, i), mat)
        # side offset variety
        spawn_sm(mesh, (loc[0] + fy*80, loc[1] - fx*80, loc[2]), (sc[0]*0.6, sc[1]*0.6, sc[2]*0.6), None, "AAA_L21_%s_Side_%d" % (name, i), mats[(i+1)%len(mats)])
        placed += 2
    # point light at first object
    first = (cam_loc[0] + fx * distance, cam_loc[1] + fy * distance, cam_loc[2] + fz * distance + 100)
    pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*first), unreal.Rotator())
    if pl:
        pl.set_actor_label("AAA_L21_%s_Light" % name)
        try:
            c = pl.get_component_by_class(unreal.PointLightComponent)
            if c:
                c.set_intensity(150000.0)
                c.set_editor_property("attenuation_radius", 6000.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            try:
                # alternate API
                pass
            except Exception:
                pass
    return placed

def densify_failed_cams(cams_spec, mats):
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    air = load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    total = 0
    for name, loc, rot in cams_spec:
        # only force content for previously failed beauty cams; still densify all for consistency
        total += place_in_front_of_cam(name, loc, rot, cube, mats, distance=350.0, scale=(10, 6, 6))
        # additional plane wall perpendicular to view
        fx, fy, fz = forward_from_rot(rot[0], rot[1])
        wall = (loc[0] + fx * 500, loc[1] + fy * 500, loc[2] + fz * 500)
        spawn_sm(plane, wall, (40, 25, 1), unreal.Rotator(rot[0], rot[1] + 90, 90), "AAA_L21_%s_Wall" % name, mats[0])
        spawn_sm(sphere, (wall[0], wall[1], wall[2] + 150), (5,5,5), None, "AAA_L21_%s_Ball" % name, mats[1])
    # world anchors near known aircraft/city
    for i in range(12):
        spawn_sm(cyl, (-i*30, 40, 330), (1.3,1.3,1.0), unreal.Rotator(0,0,90), "AAA_L21_YakSeg_%d"%i, air)
    spawn_sm(cube, (0,40,325), (14,2.2,0.2), None, "AAA_L21_YakWing", air)
    spawn_sm(sphere, (-280,40,330), (2.0,2.0,2.0), None, "AAA_L21_YakNose", air)
    # ocean wall of planes filling +X sea
    ocean = load_mat("/Game/Skyguard/Materials/M_Ocean") or mats[2]
    for i,x in enumerate([500,1500,2500,3500,4500]):
        for j,y in enumerate(range(-5000,5001,1600)):
            spawn_sm(plane, (x,y,2), (160,160,1), None, "AAA_L21_Ocean_%d_%d"%(i,j), ocean)
    log("forced frustum densify objects~" + str(total))

def densify_lights():
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,4000), unreal.Rotator(-45, 30, 0))
    if sun:
        sun.set_actor_label("AAA_L21_Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(20.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
                c.set_editor_property("atmosphere_sun_light", True)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L21_Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(3.0)
                c.set_editor_property("real_time_capture", True)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sky " + str(e))
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator())
        if a: a.set_actor_label("AAA_L21_Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L21_PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    # flood lights near failed cam origins
    for i, loc in enumerate([
        (620,-1050,500),(1800,-900,420),(500,-1700,750),(-650,-1300,260),
        (0,40,400),(-100,-200,340),(1000,-80,450)
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L21_Flood_%d"%i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(200000.0)
                    c.set_editor_property("attenuation_radius", 8000.0)
                    c.set_mobility(unreal.ComponentMobility.MOVABLE)
            except Exception:
                pass
    log("lights densify done")

def png_rgb_stats(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        px = list(im.getdata())
        step = max(1, len(px)//25000)
        sample = px[::step]
        black = sum(1 for c in sample if c[0]<8 and c[1]<8 and c[2]<8)/float(len(sample))
        uniq = len(set(sample))
        small = im.resize((64,36))
        s=list(small.getdata()); diffs=[]
        for y in range(36):
            for x in range(63):
                a=s[y*64+x]; b=s[y*64+x+1]
                diffs.append(abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2]))
        edge = sum(diffs)/float(len(diffs)) if diffs else 0.0
        return black, uniq, os.path.getsize(path), edge
    except Exception as e:
        log("pil stats fail " + str(e))
        return 1.0, 0, os.path.getsize(path) if os.path.isfile(path) else 0, 0.0

def capture(out_dir, cams_spec):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    # RT
    path = "/Game/Skyguard/Capture/RT_AAA_L21"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt = unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L21", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    for name, loc, rot in cams_spec:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label("AAA_L21_SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_every_frame", True)
    try:
        comp.set_editor_property("fov_angle", 85.0)
    except Exception:
        pass

    # Capture sources to try: BaseColor first (less light-dependent), then Final
    sources = []
    try:
        sources.append(("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception:
        pass
    try:
        sources.append(("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        try:
            sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
        except Exception:
            sources.append(("DEFAULT", None))

    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    saved = []
    for name, loc, rot in cams_spec:
        best = None
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("source set " + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(10):
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
            if os.path.isfile(out_png) and os.path.getsize(out_png) > 1000:
                black, uniq, size, edge = png_rgb_stats(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                valid = (black < 0.50 and uniq > 250 and edge > 4.0 and size > 100000) or (black < 0.20 and uniq > 800)
                log("still %s black=%.3f uniq=%d edge=%.1f size=%d valid=%s" % (out_name, black, uniq, edge, size, valid))
                rec = (out_png, size, h, black, uniq, edge, valid, src_name)
                saved.append(rec)
                score = (0 if not valid else 100000) + uniq + int((1.0-black)*1000) + int(edge*10)
                if best is None or score > best[0]:
                    best = (score, rec)
        if best and best[1][6]:
            # write canonical best
            canon = os.path.join(out_dir, name + ".png")
            try:
                import shutil
                shutil.copyfile(best[1][0], canon)
                log("canonical %s from %s" % (name, best[1][7]))
            except Exception as e:
                log("canon copy " + str(e))

    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass

    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop21 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        vc = 0
        for path, size, h, black, uniq, edge, valid, src in saved:
            f.write("%s  %d  black=%.3f uniq=%d edge=%.1f valid=%s src=%s  %s\n" % (h, size, black, uniq, edge, valid, src, path))
            if valid:
                vc += 1
        f.write("valid_count=%d total=%d\n" % (vc, len(saved)))
    log("manifest valid=%d/%d" % (sum(1 for s in saved if s[6]), len(saved)))
    return saved

def reseed_combat():
    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (20,105,360), "AAA_L21_CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800,0,520), "AAA_L21_CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-270,40,330), "AAA_L21_PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))

def main():
    log("loop21 near-plane densify + multi-source capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L21_")

    mats = [
        rebuild_bright_lit("M_L21_BrightMetal", (0.72, 0.74, 0.70), metallic=0.65, roughness=0.3),
        rebuild_bright_lit("M_L21_BrightSand", (0.86, 0.74, 0.48), metallic=0.0, roughness=0.85),
        rebuild_bright_lit("M_L21_BrightOcean", (0.08, 0.35, 0.55), metallic=0.1, roughness=0.15),
        rebuild_bright_lit("M_L21_BrightBrick", (0.55, 0.28, 0.18), metallic=0.0, roughness=0.8),
        rebuild_bright_lit("M_L21_BrightWhite", (0.92, 0.92, 0.9), metallic=0.05, roughness=0.4),
    ]
    mats = [m for m in mats if m]
    if not mats:
        mats = [load_mat("/Game/Skyguard/Materials/M_Metal"), load_mat("/Game/Skyguard/Materials/M_Beach"), load_mat("/Game/Skyguard/Materials/M_Ocean")]
        mats = [m for m in mats if m]

    # camera set: prioritize previously failed + keep known good
    cams = [
        ("AAA_Cam_L21_YakBeauty", (300, -400, 380), (-8, 150, 0)),   # closer than L20
        ("AAA_Cam_L21_Ocean", (900, -200, 200), (-12, 10, 0)),        # look over water planes
        ("AAA_Cam_L21_Harbor", (-500, -400, 220), (-8, -30, 0)),
        ("AAA_Cam_L21_Wide", (200, -800, 500), (-15, 120, 0)),
        ("AAA_Cam_L21_Prop", (-50, -120, 340), (-5, 30, 0)),
        ("AAA_Cam_L21_City", (-1200, -700, 400), (-9, 25, 0)),
        ("AAA_Cam_L21_Cockpit", (30, 115, 372), (-6, 8, 0)),
        ("AAA_Cam_L21_Combat", (800, -50, 420), (-8, 185, 0)),
    ]

    densify_lights()
    densify_failed_cams(cams, mats)
    reseed_combat()

    saved = capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L21", cams)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    vc = sum(1 for s in saved if s[6]) if saved else 0
    log("Loop21 complete stills=%d valid=%d" % (len(saved) if saved else 0, vc))
    if vc < 5:
        log("CRITIC: partial capture only; overall still FAIL vs AAA")
    else:
        log("CRITIC: multiple valid stills; harsh blind still required for AAA claim")

if __name__ == "__main__":
    main()
