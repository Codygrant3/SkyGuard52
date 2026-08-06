"""Fresh-process editor acceptance for the governed M01 Landscape + PCG graph.

This script is read-only. It loads and audits the immutable v5 map and graph,
then proves generation stayed locked with licensed mesh slots empty.
"""

import json
from collections import Counter
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE4_M01_PCG_LANDSCAPE_AUTHORING_CONTRACT.json"
)
REPORT_PATH = (
    ROOT / "Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_EDITOR_ACCEPTANCE.json"
)


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    targets = contract["serialized_targets"]
    graph_contract = contract["graph_contract"]
    map_path = targets["map"]
    graph_path = targets["pcg_graph"]

    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        raise RuntimeError("Missing governed v5 Landscape map: " + map_path)
    if not unreal.EditorAssetLibrary.does_asset_exist(graph_path):
        raise RuntimeError("Missing governed authored PCG graph: " + graph_path)
    if not unreal.EditorLevelLibrary.load_level(map_path):
        raise RuntimeError("Could not round-trip governed v5 Landscape map")

    graph = unreal.load_asset(graph_path)
    if graph is None or graph.get_class().get_name() != "PCGGraph":
        raise RuntimeError("Governed PCG path did not load as PCGGraph")

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    landscape_tag = unreal.Name(targets["landscape_actor_tag"])
    landscapes = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        in {"Landscape", "LandscapeStreamingProxy"}
        and landscape_tag in list(actor.get_editor_property("tags") or [])
    ]
    directors = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission01EnvironmentDirector"
        and actor.get_actor_label() == targets["director_actor_label"]
    ]

    authoring = getattr(
        unreal, "SkyguardMission01EnvironmentAuthoringLibrary", None
    )
    if authoring is None:
        raise RuntimeError("Native Phase 4 editor audit bridge unavailable")
    audit = (
        authoring.audit_governed_landscape_and_graph(directors[0])
        if len(directors) == 1
        else None
    )

    present_counts = Counter(
        list(audit.graph_node_setting_classes) if audit else []
    )
    required_counts = graph_contract["required_node_type_counts"]
    landscape = landscapes[0] if len(landscapes) == 1 else None
    landscape_label_exact = bool(
        landscape
        and landscape.get_actor_label()
        == targets["landscape_actor_label"]
    )
    checks = {
        "target_map_round_trip_loaded": True,
        "exactly_one_landscape_actor": len(landscapes) == 1,
        "landscape_label_and_tag_exact": landscape_label_exact,
        "landscape_guid_valid": bool(audit and audit.landscape_guid_valid),
        "landscape_component_grid_is_8_by_2": bool(
            audit and int(audit.landscape_component_count) == 16
        ),
        "landscape_transform_exact": bool(
            audit and audit.landscape_transform_exact
        ),
        "exactly_one_environment_director": len(directors) == 1,
        "authored_pcg_graph_serialized": graph is not None,
        "all_required_graph_node_types_present": all(
            present_counts.get(node_type, 0) == count
            for node_type, count in required_counts.items()
        ),
        "graph_topology_valid": bool(audit and audit.graph_contract_valid),
        "director_structural_handoff_ready": bool(
            audit and audit.authored_structure_ready
        ),
        "licensed_mesh_slots_intentionally_empty": bool(
            audit
            and audit.licensed_mesh_slots_empty
            and graph_contract["licensed_mesh_slots"] == []
        ),
        "pcg_generation_locked": bool(audit and audit.generation_locked),
        "pcg_instance_count_at_or_below_1024": bool(
            audit
            and int(audit.generated_pcg_instance_count)
            <= int(graph_contract["spawn_limits"][
                "maximum_generated_instances"
            ])
        ),
        "route_and_beach_have_zero_generated_instances": bool(
            audit and audit.route_and_beach_generated_instances_zero
        ),
        "native_audit_passed": bool(audit and audit.success),
    }
    report = {
        "schema": (
            "skyguard.phase4.m01-pcg-landscape-editor-acceptance.v2"
        ),
        "map": map_path,
        "graph": graph_path,
        "graph_setting_classes": (
            sorted(list(audit.graph_node_setting_classes)) if audit else []
        ),
        "landscape_actor_count": len(landscapes),
        "director_count": len(directors),
        "generated_pcg_component_count": (
            int(audit.generated_pcg_component_count) if audit else -1
        ),
        "generated_pcg_instance_count": (
            int(audit.generated_pcg_instance_count) if audit else -1
        ),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": {
            "serialized_p4_4_handoff_complete": all(checks.values()),
            "production_vegetation_complete": False,
            "visible_gpu_accepted": False,
            "aaa_accepted": False,
        },
        "rendered_review_status": "PENDING_VISIBLE_GPU_REVIEW",
        "limitations": [
            "Licensed vegetation slots are intentionally empty.",
            "PCG generation remains locked and no output was generated or baked.",
            "NullRHI cannot establish Landscape or vegetation visual quality or GPU cost.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log(
        "[SkyguardPhase4PCGLandscapeEditor] " + json.dumps(report)
    )
    if report["gate"] != "PASS":
        raise RuntimeError("M01 Landscape/PCG editor acceptance failed")


if __name__ == "__main__":
    main()
