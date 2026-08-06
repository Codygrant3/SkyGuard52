"""Independently reopen and verify the persisted Mission 1 Wave 1 candidate."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
AUDIT_PATH = ROOT / "Saved/Reports/M01_WAVE1_UNREAL_AUDIT.json"
VERIFY_PATH = ROOT / "Saved/Reports/M01_WAVE1_PERSISTENCE_AUDIT.json"
DEST_PATH = "/Game/Skyguard/Meshes/Mission01/Wave1Coast"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Validation"
PREFIX = "M01_W1_"


def main():
    with open(AUDIT_PATH, "r", encoding="utf-8") as stream:
        source_audit = json.load(stream)

    loaded = unreal.EditorLevelLibrary.load_level(MAP_PATH)
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    labeled = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    bosses = [
        actor for actor in labeled
        if actor.get_actor_label() == PREFIX + "Boss_Pathfinder_Live"
    ]
    bindings = {}
    if len(bosses) == 1:
        for component in bosses[0].get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            bindings[component.get_name()] = mesh.get_name() if mesh else None

    mesh_paths = {}
    for path in unreal.EditorAssetLibrary.list_assets(DEST_PATH, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            mesh_paths[asset.get_name()] = path

    expected_bindings = source_audit["required_pathfinder_mesh_bindings"]
    checks = {
        "map_loaded": bool(loaded),
        "persisted_actor_count_matches": (
            len(labeled) == source_audit["validation_actor_count"]
        ),
        "single_pathfinder_persisted": len(bosses) == 1,
        "persisted_pathfinder_meshes_bound": all(
            bindings.get(component) == mesh
            for component, mesh in expected_bindings.items()
        ),
        "persisted_static_mesh_count_matches": (
            len(mesh_paths) == source_audit["static_mesh_count"] == 36
        ),
        "persisted_mesh_paths_match": mesh_paths == source_audit["mesh_paths"],
    }
    report = {
        "schema": "skyguard.m01.wave1.persistence-audit.v1",
        "map": MAP_PATH,
        "asset_root": DEST_PATH,
        "persisted_validation_actor_count": len(labeled),
        "persisted_static_mesh_count": len(mesh_paths),
        "persisted_pathfinder_mesh_bindings": bindings,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "mission01_wave1_candidate_not_final_aaa_acceptance",
    }
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VERIFY_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardM01Persistence] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 Wave 1 persistence gate failed")


if __name__ == "__main__":
    main()
