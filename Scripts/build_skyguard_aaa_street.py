"""Create high density set dressing + more cinematic cameras for critic stills."""
import unreal

def log(m): unreal.log(f"[SkyguardAAA] {m}")

def clear_prefix(prefix):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            n=a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def mesh(p): return unreal.EditorAssetLibrary.load_asset(p)
def mat(p): return unreal.EditorAssetLibrary.load_asset(p)

def sm(m, loc, scale=None, rot=None, label=None, material=None):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a: return None
    c=a.static_mesh_component
    c.set_static_mesh(m)
    if scale: a.set_actor_scale3d(unreal.Vector(*scale))
    if label: a.set_actor_label(label)
    if material: c.set_material(0, material)
    return a

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_Street_")
    cube=mesh("/Engine/BasicShapes/Cube")
    cyl=mesh("/Engine/BasicShapes/Cylinder")
    sphere=mesh("/Engine/BasicShapes/Sphere")
    asphalt=mat("/Game/Skyguard/Materials/M_Tex_concrete") or mat("/Game/Skyguard/Materials/M_CityConcrete")
    metal=mat("/Game/Skyguard/Materials/M_Tex_metal") or mat("/Game/Skyguard/Materials/M_MetalRust")
    glass=mat("/Game/Skyguard/Materials/M_CityGlass")
    # cars as simple proxies along road
    for i in range(50):
        y=-2400 + i*100
        sm(cube, (-1180, y, 45), (1.8,0.8,0.55), None, f"AAA_Street_Car_{i}", metal)
        if i%2==0:
            sm(cube, (-1180, y, 62), (1.2,0.75,0.35), None, f"AAA_Street_CarCabin_{i}", glass)
    # street lamps
    for i in range(35):
        y=-2300 + i*140
        sm(cyl, (-1220, y, 90), (0.08,0.08,2.5), None, f"AAA_Street_Lamp_{i}", metal)
        sm(sphere, (-1220, y, 160), (0.2,0.2,0.2), None, f"AAA_Street_LampHead_{i}", glass)
    # additional coastal rocks
    for i in range(40):
        y=-2300 + i*120
        sm(sphere, (-900, y, 20), (0.6+(i%3)*0.2, 0.8, 0.35), None, f"AAA_Street_Rock_{i}", asphalt)
    unreal.EditorLevelLibrary.save_current_level()
    log("street densification complete")
    log("CRITIC still FAIL AAA: primitives + textures only")

if __name__=="__main__":
    main()
