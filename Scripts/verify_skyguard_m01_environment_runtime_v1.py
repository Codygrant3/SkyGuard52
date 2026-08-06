"""Round-trip structural audit for the isolated Mission 1 environment map."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Environment_Runtime_v3"
REPORT_PATH = ROOT / "Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_AUDIT.json"
PREFIX = "M01_ENV1_"
CAPABILITY_TAGS = (
    "Skyguard.Environment.Water",
    "Skyguard.Environment.Landmass",
    "Skyguard.Environment.PCG",
    "Skyguard.Environment.Atmosphere",
    "Skyguard.Environment.Cloud",
    "Skyguard.Environment.Fog",
    "Skyguard.Environment.Wind",
)


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Missing environment map: " + MAP_PATH)
    if not unreal.EditorLevelLibrary.load_level(MAP_PATH):
        raise RuntimeError("Could not load environment map: " + MAP_PATH)

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    revision = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    directors = [
        actor for actor in revision
        if actor.get_class().get_name() == "SkyguardCoastalEnvironmentDirector"
    ]
    tag_counts = {
        tag: sum(
            1 for actor in actors
            if unreal.Name(tag) in list(actor.get_editor_property("tags") or [])
        )
        for tag in CAPABILITY_TAGS
    }
    director_state = {}
    if directors:
        director = directors[0]
        try:
            director.refresh_capability_bindings()
            readiness = director.get_readiness()
            vfx_pool = director.get_editor_property("vfx_pool")
            configured_pool_capacity = (
                int(vfx_pool.get_editor_property("pool_capacity"))
                if vfx_pool else 0
            )
            configured_vfx_system_count = sum(
                1
                for property_name in (
                    "smoke_system",
                    "fire_system",
                    "sparks_system",
                    "explosion_system",
                )
                if vfx_pool
                and vfx_pool.get_editor_property(property_name) is not None
            )
            director_state = {
                "bound_capability_count": int(readiness.bound_capability_count),
                "tree_instance_count": int(readiness.tree_instance_count),
                "shrub_instance_count": int(readiness.shrub_instance_count),
                "vfx_pool_size": int(readiness.vfx_pool_size),
                "configured_vfx_pool_capacity": configured_pool_capacity,
                "configured_vfx_system_count": configured_vfx_system_count,
                "vfx_allocation_phase": "BeginPlay/runtime",
                "route_corridor_safe": bool(
                    director.is_vegetation_outside_route_corridor()
                ),
            }
        except Exception as exc:
            director_state = {"inspection_error": str(exc)}

    labels = sorted(actor.get_actor_label() for actor in revision)
    checks = {
        "map_round_trip_loaded": True,
        "single_native_director": len(directors) == 1,
        "all_capability_tags_present": all(value > 0 for value in tag_counts.values()),
        "water_plugin_or_fallback_present": any(
            "Water" in actor.get_class().get_name()
            or "OceanVisibleFallback" in actor.get_actor_label()
            for actor in revision
        ),
        "atmosphere_present": any(
            actor.get_class().get_name() == "SkyAtmosphere" for actor in revision
        ),
        "volumetric_cloud_present": any(
            actor.get_class().get_name() == "VolumetricCloud" for actor in revision
        ),
        "volumetric_fog_present": any(
            actor.get_class().get_name() == "ExponentialHeightFog" for actor in revision
        ),
        "route_corridor_safe": director_state.get("route_corridor_safe") is True,
        # A round-trip editor load does not run BeginPlay. Validate the fixed
        # pool configuration here; native automation validates runtime
        # allocation and repeated round-robin activation.
        "fixed_vfx_pool_configured": (
            director_state.get("configured_vfx_pool_capacity", 0) > 0
            and director_state.get("configured_vfx_system_count", 0) == 4
        ),
    }
    report = {
        "schema": "skyguard.m01.environment-runtime-audit.v1",
        "map": MAP_PATH,
        "revision_actor_count": len(revision),
        "revision_actor_labels": labels,
        "capability_tag_counts": tag_counts,
        "director_state": director_state,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "profile_note": (
            "Native automation logs CPU timings for deterministic vegetation rebuild "
            "and one hundred fixed-pool Niagara activations. GPU/render timing still "
            "requires a visible-editor or packaged Development run."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardM01EnvironmentAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 environment round-trip audit failed")


if __name__ == "__main__":
    main()
