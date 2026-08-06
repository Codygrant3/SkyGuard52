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

def main():
    raise RuntimeError(
        "DEPRECATED_FAIL_CLOSED: this legacy Loop10 script targets the quarantined "
        "/Game/Skyguard/Audio/Imported bank. Use the governed Phase 5 production "
        "audio pipeline and PHASE5_AUTHENTIC_AUDIO_UNREAL_IMPORT_MIX_RUNBOOK.md."
    )
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L10A_")
    # List imported audio
    assets = []
    try:
        assets = unreal.EditorAssetLibrary.list_assets("/Game/Skyguard/Audio/Imported", True, False)
    except Exception as e:
        log("list audio " + str(e))
    log("audio assets=" + str(len(assets)))
    for a in assets:
        log(" audio " + a)

    # Place ambient audio actors near propeller / city / combat
    # AmbientSound class if available
    placed = 0
    try:
        cls = getattr(unreal, "AmbientSound", None)
        if cls:
            spots = [
                ("AAA_L10A_PropLoop", (0, -500, 320)),
                ("AAA_L10A_CityAmb", (-1900, 0, 50)),
                ("AAA_L10A_HarborAmb", (-400, -1000, 40)),
                ("AAA_L10A_CombatAmb", (2500, 0, 400)),
            ]
            for label, loc in spots:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
                    placed += 1
        else:
            log("AmbientSound class missing")
    except Exception as e:
        log("ambient " + str(e))

    # Also create Sound Cues / MetaSound placeholders note via text asset folder
    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Skyguard/Audio/Cues"):
        unreal.EditorAssetLibrary.make_directory("/Game/Skyguard/Audio/Cues")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop10 audio staging complete placedAmbient=" + str(placed))
    log("CRITIC: audio still FAIL until sounds bound to fire/explosion gameplay events")

if __name__ == "__main__":
    main()
