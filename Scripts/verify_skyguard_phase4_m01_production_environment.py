"""Round-trip verification for Mission 1 ProductionEnvironment_v4."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02"
REPORT_PATH = ROOT / "Saved/Reports/PHASE4_M01_PRODUCTION_ENVIRONMENT_AUDIT.json"
PREFIX = "M01_P4_"


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Missing production environment map: " + MAP_PATH)
    if not unreal.EditorLevelLibrary.load_level(MAP_PATH):
        raise RuntimeError("Could not round-trip production environment map")

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    revision = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    directors = [
        actor for actor in revision
        if actor.get_class().get_name() == "SkyguardMission01EnvironmentDirector"
    ]
    state = {}
    if len(directors) == 1:
        director = directors[0]
        readiness = director.get_readiness()
        state = {
            "ocean_tile_count": int(readiness.ocean_tile_count),
            "beach_tile_count": int(readiness.beach_tile_count),
            "land_tile_count": int(readiness.land_tile_count),
            "continuous_coastline": bool(readiness.continuous_coastline),
            "route_exclusion_valid": bool(readiness.route_exclusion_valid),
            "route_sample_rejected": not bool(
                director.is_point_allowed_for_pcg(unreal.Vector(20000.0, 0.0, 0.0))
            ),
            "beach_sample_rejected": not bool(
                director.is_point_allowed_for_pcg(unreal.Vector(20000.0, 6000.0, 0.0))
            ),
            "inland_sample_accepted": bool(
                director.is_point_allowed_for_pcg(unreal.Vector(20000.0, 12000.0, 0.0))
            ),
        }

    labels = sorted(actor.get_actor_label() for actor in revision)
    class_names = [actor.get_class().get_name() for actor in revision]
    checks = {
        "map_round_trip_loaded": True,
        "single_native_production_director": len(directors) == 1,
        "district_counts_persisted": (
            state.get("ocean_tile_count") == 6
            and state.get("beach_tile_count") == 6
            and state.get("land_tile_count") == 6
        ),
        "coastline_continuity_persisted": state.get("continuous_coastline") is True,
        "route_exclusion_persisted": state.get("route_exclusion_valid") is True,
        "pcg_samples_obey_bounds": all(
            state.get(key) is True
            for key in (
                "route_sample_rejected",
                "beach_sample_rejected",
                "inland_sample_accepted",
            )
        ),
        "no_water_or_landmass_plugin_actors": not any(
            name in {"WaterBodyOcean", "WaterZone", "CustomBrush_Landmass"}
            for name in class_names
        ),
        "governed_refined_geometry_present": any(
            label.startswith(PREFIX + "Refined_") for label in labels
        ),
        "pathfinder_present": PREFIX + "Boss_Pathfinder" in labels,
        "review_camera_present": PREFIX + "ReviewCamera_Coast" in labels,
    }
    report = {
        "schema": "skyguard.phase4.m01-production-environment-audit.v1",
        "map": MAP_PATH,
        "revision_actor_count": len(revision),
        "revision_actor_labels": labels,
        "director_state": state,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "rendered_review_status": "PENDING_VISIBLE_GPU_REVIEW",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardPhase4Audit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Phase 4 Mission 1 persistence audit failed")


if __name__ == "__main__":
    main()
