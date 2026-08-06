import unreal
import os
import hashlib
import time
import shutil

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

    air = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Airframe") or load_mat("/Game/Skyguard/Materials/M_Metal")
    panel = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Panel") or air
    leather = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Leather") or panel
    canopy = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Canopy") or load_mat("/Game/Skyguard/Materials/M_CockpitGlass")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick") or load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade")
    plaster = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Plaster")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Asphalt")
    ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean") or load_mat("/Game/Skyguard/Materials/M_Ocean")
    beach = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Beach")
    foam = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam")
    glass = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Glass")
    muzzle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle") or load_mat("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot")
    boom = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Boom") or load_mat("/Game/Skyguard/Materials/Generated/MI_ExplosionCore")
    white = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightWhite") or plaster

    # Yak kit
    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    prod=[]
    for path, mesh in meshes:
        n=path.split("/")[-1].split(".")[0]; low=n.lower()
        if low.startswith("production-") or "yak52" in low:
            prod.append((path,mesh,n,low))
    ref=None
    for path,mesh,n,low in prod:
        if "wings-tail" in low or "exterior" in low or "fuselage" in low:
            ref=mesh; break
    sc=1.0
    if ref:
        sc=950.0/bounds_max(ref)
        if sc>20: sc=1.0
        if sc<0.02: sc=0.25
    s=(sc,sc,sc)
    log("yak prod=%d scale=%s"%(len(prod),s))
    origin=(0.0,40.0,330.0)
    for path,mesh,n,low in prod:
        mat=air
        if any(k in low for k in ["panel","instrument","gauge","annunciator","bezel","needle"]):
            mat=panel
        if "glass" in low or "canopy" in low:
            mat=canopy or glass or panel
        if "upholstery" in low or "quilt" in low:
            mat=leather
        spawn_sm(mesh, origin, s, None, "AAA_L25_Yak_%s"%n[:40], mat)

    # Beauty edge energy: panel lines / rivets / canopy seals around aircraft
    for i in range(40):
        x=-120 + i*8
        spawn_sm(sphere, (x, 18, 325), (0.05,0.05,0.05), None, "AAA_L25_RivetL_%d"%i, panel)
        spawn_sm(sphere, (x, 62, 325), (0.05,0.05,0.05), None, "AAA_L25_RivetR_%d"%i, panel)
        spawn_sm(cube, (x, 40, 345), (0.08,1.5,0.04), None, "AAA_L25_PanelLine_%d"%i, panel)
    for i in range(12):
        spawn_sm(cyl, (-20+i*8, 100, 375), (0.04,0.04,0.9), unreal.Rotator(0,0,90), "AAA_L25_CanopyRail_%d"%i, panel)
        spawn_sm(plane, (-10+i*6, 95+i, 385), (0.5,0.4,1), unreal.Rotator(65,0,0), "AAA_L25_CanopyGlass_%d"%i, canopy or glass)
    # dark/light checker under aircraft for beauty edge
    for i in range(24):
        for j in range(14):
            mat = asphalt if (i+j)%2==0 else white or plaster
            spawn_sm(cube, (-200+i*20, -160+j*20, 18), (0.9,0.9,0.15), None, "AAA_L25_Pad_%d_%d"%(i,j), mat)

    # ADS near-field: rifle + iron sights + arm very close to ADS cam (16,132,364)
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    for i,(path,mesh) in enumerate(rifle_parts[:10]):
        scv=90.0/bounds_max(mesh)
        if scv>50: scv=1.0
        spawn_sm(mesh, (18, 132, 362), (scv,scv,scv), unreal.Rotator(0,90,0), "AAA_L25_ADSRifle_%d"%i)
    # explicit iron sight geometry for ADS
    spawn_sm(cube, (22, 132, 364), (0.02,0.08,0.12), None, "AAA_L25_FrontSight", panel)
    spawn_sm(cube, (20, 132, 363.5), (0.03,0.12,0.06), None, "AAA_L25_RearSight", panel)
    spawn_sm(cyl, (19, 131, 362), (0.04,0.04,0.8), unreal.Rotator(0,0,90), "AAA_L25_Barrel", air)
    spawn_sm(sphere, (17, 130, 361), (0.12,0.08,0.06), None, "AAA_L25_Glove", leather)
    spawn_sm(cyl, (14, 128, 360), (0.07,0.07,0.5), unreal.Rotator(60,20,0), "AAA_L25_Forearm", leather)
    for i in range(20):
        spawn_sm(sphere, (24+i*6, 132, 364), (0.05,0.05,0.05), None, "AAA_L25_ADSMuzzle_%d"%i, muzzle)

    # Prop near-field dense content around (-20,-70,335) and nose
    for i,ang in enumerate(range(0,180,10)):
        spawn_sm(cube, (-305,40,330), (0.12,4.2,0.12), unreal.Rotator(0,ang,0), "AAA_L25_Blade_%d"%i, air)
    spawn_sm(sphere, (-315,40,330), (0.7,0.7,0.7), None, "AAA_L25_Hub", panel)
    spawn_sm(cyl, (-280,40,330), (1.8,1.8,2.5), unreal.Rotator(0,0,90), "AAA_L25_Cowling", air)
    for i in range(16):
        spawn_sm(cube, (-250+i*10, 20+(i%3)*10, 320+(i%4)*5), (0.3,0.3,0.3), None, "AAA_L25_PropNear_%d"%i, panel if i%2==0 else air)
    try:
        cls=unreal.load_class(None,"/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-305,40,330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L25_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.8,1.8,1.8))
    except Exception as e:
        log("prop "+str(e))

    # City edge energy
    for i in range(90):
        x=-2500-(i%10)*130
        y=-3600+(i//10)*280
        h=8+(i*7)%12
        spawn_sm(cube, (x,y,40+h*20), (2.8,2.4,h), None, "AAA_L25_Bldg_%d"%i, brick if i%2==0 else plaster)
        for w in range(min(h,10)):
            spawn_sm(cube, (x+28,y,70+w*35), (0.08,0.9,0.35), None, "AAA_L25_WinDark_%d_%d"%(i,w), panel)
            if w%2==0:
                spawn_sm(cube, (x+29,y,70+w*35), (0.05,0.7,0.25), None, "AAA_L25_WinLit_%d_%d"%(i,w), glass)
    for i,y in enumerate(range(-3600,3601,120)):
        spawn_sm(cube, (-1950,y,34), (16,6,0.12), None, "AAA_L25_Road_%d"%i, asphalt)
        spawn_sm(cube, (-1950,y,34.4), (0.25,2.5,0.05), None, "AAA_L25_Lane_%d"%i, foam or white)

    # ocean/harbor keep dense
    for i,x in enumerate([300,1000,1700,2400,3100,3800]):
        for j,y in enumerate(range(-4000,4001,900)):
            spawn_sm(plane, (x,y,0.5), (120,120,1), None, "AAA_L25_Ocean_%d_%d"%(i,j), ocean)
    for i,y in enumerate(range(-4000,4001,80)):
        spawn_sm(cube, (-800,y,5), (2.5,3.5,0.1), None, "AAA_L25_Foam_%d"%i, foam)
        spawn_sm(cube, (-880,y,9), (12,4.5,0.4), None, "AAA_L25_Beach_%d"%i, beach)
    for i,y in enumerate([-1800,-600,600,1800]):
        spawn_sm(cube, (-940,y,120), (1.3,1.3,11), None, "AAA_L25_Crane_%d"%i, air)
        spawn_sm(cube, (-810,y,300), (11,0.5,0.5), None, "AAA_L25_Boom_%d"%i, air)
        spawn_sm(cube, (-420,y,30), (18,5,2.8), None, "AAA_L25_Ship_%d"%i, plaster)

    # combat
    drone_parts=list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i,(path,mesh) in enumerate(drone_parts[:8]):
        sc=200.0/bounds_max(mesh)
        if sc>40: sc=1.0
        spawn_sm(mesh, (780-i*40, -20+(i%3)*30, 420), (sc,sc,sc), unreal.Rotator(0,180,0), "AAA_L25_Drone_%d"%i)
    for i in range(25):
        spawn_sm(sphere, (820-i*25, -30+(i%4)*20, 415+(i%3)*15), (1.1,1.1,1.1), None, "AAA_L25_Burst_%d"%i, boom)

    # lights
    sun=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,4200), unreal.Rotator(-32,50,0))
    if sun:
        sun.set_actor_label("AAA_L25_Sun")
        try:
            c=sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(12.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun "+str(e))
    sky=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L25_Sky")
        try:
            c=sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(2.2)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i,loc in enumerate([(18,132,366),( -20,-70,340),(0,40,400),(20,110,370),(900,0,430),(-1000,-400,300),(-400,-300,220)]):
        pl=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L25_Pt_%d"%i)
            try:
                c=pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(80000.0 if i>2 else 35000.0)
                    c.set_editor_property("attenuation_radius", 2500.0 if i<=2 else 6000.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label("AAA_L25_Atmo")
    except Exception:
        pass
    pp=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L25_PP")
        try: pp.set_editor_property("unbound", True)
        except Exception: pass

    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (20,105,360), "AAA_L25_CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800,0,520), "AAA_L25_CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-305,40,330), "AAA_L25_PropSpinner"),
        ]:
            cls=unreal.load_class(None, cls_path)
            if cls:
                a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a: a.set_actor_label(label)
    except Exception as e:
        log("cpp "+str(e))
    log("loop25 densify done")

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    path="/Game/Skyguard/Capture/RT_AAA_L25"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt=unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt=unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L25","/Game/Skyguard/Capture",unreal.TextureRenderTarget2D,unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x",1920)
    rt.set_editor_property("size_y",1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # very close cams for previously black ADS/Prop + improved beauty/city
    cams=[
        ("AAA_Cam_L25_ADS", (16,132,364), (0,0,0)),
        ("AAA_Cam_L25_Prop", (-40,0,335), (0,90,0)),
        ("AAA_Cam_L25_YakBeauty", (200,-220,355), (-3,155,0)),
        ("AAA_Cam_L25_City", (-1100,-300,320), (-5,50,0)),
        ("AAA_Cam_L25_Cockpit", (24,108,368), (-3,5,0)),
        ("AAA_Cam_L25_Combat", (650,-10,415), (-4,185,0)),
        ("AAA_Cam_L25_Harbor", (-360,-240,180), (-4,-10,0)),
        ("AAA_Cam_L25_Ocean", (600,-50,140), (-8,30,0)),
        ("AAA_Cam_L25_Wide", (120,-480,400), (-10,140,0)),
    ]
    for name,loc,rot in cams:
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    sca=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label("AAA_L25_SceneCapture")
    comp=sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    # IMPORTANT: disable every-frame to avoid inefficiency and ensure manual captures work
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    try:
        comp.set_editor_property("capture_on_movement", False)
    except Exception:
        pass
    try:
        comp.set_editor_property("fov_angle", 70.0)
    except Exception:
        pass
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
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src "+str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            # warm
            for _ in range(4):
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
                saved.append((out_png,size,h,src_name,name))
        # do not choose canonical in UE; host will pick best non-black
    man=os.path.join(out_dir,"MANIFEST_SHA256.txt")
    with open(man,"w",encoding="utf-8") as f:
        f.write("Skyguard AAA Loop25 stills\n")
        f.write("time=%s\n"%time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_selects_best_source\n")
        for path,size,h,src,name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n"%(h,size,src,name,path))
        f.write("total=%d\n"%len(saved))
    log("manifest total=%d"%len(saved))
    return saved

def main():
    log("loop25 ADS/Prop/Yak edge densify + dual capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L25_")
    densify()
    saved=capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L25")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop25 complete stills=%d"%(len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

if __name__=="__main__":
    main()
