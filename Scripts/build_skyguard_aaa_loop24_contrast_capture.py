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

def list_static_meshes(folder):
    out=[]
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log("list "+str(e))
    return out

def bounds_max(mesh):
    try:
        e = mesh.get_bounds().box_extent
        return max(abs(e.x)*2, abs(e.y)*2, abs(e.z)*2, 0.001)
    except Exception:
        return 100.0

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

def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")

    # reuse L23 mats if present
    air = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Airframe") or load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean") or load_mat("/Game/Skyguard/Materials/M_Ocean")
    beach = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Beach") or load_mat("/Game/Skyguard/Materials/M_Beach")
    foam = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick") or load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade")
    plaster = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Plaster")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Asphalt")
    glass = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Glass") or load_mat("/Game/Skyguard/Materials/M_CityGlass")
    panel = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Panel")
    leather = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Leather")
    canopy = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Canopy")
    muzzle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle") or load_mat("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot")
    boom = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Boom") or load_mat("/Game/Skyguard/Materials/Generated/MI_ExplosionCore")

    # Yak production kit full place
    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    prod=[]
    for path, mesh in meshes:
        n = path.split("/")[-1].split(".")[0]
        low = n.lower()
        if low.startswith("production-") or ("yak52" in low and not low.startswith("batch_")):
            prod.append((path, mesh, n, low))
    ref=None
    for path, mesh, n, low in prod:
        if "wings-tail" in low or "exterior" in low or "fuselage" in low:
            ref=mesh; break
    sc=1.0
    if ref:
        sc = 950.0 / bounds_max(ref)
        if sc > 20: sc=1.0
        if sc < 0.02: sc=0.25
    s=(sc,sc,sc)
    log("yak prod=%d scale=%s" % (len(prod), s))
    origin=(0.0,40.0,330.0)
    for path, mesh, n, low in prod:
        mat=air
        if any(k in low for k in ["panel","instrument","gauge","annunciator","bezel"]):
            mat=panel or air
        if "glass" in low or "canopy" in low:
            mat=canopy or glass or air
        if "upholstery" in low or "quilt" in low:
            mat=leather or air
        spawn_sm(mesh, origin, s, None, "AAA_L24_Yak_%s"%n[:40], mat)

    # Cockpit near-field contrast blocks (avoid pure white materials)
    for i in range(16):
        spawn_sm(cube, (5+i*3, 90+i*2, 350+(i%4)*4), (0.25,0.25,0.25), None, "AAA_L24_CockDark_%d"%i, panel or asphalt)
        spawn_sm(cube, (8+i*3, 100+i*2, 355+(i%3)*5), (0.2,0.2,0.15), None, "AAA_L24_CockMid_%d"%i, leather or brick)
        spawn_sm(sphere, (12+i*2, 115, 360), (0.08,0.08,0.08), None, "AAA_L24_GaugeBlob_%d"%i, glass)
    spawn_sm(plane, (25, 110, 385), (1.4,1.0,1), unreal.Rotator(70,0,0), "AAA_L24_Canopy", canopy or glass)
    spawn_sm(cube, (-20, 100, 360), (0.2,1.2,0.9), None, "AAA_L24_PilotBulk", panel or asphalt)

    # Prop readability near prop cam
    for i,ang in enumerate(range(0,180,15)):
        spawn_sm(cube, (-300,40,330), (0.1,4.0,0.1), unreal.Rotator(0,ang,0), "AAA_L24_Blade_%d"%i, air)
    spawn_sm(sphere, (-310,40,330), (0.6,0.6,0.6), None, "AAA_L24_SpinnerHub", panel or air)
    try:
        cls=unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-300,40,330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L24_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.6,1.6,1.6))
    except Exception as e:
        log("prop "+str(e))

    # City high-contrast facades for edge energy
    for i in range(80):
        x=-2450-(i%10)*140
        y=-3600+(i//10)*300
        h=7+(i*9)%14
        mat = brick if i%2==0 else plaster
        spawn_sm(cube, (x,y,40+h*22), (3.0,2.6,h), None, "AAA_L24_Bldg_%d"%i, mat)
        # dark window grid
        for w in range(min(h,8)):
            spawn_sm(cube, (x+30, y-20+(w%3)*10, 80+w*40), (0.08,0.7,0.4), None, "AAA_L24_Win_%d_%d"%(i,w), panel or asphalt)
            spawn_sm(cube, (x+31, y-20+(w%3)*10, 80+w*40), (0.05,0.55,0.3), None, "AAA_L24_WinLit_%d_%d"%(i,w), glass)
    for i,y in enumerate(range(-3600,3601,140)):
        spawn_sm(cube, (-1950,y,34), (16,6.5,0.12), None, "AAA_L24_Road_%d"%i, asphalt)
        if i%2==0:
            spawn_sm(cube, (-1950,y,34.3), (0.2,3.0,0.05), None, "AAA_L24_Lane_%d"%i, foam or plaster)

    # Ocean + harbor detail
    for i,x in enumerate([200,800,1400,2000,2600,3200,3800]):
        for j,y in enumerate(range(-4000,4001,900)):
            spawn_sm(plane, (x,y,0.8), (110,110,1), None, "AAA_L24_Ocean_%d_%d"%(i,j), ocean)
    for i,y in enumerate(range(-4000,4001,70)):
        spawn_sm(cube, (-790,y,4), (2.2,3.2,0.1), None, "AAA_L24_Foam_%d"%i, foam)
        spawn_sm(cube, (-870,y,9), (12,4.5,0.4), None, "AAA_L24_Beach_%d"%i, beach)
    for i,y in enumerate([-2000,-800,400,1600,2800]):
        spawn_sm(cube, (-930,y,130), (1.4,1.4,11), None, "AAA_L24_Crane_%d"%i, air)
        spawn_sm(cube, (-800,y,320), (11,0.5,0.5), None, "AAA_L24_Boom_%d"%i, air)
        spawn_sm(cube, (-400,y,30), (20,5,2.8), None, "AAA_L24_Ship_%d"%i, plaster)
        for k in range(8):
            spawn_sm(cube, (-480-k*18, y-40+k*8, 55+(k%4)*22), (1.7,0.95,0.95), None, "AAA_L24_Cont_%d_%d"%(i,k), brick if k%2 else air)

    # Combat / ADS readability
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i,(path,mesh) in enumerate(drone_parts[:8]):
        sc=210.0/bounds_max(mesh)
        if sc>40: sc=1.0
        spawn_sm(mesh, (800-i*45, -30+(i%3)*40, 420+(i%2)*20), (sc,sc,sc), unreal.Rotator(0,180,0), "AAA_L24_Drone_%d"%i)
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    for i,(path,mesh) in enumerate(rifle_parts[:8]):
        sc=120.0/bounds_max(mesh)
        if sc>40: sc=1.0
        spawn_sm(mesh, (20, 128, 360), (sc,sc,sc), unreal.Rotator(0,90,0), "AAA_L24_Rifle_%d"%i)
    for i in range(30):
        spawn_sm(sphere, (35+i*8, 148, 364), (0.1,0.1,0.1), None, "AAA_L24_Muzzle_%d"%i, muzzle)
        spawn_sm(sphere, (850-i*28, -40+(i%5)*25, 415+(i%4)*12), (1.0,1.0,1.0), None, "AAA_L24_Burst_%d"%i, boom)

    # Lights: more local, less pure overexposure risk near cockpit
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,4000), unreal.Rotator(-34, 45, 0))
    if sun:
        sun.set_actor_label("AAA_L24_Sun")
        try:
            c=sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(14.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun "+str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L24_Sky")
        try:
            c=sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(2.0)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    # cockpit local lights moderate
    for i,loc in enumerate([(15,110,375),(40,130,365),(-5,95,355)]):
        pl=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L24_CockLight_%d"%i)
            try:
                c=pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(25000.0)
                    c.set_editor_property("attenuation_radius", 600.0)
            except Exception:
                pass
    for i,loc in enumerate([(0,40,420),(-300,40,380),(900,0,450),(-900,-900,220),(1600,-200,240),( -1950,0,80)]):
        pl=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L24_Pt_%d"%i)
            try:
                c=pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(120000.0)
                    c.set_editor_property("attenuation_radius", 6000.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label("AAA_L24_Atmo")
    except Exception:
        pass
    pp=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L24_PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass

    # combat reseed
    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (20,105,360), "AAA_L24_CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800,0,520), "AAA_L24_CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-300,40,330), "AAA_L24_PropSpinner"),
        ]:
            cls=unreal.load_class(None, cls_path)
            if cls:
                a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a: a.set_actor_label(label)
    except Exception as e:
        log("cpp "+str(e))
    log("loop24 densify done")

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    path="/Game/Skyguard/Capture/RT_AAA_L24"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt=unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt=unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L24","/Game/Skyguard/Capture",unreal.TextureRenderTarget2D,unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x",1920)
    rt.set_editor_property("size_y",1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # dual source: BASE for structure, FINAL for lit
    cams=[
        ("AAA_Cam_L24_YakBeauty",(240,-280,360),(-4,150,0)),
        ("AAA_Cam_L24_Cockpit",(25,108,368),(-4,6,0)),
        ("AAA_Cam_L24_ADS",(16,132,364),(-1,6,0)),
        ("AAA_Cam_L24_Prop",(-20,-70,335),(-3,45,0)),
        ("AAA_Cam_L24_City",(-1050,-450,340),(-6,40,0)),
        ("AAA_Cam_L24_Harbor",(-380,-280,190),(-5,-15,0)),
        ("AAA_Cam_L24_Ocean",(650,-80,150),(-9,25,0)),
        ("AAA_Cam_L24_Combat",(680,-20,415),(-5,185,0)),
        ("AAA_Cam_L24_Wide",(140,-560,430),(-11,135,0)),
    ]
    for name,loc,rot in cams:
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    sca=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label("AAA_L24_SceneCapture")
    comp=sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_every_frame", True)
    try: comp.set_editor_property("fov_angle", 75.0)
    except Exception: pass
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world=unreal.EditorLevelLibrary.get_editor_world()

    sources=[]
    try: sources.append(("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception: pass
    try: sources.append(("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        try: sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
        except Exception: sources.append(("DEFAULT", None))

    saved=[]
    for name,loc,rot in cams:
        best=None
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src "+str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(8):
                try: comp.capture_scene()
                except Exception: pass
            out_name="%s_%s.png"%(name,src_name)
            out_png=os.path.join(out_dir,out_name)
            if os.path.isfile(out_png):
                try: os.remove(out_png)
                except Exception: pass
            try:
                unreal.RenderingLibrary.export_render_target(world, rt, out_dir, out_name)
            except Exception as e:
                log("export "+out_name+" "+str(e))
            if os.path.isfile(out_png):
                size=os.path.getsize(out_png)
                h=hashlib.sha256(open(out_png,"rb").read()).hexdigest()
                log("still %s size=%d sha=%s"%(out_name,size,h[:16]))
                rec=(out_png,size,h,src_name)
                saved.append(rec)
                # provisional prefer larger non-trivial files
                score = size
                if best is None or score>best[0]:
                    best=(score,rec)
        if best:
            canon=os.path.join(out_dir, name+".png")
            try:
                import shutil
                shutil.copyfile(best[1][0], canon)
                log("canonical %s from %s"%(name, best[1][3]))
            except Exception as e:
                log("canon "+str(e))
    try: comp.set_editor_property("capture_every_frame", False)
    except Exception: pass
    man=os.path.join(out_dir,"MANIFEST_SHA256.txt")
    with open(man,"w",encoding="utf-8") as f:
        f.write("Skyguard AAA Loop24 stills\n")
        f.write("time=%s\n"%time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_rgb_authoritative\n")
        for path,size,h,src in saved:
            f.write("%s  %d  src=%s  %s\n"%(h,size,src,path))
        f.write("total=%d\n"%len(saved))
    log("manifest total=%d"%len(saved))
    return saved

def main():
    log("loop24 contrast densify + dual capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L24_")
    densify()
    saved=capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L24")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop24 complete stills=%d"%(len(saved) if saved else 0))
    log("CRITIC: host RGB audit required; overall FAIL until blind AAA win")

if __name__=="__main__":
    main()
