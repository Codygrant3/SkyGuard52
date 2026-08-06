"""Offline, fail-closed audit for the R3 component-only Unreal import lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_YAK_R3_COMPONENT_IMPORT_CONTRACT.json"
REPORT_PATH = ROOT / "Saved/Reports/M01_YAK_R3_COMPONENT_SOURCE_AUDIT.json"
BUILDER_PATH = ROOT / "Scripts/build_m01_yak_r3_component_quarantine.py"
VERIFIER_PATH = ROOT / "Scripts/verify_m01_yak_r3_component_quarantine.py"
RUNNER_PATH = ROOT / "Scripts/run_m01_yak_r3_component_quarantine_gate.ps1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("not a binary glTF file")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_length != len(data):
        raise ValueError("invalid GLB version or declared length")
    offset = 12
    while offset + 8 <= len(data):
        size, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + size]
        offset += size
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.rstrip(b" \t\r\n\0"))
    raise ValueError("GLB has no JSON chunk")


def add(checks: list[dict[str, Any]], name: str, passed: bool, detail: Any) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def verify_bound_file(
    checks: list[dict[str, Any]], name: str, record: dict[str, Any]
) -> Path:
    path = ROOT / record["path"]
    actual_bytes = path.stat().st_size if path.is_file() else None
    actual_hash = sha256(path) if path.is_file() else None
    passed = actual_bytes == record["bytes"] and actual_hash == record["sha256"]
    add(
        checks,
        "bound_" + name,
        passed,
        {
            "path": record["path"],
            "expected_bytes": record["bytes"],
            "actual_bytes": actual_bytes,
            "expected_sha256": record["sha256"],
            "actual_sha256": actual_hash,
        },
    )
    return path


def audit_source(contract_path: Path = CONTRACT_PATH) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    contract = load_json(contract_path)
    source = verify_bound_file(checks, "source_glb", contract["source"])
    evidence_paths = {
        name: verify_bound_file(checks, name, record)
        for name, record in contract["bound_evidence"].items()
    }

    try:
        document = glb_json(source)
        node_names = {node.get("name", "") for node in document.get("nodes", [])}
    except Exception as exc:
        document, node_names = {}, set()
        add(checks, "glb_parse", False, str(exc))
    else:
        add(checks, "glb_parse", True, {"node_count": len(node_names)})

    required_nodes = (
        set(contract["component_meshes"])
        | set(contract["reference_datums"])
        | set(contract["safety_volumes"])
    )
    missing_nodes = sorted(required_nodes - node_names)
    add(checks, "required_glb_nodes", not missing_nodes, {"missing": missing_nodes})
    glb_materials = {
        material.get("name", "") for material in document.get("materials", [])
    }
    missing_materials = sorted(set(contract["support_materials"]) - glb_materials)
    add(
        checks,
        "contracted_support_materials",
        not missing_materials,
        {"missing": missing_materials},
    )
    add(
        checks,
        "source_has_no_texture_payload",
        not document.get("textures") and not document.get("images")
        and contract["support_textures"] == [],
        {
            "texture_count": len(document.get("textures", [])),
            "image_count": len(document.get("images", [])),
        },
    )
    camera_name = contract["camera_reference"]["name"]
    add(
        checks,
        "camera_is_contract_reference_not_glb_claim",
        not contract["camera_reference"]["glb_node_expected"]
        and camera_name not in node_names,
        {"camera": camera_name, "present_in_glb": camera_name in node_names},
    )

    manifest = load_json(evidence_paths["manifest"])
    manifest_text = json.dumps(manifest, sort_keys=True)
    expected_donors = set(contract["component_meshes"]) | set(
        contract["reference_datums"]
    )
    add(
        checks,
        "manifest_donor_identity",
        all(name in manifest_text for name in expected_donors),
        {"expected_count": len(expected_donors)},
    )
    false_claims = {
        key: manifest.get(key)
        for key in (
            "aaa",
            "final",
            "matched_visual_review_accepted",
            "unreal_accepted",
        )
    }
    add(
        checks,
        "manifest_has_no_promotion_claim",
        not any(value is True for value in false_claims.values()),
        false_claims,
    )
    review_text = evidence_paths["visual_review"].read_text(encoding="utf-8-sig")
    normalized_review = " ".join(review_text.split())
    add(
        checks,
        "visual_review_component_only",
        "ACCEPTED_FOR_UNREAL_IMPORT_EVALUATION" in normalized_review
        and "not a whole-aircraft runtime replacement" in normalized_review
        and "Do not replace the current runtime Yak" in normalized_review,
        "matched component-level review language",
    )

    source_contract = load_json(evidence_paths["source_contract"])
    add(
        checks,
        "retained_l88_bundles_exact",
        source_contract.get("preserved_bundles") == contract["retained_l88_bundles"],
        source_contract.get("preserved_bundles"),
    )
    add(
        checks,
        "promotion_remains_false",
        source_contract.get("inheritance_policy", {}).get("promotion_allowed_value")
        is False
        and contract["unreal"]["promotion_allowed"] is False,
        "source and import contracts both forbid promotion",
    )

    policy_files = [BUILDER_PATH, VERIFIER_PATH, RUNNER_PATH]
    missing_policy_files = [str(path.relative_to(ROOT)) for path in policy_files if not path.is_file()]
    add(checks, "implementation_files_present", not missing_policy_files, missing_policy_files)
    if not missing_policy_files:
        texts = {path.name: path.read_text(encoding="utf-8-sig") for path in policy_files}
        combined = "\n".join(texts.values())
        forbidden = [
            "EditorLevelLibrary",
            "LevelEditorSubsystem",
            "save_current_level",
            "load_level(",
            "DefaultEngine.ini",
            "DefaultGame.ini",
            "/Game/Skyguard/Maps",
            "/Game/Skyguard/Missions",
        ]
        found = [token for token in forbidden if token in combined]
        add(checks, "no_runtime_map_or_config_mutation", not found, found)
        add(
            checks,
            "quarantine_destination_hard_bound",
            contract["unreal"]["destination"] in texts[BUILDER_PATH.name]
            and contract["unreal"]["destination"] in texts[VERIFIER_PATH.name],
            contract["unreal"]["destination"],
        )
        asset_factory_patterns = [
            "DataAssetFactory",
            "unreal.DataAsset",
            "unreal.PrimaryDataAsset",
        ]
        asset_factory_found = [
            token
            for token in asset_factory_patterns
            if token in texts[BUILDER_PATH.name]
        ]
        add(
            checks,
            "reference_metadata_avoids_abstract_assets",
            contract["unreal"]["reference_storage"] == "metadata_on_each_component"
            and "Skyguard.PivotReferenceJson" in texts[BUILDER_PATH.name]
            and "Skyguard.SafetyCameraReferenceJson" in texts[BUILDER_PATH.name]
            and not asset_factory_found,
            {"forbidden_asset_factory_patterns_found": asset_factory_found},
        )

    passed = all(check["passed"] for check in checks)
    return {
        "schema": "skyguard.m01.yak-r3-component-source-audit.v1",
        "gate": "PASS_COMPONENT_IMPORT_SOURCE_AUDIT" if passed else "FAIL",
        "promotion_allowed": False,
        "source_only": True,
        "checks": checks,
    }


def verify_evaluation(path: Path, contract_path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = load_json(contract_path)
    record = load_json(path)
    errors: list[str] = []

    def valid_evidence(entries: Any, label: str) -> bool:
        if not isinstance(entries, list) or not entries:
            errors.append("missing " + label)
            return False
        valid = True
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) < {"path", "bytes", "sha256"}:
                errors.append(f"{label}[{index}]: invalid evidence record")
                valid = False
                continue
            evidence_path = ROOT / entry["path"]
            try:
                evidence_path.resolve().relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{label}[{index}]: evidence escapes project root")
                valid = False
                continue
            if (
                not evidence_path.is_file()
                or evidence_path.stat().st_size != entry["bytes"]
                or sha256(evidence_path) != entry["sha256"]
            ):
                errors.append(f"{label}[{index}]: hash-bound evidence mismatch")
                valid = False
        return valid

    components = record.get("components", [])
    by_id = {item.get("ledger_identity"): item for item in components}
    expected = set(contract["component_meshes"])
    if set(by_id) != expected:
        errors.append("evaluation component identities are not the exact donor set")
    for identity in sorted(expected):
        item = by_id.get(identity, {})
        for field in contract["promotion_requirements"]["per_component"]:
            valid_evidence(item.get(field), f"{identity}:{field}")
    for field in contract["promotion_requirements"]["global"]:
        valid_evidence(
            record.get("global_evidence", {}).get(field), "global:" + field
        )
    return {
        "schema": "skyguard.m01.yak-r3-component-evaluation-audit.v1",
        "gate": "READY_FOR_MANUAL_PROMOTION_REVIEW" if not errors else "NOT_PROMOTABLE",
        "automatic_promotion": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    report = (
        verify_evaluation(args.evaluation)
        if args.evaluation
        else audit_source()
    )
    if not args.no_write:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["gate"].startswith(("PASS", "READY")) else 2


if __name__ == "__main__":
    sys.exit(main())
