import unreal
import os
import hashlib
import time
import struct
import zlib
from collections import Counter

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

def densify_failed_frustums():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    air = load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    ocean = load_mat("/Game/Skyguard/Materials/M_Ocean")
    deep = load_mat("/Game/Skyguard/Materials/M_OceanDeep")
    beach = load_mat("/Game/Skyguard/Materials/M_Beach")
    foam = load_mat("/Game/Skyguard/Materials/M_L5_SeaFoam")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade") or load_mat("/Game/Skyguard/Materials/M_Tex_brick")
    concrete = load_mat("/Game/Skyguard/Materials/Generated/M_ConcreteWall") or load_mat("/Game/Skyguard/Materials/M_CityConcrete")
    glass = load_mat("/Game/Skyguard/Materials/M_CityGlass")
    prop = load_mat("/Game/Skyguard/Materials/M_PropDisc") or air

    # Yak beauty frustum fill around (0,40,330) facing from (650,-1100,520)
    spawn_sm(cyl, (0,40,330), (1.4,1.4,9.0), unreal.Rotator(0,0,90), "AAA_L20_YakFuse", air)
    spawn_sm(cube, (0,40,325), (12,1.8,0.18), None, "AAA_L20_YakWing", air)
    spawn_sm(cube, (300,40,370), (0.2,1.4,2.2), None, "AAA_L20_YakFin", air)
    spawn_sm(sphere, (-240,40,330), (1.8,1.8,1.8), None, "AAA_L20_YakNose", air)
    for i,ang in enumerate(range(0,180,30)):
        spawn_sm(cube, (-270,40,330), (0.12,3.5,0.08), unreal.Rotator(0,ang,0), "AAA_L20_Blade_%d"%i, prop)
    # bright ground checker under aircraft for beauty cam floor read
    for i in range(20):
        for j in range(12):
            mat = concrete if (i+j)%2==0 else brick
            spawn_sm(cube, (-200+i*40, -200+j*40, 20), (1.8,1.8,0.2), None, "AAA_L20_Pad_%d_%d"%(i,j), mat)

    # Ocean frustum: large bright planes + foam near harbor cams
    for i,x in enumerate([0,800,1600,2400,3200,4000]):
        for j,y in enumerate(range(-5200,5201,1800)):
            spawn_sm(plane, (x,y,0.5), (140,140,1), None, "AAA_L20_Ocean_%d_%d"%(i,j), ocean if x<2000 else deep)
    for i,y in enumerate(range(-4800,4801,90)):
        spawn_sm(cube, (-780,y,4), (3,4,0.08), None, "AAA_L20_Foam_%d"%i, foam)
        spawn_sm(cube, (-860,y,8), (10,4.5,0.35), None, "AAA_L20_Beach_%d"%i, beach)

    # Harbor densify in failed harbor frustum
    for i,y in enumerate([-2000,-1000,0,1000,2000]):
        spawn_sm(cube, (-920,y,100), (1.2,1.2,10), None, "AAA_L20_CraneM_%d"%i, air)
        spawn_sm(cube, (-820,y,280), (9,0.5,0.5), None, "AAA_L20_CraneB_%d"%i, air)
        spawn_sm(cube, (-450,y,30), (18,4.5,2.5), None, "AAA_L20_Ship_%d"%i, concrete)
        for k in range(6):
            spawn_sm(cube, (-500-k*20, y-30+k*10, 50+(k%3)*25), (1.6,0.9,0.9), None, "AAA_L20_Cont_%d_%d"%(i,k), brick if k%2 else air)

    # Wide cam skyline reinforcement
    for i in range(40):
        spawn_sm(cube, (-2400-(i%8)*160, -3000+(i//8)*450, 200+(i%7)*60), (3.5,3.0,8+(i%6)), None, "AAA_L20_Skyline_%d"%i, brick if i%2 else concrete)
        spawn_sm(cube, (-2360-(i%8)*160, -3000+(i//8)*450, 260+(i%5)*50), (0.1,2.2,0.6), None, "AAA_L20_SkyWin_%d"%i, glass)

    # lights hard
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,3500), unreal.Rotator(-42,35,0))
    if sun:
        sun.set_actor_label("AAA_L20_Sun")
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1400), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L20_Sky")
    for i,loc in enumerate([(0,40,450),(-200,40,400),(200,100,380),(-900,-1000,200),(1500,0,300)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L20_Pt_%d"%i)
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label("AAA_L20_Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L20_PP")
        try: pp.set_editor_property("unbound", True)
        except Exception: pass

    # combat reseed
    try:
        g=unreal.load_class(None,"/Script/Skyguard52.SkyguardGunner")
        s=unreal.load_class(None,"/Script/Skyguard52.SkyguardDroneSpawner")
        if g:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(g,unreal.Vector(20,105,360),unreal.Rotator())
            if a: a.set_actor_label("AAA_L20_CPP_Gunner")
        if s:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(s,unreal.Vector(2800,0,520),unreal.Rotator())
            if a: a.set_actor_label("AAA_L20_CPP_Spawner")
        pcls=unreal.load_class(None,"/Script/Skyguard52.SkyguardPropSpinner")
        if pcls:
            a=unreal.EditorLevelLibrary.spawn_actor_from_class(pcls,unreal.Vector(-270,40,330),unreal.Rotator())
            if a: a.set_actor_label("AAA_L20_PropSpinner")
    except Exception as e:
        log("cpp "+str(e))
    log("failed-frustum densify done")

def png_rgb_stats(path):
    # Prefer approximate RGB stats via raw decode when possible
    try:
        from PIL import Image
        im = Image.open(path).convert('RGB')
        px = list(im.getdata())
        step = max(1, len(px)//25000)
        sample = px[::step]
        black = sum(1 for c in sample if c[0]<8 and c[1]<8 and c[2]<8)/float(len(sample))
        uniq = len(set(sample))
        # edge
        small = im.resize((64,36))
        s=list(small.getdata()); diffs=[]
        for y in range(36):
            for x in range(63):
                a=s[y*64+x]; b=s[y*64+x+1]
                diffs.append(abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2]))
        edge = sum(diffs)/float(len(diffs)) if diffs else 0
        return black, uniq, os.path.getsize(path), edge
    except Exception:
        # fallback zlib
        try:
            data=open(path,'rb').read(); pos=8; idat=b''
            while pos+8<=len(data):
                ln=struct.unpack('>I',data[pos:pos+4])[0]; ct=data[pos+4:pos+8]; ch=data[pos+8:pos+8+ln]
                if ct==b'IDAT': idat+=ch
                if ct==b'IEND': break
                pos+=12+ln
            raw=zlib.decompress(idat); step=max(1,len(raw)//50000); sample=raw[::step]
            black=sum(1 for b in sample if b<8)/float(len(sample)); uniq=len(set(sample[:8000]))
            return black, uniq, os.path.getsize(path), 0.0
        except Exception:
            return 1.0,0,os.path.getsize(path) if os.path.isfile(path) else 0,0.0

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    path="/Game/Skyguard/Capture/RT_AAA_L20"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt=unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt=unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L20","/Game/Skyguard/Capture",unreal.TextureRenderTarget2D,unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x",1920); rt.set_editor_property("size_y",1080)
    try: rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception: pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams=[
        ("AAA_Cam_L20_YakBeauty",(620,-1050,500),(-10,138,0)),
        ("AAA_Cam_L20_Ocean",(1800,-900,420),(-8,170,0)),
        ("AAA_Cam_L20_Harbor",(-650,-1300,260),(-7,30,0)),
        ("AAA_Cam_L20_Wide",(500,-1700,750),(-16,125,0)),
        ("AAA_Cam_L20_City",(-1200,-700,400),(-8,25,0)),
        ("AAA_Cam_L20_Cockpit",(30,115,372),(-6,8,0)),
        ("AAA_Cam_L20_Prop",(-80,-180,340),(-4,25,0)),
        ("AAA_Cam_L20_Combat",(1000,-80,450),(-9,185,0)),
    ]
    for name,loc,rot in cams:
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*loc),unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    sca=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,0,400),unreal.Rotator())
    sca.set_actor_label("AAA_L20_SceneCapture")
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
    try: comp.set_editor_property("fov_angle", 78.0)
    except Exception: pass
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world=unreal.EditorLevelLibrary.get_editor_world()

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
            black,uniq,size,edge=png_rgb_stats(out_png)
            h=hashlib.sha256(open(out_png,'rb').read()).hexdigest()
            valid = (black < 0.55 and uniq > 200 and edge > 4.0 and size > 80000) or (black < 0.25 and uniq > 1000)
            log("still %s black=%.3f uniq=%d edge=%.1f size=%d valid=%s"%(name,black,uniq,edge,size,valid))
            saved.append((out_png,size,h,black,uniq,edge,valid))
        else:
            log("missing "+name)
    try: comp.set_editor_property("capture_every_frame", False)
    except Exception: pass
    man=os.path.join(out_dir,"MANIFEST_SHA256.txt")
    with open(man,"w",encoding="utf-8") as f:
        f.write("Skyguard AAA Loop20 stills\n")
        f.write("time=%s\n"%time.strftime("%Y-%m-%dT%H:%M:%S"))
        vc=0
        for path,size,h,black,uniq,edge,valid in saved:
            f.write("%s  %d  black=%.3f uniq=%d edge=%.1f valid=%s  %s\n"%(h,size,black,uniq,edge,valid,path))
            if valid: vc+=1
        f.write("valid_count=%d total=%d\n"%(vc,len(saved)))
    log("manifest valid=%d/%d"%(sum(1 for s in saved if s[6]), len(saved)))
    return saved

def main():
    log("loop20 frustum densify + RGB-gated capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L20_")
    densify_failed_frustums()
    saved=capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L20")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    vc=sum(1 for s in saved if s[6]) if saved else 0
    log("Loop20 complete stills=%d valid=%d"%(len(saved) if saved else 0, vc))
    if vc==0:
        log("CRITIC: FAIL; stills still not usable for AAA blind win")
    else:
        log("CRITIC: valid stills present; require harsh blind vs refs before any complete claim")

if __name__=="__main__":
    main()
