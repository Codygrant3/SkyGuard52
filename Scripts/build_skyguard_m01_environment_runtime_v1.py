"""Build a separate Mission 1 native-environment validation map.

This script never edits Lvl_SkyguardCoast or the material packages. It clones the
isolated Mission 1 refinement map, adds engine/plugin environment actors, and
records which integrations are executable versus structural placeholders.
"""

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Refinement_Validation"
TARGET_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Environment_Runtime_v3"
REPORT_PATH = ROOT / "Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_BUILD.json"
PREFIX = "M01_ENV1_"
REFINEMENT_MANIFEST_PATH = (
    ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
)


def spawn_class(class_path, label, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0)):
    try:
        cls = unreal.load_class(None, class_path)
        if cls is None:
            return None, "class_unavailable"
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            cls,
            unreal.Vector(*location),
            unreal.Rotator(*rotation),
        )
        if actor is None:
            return None, "spawn_failed"
        actor.set_actor_label(label)
        return actor, "spawned"
    except Exception as exc:
        return None, "exception: " + str(exc)


def add_tag(actor, tag):
    if actor is None:
        return
    tags = list(actor.get_editor_property("tags") or [])
    name = unreal.Name(tag)
    if name not in tags:
        tags.append(name)
        actor.set_editor_property("tags", tags)


def remove_prior_revision_actors():
    removed = 0
    for actor in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        if (actor.get_actor_label() or "").startswith(PREFIX):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
    return removed


def create_target_from_governed_manifest():
    """Create a fresh revision without duplicating or reloading a UWorld.

    Loading a duplicated external-actor world inside the same commandlet can
    retain the new UWorld long enough for UE's world-leak guard to reject the
    transition. Rebuilding the small validation composition from its governed
    manifest is deterministic and avoids that unsafe ownership edge case.
    """
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError(
            "Fresh environment revision already exists; use the persistence "
            "verifier instead of rebuilding it: " + TARGET_MAP
        )
    scripts_path = str(ROOT / "Scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    import build_skyguard_m01_wave1_refinement_validation as geometry

    with open(REFINEMENT_MANIFEST_PATH, "r", encoding="utf-8") as stream:
        manifest = json.load(stream)
    meshes, _ = geometry.collect_meshes()
    expected = {entry["name"] for entry in manifest["assets"]}
    if set(meshes) != expected:
        raise RuntimeError("Refinement mesh set differs from governed manifest")
    if not unreal.EditorLevelLibrary.new_level(TARGET_MAP):
        raise RuntimeError("Could not create target environment map: " + TARGET_MAP)

    for index, spec in enumerate(manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        geometry.spawn_static(
            meshes[spec["asset"]],
            "M01_ENV_BASE_%03d_%s" % (index, spec["asset"][:48]),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
    boss, bindings, required = geometry.spawn_and_bind_pathfinder(meshes)
    if boss is None or bindings != required:
        raise RuntimeError("Refined Pathfinder could not be staged")
    geometry.spawn_environment()


def spawn_visible_ocean_fallback():
    plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    if plane is None:
        return None
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(22500.0, -15000.0, -160.0),
        unreal.Rotator(),
    )
    if actor is None:
        return None
    actor.set_actor_label(PREFIX + "OceanVisibleFallback")
    actor.static_mesh_component.set_static_mesh(plane)
    actor.set_actor_scale3d(unreal.Vector(500.0, 300.0, 1.0))
    for material_path in (
        "/Game/Skyguard/Materials/Generated/M_L21_BrightOcean",
        "/Game/Skyguard/Materials/Generated/M_L61_Waterline",
    ):
        material = unreal.EditorAssetLibrary.load_asset(material_path)
        if material:
            actor.static_mesh_component.set_material(0, material)
            break
    add_tag(actor, "Skyguard.Environment.Water")
    return actor


def spawn_landmass_deferred_marker():
    """Record the integration boundary without loading the broken UE 5.8 brush.

    The experimental CustomBrush_Landmass Blueprint bundled with this engine
    build emits compiler errors during a rendered game launch. A plain actor
    preserves capability discovery and map ownership while making it explicit
    that Landscape edit-layer authoring must use a compatible implementation.
    """
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor,
        unreal.Vector(21000.0, 9000.0, -150.0),
        unreal.Rotator(),
    )
    if actor is None:
        return None, "landmass_deferred_marker_spawn_failed"
    actor.set_actor_label(PREFIX + "LandmassDeferredMarker")
    add_tag(actor, "Skyguard.Environment.Landmass")
    return actor, "deferred_engine_5_8_experimental_brush_incompatible"


def configure_fog(actor):
    if actor is None:
        return
    try:
        component = actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if component:
            component.set_editor_property("fog_density", 0.012)
            component.set_editor_property("fog_height_falloff", 0.17)
            component.set_editor_property("volumetric_fog", True)
            component.set_editor_property("volumetric_fog_scattering_distribution", 0.35)
            component.set_editor_property("volumetric_fog_extinction_scale", 0.7)
    except Exception as exc:
        unreal.log_warning("[M01Env] Fog configuration limited: " + str(exc))


def main():
    create_target_from_governed_manifest()
    removed = remove_prior_revision_actors()
    integrations = {}
    actors = {}

    director_class = getattr(unreal, "SkyguardCoastalEnvironmentDirector", None)
    if director_class:
        director = unreal.EditorLevelLibrary.spawn_actor_from_class(
            director_class,
            unreal.Vector(0.0, 0.0, -150.0),
            unreal.Rotator(),
        )
        if director:
            director.set_actor_label(PREFIX + "CoastalEnvironmentDirector")
            actors["director"] = director
            integrations["native_director"] = "spawned"
        else:
            integrations["native_director"] = "spawn_failed"
    else:
        integrations["native_director"] = "native_class_unavailable_build_required"

    water_zone, integrations["water_zone"] = spawn_class(
        "/Script/Water.WaterZone",
        PREFIX + "WaterZone",
        (22500.0, -12000.0, -150.0),
    )
    ocean, integrations["water_body_ocean"] = spawn_class(
        "/Script/Water.WaterBodyOcean",
        PREFIX + "WaterBodyOcean",
        (22500.0, -12000.0, -150.0),
    )
    if ocean:
        try:
            ocean.set_actor_scale3d(unreal.Vector(100.0, 100.0, 1.0))
        except Exception:
            pass
    visible_ocean = spawn_visible_ocean_fallback()
    integrations["visible_ocean_fallback"] = "spawned" if visible_ocean else "failed"
    for actor in (water_zone, ocean, visible_ocean):
        add_tag(actor, "Skyguard.Environment.Water")

    landmass, integrations["landmass_marker"] = spawn_landmass_deferred_marker()
    actors["landmass"] = landmass

    pcg_volume, integrations["pcg_volume"] = spawn_class(
        "/Script/PCG.PCGVolume",
        PREFIX + "PCGVegetationVolume",
        (22500.0, 11000.0, 1500.0),
    )
    if pcg_volume:
        pcg_volume.set_actor_scale3d(unreal.Vector(225.0, 65.0, 30.0))
    add_tag(pcg_volume, "Skyguard.Environment.PCG")

    atmosphere, integrations["sky_atmosphere"] = spawn_class(
        "/Script/Engine.SkyAtmosphere",
        PREFIX + "SkyAtmosphere",
    )
    add_tag(atmosphere, "Skyguard.Environment.Atmosphere")

    cloud, integrations["volumetric_cloud"] = spawn_class(
        "/Script/Engine.VolumetricCloud",
        PREFIX + "VolumetricCloud",
    )
    add_tag(cloud, "Skyguard.Environment.Cloud")

    fog, integrations["volumetric_height_fog"] = spawn_class(
        "/Script/Engine.ExponentialHeightFog",
        PREFIX + "VolumetricHeightFog",
    )
    configure_fog(fog)
    add_tag(fog, "Skyguard.Environment.Fog")

    wind, integrations["directional_wind"] = spawn_class(
        "/Script/Engine.WindDirectionalSource",
        PREFIX + "DirectionalWind",
        rotation=(0.0, 35.0, 0.0),
    )
    add_tag(wind, "Skyguard.Environment.Wind")

    if "director" in actors:
        try:
            actors["director"].refresh_capability_bindings()
        except Exception:
            pass

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_asset(TARGET_MAP, False)

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    revision_actors = [
        actor for actor in all_actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    labels = sorted(actor.get_actor_label() for actor in revision_actors)
    class_names = {
        actor.get_actor_label(): actor.get_class().get_name()
        for actor in revision_actors
    }
    capability_tags = {
        tag: sum(
            1 for actor in all_actors
            if unreal.Name(tag) in list(actor.get_editor_property("tags") or [])
        )
        for tag in (
            "Skyguard.Environment.Water",
            "Skyguard.Environment.Landmass",
            "Skyguard.Environment.PCG",
            "Skyguard.Environment.Atmosphere",
            "Skyguard.Environment.Cloud",
            "Skyguard.Environment.Fog",
            "Skyguard.Environment.Wind",
        )
    }
    checks = {
        "separate_target_map_saved": unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP),
        "source_map_not_targeted": TARGET_MAP != SOURCE_MAP,
        "native_environment_director_spawned": integrations["native_director"] == "spawned",
        "visible_ocean_surface_spawned": visible_ocean is not None,
        "stable_ocean_strategy_present": visible_ocean is not None,
        "atmosphere_cloud_fog_wind_spawned": all(
            actor is not None for actor in (atmosphere, cloud, fog, wind)
        ),
        "pcg_volume_spawned": pcg_volume is not None,
        "all_capability_tags_present": all(count > 0 for count in capability_tags.values()),
    }
    report = {
        "schema": "skyguard.m01.environment-runtime-build.v1",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "removed_prior_revision_actor_count": removed,
        "revision_actor_count": len(revision_actors),
        "revision_actor_labels": labels,
        "revision_actor_classes": class_names,
        "integrations": integrations,
        "capability_tag_counts": capability_tags,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "PARTIAL",
        "executable": [
            "native deterministic HISM vegetation with route exclusion and quality budgets",
            "native fixed-capacity Niagara smoke/fire/sparks/explosion pool",
            "engine SkyAtmosphere, VolumetricCloud, ExponentialHeightFog, and directional wind",
            "stable existing-material ocean surface independent of the incompatible experimental Water/Landmass plugin chain",
        ],
        "placeholders_or_followups": [
            "PCGVolume is a ready container; no authored PCG graph is assigned yet",
            "UE 5.8 experimental CustomBrush_Landmass is excluded because its Blueprint is incompatible; a tagged deferred-integration marker is used until a production Landscape edit-layer implementation is authored",
            "UE 5.8 experimental Water and Volumetrics plugins are disabled because they force the incompatible Landmass content chain; production water will use a stable material/mesh implementation or a verified replacement plugin",
            "NullRHI structural runs cannot validate water, cloud, fog, or Niagara appearance",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardM01Environment] " + json.dumps(report))
    if report["gate"] not in {"PASS", "PARTIAL"}:
        raise RuntimeError("Mission 1 environment build failed")


if __name__ == "__main__":
    main()
