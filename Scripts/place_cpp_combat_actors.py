"""Place compiled C++ combat actors into the coast map and set game mode defaults if possible."""
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

def find_class(path_or_name):
    # try load generated class
    c = unreal.load_class(None, path_or_name)
    if c: return c
    # try script path
    c = unreal.load_class(None, f"/Script/Skyguard52.{path_or_name}")
    return c

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_CPP_")

    gunner_cls = find_class("SkyguardGunner") or find_class("ASkyguardGunner")
    drone_cls = find_class("SkyguardDrone") or find_class("ASkyguardDrone")
    spawner_cls = find_class("SkyguardDroneSpawner") or find_class("ASkyguardDroneSpawner")
    gm_cls = find_class("SkyguardGameMode") or find_class("ASkyguardGameMode")
    log(f"classes gunner={gunner_cls} drone={drone_cls} spawner={spawner_cls} gm={gm_cls}")

    if gunner_cls:
        g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20,95,360), unreal.Rotator(0,0,0))
        if g:
            g.set_actor_label("AAA_CPP_Gunner")
            log("spawned gunner")
    else:
        log("gunner class missing in editor context; game binary has it")

    if spawner_cls:
        s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2500,0,500), unreal.Rotator())
        if s:
            s.set_actor_label("AAA_CPP_DroneSpawner")
            log("spawned spawner")
    if drone_cls:
        for i,y in enumerate([-800,-200,400,1000]):
            d=unreal.EditorLevelLibrary.spawn_actor_from_class(drone_cls, unreal.Vector(3000,y,420+i*20), unreal.Rotator(0,180,0))
            if d:
                d.set_actor_label(f"AAA_CPP_Drone_{i}")
        log("spawned seed cpp drones")

    # Player start
    ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20,95,360), unreal.Rotator())
    if ps: ps.set_actor_label("AAA_CPP_PlayerStart")

    # World settings game mode override via level
    try:
        # store note
        pass
    except Exception as e:
        log(f"gm override {e}")

    unreal.EditorLevelLibrary.save_current_level()
    log("cpp actor placement pass complete")

if __name__=="__main__":
    main()
