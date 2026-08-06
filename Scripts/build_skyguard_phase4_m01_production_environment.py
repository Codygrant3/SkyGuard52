"""Build the isolated Mission 1 production-environment revision.

The map is assembled from the governed refinement manifest and the native
SkyguardMission01EnvironmentDirector. It intentionally does not instantiate
WaterBody, Landmass brush, or Volumetrics plugin classes.
"""

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02"
REPORT_PATH = ROOT / "Saved/Reports/PHASE4_M01_PRODUCTION_ENVIRONMENT_BUILD.json"
MANIFEST_PATH = ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
PREFIX = "M01_P4_"


def add_tag(actor, tag):
    tags = list(actor.get_editor_property("tags") or [])
    value = unreal.Name(tag)
    if value not in tags:
        tags.append(value)
        actor.set_editor_property("tags", tags)


def spawn_actor(class_path, label, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0)):
    cls = unreal.load_class(None, class_path)
    if cls is None:
        return None
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        cls, unreal.Vector(*location), unreal.Rotator(*rotation)
    )
    if actor:
        actor.set_actor_label(label)
    return actor


def main():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError(
            "Attempt package already exists; verify it or increment the immutable "
            "attempt suffix instead of overwriting: " + TARGET_MAP
        )

    scripts_path = str(ROOT / "Scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    import build_skyguard_m01_wave1_refinement_validation as geometry

    with MANIFEST_PATH.open("r", encoding="utf-8") as stream:
        manifest = json.load(stream)
    meshes, _ = geometry.collect_meshes()
    expected = {entry["name"] for entry in manifest["assets"]}
    if set(meshes) != expected:
        raise RuntimeError("Imported refined mesh set differs from governed manifest")
    if not unreal.EditorLevelLibrary.new_level(TARGET_MAP):
        raise RuntimeError("Could not create production environment map")

    placed = []
    for index, spec in enumerate(manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        geometry.spawn_static(
            meshes[spec["asset"]],
            "%sRefined_%03d_%s" % (PREFIX, index, spec["asset"][:42]),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
        placed.append(spec["asset"])

    boss, bindings, required = geometry.spawn_and_bind_pathfinder(meshes)
    if boss is None or bindings != required:
        raise RuntimeError("Governed Pathfinder could not be bound")
    boss.set_actor_label(PREFIX + "Boss_Pathfinder")

    director_class = getattr(unreal, "SkyguardMission01EnvironmentDirector", None)
    if director_class is None:
        raise RuntimeError("Native Mission 1 production director is unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector(), unreal.Rotator()
    )
    if director is None:
        raise RuntimeError("Native Mission 1 production director did not spawn")
    director.set_actor_label(PREFIX + "ProductionEnvironmentDirector")
    director.rebuild_production_layout()

    atmosphere = spawn_actor(
        "/Script/Engine.SkyAtmosphere", PREFIX + "SkyAtmosphere"
    )
    cloud = spawn_actor(
        "/Script/Engine.VolumetricCloud", PREFIX + "VolumetricCloud"
    )
    fog = spawn_actor(
        "/Script/Engine.ExponentialHeightFog", PREFIX + "HeightFog"
    )
    wind = spawn_actor(
        "/Script/Engine.WindDirectionalSource",
        PREFIX + "WorldWind",
        rotation=(0.0, 35.0, 0.0),
    )
    sun = spawn_actor(
        "/Script/Engine.DirectionalLight",
        PREFIX + "Sun",
        location=(-4200.0, -5000.0, 7500.0),
        rotation=(-38.0, -32.0, 0.0),
    )
    skylight = spawn_actor(
        "/Script/Engine.SkyLight",
        PREFIX + "SkyFill",
        location=(0.0, 0.0, 3500.0),
    )
    for actor, tag in (
        (atmosphere, "Skyguard.Environment.Atmosphere"),
        (cloud, "Skyguard.Environment.Cloud"),
        (fog, "Skyguard.Environment.Fog"),
        (wind, "Skyguard.Environment.Wind"),
    ):
        if actor:
            add_tag(actor, tag)

    if fog:
        component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if component:
            component.set_editor_property("fog_density", 0.012)
            component.set_editor_property("fog_height_falloff", 0.17)
    if sun:
        component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if component:
            component.set_editor_property("intensity", 4.5)
            component.set_editor_property("atmosphere_sun_light", True)
    if skylight:
        component = skylight.get_component_by_class(unreal.SkyLightComponent)
        if component:
            component.set_editor_property("intensity", 1.2)

    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(-8200.0, -9800.0, 5200.0),
        unreal.Rotator(-17.0, 40.0, 0.0),
    )
    if camera:
        camera.set_actor_label(PREFIX + "ReviewCamera_Coast")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_asset(TARGET_MAP, False)

    readiness = director.get_readiness()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    revision = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    class_names = [actor.get_class().get_name() for actor in revision]
    forbidden_exact_classes = {
        "WaterBodyOcean",
        "WaterZone",
        "CustomBrush_Landmass",
        "VolumetricCloudRenderingComponent",
    }
    checks = {
        "separate_v4_map_saved": unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP),
        "governed_refined_assets_reused": len(placed) > 0,
        "pathfinder_bindings_complete": bindings == required,
        "native_production_director_present": director is not None,
        "six_ocean_tiles": int(readiness.ocean_tile_count) == 6,
        "six_beach_tiles": int(readiness.beach_tile_count) == 6,
        "six_land_tiles": int(readiness.land_tile_count) == 6,
        "continuous_coastline": bool(readiness.continuous_coastline),
        "route_exclusion_valid": bool(readiness.route_exclusion_valid),
        "stable_atmosphere_stack": all(
            actor is not None for actor in (atmosphere, cloud, fog, wind, sun, skylight)
        ),
        "no_unstable_plugin_actor_classes": not any(
            name in forbidden_exact_classes for name in class_names
        ),
    }
    report = {
        "schema": "skyguard.phase4.m01-production-environment-build.v1",
        "target_map": TARGET_MAP,
        "manifest": str(MANIFEST_PATH),
        "governed_asset_count": len(expected),
        "placed_non_boss_asset_count": len(placed),
        "revision_actor_count": len(revision),
        "revision_actor_labels": sorted(
            actor.get_actor_label() for actor in revision
        ),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "rendered_limitations": [
            "NullRHI build cannot validate ocean shading, coastline transitions, cloud/fog appearance, shadows, or horizon seams",
            "PCG-ready inclusion/exclusion bounds are native and deterministic; an authored PCG graph and final licensed vegetation library remain follow-up content",
            "The stable ocean is a tiled material-mesh surface; final wave displacement, foam, wakes, depth color and wet shoreline blending require a visible GPU pass",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardPhase4] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Phase 4 Mission 1 production environment build failed")


if __name__ == "__main__":
    main()
