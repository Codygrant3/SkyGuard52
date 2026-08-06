import unreal

def log(m):
    unreal.log(f"[SkyguardAAA] {m}")

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20,95,360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_Play_GunnerStart")
    existing=set()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            existing.add(a.get_actor_label())
        except Exception:
            pass
    cams=[("AAA_Cam_Cockpit",(25,95,368),(-8,5,0)),("AAA_Cam_ADS",(18,110,362),(-3,8,0)),("AAA_Cam_CityInbound",(2500,200,700),(-15,-175,0)),("AAA_Cam_CoastWide",(800,-2200,900),(-20,50,0)),("AAA_Cam_ExteriorChase",(600,-900,520),(-12,130,0))]
    for name,loc,rot in cams:
        if name in existing:
            continue
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
    unreal.EditorLevelLibrary.save_current_level()
    log("play anchors updated")

if __name__ == "__main__":
    main()
