import unreal

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

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def spawn_sm(mesh, loc, scale=None, rot=None, label=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    if scale:
        a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    return a

def main():
    raise RuntimeError(
        "DEPRECATED_FAIL_CLOSED: this legacy placement script binds quarantined "
        "/Game/Skyguard/Audio/Imported assets. Use the Phase 5 production bank and "
        "serialized MetaSound routing after authentic-source approval."
    )
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L10W_")

    # Known imported static meshes from webgame glbs
    rifle_parts = [
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-gunmetal",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-matteBlack",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fdeDark",
    ]
    drone_parts = [
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body",
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-wing",
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-fins",
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-motor",
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-prop",
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/armor-stripe",
    ]
    igla_parts = [
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-tube",
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-grip",
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-sight",
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-control",
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/interceptor-missile-body_001",
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/interceptor-missile-fins_001",
    ]
    occupant_parts = [
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-olive",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-leather",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-seat",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-webbing",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-matteBlack",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-oliveDark",
    ]

    # Assemble rifle at gunner hands
    base = unreal.Vector(18, 118, 358)
    for i, p in enumerate(rifle_parts):
        m = load_sm(p)
        spawn_sm(m, (base.x, base.y, base.z), (100, 100, 100), unreal.Rotator(0, 10, 0), "AAA_L10W_RiflePart_%d" % i)
        log("rifle part %s => %s" % (p, bool(m)))

    # Occupant in cockpit
    for i, p in enumerate(occupant_parts):
        m = load_sm(p)
        spawn_sm(m, (0, 70, 350), (100, 100, 100), None, "AAA_L10W_Occupant_%d" % i)
        log("occupant %s => %s" % (p, bool(m)))

    # Igla on left rail
    for i, p in enumerate(igla_parts):
        m = load_sm(p)
        spawn_sm(m, (-34, 95, 350), (100, 100, 100), unreal.Rotator(0, -8, 5), "AAA_L10W_Igla_%d" % i)
        log("igla %s => %s" % (p, bool(m)))

    # Drone swarm using real drone parts (body+wing at least)
    body = load_sm(drone_parts[0])
    wing = load_sm(drone_parts[1])
    for lane, y in enumerate([-2000, -800, 400, 1600]):
        for n in range(6):
            x = 2600 + n * 450
            z = 380 + (n % 3) * 40
            spawn_sm(body, (x, y, z), (120, 120, 120), unreal.Rotator(0, 180, 0), "AAA_L10W_DroneBody_%d_%d" % (lane, n))
            spawn_sm(wing, (x, y, z), (120, 120, 120), unreal.Rotator(0, 180, 0), "AAA_L10W_DroneWing_%d_%d" % (lane, n))

    # Ambient audio actors already placed; attach sound waves if API allows via AudioComponent on AmbientSound
    try:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            n = a.get_actor_label() or ""
            if not n.startswith("AAA_L10A_"):
                continue
            # best effort: set sound on ambient
            sound = None
            if "Prop" in n:
                sound = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Audio/Imported/aircraft-propeller-texture-loop")
            elif "Combat" in n:
                sound = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Audio/Imported/explosion-distant-01")
            if sound:
                try:
                    # AmbientSound has audio component
                    ac = a.get_component_by_class(unreal.AudioComponent)
                    if ac:
                        ac.set_sound(sound)
                        ac.set_editor_property("bAutoActivate", True)
                        log("bound sound on " + n)
                except Exception as e:
                    log("bind fail " + n + " " + str(e))
    except Exception as e:
        log("audio bind " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop10 web static placement complete")
    log("CRITIC: hero mesh quality improved with webgame assets; still FAIL vs AAA Fab/Megascans grade")

if __name__ == "__main__":
    main()
