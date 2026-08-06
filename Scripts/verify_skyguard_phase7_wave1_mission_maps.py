"""Fresh-process persistence and differentiation audit for M02-M04 maps."""

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_skyguard_phase7_wave1_mission_maps as source


REPORT_PATH = ROOT / "Saved/Reports/PHASE7_WAVE1_MISSION_MAP_PERSISTENCE_AUDIT.json"


def normalize_validation(result):
    if isinstance(result, tuple):
        return bool(result[0]), [str(item) for item in result[1]]
    if isinstance(result, list) or type(result).__name__.endswith("Array"):
        errors = [str(item) for item in result]
        return not errors, errors
    return bool(result), []


def vector_tuple(vector):
    return (
        round(float(vector.x), 2),
        round(float(vector.y), 2),
        round(float(vector.z), 2),
    )


def main():
    failures = []
    map_reports = []
    layout_signatures = set()
    skyline_styles = set()
    route_signatures = set()

    for spec in source.MAP_SPECS:
        prefix = "P7W1_%s_" % spec["short"]
        checks = {
            "map_exists": unreal.EditorAssetLibrary.does_asset_exist(spec["map"])
        }
        if not checks["map_exists"] or not unreal.EditorLevelLibrary.load_level(spec["map"]):
            failures.append("Missing or unloadable map: " + spec["map"])
            map_reports.append({"map": spec["map"], "checks": checks})
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
            failures.append("No native director in " + spec["map"])
            map_reports.append({"map": spec["map"], "checks": checks})
            continue
        director = directors[0]

        valid, errors = normalize_validation(director.validate_assembly())
        checks["native_assembly_validation"] = valid and not errors
        definition = director.get_editor_property("mission_definition")
        checks["definition_reference"] = (
            definition is not None
            and definition.get_path_name().split(".", 1)[0] == spec["mission_asset"]
        )
        checks["mission_identity"] = (
            str(director.get_editor_property("mission_id")) == spec["mission_id"]
        )
        checks["assembly_revision"] = (
            str(director.get_editor_property("assembly_revision")) == source.REVISION
        )

        route_points = [
            vector_tuple(point)
            for point in director.get_editor_property("route_points")
        ]
        route_signatures.add(tuple(route_points))
        checks["four_point_route"] = len(route_points) == 4

        landmarks = list(director.get_editor_property("landmark_anchors"))
        landmark_ids = [
            str(anchor.get_editor_property("landmark_id"))
            for anchor in landmarks
        ]
        landmark_roles = [
            str(anchor.get_editor_property("role"))
            for anchor in landmarks
        ]
        exclusive_count = sum(
            1
            for anchor in landmarks
            if bool(anchor.get_editor_property("mission_exclusive"))
        )
        checks["landmark_contract"] = (
            len(landmarks) >= 3
            and len(set(landmark_ids)) == len(landmarks)
            and len(set(landmark_roles)) >= 3
            and exclusive_count >= 2
        )
        checks["landmarks_outside_flight_clearance"] = all(
            not director.is_point_inside_flight_clearance(
                anchor.get_editor_property("world_location")
            )
            for anchor in landmarks
        )

        objective_targets = [
            actor
            for actor in owned
            if unreal.Name("Skyguard.CampaignMap.ObjectiveAnchor")
            in list(actor.get_editor_property("tags") or [])
        ]
        checks["objective_target_count"] = (
            len(objective_targets) == len(spec["objective_locations"])
        )

        expected_hero_labels = {
            prefix + placement[0] for placement in spec["placements"]
        }
        actual_labels = {actor.get_actor_label() for actor in owned}
        checks["hero_placeholders_present"] = expected_hero_labels.issubset(
            actual_labels
        )
        checks["minimum_spatial_density"] = len(owned) >= 35

        style_text = str(director.get_editor_property("skyline_style"))
        skyline_styles.add(style_text)
        placement_signature = tuple(
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
        layout_signatures.add(placement_signature)

        readiness = director.get_readiness()
        checks["native_readiness"] = (
            bool(readiness.definition_valid)
            and bool(readiness.route_matches_definition)
            and bool(readiness.required_objectives_anchored)
            and bool(readiness.landmarks_distinct)
            and bool(readiness.weather_matches_definition)
            and int(readiness.mission_exclusive_landmark_count) >= 2
        )

        failed_checks = [key for key, passed in checks.items() if not passed]
        if failed_checks:
            failures.append(
                "%s failed: %s" % (spec["mission_id"], ", ".join(failed_checks))
            )
        map_reports.append(
            {
                "map": spec["map"],
                "mission_id": spec["mission_id"],
                "owned_actor_count": len(owned),
                "route_points": route_points,
                "skyline_style": style_text,
                "landmark_ids": landmark_ids,
                "landmark_roles": landmark_roles,
                "mission_exclusive_landmarks": exclusive_count,
                "objective_target_count": len(objective_targets),
                "native_validation_errors": errors,
                "checks": checks,
                "content_state": "spatial_gameplay_assembly_with_placeholder_art",
            }
        )

    global_checks = {
        "three_maps_loaded": len(map_reports) == 3
        and all(report["checks"].get("map_exists") for report in map_reports),
        "routes_are_distinct": len(route_signatures) == 3,
        "skyline_styles_are_distinct": len(skyline_styles) == 3,
        "layouts_are_not_clones": len(layout_signatures) == 3,
        "target_paths_are_distinct": len({spec["map"] for spec in source.MAP_SPECS}) == 3,
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
        "maps": map_reports,
        "failures": failures,
        "limitations": [
            "Proxy meshes, engine primitives, and simple materials remain visible.",
            "This audit does not prove final art, full objectives, enemy waves, bosses, lighting, audio, cinematics, streaming, navigation, or packaged playability.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE1_MAP_AUDIT " + json.dumps(report, sort_keys=True))
    if failures:
        raise RuntimeError("Phase 7 Wave 1 map audit failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
