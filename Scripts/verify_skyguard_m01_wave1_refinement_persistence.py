"""Reopen the isolated refinement map and verify saved assets and bindings."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_AUDIT_PATH = ROOT / "Saved/Reports/M01_WAVE1_REFINEMENT_UNREAL_AUDIT.json"
VERIFY_PATH = ROOT / "Saved/Reports/M01_WAVE1_REFINEMENT_PERSISTENCE_AUDIT.json"
DEST_PATH = "/Game/Skyguard/Meshes/Mission01/Wave1Refinement"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Refinement_Validation"
PREFIX = "M01_W1R_"


def main():
    with open(SOURCE_AUDIT_PATH, "r", encoding="utf-8") as stream:
        source_audit = json.load(stream)

    loaded = unreal.EditorLevelLibrary.load_level(MAP_PATH)
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    labeled = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    bosses = [
        actor for actor in labeled
        if actor.get_actor_label() == PREFIX + "Boss_Pathfinder_Live_AAA"
    ]

    bindings = {}
    if len(bosses) == 1:
        for component in bosses[0].get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            bindings[component.get_name()] = mesh.get_name() if mesh else None

    meshes = {}
    paths = {}
    nanite_enabled = []
    complex_as_simple = []
    for path in unreal.EditorAssetLibrary.list_assets(DEST_PATH, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(asset, unreal.StaticMesh):
            continue
        name = asset.get_name()
        meshes[name] = asset
        paths[name] = path
        if asset.get_editor_property("nanite_settings").enabled:
            nanite_enabled.append(name)
        body_setup = asset.get_editor_property("body_setup")
        if (
            body_setup.get_editor_property("collision_trace_flag")
            == unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
        ):
            complex_as_simple.append(name)

    expected_bindings = source_audit["required_pathfinder_mesh_bindings"]
    expected_nanite = sorted(
        name
        for name, result in source_audit["nanite_results"].items()
        if result["enabled"]
    )
    expected_complex = sorted(
        name
        for name, result in source_audit["collision_results"].items()
        if result["contract"] == "complex_as_simple"
    )
    checks = {
        "map_loaded": bool(loaded),
        "persisted_actor_count_matches": (
            len(labeled) == source_audit["validation_actor_count"] == 17
        ),
        "single_refined_pathfinder_persisted": len(bosses) == 1,
        "refined_pathfinder_bindings_persisted": all(
            bindings.get(component) == mesh
            for component, mesh in expected_bindings.items()
        ),
        "all_refined_meshes_persisted": len(meshes) == 20,
        "mesh_paths_persisted": paths == source_audit["mesh_paths"],
        "selective_nanite_policy_persisted": sorted(nanite_enabled) == expected_nanite,
        "complex_as_simple_policy_persisted": (
            sorted(complex_as_simple) == expected_complex
        ),
    }
    report = {
        "schema": "skyguard.m01.wave1.refinement.persistence-audit.v1",
        "map": MAP_PATH,
        "asset_root": DEST_PATH,
        "persisted_validation_actor_count": len(labeled),
        "persisted_static_mesh_count": len(meshes),
        "persisted_pathfinder_mesh_bindings": bindings,
        "persisted_nanite_enabled_assets": sorted(nanite_enabled),
        "persisted_complex_as_simple_assets": sorted(complex_as_simple),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "refinement_candidate_requires_rendered_visual_and_runtime_performance_acceptance",
    }
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VERIFY_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardM01RefinementPersistence] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 refinement persistence gate failed")


if __name__ == "__main__":
    main()
