"""Reload and verify the isolated Yak-52 runtime parent map."""

from __future__ import annotations

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
MAP_PATH = "/Game/Skyguard/Maps/Lvl_Yak52_RuntimeAssembly_v1"
REPORT_PATH = ROOT / "Saved/Reports/PHASE2_YAK_RUNTIME_PERSISTENCE.json"


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Missing Yak runtime map: " + MAP_PATH)
    if not unreal.EditorLevelLibrary.load_level(MAP_PATH):
        raise RuntimeError("Could not load Yak runtime map: " + MAP_PATH)

    actors = [
        actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if actor.get_actor_label() == "PHASE2_Yak52_RuntimeParent"
    ]
    aircraft = actors[0] if len(actors) == 1 else None
    components = (
        list(aircraft.get_components_by_class(unreal.ActorComponent))
        if aircraft
        else []
    )
    by_name = {component.get_name(): component for component in components}
    mesh_components = [
        component
        for component in components
        if isinstance(component, unreal.StaticMeshComponent)
    ]

    rear_eye = by_name.get("SO_RearEye")
    rear_weapon = by_name.get("SO_RearWeaponMount")
    pilot_blocker = by_name.get("PilotProtection")
    cockpit_blocker = by_name.get("CockpitProtection")
    rear_eye_location = (
        rear_eye.get_editor_property("relative_location") if rear_eye else None
    )
    rear_weapon_location = (
        rear_weapon.get_editor_property("relative_location") if rear_weapon else None
    )
    checks = {
        "single_runtime_parent_persisted": len(actors) == 1,
        "all_core_meshes_persisted": (
            len(mesh_components) == 11
            and all(
                component.get_editor_property("static_mesh") is not None
                for component in mesh_components
            )
        ),
        "rear_eye_marker_persisted": (
            rear_eye_location is not None
            and abs(rear_eye_location.x - -65.0) < 0.01
            and abs(rear_eye_location.y - -64.0) < 0.01
            and abs(rear_eye_location.z - 102.0) < 0.01
        ),
        "rear_weapon_marker_persisted": (
            rear_weapon_location is not None
            and abs(rear_weapon_location.x - -32.0) < 0.01
            and abs(rear_weapon_location.y - -64.0) < 0.01
            and abs(rear_weapon_location.z - 60.0) < 0.01
        ),
        "pilot_and_cockpit_shot_blockers_persisted": (
            isinstance(pilot_blocker, unreal.BoxComponent)
            and isinstance(cockpit_blocker, unreal.BoxComponent)
        ),
    }
    report = {
        "schema": "skyguard.phase2.yak-runtime-persistence.v1",
        "map": MAP_PATH,
        "actor_count": len(actors),
        "component_count": len(components),
        "static_mesh_component_count": len(mesh_components),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "HOLD",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardPhase2] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Yak runtime persistence gate failed")


if __name__ == "__main__":
    main()
