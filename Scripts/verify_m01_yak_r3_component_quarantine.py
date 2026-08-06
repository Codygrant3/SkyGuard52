"""Fresh-process Unreal persistence audit for the R3 component quarantine."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from audit_m01_yak_r3_component_import_source import audit_source, load_json  # noqa: E402


CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_YAK_R3_COMPONENT_IMPORT_CONTRACT.json"
DESTINATION = "/Game/Skyguard/Quarantine/M01/YakR3ComponentEval"
REPORT_PATH = ROOT / "Saved/Reports/M01_YAK_R3_COMPONENT_QUARANTINE_AUDIT.json"


def asset_class(asset) -> str:
    return asset.get_class().get_name() if asset else "Missing"


def tag(asset, key: str) -> str:
    return str(unreal.EditorAssetLibrary.get_metadata_tag(asset, key))


def mesh_observation(asset) -> dict:
    materials = []
    for slot in list(asset.get_editor_property("static_materials") or []):
        interface = slot.get_editor_property("material_interface")
        materials.append(interface.get_path_name() if interface else None)
    bounds = asset.get_bounds()
    body_setup = asset.get_editor_property("body_setup")
    aggregate = body_setup.get_editor_property("agg_geom") if body_setup else None
    simple_collision_count = 0
    if aggregate:
        for field in ("box_elems", "sphere_elems", "sphyl_elems", "convex_elems"):
            simple_collision_count += len(list(aggregate.get_editor_property(field) or []))
    return {
        "material_slots": materials,
        "material_slot_count": len(materials),
        "bounds_origin_cm": [
            bounds.origin.x,
            bounds.origin.y,
            bounds.origin.z,
        ],
        "bounds_extent_cm": [
            bounds.box_extent.x,
            bounds.box_extent.y,
            bounds.box_extent.z,
        ],
        "simple_collision_primitive_count": simple_collision_count,
        "complex_collision_trace_flag": str(
            body_setup.get_editor_property("collision_trace_flag") if body_setup else "None"
        ),
        "evidence_complete_for_promotion": False,
    }


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    checks = []
    source = audit_source()
    checks.append(
        {
            "name": "source_audit",
            "passed": source["gate"] == "PASS_COMPONENT_IMPORT_SOURCE_AUDIT",
            "detail": source["gate"],
        }
    )
    assets = list(unreal.EditorAssetLibrary.list_assets(DESTINATION, True, False))
    allowed_support_names = set(contract["support_materials"]) | set(
        contract["support_textures"]
    )
    pivot_payload = {
        "build_id": contract["build_id"],
        "reference_datums": contract["reference_datums"],
        "promotion_allowed": False,
    }
    safety_payload = {
        "build_id": contract["build_id"],
        "camera_reference": contract["camera_reference"],
        "safety_volumes": contract["safety_volumes"],
        "retained_l88_bundles": contract["retained_l88_bundles"],
        "promotion_allowed": False,
    }
    expected_pivot_json = json.dumps(pivot_payload, sort_keys=True)
    expected_safety_json = json.dumps(safety_payload, sort_keys=True)
    by_name = {}
    forbidden = []
    unexpected = []
    for path in assets:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        name = asset.get_name() if asset else ""
        kind = asset_class(asset)
        by_name[name] = (path, asset, kind)
        if kind in contract["forbidden_import_classes"]:
            forbidden.append(f"{path}:{kind}")
        if (
            not isinstance(asset, unreal.StaticMesh)
            and not (
                name in allowed_support_names
                and kind in {"Material", "MaterialInstanceConstant", "Texture2D"}
            )
        ):
            unexpected.append(f"{path}:{kind}")

    expected = contract["component_meshes"]
    observations = []
    component_errors = []
    for identity, name in expected.items():
        record = by_name.get(name)
        if not record or not isinstance(record[1], unreal.StaticMesh):
            component_errors.append("missing " + name)
            continue
        path, asset, _ = record
        expected_tags = {
            "Skyguard.BuildId": contract["build_id"],
            "Skyguard.R3LedgerIdentity": identity,
            "Skyguard.SourceSha256": contract["source"]["sha256"],
            "Skyguard.Quarantine": "true",
            "Skyguard.EvaluationOnly": "true",
            "Skyguard.PromotionAllowed": "false",
        }
        bad_tags = {
            key: {"expected": value, "actual": tag(asset, key)}
            for key, value in expected_tags.items()
            if tag(asset, key).lower() != value.lower()
        }
        if bad_tags:
            component_errors.append(name + " metadata mismatch " + json.dumps(bad_tags))
        if tag(asset, "Skyguard.PivotReferenceJson") != expected_pivot_json:
            component_errors.append(name + " pivot reference metadata mismatch")
        if tag(asset, "Skyguard.SafetyCameraReferenceJson") != expected_safety_json:
            component_errors.append(name + " safety/camera reference metadata mismatch")
        observations.append(
            {
                "ledger_identity": identity,
                "asset": path,
                "metadata_valid": not bad_tags,
                **mesh_observation(asset),
            }
        )

    actual_static_names = {
        name for name, (_, asset, _) in by_name.items() if isinstance(asset, unreal.StaticMesh)
    }
    extra_static = sorted(actual_static_names - set(expected.values()))
    missing_support = sorted(allowed_support_names - set(by_name))
    checks.extend(
        [
            {"name": "component_set", "passed": not component_errors and not extra_static,
             "detail": {"errors": component_errors, "extra_static": extra_static}},
            {"name": "reference_metadata", "passed": not component_errors,
             "detail": "pivot and safety/camera JSON must match on every donor"},
            {"name": "forbidden_classes", "passed": not forbidden, "detail": forbidden},
            {"name": "unexpected_classes", "passed": not unexpected, "detail": unexpected},
            {"name": "support_asset_set", "passed": not missing_support,
             "detail": {"missing": missing_support, "expected": sorted(allowed_support_names)}},
        ]
    )
    passed = all(check["passed"] for check in checks)
    report = {
        "schema": "skyguard.m01.yak-r3-component-quarantine-audit.v1",
        "gate": (
            "PASS_QUARANTINE_IMPORT_PERSISTED_NOT_PROMOTABLE" if passed else "FAIL"
        ),
        "destination": DESTINATION,
        "fresh_process_audit": True,
        "runtime_map_changed": False,
        "config_changed": False,
        "promotion_allowed": False,
        "components": observations,
        "missing_promotion_evidence": contract["promotion_requirements"],
        "checks": checks,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not passed:
        raise RuntimeError("R3 component quarantine persistence audit failed")


if __name__ == "__main__":
    main()
