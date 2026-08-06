"""Fresh-process persistence and differentiation audit for M08-M10 maps."""

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_skyguard_phase7_wave3_mission_maps as source


REPORT_PATH = (
    ROOT / "Saved/Reports/PHASE7_WAVE3_MISSION_MAP_PERSISTENCE_AUDIT.json"
)


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
    route_signatures = set()
    skyline_styles = set()
    layout_signatures = set()
    objective_signatures = set()

    for spec in source.MAP_SPECS:
        prefix = "P7W3_%s_" % spec["short"]
        checks = {
            "map_exists": unreal.EditorAssetLibrary.does_asset_exist(spec["map"])
        }
        if (
            not checks["map_exists"]
            or not unreal.EditorLevelLibrary.load_level(spec["map"])
        ):
            failures.append("Missing or unloadable map: " + spec["map"])
            map_reports.append({"map": spec["map"], "checks": checks})
            continue

        actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
        owned = [
            actor
            for actor in actors
            if (actor.get_actor_label() or "").startswith(prefix)
        ]
        directors = [
            actor
            for actor in owned
            if actor.get_class().get_name()
            == "SkyguardMissionMapAssemblyDirector"
        ]
        checks["single_native_director"] = len(directors) == 1
        if len(directors) != 1:
            failures.append("Expected one native director in " + spec["map"])
            map_reports.append({"map": spec["map"], "checks": checks})
            continue
        director = directors[0]

        valid, errors = normalize_validation(director.validate_assembly())
        checks["native_assembly_validation"] = valid and not errors
        definition = director.get_editor_property("mission_definition")
        checks["definition_reference"] = (
            definition is not None
            and definition.get_path_name().split(".", 1)[0]
            == spec["mission_asset"]
        )
        checks["mission_identity"] = (
            str(director.get_editor_property("mission_id"))
            == spec["mission_id"]
        )
        checks["assembly_revision"] = (
            str(director.get_editor_property("assembly_revision"))
            == source.REVISION
        )

        route_points = [
            vector_tuple(point)
            for point in director.get_editor_property("route_points")
        ]
        route_signatures.add(tuple(route_points))
        checks["four_point_distinct_route"] = len(route_points) == 4

        style = str(director.get_editor_property("skyline_style"))
        skyline_styles.add(style)
        checks["expected_skyline_family"] = spec["style"].replace("_", "") in (
            style.replace("_", "").upper()
        )

        landmarks = list(director.get_editor_property("landmark_anchors"))
        landmark_roles = {
            str(item.get_editor_property("role")) for item in landmarks
        }
        landmark_ids = [
            str(item.get_editor_property("landmark_id")) for item in landmarks
        ]
        exclusive_count = sum(
            1
            for item in landmarks
            if bool(item.get_editor_property("mission_exclusive"))
        )
        checks["landmark_contract"] = (
            len(landmarks) >= 4
            and len(set(landmark_ids)) == len(landmark_ids)
            and exclusive_count >= 3
        )
        checks["required_hero_roles"] = set(spec["required_roles"]).issubset(
            landmark_roles
        )

        expected_labels = {
            prefix + placement[0] for placement in spec["placements"]
        }
        actual_labels = {actor.get_actor_label() for actor in owned}
        checks["all_hero_proxies_present"] = expected_labels.issubset(
            actual_labels
        )
        checks["boss_proxy_present"] = any(
            label.startswith(prefix + "Boss_") for label in actual_labels
        )

        objective_targets = [
            actor
            for actor in owned
            if unreal.Name("Skyguard.CampaignMap.ObjectiveAnchor")
            in list(actor.get_editor_property("tags") or [])
        ]
        objective_signature = tuple(
            sorted(
                (
                    actor.get_actor_label().replace(prefix, "", 1),
                    vector_tuple(actor.get_actor_location()),
                )
                for actor in objective_targets
            )
        )
        objective_signatures.add(objective_signature)
        checks["objective_target_count"] = (
            len(objective_targets) == len(spec["objective_locations"])
        )

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
        checks["minimum_spatial_density"] = len(owned) >= 35

        readiness = director.get_readiness()
        checks["native_readiness"] = (
            bool(readiness.definition_valid)
            and bool(readiness.route_matches_definition)
            and bool(readiness.required_objectives_anchored)
            and bool(readiness.weather_matches_definition)
            and bool(readiness.landmarks_distinct)
            and int(readiness.mission_exclusive_landmark_count) >= 3
        )

        mission = unreal.EditorAssetLibrary.load_asset(spec["mission_asset"])
        mission_map = (
            str(mission.get_editor_property("mission_map")) if mission else ""
        )
        checks["mission_dataasset_map_binding"] = spec["map"] in mission_map

        failed = [key for key, passed in checks.items() if not passed]
        if failed:
            failures.append(
                "%s failed: %s" % (spec["mission_id"], ", ".join(failed))
            )
        map_reports.append(
            {
                "map": spec["map"],
                "mission_id": spec["mission_id"],
                "owned_actor_count": len(owned),
                "route_points": route_points,
                "skyline_style": style,
                "landmark_ids": landmark_ids,
                "landmark_roles": sorted(landmark_roles),
                "objective_signature": objective_signature,
                "native_validation_errors": errors,
                "checks": checks,
                "content_state": (
                    "distinct_spatial_gameplay_assembly_with_proxy_art"
                ),
            }
        )

    global_checks = {
        "three_maps_loaded": len(map_reports) == 3
        and all(item["checks"].get("map_exists") for item in map_reports),
        "routes_are_distinct": len(route_signatures) == 3,
        "skyline_families_are_distinct": len(skyline_styles) == 3,
        "layouts_are_not_clones": len(layout_signatures) == 3,
        "objective_placements_are_distinct": len(objective_signatures) == 3,
        "target_paths_are_distinct": len(
            {spec["map"] for spec in source.MAP_SPECS}
        )
        == 3,
    }
    for key, passed in global_checks.items():
        if not passed:
            failures.append("Global differentiation failed: " + key)

    report = {
        "schema": "skyguard.phase7.wave3-map-audit.v1",
        "gate": "PASS" if not failures else "FAIL",
        "revision": source.REVISION,
        "spec_sha256": source.canonical_spec_hash(),
        "accepted_target_paths": [spec["map"] for spec in source.MAP_SPECS],
        "global_checks": global_checks,
        "maps": map_reports,
        "failures": failures,
        "limitations": [
            "Rescue helicopter, rafts, rescue vessel, metro, power station, bridge, ferry, evacuation ship, convoy hub and bosses remain proxies.",
            "This audit proves persisted differentiation and native assembly integrity, not final art, animation, mission behavior, GPU quality, or packaged playability.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE3_MAP_AUDIT " + json.dumps(report, sort_keys=True))
    if failures:
        raise RuntimeError("Wave 3 map audit failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
