"""Offline, fail-closed P4.4 PCG/Landscape authoring-readiness verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CONTRACT_SCHEMA = "skyguard.phase4.m01-pcg-landscape-authoring-contract.v1"
MANIFEST_SCHEMA = "skyguard.phase4.m01-landscape-source-manifest.v1"
REPORT_SCHEMA = "skyguard.phase4.m01-pcg-landscape-readiness-audit.v1"
REQUIRED_NODE_TYPES = {
    "UPCGGetLandscapeSettings",
    "UPCGDataFromActorSettings",
    "UPCGSurfaceSamplerSettings",
    "UPCGDifferenceSettings",
    "UPCGDensityFilterSettings",
    "UPCGTransformPointsSettings",
    "UPCGStaticMeshSpawnerSettings",
}
REQUIRED_STAGE_ORDER = [
    "landscape_data",
    "inclusion_bounds",
    "surface_sample",
    "route_and_beach_difference",
    "density_filter",
    "deterministic_transform",
    "governed_mesh_spawn",
    "graph_output",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def evaluate(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    limitations: list[str] = []

    checks["contract_schema_valid"] = (
        contract.get("schema") == CONTRACT_SCHEMA
    )
    source = contract.get("source_heightmap", {})
    targets = contract.get("serialized_targets", {})
    handoff = contract.get("director_handoff", {})
    graph = contract.get("graph_contract", {})

    checks["governed_heightmap_shape"] = (
        source.get("width") == 505
        and source.get("height") == 127
        and source.get("components_x") == 8
        and source.get("components_y") == 2
        and source.get("sections_per_component") == 1
        and source.get("quads_per_section") == 63
    )
    checks["governed_graph_target"] = (
        targets.get("pcg_graph")
        == "/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation"
    )
    checks["governed_stage_order"] = (
        graph.get("required_stages_in_order") == REQUIRED_STAGE_ORDER
    )
    node_types = graph.get("required_node_types")
    checks["governed_node_types"] = (
        isinstance(node_types, list)
        and set(node_types) == REQUIRED_NODE_TYPES
        and len(node_types) == len(REQUIRED_NODE_TYPES)
    )
    node_counts = graph.get("required_node_type_counts")
    checks["governed_node_counts"] = (
        isinstance(node_counts, dict)
        and set(node_counts) == REQUIRED_NODE_TYPES
        and node_counts.get("UPCGDataFromActorSettings") == 2
        and all(
            isinstance(count, int) and count >= 1
            for count in node_counts.values()
        )
    )
    checks["bounded_generation_policy"] = (
        graph.get("spawn_limits", {}).get("maximum_generated_instances")
        == 1024
        and graph.get("spawn_limits", {}).get("generation_on_demand") is True
        and graph.get("spawn_limits", {}).get("runtime_regeneration") is False
    )
    checks["licensed_slots_fail_closed"] = (
        graph.get("licensed_mesh_slots") == []
        and graph.get("spawn_limits", {}).get(
            "licensed_mesh_slots_must_be_nonempty_before_generation"
        )
        is True
    )
    checks["exact_bounds_handoff"] = (
        handoff.get("inclusion_component") == "LandScatterBounds"
        and handoff.get("inclusion_component_tag") == "Skyguard.PCG.Inclusion"
        and handoff.get("exclusion_component") == "RouteExclusion"
        and handoff.get("exclusion_component_tag") == "Skyguard.PCG.Exclusion"
        and handoff.get("generation_trigger") == "GenerateOnDemand"
    )

    manifest_path = _resolve(root, str(source.get("manifest_path", "")))
    heightmap_path = _resolve(root, str(source.get("path", "")))
    manifest: dict[str, Any] = {}
    checks["heightmap_manifest_present"] = manifest_path.is_file()
    checks["heightmap_source_present"] = heightmap_path.is_file()
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"heightmap manifest could not be parsed: {exc}")
    checks["heightmap_manifest_schema"] = (
        manifest.get("schema") == MANIFEST_SCHEMA
    )
    expected_bytes = int(source.get("width", 0)) * int(
        source.get("height", 0)
    ) * 2
    checks["heightmap_manifest_dimensions"] = (
        manifest.get("width") == source.get("width")
        and manifest.get("height") == source.get("height")
        and manifest.get("sample_count")
        == int(source.get("width", 0)) * int(source.get("height", 0))
        and manifest.get("bytes") == expected_bytes
    )
    checks["heightmap_manifest_logical_path"] = (
        str(manifest.get("path", "")).replace("\\", "/")
        == str(source.get("path", "")).replace("\\", "/")
    )
    checks["heightmap_bytes"] = (
        heightmap_path.is_file() and heightmap_path.stat().st_size == expected_bytes
    )
    checks["heightmap_hash"] = (
        heightmap_path.is_file()
        and isinstance(manifest.get("sha256"), str)
        and _sha256(heightmap_path) == manifest.get("sha256")
    )

    project_path = root / "Skyguard52.uproject"
    project = {}
    if project_path.is_file():
        project = json.loads(project_path.read_text(encoding="utf-8-sig"))
    plugins = {
        item.get("Name"): item.get("Enabled")
        for item in project.get("Plugins", [])
        if isinstance(item, dict)
    }
    checks["pcg_plugin_enabled"] = plugins.get("PCG") is True

    build_source = root / "Source/Skyguard52/Skyguard52.Build.cs"
    director_header = (
        root / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h"
    )
    director_cpp = (
        root / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp"
    )
    editor_acceptance = (
        root / "Scripts/verify_skyguard_phase4_m01_pcg_landscape_assets.py"
    )
    editor_report_path = (
        root
        / "Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_EDITOR_ACCEPTANCE.json"
    )
    build_text = (
        build_source.read_text(encoding="utf-8-sig")
        if build_source.is_file()
        else ""
    )
    header_text = (
        director_header.read_text(encoding="utf-8-sig")
        if director_header.is_file()
        else ""
    )
    cpp_text = (
        director_cpp.read_text(encoding="utf-8-sig")
        if director_cpp.is_file()
        else ""
    )
    checks["pcg_and_landscape_module_dependencies"] = all(
        f'"{name}"' in build_text for name in ("Landscape", "PCG")
    )
    checks["director_binding_source_present"] = all(
        marker in header_text + cpp_text
        for marker in (
            "InlandVegetationPCG",
            "ProductionLandscape",
            "AuthoredPCGGraph",
            "Skyguard.PCG.Inclusion",
            "Skyguard.PCG.Exclusion",
            "bReadyForAuthoredPCGGeneration",
            "GenerateOnDemand",
            "PCG_M01_InlandVegetation.PCG_M01_InlandVegetation",
            "bAuthoredPCGStructureReady",
            "bLicensedVegetationLibraryApproved",
            "bAllowAuthoredPCGGeneration",
        )
    )
    checks["editor_acceptance_source_present"] = editor_acceptance.is_file()

    graph_asset = (
        root
        / "Content/Skyguard/Environment/Mission01/PCG"
        / "PCG_M01_InlandVegetation.uasset"
    )
    map_name = str(targets.get("map", "")).rsplit("/", 1)[-1]
    map_asset = root / "Content/Skyguard/Maps" / f"{map_name}.umap"
    serialized = {
        "pcg_graph_asset_present": graph_asset.is_file(),
        "target_map_asset_present": map_asset.is_file(),
    }
    editor_report: dict[str, Any] = {}
    if editor_report_path.is_file():
        try:
            editor_report = json.loads(
                editor_report_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError):
            editor_report = {}
    editor_gate_passed = (
        editor_report.get("gate") == "PASS"
        and editor_report.get("map") == targets.get("map")
        and editor_report.get("graph") == targets.get("pcg_graph")
        and editor_report.get("promotion", {}).get(
            "serialized_p4_4_handoff_complete"
        )
        is True
    )
    serialized["fresh_editor_gate_passed"] = editor_gate_passed
    if not all(serialized.values()):
        limitations.extend(
            [
                "The serialized authored PCG graph and v5 Landscape map are pending an Unreal editor authoring pass.",
                "No PCG generation or bake has been performed.",
            ]
        )
    if graph.get("licensed_mesh_slots") == []:
        limitations.append(
            "Licensed vegetation slots are intentionally empty; generation remains prohibited."
        )

    failed = [name for name, value in checks.items() if not value]
    errors.extend(f"failed check: {name}" for name in failed)
    gate = "PASS" if not errors else "FAIL"
    if gate == "FAIL":
        authoring_status = "CONTRACT_INVALID"
    elif editor_gate_passed and all(
        serialized[key]
        for key in ("pcg_graph_asset_present", "target_map_asset_present")
    ):
        authoring_status = "SERIALIZED_EDITOR_GATE_PASS"
    elif serialized["pcg_graph_asset_present"] and serialized[
        "target_map_asset_present"
    ]:
        authoring_status = "SERIALIZED_ASSETS_PRESENT_REQUIRES_EDITOR_GATE"
    else:
        authoring_status = "READY_FOR_EDITOR_AUTHORING"
    return {
        "schema": REPORT_SCHEMA,
        "contract_id": contract.get("contract_id"),
        "gate": gate,
        "authoring_status": authoring_status,
        "checks": checks,
        "serialized_targets": serialized,
        "errors": errors,
        "limitations": limitations,
        "promotion": {
            "serialized_p4_4_handoff_complete": editor_gate_passed,
            "p4_4_complete": editor_gate_passed,
            "production_vegetation_complete": False,
            "aaa_visual_acceptance": False,
            "licensed_content_approved": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(r"D:\Skyguard52"))
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path(
            r"D:\Skyguard52\Docs\AAA_Review"
            r"\PHASE4_M01_PCG_LANDSCAPE_AUTHORING_CONTRACT.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            r"D:\Skyguard52\Saved\Reports"
            r"\PHASE4_M01_PCG_LANDSCAPE_READINESS_AUDIT.json"
        ),
    )
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    report = evaluate(args.root.resolve(), contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print("[SkyguardPhase4PCGLandscape] " + json.dumps(report))
    return 0 if report["gate"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
