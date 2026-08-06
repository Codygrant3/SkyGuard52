import unreal
from pathlib import Path

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def import_file(src_abs, dest_path, dest_name=None):
    src = Path(src_abs)
    if not src.exists():
        log("missing " + src_abs)
        return None
    name = dest_name or src.stem
    full = dest_path + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = str(src)
    task.destination_path = dest_path
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        a = unreal.EditorAssetLibrary.load_asset(full)
        log("imported " + full + " => " + str(type(a)))
        return a
    # search
    for a in unreal.EditorAssetLibrary.list_assets(dest_path, True, False):
        if name.lower() in a.lower():
            asset = unreal.EditorAssetLibrary.load_asset(a)
            log("imported-found " + a)
            return asset
    log("import failed " + src_abs)
    return None

def main():
    raise RuntimeError(
        "DEPRECATED_FAIL_CLOSED: this legacy web-game importer would recreate the "
        "quarantined /Game/Skyguard/Audio/Imported bank from loose OGG files. Use "
        "the governed Phase 5 production audio acquisition/import pipeline."
    )
    log("loop10 webgame import start")
    ensure_dir("/Game/Skyguard/Meshes/WebGame")
    ensure_dir("/Game/Skyguard/Audio/Imported")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    model_dir = proj + "Skyguard/Meshes/Source/webgame/"
    audio_dir = proj + "Skyguard/Audio/Source/"

    models = [
        "yak52-detail-kit.glb",
        "skyguard-rifle.glb",
        "skyguard-drone.glb",
        "skyguard-interceptor.glb",
        "skyguard-occupant.glb",
    ]
    for m in models:
        import_file(model_dir + m, "/Game/Skyguard/Meshes/WebGame")

    # import all oggs
    audio_path = Path(audio_dir)
    if audio_path.exists():
        for f in sorted(audio_path.glob("*.ogg")):
            import_file(str(f), "/Game/Skyguard/Audio/Imported")

    # also import procedural extras
    proc = proj + "Skyguard/Meshes/Source/procedural/"
    for n in ["instrument_cluster_proxy", "city_bus_proxy", "seawall_proxy"]:
        import_file(proc + n + ".obj", "/Game/Skyguard/Meshes/Hero", n)

    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("loop10 webgame import complete")
    # list results
    for p in ["/Game/Skyguard/Meshes/WebGame", "/Game/Skyguard/Audio/Imported"]:
        assets = unreal.EditorAssetLibrary.list_assets(p, True, False)
        log(p + " count=" + str(len(assets)))
        for a in assets[:30]:
            log("  " + a)

if __name__ == "__main__":
    main()
