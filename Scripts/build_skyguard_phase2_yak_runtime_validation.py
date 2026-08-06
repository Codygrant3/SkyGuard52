"""Stage the C++ Yak-52 runtime parent in an isolated validation map."""

from __future__ import annotations

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
MAP_PATH = "/Game/Skyguard/Maps/Lvl_Yak52_RuntimeAssembly_v1"
REPORT_PATH = ROOT / "Saved/Reports/PHASE2_YAK_RUNTIME_BUILD.json"


def add_light(light_class, label, location, rotation, intensity):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        light_class, unreal.Vector(*location), unreal.Rotator(*rotation)
    )
    if actor:
        actor.set_actor_label(label)
        component = actor.get_component_by_class(unreal.LightComponent)
        if component:
            component.set_editor_property("intensity", intensity)
    return actor


def component_inventory(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.ActorComponent):
        row = {
            "name": component.get_name(),
            "class": component.get_class().get_name(),
        }
        if isinstance(component, unreal.SceneComponent):
            location = component.get_editor_property("relative_location")
            row["relative_location"] = [location.x, location.y, location.z]
        if isinstance(component, unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            row["static_mesh"] = mesh.get_path_name() if mesh else None
            row["collision_enabled"] = str(component.get_collision_enabled())
        rows.append(row)
    return sorted(rows, key=lambda row: row["name"])


def main():
    map_already_exists = unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH)
    aircraft_class = getattr(unreal, "SkyguardYak52Aircraft", None)
    if aircraft_class is None:
        raise RuntimeError("SkyguardYak52Aircraft class unavailable; build the editor module")

    if map_already_exists:
        if not unreal.EditorLevelLibrary.load_level(MAP_PATH):
            raise RuntimeError("Could not load existing Yak runtime validation map")
        aircraft = next(
            (
                actor
                for actor in unreal.EditorLevelLibrary.get_all_level_actors()
                if actor.get_actor_label() == "PHASE2_Yak52_RuntimeParent"
            ),
            None,
        )
        if aircraft is None:
            aircraft = unreal.EditorLevelLibrary.spawn_actor_from_class(
                aircraft_class, unreal.Vector(0.0, 0.0, 240.0), unreal.Rotator()
            )
            if aircraft is None:
                raise RuntimeError("Could not repair the existing Yak validation map")
            aircraft.set_actor_label("PHASE2_Yak52_RuntimeParent")
    else:
        if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
            raise RuntimeError("Could not create Yak runtime validation map")
        aircraft = unreal.EditorLevelLibrary.spawn_actor_from_class(
            aircraft_class, unreal.Vector(0.0, 0.0, 240.0), unreal.Rotator()
        )
        if aircraft is None:
            raise RuntimeError("Could not spawn Yak runtime parent")
        aircraft.set_actor_label("PHASE2_Yak52_RuntimeParent")

        floor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -20.0), unreal.Rotator()
        )
        if floor:
            floor.set_actor_label("PHASE2_ValidationFloor")
            floor.static_mesh_component.set_static_mesh(
                unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
            )
            floor.set_actor_scale3d(unreal.Vector(14.0, 14.0, 0.05))

        add_light(
            unreal.DirectionalLight,
            "PHASE2_Key",
            (900.0, -700.0, 1100.0),
            (-32.0, 28.0, 0.0),
            5.0,
        )
        add_light(
            unreal.RectLight,
            "PHASE2_Fill",
            (-500.0, 650.0, 700.0),
            (-10.0, -125.0, 0.0),
            3000.0,
        )

    components = component_inventory(aircraft)
    names = {row["name"] for row in components}
    mesh_rows = [row for row in components if row["class"] == "StaticMeshComponent"]
    required = {
        "Airframe",
        "Wings",
        "EngineCowling",
        "HorizontalTail",
        "VerticalTail",
        "CockpitTub",
        "RearPanel",
        "FrontCanopyGlass",
        "RearCanopyGlass",
        "PropellerHub",
        "PropellerBlade",
        "SO_RearGunnerSeat",
        "SO_RearEye",
        "SO_RearWeaponMount",
        "PilotProtection",
        "CockpitProtection",
    }
    checks = {
        "runtime_parent_spawned": aircraft is not None,
        "required_components_present": required.issubset(names),
        "all_core_visuals_bound": all(row.get("static_mesh") for row in mesh_rows),
        "all_visuals_use_governed_l88_assets": all(
            "/Game/Skyguard/Meshes/L88/" in row.get("static_mesh", "")
            for row in mesh_rows
        ),
        "map_saved": False,
    }

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard/Maps", False, True)
    checks["map_saved"] = unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH)
    report = {
        "schema": "skyguard.phase2.yak-runtime-build.v1",
        "map": MAP_PATH,
        "actor_label": aircraft.get_actor_label(),
        "component_count": len(components),
        "static_mesh_component_count": len(mesh_rows),
        "components": components,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "HOLD",
        "promotion": (
            "runtime_hierarchy_candidate_only; final topology, PBR, skeletal crew, "
            "LOD, collision, rendered visual, and performance acceptance remain required"
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardPhase2] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Yak runtime build gate failed")


if __name__ == "__main__":
    main()
