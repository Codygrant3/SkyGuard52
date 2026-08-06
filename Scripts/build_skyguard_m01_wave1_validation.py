"""Import and stage the Mission 1 coastal/Pathfinder Wave 1 candidate.

This creates an isolated Unreal validation map. It is intentionally separate
from the campaign map so an unaccepted blockout cannot silently become final
shipping art.
"""

import hashlib
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Content/Skyguard/Meshes/Source/Mission01/wave1_coastal_pathfinder.glb"
MANIFEST_PATH = ROOT / "Saved/Reports/M01_WAVE1_ASSET_MANIFEST.json"
BLENDER_REPORT_PATH = ROOT / "Saved/Reports/M01_WAVE1_BLENDER_REPORT.json"
REPORT_PATH = ROOT / "Saved/Reports/M01_WAVE1_UNREAL_AUDIT.json"
DEST_PATH = "/Game/Skyguard/Meshes/Mission01/Wave1Coast"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Validation"
PREFIX = "M01_W1_"


def log(message):
    unreal.log("[SkyguardM01] " + str(message))


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as stream:
        return json.load(stream)


def load_blender_report():
    with open(BLENDER_REPORT_PATH, "r", encoding="utf-8") as stream:
        return json.load(stream)


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def import_glb():
    if not SOURCE.is_file():
        raise RuntimeError("Missing GLB: " + str(SOURCE))
    ensure_dir(DEST_PATH)
    task = unreal.AssetImportTask()
    task.filename = str(SOURCE)
    task.destination_path = DEST_PATH
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.imported_object_paths or [])
    if not imported:
        raise RuntimeError("Unreal imported no assets from " + str(SOURCE))
    return imported


def static_meshes():
    meshes = {}
    paths = {}
    for path in unreal.EditorAssetLibrary.list_assets(DEST_PATH, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            meshes[asset.get_name()] = asset
            paths[asset.get_name()] = path
    return meshes, paths


def collision_shape(name):
    return {
        "box": unreal.ScriptingCollisionShapeType.BOX,
        "sphere": unreal.ScriptingCollisionShapeType.SPHERE,
        "capsule": unreal.ScriptingCollisionShapeType.CAPSULE,
        # The automated convex-decomposition API is not deterministic enough
        # for this candidate gate. A 26-DOP hull is bounded and repeatable.
        "convex": unreal.ScriptingCollisionShapeType.NDOP26,
    }.get(name)


def configure_meshes(meshes, manifest):
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    contracts = {
        entry["asset"]: entry["shape"]
        for entry in manifest.get("collision_contracts", [])
    }
    configured = {}
    nanite_policy = {}
    for name, mesh in sorted(meshes.items()):
        contract = contracts.get(name, "none")
        subsystem.remove_collisions(mesh)
        primitive_count = 0
        shape = collision_shape(contract)
        if shape is not None:
            result = subsystem.add_simple_collisions(mesh, shape)
            primitive_count = 1 if int(result) >= 0 else 0

        # Wave 1 meshes are modular, low-complexity source meshes. Enabling
        # Nanite here would add overhead without useful geometric reduction.
        settings = mesh.get_editor_property("nanite_settings")
        settings.enabled = False
        mesh.set_editor_property("nanite_settings", settings)
        nanite_policy[name] = {
            "enabled": False,
            "reason": "modular_low_complexity_candidate",
        }
        configured[name] = {
            "contract": contract,
            "simple_collision_primitive_count": primitive_count,
        }
        unreal.EditorAssetLibrary.save_loaded_asset(mesh, False)
    return configured, nanite_policy


def mesh_bounds(mesh):
    ext = mesh.get_bounds().box_extent
    return [abs(ext.x) * 2.0, abs(ext.y) * 2.0, abs(ext.z) * 2.0]


def clear_map_actors():
    for actor in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        label = actor.get_actor_label() or actor.get_name()
        if label.startswith(PREFIX):
            unreal.EditorLevelLibrary.destroy_actor(actor)


def to_rotator(rotation_deg):
    # Blender XYZ Euler maps to Unreal roll/pitch/yaw for this static staging.
    return unreal.Rotator(
        float(rotation_deg[1]),
        float(rotation_deg[2]),
        float(rotation_deg[0]),
    )


def spawn_mesh(mesh, label, location_m, rotation_deg, scale_xyz, import_scale):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*(float(value) * 100.0 for value in location_m)),
        to_rotator(rotation_deg),
    )
    if actor is None:
        raise RuntimeError("Failed to spawn " + label)
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(
        unreal.Vector(
            float(scale_xyz[0]) * import_scale,
            float(scale_xyz[1]) * import_scale,
            float(scale_xyz[2]) * import_scale,
        )
    )
    return actor


def add_light(light_class, location, rotation, intensity, color, label):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        light_class, unreal.Vector(*location), unreal.Rotator(*rotation)
    )
    if actor is None:
        return None
    actor.set_actor_label(label)
    component = actor.get_component_by_class(unreal.LightComponent)
    if component:
        component.set_editor_property("intensity", intensity)
        component.set_editor_property(
            "light_color",
            unreal.Color(
                int(color[0] * 255.0),
                int(color[1] * 255.0),
                int(color[2] * 255.0),
                255,
            ),
        )
    return actor


def spawn_validation_environment():
    ocean = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0.0, -3000.0, -130.0),
        unreal.Rotator(),
    )
    if ocean:
        ocean.set_actor_label(PREFIX + "OceanValidationPlane")
        ocean.static_mesh_component.set_static_mesh(
            unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
        )
        ocean.set_actor_scale3d(unreal.Vector(32.0, 26.0, 0.08))

    add_light(
        unreal.DirectionalLight,
        (-4200.0, -5000.0, 7500.0),
        (-38.0, -32.0, 0.0),
        4.5,
        (1.0, 0.82, 0.64),
        PREFIX + "Sun",
    )
    add_light(
        unreal.SkyLight,
        (0.0, 0.0, 3500.0),
        (0.0, 0.0, 0.0),
        1.2,
        (0.62, 0.76, 1.0),
        PREFIX + "SkyFill",
    )
    for label, location, rotation in [
        ("CoastWide", (-8200.0, -9800.0, 5200.0), (-17.0, 40.0, 0.0)),
        ("CoastLow", (-4700.0, -6500.0, 1700.0), (-5.0, 38.0, 0.0)),
        ("Boss", (1900.0, -1300.0, 1100.0), (-9.0, 145.0, 0.0)),
    ]:
        camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor,
            unreal.Vector(*location),
            unreal.Rotator(*rotation),
        )
        if camera:
            camera.set_actor_label(PREFIX + "Cam_" + label)


def spawn_pathfinder():
    boss_class = getattr(unreal, "SkyguardPathfinderBoss", None)
    if boss_class is None:
        return None
    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(800.0, 400.0, 700.0),
        unreal.Rotator(0.0, 8.0, 0.0),
    )
    if boss:
        boss.set_actor_label(PREFIX + "Boss_Pathfinder_Live")
    return boss


def boss_mesh_bindings(boss):
    if boss is None:
        return {}
    bindings = {}
    for component in boss.get_components_by_class(unreal.StaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        bindings[component.get_name()] = mesh.get_name() if mesh else None
    return bindings


def main():
    manifest = load_manifest()
    blender_report = load_blender_report()
    imported = import_glb()
    meshes, mesh_paths = static_meshes()
    expected_names = {entry["name"] for entry in manifest["assets"]}
    missing = sorted(expected_names - set(meshes))
    extra = sorted(set(meshes) - expected_names)
    if missing:
        raise RuntimeError("Missing imported meshes: " + ", ".join(missing))
    collision_results, nanite_policy = configure_meshes(meshes, manifest)

    max_extent = max(max(mesh_bounds(mesh)) for mesh in meshes.values())
    import_scale = 100.0 if max_extent < 60.0 else 1.0
    log("mesh count=%d max_extent=%.3f scale=%.1f" % (len(meshes), max_extent, import_scale))

    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_map_actors()

    placed = []
    for index, spec in enumerate(manifest["placements"]):
        # The live native boss owns its body and weak-point mesh components.
        if str(spec.get("mission_role", "")).startswith("boss_"):
            continue
        mesh = meshes.get(spec["asset"])
        if mesh is None:
            continue
        label = "%s%03d_%s" % (PREFIX, index, spec["asset"][:52])
        spawn_mesh(
            mesh,
            label,
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
            import_scale,
        )
        placed.append(label)

    boss = spawn_pathfinder()
    live_boss_bindings = boss_mesh_bindings(boss)
    spawn_validation_environment()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    unreal.EditorLevelLibrary.save_current_level()

    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    labeled = [
        actor.get_actor_label()
        for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    weakpoint_names = {
        "SM_Boss_Pathfinder_CommandAntenna",
        "SM_Boss_Pathfinder_NoseCamera",
        "SM_Boss_Pathfinder_Engine",
        "SM_Boss_Pathfinder_ControlLinkage",
    }
    breakup_names = {
        "SM_Boss_Pathfinder_BreakChunk_L",
        "SM_Boss_Pathfinder_BreakChunk_R",
        "SM_Boss_Pathfinder_BreakChunk_Engine",
    }
    required_boss_bindings = {
        "BodyMesh": "SM_Boss_Pathfinder_Body",
        "CommandAntenna": "SM_Boss_Pathfinder_CommandAntenna",
        "NoseCamera": "SM_Boss_Pathfinder_NoseCamera",
        "Engine": "SM_Boss_Pathfinder_Engine",
        "ControlLinkage": "SM_Boss_Pathfinder_ControlLinkage",
        "DebrisNose": "SM_Boss_Pathfinder_BreakChunk_L",
        "DebrisCenter": "SM_Boss_Pathfinder_BreakChunk_Engine",
        "DebrisTail": "SM_Boss_Pathfinder_BreakChunk_R",
    }
    collision_contracts_satisfied = all(
        (
            result["simple_collision_primitive_count"] == 0
            if result["contract"] == "none"
            else result["simple_collision_primitive_count"] == 1
        )
        for result in collision_results.values()
    )
    checks = {
        "source_hash_matches_blender_report": (
            sha256(SOURCE) == blender_report["export_glb_sha256"]
        ),
        "static_mesh_count_matches_manifest": len(meshes) == len(expected_names),
        "no_missing_meshes": not missing,
        "no_extra_meshes": not extra,
        "all_weakpoint_meshes_present": weakpoint_names.issubset(meshes),
        "bounded_breakup_set_present": breakup_names.issubset(meshes),
        "live_pathfinder_actor_spawned": boss is not None,
        "live_pathfinder_meshes_bound": all(
            live_boss_bindings.get(component) == mesh
            for component, mesh in required_boss_bindings.items()
        ),
        "collision_contracts_satisfied": collision_contracts_satisfied,
        "nanite_policy_explicit": (
            len(nanite_policy) == len(meshes)
            and not any(spec["enabled"] for spec in nanite_policy.values())
        ),
        "production_placements_spawned": len(placed) == sum(
            1
            for spec in manifest["placements"]
            if not str(spec.get("mission_role", "")).startswith("boss_")
        ),
        "validation_map_saved": unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
    }
    report = {
        "schema": "skyguard.m01.wave1.unreal-audit.v1",
        "source_glb": str(SOURCE),
        "source_glb_sha256": sha256(SOURCE),
        "destination": DEST_PATH,
        "map": MAP_PATH,
        "imported_object_count": len(imported),
        "static_mesh_count": len(meshes),
        "mesh_paths": mesh_paths,
        "live_pathfinder_mesh_bindings": live_boss_bindings,
        "required_pathfinder_mesh_bindings": required_boss_bindings,
        "collision_results": collision_results,
        "nanite_policy": nanite_policy,
        "missing_meshes": missing,
        "extra_meshes": extra,
        "import_normalization_scale": import_scale,
        "placed_environment_actor_count": len(placed),
        "validation_actor_count": len(labeled),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "mission01_wave1_candidate_not_final_aaa_acceptance",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    log(json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 Wave 1 Unreal gate failed")


if __name__ == "__main__":
    main()
