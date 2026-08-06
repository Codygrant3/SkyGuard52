"""Import the L88 Yak blockout and stage a clean Unreal validation map.

This is a bounded import probe, not production-art promotion. It deliberately
keeps the rejected web GLBs and the Loop86 world out of the new map so the
aircraft envelope/cockpit can be judged in isolation.
"""

import os
import unreal


PROJECT_ROOT = "/Game/Skyguard"
# Use a fresh map revision for the L88 gate. The original validation map was
# saved while an earlier GLB still contained GEO_PropBlade_B; Unreal retained
# that missing package dependency even after the actor was cleared. A new
# asset path keeps the validation map self-contained and reproducible.
MAP_PATH = PROJECT_ROOT + "/Maps/Lvl_Yak52_L88_Validation_v2"
DEST_PATH = PROJECT_ROOT + "/Meshes/L88"
SOURCE = r"D:\Skyguard52\Content\Skyguard\Meshes\Source\L88\yak52_l88_silhouette_blockout.glb"


def log(message):
    unreal.log("[SkyguardL88] " + str(message))


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def import_glb(source, destination):
    if not os.path.isfile(source):
        raise RuntimeError("missing GLB: " + source)
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = destination
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.imported_object_paths or [])
    log("imported paths=" + str(len(imported)))
    for path in imported:
        log(" imported=" + str(path))
    return imported


def static_meshes(folder):
    meshes = []
    for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            meshes.append((path, asset))
    return meshes


def remove_stale_imported_meshes(folder, imported_paths):
    imported_set = set(imported_paths)
    removed = []
    for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh) and path not in imported_set:
            if unreal.EditorAssetLibrary.delete_asset(path):
                removed.append(path)
    if removed:
        log("removed stale meshes=" + str(len(removed)))


def clear_validation_actors():
    prefixes = ("L88_Validation_", "L88_Cam_", "L88_Key", "L88_Fill", "L88_Rim")
    for actor in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        label = actor.get_actor_label() or actor.get_name()
        if label.startswith(prefixes):
            unreal.EditorLevelLibrary.destroy_actor(actor)


def bounds(mesh):
    try:
        ext = mesh.get_bounds().box_extent
        return (abs(ext.x) * 2.0, abs(ext.y) * 2.0, abs(ext.z) * 2.0)
    except Exception:
        return (0.0, 0.0, 0.0)


def spawn_mesh(mesh, label, location=(0.0, 0.0, 0.0), scale=1.0):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    if actor is None:
        raise RuntimeError("failed to spawn " + label)
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    return actor


def add_light(light_class, location, intensity, color, label):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        light_class, unreal.Vector(*location), unreal.Rotator(-35.0, 35.0, 0.0)
    )
    if actor:
        actor.set_actor_label(label)
        component = actor.get_component_by_class(unreal.LightComponent)
        if component:
            component.set_editor_property("intensity", intensity)
            rgb = unreal.Color(
                int(max(0.0, min(1.0, color[0])) * 255.0),
                int(max(0.0, min(1.0, color[1])) * 255.0),
                int(max(0.0, min(1.0, color[2])) * 255.0),
                255,
            )
            component.set_editor_property("light_color", rgb)
    return actor


def main():
    log("L88 validation start")
    ensure_dir(DEST_PATH)
    imported = import_glb(SOURCE, DEST_PATH)
    remove_stale_imported_meshes(DEST_PATH, imported)

    # Start from a genuinely empty map. No Loop86 world, boards, combat, or
    # proxy actors are allowed in this asset gate.
    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_validation_actors()
    meshes = static_meshes(DEST_PATH)
    if not meshes:
        raise RuntimeError("GLB import returned no StaticMesh assets")
    for path, mesh in meshes:
        log("mesh=" + path + " bounds=" + str(bounds(mesh)))

    # GLTF importers differ on whether meters are converted to centimeters;
    # normalize only when the imported envelope is clearly in meter units.
    max_extent = max(max(bounds(mesh)) for _, mesh in meshes)
    scale = 100.0 if max_extent < 20.0 else 1.0
    log("normalization scale=" + str(scale))

    for index, (path, mesh) in enumerate(meshes):
        name = path.rsplit("/", 1)[-1]
        spawn_mesh(mesh, "L88_Validation_%03d_%s" % (index, name[:48]), scale=scale)

    # Neutral studio stage and camera markers; the map remains deliberately
    # small and static so later viewport captures cannot hide import issues.
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -120.0), unreal.Rotator()
    )
    if floor:
        floor.set_actor_label("L88_Validation_Floor")
        floor.static_mesh_component.set_static_mesh(
            unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
        )
        floor.set_actor_scale3d(unreal.Vector(12.0, 12.0, 0.05))

    add_light(unreal.RectLight, (700.0, -900.0, 900.0), 4000.0, (1.0, 0.82, 0.68), "L88_Key")
    add_light(unreal.RectLight, (-600.0, 700.0, 520.0), 2400.0, (0.46, 0.64, 1.0), "L88_Fill")
    add_light(unreal.DirectionalLight, (-300.0, -400.0, 800.0), 2.0, (0.72, 0.84, 1.0), "L88_Rim")

    for label, location, rotation in [
        ("L88_Cam_Beauty", (1100.0, -1250.0, 650.0), (-18.0, 40.0, 0.0)),
        ("L88_Cam_RearCockpit", (-240.0, -240.0, 180.0), (-8.0, 38.0, 0.0)),
        ("L88_Cam_ADS", (0.0, -120.0, 130.0), (-4.0, 0.0, 0.0)),
    ]:
        camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(*location), unreal.Rotator(*rotation)
        )
        if camera:
            camera.set_actor_label(label)

    unreal.EditorAssetLibrary.save_directory(PROJECT_ROOT, False, True)
    unreal.EditorLevelLibrary.save_current_level()
    log("L88 validation complete mesh_count=" + str(len(meshes)) + " imported=" + str(len(imported)))


if __name__ == "__main__":
    main()
