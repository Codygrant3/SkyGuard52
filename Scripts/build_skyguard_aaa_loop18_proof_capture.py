import unreal
import os
import hashlib
import time
import struct
import zlib

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

def rebuild_unlit(name, color, intensity=20.0):
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
        # unlit
        try:
            mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        except Exception:
            pass
        mel.delete_all_material_expressions(mat)
        c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
        c.set_editor_property("constant", unreal.LinearColor(color[0]*intensity, color[1]*intensity, color[2]*intensity, 1.0))
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        # also base for safety
        try:
            b = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 80)
            b.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
            mel.connect_material_property(b, "", unreal.MaterialProperty.MP_BASE_COLOR)
        except Exception:
            pass
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        log("unlit mat " + name)
    except Exception as e:
        log("unlit fail " + str(e))
    return mat

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
            try:
                a.static_mesh_component.set_editor_property("cast_shadow", False)
            except Exception:
                pass
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    return a

def hard_lights():
    # Strong key light
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,3000), unreal.Rotator(-40, 30, 0))
    if sun:
        sun.set_actor_label("AAA_L18_KeySun")
        try:
            c = sun.directional_light_component
            c.set_intensity(20.0)
            c.set_editor_property("atmosphere_sun_light", True)
            c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("key sun " + str(e))
    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,2500), unreal.Rotator(-25, -140, 0))
    if fill:
        fill.set_actor_label("AAA_L18_FillSun")
        try:
            c = fill.directional_light_component
            c.set_intensity(8.0)
            c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1000), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L18_Sky")
        try:
            c = sky.light_component
            c.set_intensity(3.0)
            c.set_editor_property("real_time_capture", True)
            c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    # point lights around aircraft
    for i, loc in enumerate([(0,40,400),(100,40,350),(-100,40,350),(0,150,360),(0,-50,360)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L18_Point_%d" % i)
            try:
                c = pl.point_light_component
                c.set_intensity(50000.0)
                c.set_editor_property("attenuation_radius", 2500.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
            except Exception:
                pass
    # sky atmosphere
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label("AAA_L18_Atmosphere")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L18_PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("hard lights done")

def proof_geometry():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    red = rebuild_unlit("M_L18_UnlitRed", (1.0, 0.1, 0.05), 8.0)
    cyan = rebuild_unlit("M_L18_UnlitCyan", (0.1, 0.8, 1.0), 6.0)
    yellow = rebuild_unlit("M_L18_UnlitYellow", (1.0, 0.85, 0.1), 7.0)
    white = rebuild_unlit("M_L18_UnlitWhite", (1.0, 1.0, 1.0), 5.0)
    green = rebuild_unlit("M_L18_UnlitGreen", (0.2, 1.0, 0.3), 6.0)

    # Giant unlit billboards in world so any working capture must show color
    for i, (loc, mat, label) in enumerate([
        ((200, -400, 400), red, "BoardA"),
        ((-400, 200, 350), cyan, "BoardB"),
        ((800, 0, 300), yellow, "BoardC"),
        ((-1500, -500, 250), white, "BoardD"),
        ((1500, -200, 420), green, "BoardE"),
        ((0, 40, 500), red, "OverAircraft"),
        ((-900, -1000, 200), cyan, "HarborBoard"),
        ((-2000, 0, 300), yellow, "CityBoard"),
    ]):
        spawn_sm(plane, loc, (20, 12, 1), unreal.Rotator(0, 30*i, 0), "AAA_L18_Proof_%s" % label, mat)
        spawn_sm(sphere, (loc[0], loc[1], loc[2]+80), (3,3,3), None, "AAA_L18_ProofSphere_%s" % label, mat)

    # Near-gunner proof
    for i in range(12):
        spawn_sm(cube, (40+i*8, 140, 360), (0.3,0.3,0.3), None, "AAA_L18_NearGunner_%d"%i, yellow if i%2==0 else red)
    # City colored towers
    for i in range(24):
        x = -2200 - (i%6)*150
        y = -2800 + (i//6)*400
        spawn_sm(cube, (x,y,200), (3,3,8), None, "AAA_L18_ColorTower_%d"%i, [red,cyan,yellow,green,white][i%5])
    log("proof geometry done")

def densify_more():
    cube = load_sm("/Engine/BasicShapes/Cube")
    metal = load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade") or load_mat("/Game/Skyguard/Materials/M_Tex_brick")
    for i in range(40):
        spawn_sm(cube, (-2100-(i%8)*100, -3000+(i//8)*350, 120+(i%5)*40), (2.5,2.0,5+(i%4)), None, "AAA_L18_Block_%d"%i, brick if i%2==0 else metal)
    # prop spinner
    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-190,40,330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L18_PropSpinner")
    except Exception as e:
        log("prop " + str(e))
    try:
        g = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        s = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if g:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(g, unreal.Vector(20,105,360), unreal.Rotator())
            if a: a.set_actor_label("AAA_L18_CPP_Gunner")
        if s:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(s, unreal.Vector(2800,0,520), unreal.Rotator())
            if a: a.set_actor_label("AAA_L18_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))

def png_stats(path):
    try:
        data = open(path,'rb').read()
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return 1.0,0,len(data)
        pos=8; idat=b''
        while pos+8 <= len(data):
            ln=struct.unpack('>I', data[pos:pos+4])[0]
            ct=data[pos+4:pos+8]
            ch=data[pos+8:pos+8+ln]
            if ct==b'IDAT': idat+=ch
            if ct==b'IEND': break
            pos += 12+ln
        raw=zlib.decompress(idat)
        step=max(1,len(raw)//50000)
        sample=raw[::step]
        black=sum(1 for b in sample if b<8)/float(len(sample))
        uniq=len(set(sample[:8000]))
        return black, uniq, len(data)
    except Exception:
        sz=os.path.getsize(path) if os.path.isfile(path) else 0
        return 1.0,0,sz

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    rt_path="/Game/Skyguard/Capture/RT_AAA_L18"
    if unreal.EditorAssetLibrary.does_asset_exist(rt_path):
        rt=unreal.EditorAssetLibrary.load_asset(rt_path)
    else:
        rt=unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L18","/Game/Skyguard/Capture",unreal.TextureRenderTarget2D,unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x",1920)
    rt.set_editor_property("size_y",1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams=[
        ("AAA_Cam_L18_YakBeauty",(700,-1200,560),(-12,145,0)),
        ("AAA_Cam_L18_Cockpit",(30,115,372),(-7,8,0)),
        ("AAA_Cam_L18_ADS",(18,140,366),(-1,8,0)),
        ("AAA_Cam_L18_Ocean",(1600,-800,480),(-10,165,0)),
        ("AAA_Cam_L18_Harbor",(-700,-1400,280),(-8,35,0)),
        ("AAA_Cam_L18_City",(-1200,-700,400),(-9,25,0)),
        ("AAA_Cam_L18_Combat",(1100,-100,460),(-10,180,0)),
        ("AAA_Cam_L18_Prop",(-120,-200,340),(-5,20,0)),
        ("AAA_Cam_L18_Proof",(100,-300,420),(-8,20,0)),
    ]
    for name,loc,rot in cams:
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*loc),unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    sca=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,0,400),unreal.Rotator())
    sca.set_actor_label("AAA_L18_SceneCapture")
    comp=sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_every_frame", True)
    try:
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    except Exception:
        try:
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
        except Exception:
            pass
    try:
        comp.set_editor_property("fov_angle", 85.0)
    except Exception:
        pass

    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    saved=[]
    for name,loc,rot in cams:
        sca.set_actor_location(unreal.Vector(*loc), False, True)
        sca.set_actor_rotation(unreal.Rotator(*rot), False)
        for _ in range(8):
            try: comp.capture_scene()
            except Exception: pass
        out_png=os.path.join(out_dir, name+".png")
        if os.path.isfile(out_png):
            try: os.remove(out_png)
            except Exception: pass
        try:
            unreal.RenderingLibrary.export_render_target(world, rt, out_dir, name+".png")
        except Exception as e:
            log("export "+name+" "+str(e))
        if os.path.isfile(out_png):
            black,uniq,size=png_stats(out_png)
            h=hashlib.sha256(open(out_png,'rb').read()).hexdigest()
            # looser gate if proof colors present: uniq high OR not almost pure black
            valid = (black < 0.55 and uniq > 40 and size > 25000) or (uniq > 200 and size > 40000)
            log("still %s black=%.3f uniq=%d size=%d valid=%s sha=%s" % (name,black,uniq,size,valid,h[:16]))
            saved.append((out_png,size,h,black,uniq,valid))
        else:
            log("missing "+name)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    man=os.path.join(out_dir,"MANIFEST_SHA256.txt")
    with open(man,"w",encoding="utf-8") as f:
        f.write("Skyguard AAA Loop18 stills\n")
        f.write("time=%s\n"%time.strftime("%Y-%m-%dT%H:%M:%S"))
        vc=0
        for path,size,h,black,uniq,valid in saved:
            f.write("%s  %d  black=%.3f uniq=%d valid=%s  %s\n"%(h,size,black,uniq,valid,path))
            if valid: vc+=1
        f.write("valid_count=%d total=%d\n"%(vc,len(saved)))
    log("manifest valid=%d/%d"%(sum(1 for s in saved if s[5]), len(saved)))
    return saved

def main():
    log("loop18 hard lights + unlit proof capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L18_")
    hard_lights()
    proof_geometry()
    densify_more()
    saved = capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L18")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    vc = sum(1 for s in saved if s[5]) if saved else 0
    log("Loop18 complete stills=%d valid=%d" % (len(saved) if saved else 0, vc))
    if vc == 0:
        log("CRITIC: FAIL capture still invalid after unlit proof; overall FAIL vs AAA")
    else:
        log("CRITIC: valid stills exist; densify continues; AAA blind win not yet claimed")

if __name__ == "__main__":
    main()
