"""Fresh-process audit for distinct M05-M07 campaign assembly maps."""

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_skyguard_phase7_wave1_mission_maps as shared
import build_skyguard_phase7_wave2_mission_maps as source


REPORT_PATH = ROOT / "Saved/Reports/PHASE7_WAVE2_MISSION_MAP_PERSISTENCE_AUDIT.json"


def vector_tuple(vector):
    return (
        round(float(vector.x), 2),
        round(float(vector.y), 2),
        round(float(vector.z), 2),
    )


def main():
    failures = []
    reports = []
    route_signatures = set()
    layout_signatures = set()
    skyline_styles = set()
    weather_profiles = set()
    boss_spawns = set()
    objective_layouts = set()

    for spec in source.MAP_SPECS:
        prefix = "P7W2_%s_" % spec["short"]
        checks = {
            "map_exists": unreal.EditorAssetLibrary.does_asset_exist(spec["map"])
        }
        if not checks["map_exists"] or not unreal.EditorLevelLibrary.load_level(spec["map"]):
            failures.append("Missing or unloadable map: " + spec["map"])
            reports.append({"map": spec["map"], "checks": checks})
            continue

        actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
        owned = [
            actor for actor in actors
            if (actor.get_actor_label() or "").startswith(prefix)
        ]
        directors = [
            actor for actor in owned
            if actor.get_class().get_name() == "SkyguardMissionMapAssemblyDirector"
        ]
        checks["single_native_director"] = len(directors) == 1
        if not directors:
            failures.append("Missing native director: " + spec["map"])
            reports.append({"map": spec["map"], "checks": checks})
            continue
        director = directors[0]

        valid, validation_errors = shared.normalize_validation(
            director.validate_assembly()
        )
        checks["native_validation"] = valid and not validation_errors
        definition = director.get_editor_property("mission_definition")
        checks["definition_reference"] = (
            definition is not None
            and definition.get_path_name().split(".", 1)[0] == spec["mission_asset"]
        )
        checks["mission_identity"] = (
            str(director.get_editor_property("mission_id")) == spec["mission_id"]
        )
        checks["revision"] = (
            str(director.get_editor_property("assembly_revision")) == source.REVISION
        )

        route = tuple(
            vector_tuple(point)
            for point in director.get_editor_property("route_points")
        )
        route_signatures.add(route)
        checks["route"] = len(route) == 4

        style = str(director.get_editor_property("skyline_style"))
        weather = str(director.get_editor_property("weather_profile_id"))
        skyline_styles.add(style)
        weather_profiles.add(weather)
        checks["style"] = spec["style"].replace("_", "") in style.upper().replace("_", "")

        landmarks = list(director.get_editor_property("landmark_anchors"))
        roles = {
            str(anchor.get_editor_property("role"))
            for anchor in landmarks
        }
        exclusive = sum(
            1 for anchor in landmarks
            if bool(anchor.get_editor_property("mission_exclusive"))
        )
        checks["landmark_contract"] = (
            len(landmarks) >= 4 and len(roles) >= 4 and exclusive >= 2
        )
        checks["landmark_clearance"] = all(
            not director.is_point_inside_flight_clearance(
                anchor.get_editor_property("world_location")
            )
            for anchor in landmarks
        )

        objective_targets = [
            actor for actor in owned
            if unreal.Name("Skyguard.CampaignMap.ObjectiveAnchor")
            in list(actor.get_editor_property("tags") or [])
        ]
        objective_signature = tuple(
            sorted(vector_tuple(actor.get_actor_location()) for actor in objective_targets)
        )
        objective_layouts.add(objective_signature)
        checks["objective_targets"] = (
            len(objective_targets) == len(spec["objectives"])
        )

        boss_targets = [
            actor for actor in owned
            if unreal.Name("Skyguard.CampaignMap.BossSpawn")
            in list(actor.get_editor_property("tags") or [])
        ]
        checks["single_boss_spawn"] = len(boss_targets) == 1
        if boss_targets:
            persisted_boss_spawn = vector_tuple(boss_targets[0].get_actor_location())
            boss_spawns.add(persisted_boss_spawn)
            checks["boss_spawn_location"] = persisted_boss_spawn == tuple(
                float(value) for value in spec["boss_spawn"]
            )

        placeholder_signature = tuple(
            sorted(
                (
                    actor.get_actor_label().replace(prefix, "", 1),
                    vector_tuple(actor.get_actor_location()),
                )
                for actor in owned
                if unreal.Name("Skyguard.CampaignMap.Placeholder")
                in list(actor.get_editor_property("tags") or [])
            )
        )
        layout_signatures.add(placeholder_signature)
        checks["minimum_spatial_density"] = len(owned) >= 24

        readiness = director.get_readiness()
        checks["readiness"] = (
            bool(readiness.definition_valid)
            and bool(readiness.route_matches_definition)
            and bool(readiness.required_objectives_anchored)
            and bool(readiness.landmarks_distinct)
            and bool(readiness.weather_matches_definition)
        )

        failed = [key for key, passed in checks.items() if not passed]
        if failed:
            failures.append(
                "%s failed: %s" % (spec["mission_id"], ", ".join(failed))
            )
        reports.append(
            {
                "map": spec["map"],
                "mission_id": spec["mission_id"],
                "owned_actor_count": len(owned),
                "route": route,
                "skyline_style": style,
                "weather_profile_id": weather,
                "landmark_roles": sorted(roles),
                "exclusive_landmarks": exclusive,
                "objective_target_count": len(objective_targets),
                "boss_spawn": (
                    vector_tuple(boss_targets[0].get_actor_location())
                    if boss_targets else None
                ),
                "native_validation_errors": validation_errors,
                "checks": checks,
                "content_state": "spatial_gameplay_assembly_with_placeholder_art",
            }
        )

    global_checks = {
        "three_maps_loaded": len(reports) == 3
        and all(item["checks"].get("map_exists") for item in reports),
        "routes_are_distinct": len(route_signatures) == 3,
        "layouts_are_not_clones": len(layout_signatures) == 3,
        "skyline_styles_are_distinct": len(skyline_styles) == 3,
        "weather_profiles_are_distinct": len(weather_profiles) == 3,
        "objective_layouts_are_distinct": len(objective_layouts) == 3,
        "boss_spawns_are_distinct": len(boss_spawns) == 3,
    }
    for key, passed in global_checks.items():
        if not passed:
            failures.append("Global differentiation failed: " + key)

    report = {
        "gate": "PASS" if not failures else "FAIL",
        "revision": source.REVISION,
        "content_scope": "spatial_gameplay_assemblies_with_placeholder_art",
        "spec_sha256": source.canonical_spec_hash(),
        "accepted_target_paths": [spec["map"] for spec in source.MAP_SPECS],
        "global_checks": global_checks,
        "maps": reports,
        "failures": failures,
        "limitations": [
            "Proxy meshes, engine primitives, and simple materials remain visible.",
            "Weather identity is persisted as governed data but final weather presentation is not implemented.",
            "No claim is made for final art, full gameplay, audio, cinematics, streaming, performance, or packaged playability.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE2_MAP_AUDIT " + json.dumps(report, sort_keys=True))
    if failures:
        raise RuntimeError("Phase 7 Wave 2 map audit failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
