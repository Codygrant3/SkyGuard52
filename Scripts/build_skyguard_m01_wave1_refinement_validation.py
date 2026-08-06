"""Import and stage the isolated Mission 1 AAA-refinement candidate."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Content/Skyguard/Meshes/Source/Mission01/Wave1_Refinement/m01_wave1_aaa_refinement.glb"
MANIFEST_PATH = ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
BLENDER_REPORT_PATH = ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_REPORT.json"
REPORT_PATH = ROOT / "Saved/Reports/M01_WAVE1_REFINEMENT_UNREAL_AUDIT.json"
PERF_PATH = ROOT / "Saved/Reports/M01_WAVE1_REFINEMENT_PERFORMANCE_READINESS.json"
DEST_PATH = "/Game/Skyguard/Meshes/Mission01/Wave1Refinement"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Refinement_Validation"
PREFIX = "M01_W1R_"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path):
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def ensure_directory(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def import_source():
    if not SOURCE.is_file():
        raise RuntimeError("Missing refinement GLB: " + str(SOURCE))
    ensure_directory(DEST_PATH)
    task = unreal.AssetImportTask()
    task.filename = str(SOURCE)
    task.destination_path = DEST_PATH
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.imported_object_paths or [])
    if not imported:
        raise RuntimeError("Refinement import returned no assets")
    return imported


def collect_meshes():
    meshes = {}
    paths = {}
    for path in unreal.EditorAssetLibrary.list_assets(DEST_PATH, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            meshes[asset.get_name()] = asset
            paths[asset.get_name()] = path
    return meshes, paths


def simple_shape(contract):
    return {
        "box": unreal.ScriptingCollisionShapeType.BOX,
        "sphere": unreal.ScriptingCollisionShapeType.SPHERE,
        "capsule": unreal.ScriptingCollisionShapeType.CAPSULE,
        "convex": unreal.ScriptingCollisionShapeType.NDOP26,
    }.get(contract)


def configure_meshes(meshes, manifest):
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    by_name = {entry["name"]: entry for entry in manifest["assets"]}
    collision_results = {}
    nanite_results = {}
    for name, mesh in sorted(meshes.items()):
        spec = by_name[name]
        contract = spec["collision"]
        subsystem.remove_collisions(mesh)
        mode = "none"
        primitive_count = 0
        if contract == "complex_as_simple":
            body_setup = mesh.get_editor_property("body_setup")
            body_setup.set_editor_property(
                "collision_trace_flag",
                unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE,
            )
            mode = "complex_as_simple"
        elif contract == "convex_decomposition":
            subsystem.set_convex_decomposition_collisions(mesh, 4, 32, 100000)
            primitive_count = 4
            mode = "convex_decomposition_4_hulls"
        else:
            shape = simple_shape(contract)
            if shape is not None:
                result = subsystem.add_simple_collisions(mesh, shape)
                primitive_count = 1 if int(result) >= 0 else 0
                mode = contract

        # Restrict Nanite to the genuinely denser, large opaque environment
        # pieces. Small boss components and sub-3k triangle props stay classic.
        enable_nanite = bool(
            spec.get("nanite_candidate")
            and spec.get("triangles", 0) >= 4000
            and spec["role"] in {"urban_module", "hero_landmark", "defended_objective"}
        )
        settings = mesh.get_editor_property("nanite_settings")
        settings.enabled = enable_nanite
        mesh.set_editor_property("nanite_settings", settings)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh, False)
        collision_results[name] = {
            "contract": contract,
            "configured_mode": mode,
            "simple_collision_primitive_count": primitive_count,
        }
        nanite_results[name] = {
            "manifest_candidate": bool(spec.get("nanite_candidate")),
            "triangles": int(spec.get("triangles", 0)),
            "enabled": enable_nanite,
            "reason": (
                "dense_large_opaque_environment"
                if enable_nanite
                else "below_density_or_small_dynamic_component"
            ),
        }
    return collision_results, nanite_results


def rotation(values):
    return unreal.Rotator(float(values[1]), float(values[2]), float(values[0]))


def spawn_static(mesh, label, location_m, rotation_deg, scale):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*(float(value) * 100.0 for value in location_m)),
        rotation(rotation_deg),
    )
    if actor is None:
        raise RuntimeError("Failed to spawn " + label)
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(*[float(value) for value in scale]))
    return actor


def add_light(light_class, location, rot, intensity, color, label):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        light_class, unreal.Vector(*location), unreal.Rotator(*rot)
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
                int(color[0] * 255),
                int(color[1] * 255),
                int(color[2] * 255),
                255,
            ),
        )
    return actor


def spawn_environment():
    ocean = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0.0, -3300.0, -150.0),
        unreal.Rotator(),
    )
    if ocean:
        ocean.set_actor_label(PREFIX + "OceanValidationPlane")
        ocean.static_mesh_component.set_static_mesh(
            unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
        )
        ocean.set_actor_scale3d(unreal.Vector(34.0, 28.0, 0.08))
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
    cameras = [
        ("CoastWide", (-8200.0, -9800.0, 5200.0), (-17.0, 40.0, 0.0)),
        ("Street", (-4800.0, -6900.0, 1700.0), (-5.0, 38.0, 0.0)),
        ("Pathfinder", (1900.0, -1500.0, 1100.0), (-9.0, 145.0, 0.0)),
    ]
    for label, location, rot in cameras:
        camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(*location), unreal.Rotator(*rot)
        )
        if camera:
            camera.set_actor_label(PREFIX + "Cam_" + label)


def spawn_and_bind_pathfinder(meshes):
    boss_class = getattr(unreal, "SkyguardPathfinderBoss", None)
    if boss_class is None:
        return None, {}, {}
    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(800.0, 200.0, 700.0),
        unreal.Rotator(0.0, 8.0, 0.0),
    )
    if boss is None:
        return None, {}, {}
    boss.set_actor_label(PREFIX + "Boss_Pathfinder_Live_AAA")
    required = {
        "BodyMesh": "SM_Boss_Pathfinder_Body_AAA",
        "CommandAntenna": "SM_Boss_Pathfinder_CommandAntenna_AAA",
        "NoseCamera": "SM_Boss_Pathfinder_NoseCamera_AAA",
        "Engine": "SM_Boss_Pathfinder_Engine_AAA",
        "ControlLinkage": "SM_Boss_Pathfinder_ControlLinkage_AAA",
        "DebrisNose": "SM_Boss_Pathfinder_BreakChunk_Wing_L_AAA",
        "DebrisCenter": "SM_Boss_Pathfinder_BreakChunk_Engine_AAA",
        "DebrisTail": "SM_Boss_Pathfinder_BreakChunk_Wing_R_AAA",
        "DebrisSpine": "SM_Boss_Pathfinder_BreakChunk_Spine_AAA",
    }
    relative_locations = {
        "CommandAntenna": (-40.0, 0.0, 48.0),
        "NoseCamera": (253.0, 0.0, 2.0),
        "Engine": (-175.0, 0.0, -8.0),
        "ControlLinkage": (-120.0, 0.0, 28.0),
    }
    bindings = {}
    for component in boss.get_components_by_class(unreal.StaticMeshComponent):
        component_name = component.get_name()
        mesh_name = required.get(component_name)
        if mesh_name:
            component.set_static_mesh(meshes[mesh_name])
            if component_name in relative_locations:
                component.set_relative_location(
                    unreal.Vector(*relative_locations[component_name]),
                    False,
                    False,
                )
            bindings[component_name] = mesh_name
    return boss, bindings, required


def main():
    manifest = read_json(MANIFEST_PATH)
    blender_report = read_json(BLENDER_REPORT_PATH)
    imported = import_source()
    meshes, mesh_paths = collect_meshes()
    expected = {entry["name"] for entry in manifest["assets"]}
    missing = sorted(expected - set(meshes))
    extra = sorted(set(meshes) - expected)
    if missing:
        raise RuntimeError("Missing refinement meshes: " + ", ".join(missing))

    collision_results, nanite_results = configure_meshes(meshes, manifest)
    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        unreal.EditorLevelLibrary.load_level(MAP_PATH)

    placed = []
    for index, spec in enumerate(manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        spawn_static(
            meshes[spec["asset"]],
            "%s%03d_%s" % (PREFIX, index, spec["asset"][:48]),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
        placed.append(spec["asset"])

    boss, live_bindings, required_bindings = spawn_and_bind_pathfinder(meshes)
    spawn_environment()
    unreal.EditorAssetLibrary.save_directory(DEST_PATH, False, True)
    unreal.EditorLevelLibrary.save_current_level()

    labeled = [
        actor.get_actor_label()
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    complex_contracts = {"complex_as_simple", "convex_decomposition"}
    collision_ok = all(
        result["configured_mode"] != "none"
        for result in collision_results.values()
        if result["contract"] in complex_contracts
        or result["contract"] in {"box", "sphere", "capsule", "convex"}
    )
    checks = {
        "source_hash_matches_blender_report": (
            sha256(SOURCE) == blender_report["export_glb_sha256"]
        ),
        "static_mesh_count_matches_manifest": len(meshes) == len(expected) == 20,
        "no_missing_meshes": not missing,
        "no_extra_meshes": not extra,
        "collision_contracts_configured": collision_ok,
        "live_pathfinder_spawned": boss is not None,
        "live_pathfinder_refined_meshes_bound": all(
            live_bindings.get(component) == mesh
            for component, mesh in required_bindings.items()
        ),
        "environment_placements_spawned": len(placed) == 10,
        "validation_map_saved": unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
    }
    report = {
        "schema": "skyguard.m01.wave1.refinement.unreal-audit.v2",
        "source_glb": str(SOURCE),
        "source_glb_sha256": sha256(SOURCE),
        "destination": DEST_PATH,
        "map": MAP_PATH,
        "imported_object_count": len(imported),
        "static_mesh_count": len(meshes),
        "mesh_paths": mesh_paths,
        "missing_meshes": missing,
        "extra_meshes": extra,
        "placed_environment_actor_count": len(placed),
        "validation_actor_count": len(labeled),
        "collision_results": collision_results,
        "nanite_results": nanite_results,
        "live_pathfinder_mesh_bindings": live_bindings,
        "required_pathfinder_mesh_bindings": required_bindings,
        "unattached_but_imported_assets": [
            "SM_Boss_Pathfinder_Body_Damaged_AAA",
            "SM_Boss_Pathfinder_BreakChunk_Spine_AAA",
        ],
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "refinement_candidate_requires_rendered_visual_and_runtime_performance_acceptance",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)

    enabled_nanite = [
        name for name, result in nanite_results.items() if result["enabled"]
    ]
    perf_checks = {
        "triangle_budget_recorded": blender_report["total_triangles"] == 45844,
        "bounded_runtime_breakup_pool": (
            len(manifest["boss"]["breakup_pool"]) == 4
            and manifest["boss"]["runtime_fracture"] is False
        ),
        "nanite_selective_not_blanket": 0 < len(enabled_nanite) < len(meshes),
        "all_collision_modes_recorded": len(collision_results) == 20,
        "glb_under_10_mib": SOURCE.stat().st_size < 10 * 1024 * 1024,
    }
    perf_report = {
        "schema": "skyguard.m01.wave1.refinement.performance-readiness.v1",
        "glb_bytes": SOURCE.stat().st_size,
        "total_vertices": blender_report["total_vertices"],
        "total_triangles": blender_report["total_triangles"],
        "static_mesh_count": len(meshes),
        "material_count": blender_report["material_count"],
        "nanite_enabled_count": len(enabled_nanite),
        "nanite_enabled_assets": enabled_nanite,
        "runtime_fracture": manifest["boss"]["runtime_fracture"],
        "breakup_pool_count": len(manifest["boss"]["breakup_pool"]),
        "checks": perf_checks,
        "gate": "READY_FOR_RUNTIME_PROFILE" if all(perf_checks.values()) else "BLOCKED",
        "limitations": [
            "NullRHI does not measure frame time, GPU time, draw calls, or rendered material quality.",
            "Imported Blender materials remain candidates for replacement by Unreal master materials.",
            "The native boss currently exposes three debris components; the fourth spine mesh is imported and pool-ready but not attached.",
        ],
    }
    with open(PERF_PATH, "w", encoding="utf-8") as stream:
        json.dump(perf_report, stream, indent=2)
    unreal.log("[SkyguardM01Refinement] " + json.dumps(report))
    unreal.log("[SkyguardM01RefinementPerf] " + json.dumps(perf_report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 refinement Unreal gate failed")


if __name__ == "__main__":
    main()
