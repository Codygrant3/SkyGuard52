"""Offline source and optional artifact verifier for BLD-M01-COAST-PROD-001."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path


BUILD_ID = "BLD-M01-COAST-PROD-001"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Docs" / "AAA_Review" / "BLD_M01_COAST_PROD_001_CONTRACT.json"
GENERATOR_PATH = ROOT / "Scripts" / "blender_bld_m01_coast_prod_001.py"
AUDIT_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_COAST_PROD_001_SOURCE_AUDIT.json"
EXPECTED_ASSET_COUNT = 38
FORBIDDEN_IMPORT_MARKERS = (
    "bpy.ops.import_scene.gltf",
    "bpy.ops.import_scene.fbx",
    "bpy.ops.wm.obj_import",
    "bpy.ops.wm.open_mainfile",
    "bpy.ops.wm.append",
    "bpy.ops.wm.link",
    "bpy.data.libraries.load",
    "bpy.data.images.load",
)
REQUIRED_GENERATOR_MARKERS = (
    "bpy.ops.wm.read_factory_settings",
    "bpy.ops.wm.save_as_mainfile",
    "bpy.ops.export_scene.gltf",
    "ensure_uv0_uv1",
    "create_solid_terrain",
    "create_snap_sockets",
    "apply_asset_metadata",
    "verify_rejection_evidence",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def add(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def source_checks(contract: dict, generator_text: str) -> list[dict]:
    checks: list[dict] = []
    add(checks, "contract_schema", contract.get("schema") == "skyguard.blender-source-contract.v1",
        str(contract.get("schema")))
    add(checks, "build_id", contract.get("build_id") == BUILD_ID, str(contract.get("build_id")))
    add(checks, "source_only_status", contract.get("status") == "source_only_not_run",
        str(contract.get("status")))
    quality = str(contract.get("quality_claim", "")).lower()
    add(checks, "no_aaa_claim",
        quality == "production_direction_candidate_not_aaa", quality)
    version = contract.get("blender_version")
    add(checks, "blender_52",
        version == "5.2" or version == {"major": 5, "minor": 2}, str(version))

    try:
        ast.parse(generator_text, filename=str(GENERATOR_PATH))
        syntax_ok, syntax_detail = True, "Python syntax valid"
    except SyntaxError as exc:
        syntax_ok, syntax_detail = False, str(exc)
    add(checks, "generator_syntax", syntax_ok, syntax_detail)
    missing_markers = [marker for marker in REQUIRED_GENERATOR_MARKERS if marker not in generator_text]
    add(checks, "generator_capabilities", not missing_markers,
        "missing=" + ",".join(missing_markers) if missing_markers else "all required markers present")
    found_imports = [marker for marker in FORBIDDEN_IMPORT_MARKERS if marker in generator_text]
    add(checks, "no_external_geometry_or_image_import", not found_imports,
        "found=" + ",".join(found_imports) if found_imports else "none")

    evidence = contract.get("rejection_evidence", {})
    evidence_path = ROOT / str(evidence.get("path", ""))
    evidence_ok = (
        evidence_path.is_file()
        and evidence_path.stat().st_size == evidence.get("bytes")
        and sha256_file(evidence_path) == evidence.get("sha256")
    )
    add(checks, "rejection_evidence_hash_bound", evidence_ok, rel(evidence_path))
    add(checks, "rejection_evidence_scope",
        evidence.get("allowed_use") == "Visual rejection evidence only."
        and str(evidence.get("forbidden_use", "")).startswith("No geometry"),
        f"allowed={evidence.get('allowed_use')}")

    outputs = contract.get("outputs", {})
    output_values = [str(value).replace("\\", "/") for value in outputs.values()]
    isolated = all(
        ("Coastal_Production_001" in value or "BLD_M01_COAST_PROD_001" in value)
        for value in output_values
    )
    add(checks, "isolated_output_namespace", isolated, "; ".join(output_values))
    policy = contract.get("source_policy", {})
    policy_text = json.dumps(policy).lower()
    add(checks, "factory_procedural_policy",
        "factory" in policy_text and "external" in policy_text and "wave1" in policy_text,
        policy_text)

    uv = contract.get("uv_contract", {})
    add(checks, "uv0_uv1_contract", uv.get("required_layers") == ["UV0", "UV1"],
        str(uv.get("required_layers")))
    material_ids = contract.get("material_id_contract", {})
    values = list(material_ids.values())
    add(checks, "material_ids_unique", len(values) == len(set(values)), str(values))
    add(checks, "trim_and_decal_ids", {90, 100, 101, 102}.issubset(set(values)), str(values))

    specs = contract.get("asset_specs", [])
    names = [str(spec.get("name", "")) for spec in specs]
    add(checks, "asset_count", len(specs) == EXPECTED_ASSET_COUNT, str(len(specs)))
    add(checks, "asset_names_unique", len(names) == len(set(names)), str(len(set(names))))
    forbidden_tokens = [str(token).lower() for token in contract.get("forbidden_name_tokens", [])]
    invalid_names = [
        name for name in names
        if any(token in name.lower() for token in forbidden_tokens)
    ]
    add(checks, "production_names", not invalid_names,
        "invalid=" + ",".join(invalid_names) if invalid_names else "no forbidden tokens")

    dimensions_ok = all(
        len(spec.get("dimensions_m", [])) == 3
        and all(isinstance(value, (int, float)) and value > 0 for value in spec["dimensions_m"])
        for spec in specs
    )
    add(checks, "positive_exact_dimensions", dimensions_ok, f"assets={len(specs)}")
    kinds = {str(spec.get("kind", "")) for spec in specs}
    required_kind_terms = ("terrain", "road", "curb", "sidewalk", "drain", "building",
                           "roof", "window", "balcony")
    missing_kinds = [term for term in required_kind_terms if not any(term in kind for kind in kinds)]
    add(checks, "required_asset_families", not missing_kinds,
        "missing=" + ",".join(missing_kinds) if missing_kinds else ",".join(sorted(kinds)))
    add(checks, "corner_and_end_variants",
        any("Corner" in name for name in names) and any("End" in name for name in names),
        "corner/end module names")

    terrains = [
        spec for spec in specs
        if spec.get("kind") in {"terrain", "terrain_transition"}
    ]
    terrain_ok = (
        len(terrains) == 4
        and all(spec["dimensions_m"][0] == 100.0 and spec["dimensions_m"][1] == 80.0
                and spec["dimensions_m"][2] >= 2.0 for spec in terrains)
    )
    add(checks, "terrain_100m_class", terrain_ok, f"terrain_count={len(terrains)}")
    terrain_sockets_ok = all(
        set(spec.get("snap_sockets", [])) == {"W", "E", "S", "N"} for spec in terrains
    )
    add(checks, "terrain_four_edge_snap", terrain_sockets_ok, f"terrain_count={len(terrains)}")
    add(checks, "all_assets_have_snap_and_collision",
        all(spec.get("snap_sockets") and spec.get("collision") for spec in specs),
        f"assets={len(specs)}")
    add(checks, "nanite_and_lod_intent",
        all(isinstance(spec.get("nanite"), bool) and spec.get("lod_intent") for spec in specs),
        f"assets={len(specs)}")
    return checks


def artifact_checks(contract: dict, manifest_path: Path) -> tuple[str, list[dict]]:
    if not manifest_path.is_file():
        return "NOT_RUN", []
    checks: list[dict] = []
    manifest = load_json(manifest_path)
    add(checks, "artifact_schema",
        manifest.get("schema") == "skyguard.bld-m01-coast-prod-001.artifact-manifest.v1",
        str(manifest.get("schema")))
    add(checks, "artifact_build_id", manifest.get("build_id") == BUILD_ID,
        str(manifest.get("build_id")))
    add(checks, "artifact_blender_52", str(manifest.get("blender_version", "")).startswith("5.2"),
        str(manifest.get("blender_version")))
    add(checks, "artifact_contract_hash",
        manifest.get("contract", {}).get("sha256") == sha256_file(CONTRACT_PATH),
        str(manifest.get("contract", {}).get("sha256")))
    add(checks, "artifact_generator_hash",
        manifest.get("generator", {}).get("sha256") == sha256_file(GENERATOR_PATH),
        str(manifest.get("generator", {}).get("sha256")))
    evidence = contract["rejection_evidence"]
    add(checks, "artifact_evidence_hash",
        manifest.get("rejection_evidence", {}).get("sha256") == evidence["sha256"],
        str(manifest.get("rejection_evidence", {}).get("sha256")))

    specs = {spec["name"]: spec for spec in contract["asset_specs"]}
    assets = manifest.get("assets", [])
    add(checks, "artifact_asset_count",
        manifest.get("asset_count") == EXPECTED_ASSET_COUNT and len(assets) == EXPECTED_ASSET_COUNT,
        f"manifest={manifest.get('asset_count')} records={len(assets)}")
    names = [asset.get("name") for asset in assets]
    add(checks, "artifact_exact_asset_set", set(names) == set(specs) and len(names) == len(set(names)),
        f"unique={len(set(names))}")
    records_ok = True
    errors: list[str] = []
    for asset in assets:
        name = asset.get("name")
        spec = specs.get(name)
        path = ROOT / str(asset.get("path", ""))
        if not spec:
            records_ok, errors = False, errors + [f"{name}:unexpected"]
            continue
        if not path.is_file() or path.stat().st_size != asset.get("bytes") or sha256_file(path) != asset.get("sha256"):
            records_ok, errors = False, errors + [f"{name}:file/hash"]
        if asset.get("dimensions_m") != spec["dimensions_m"]:
            records_ok, errors = False, errors + [f"{name}:dimensions"]
        if asset.get("uv_layers") != ["UV0", "UV1"]:
            records_ok, errors = False, errors + [f"{name}:uv"]
        if not asset.get("collision") or not asset.get("snap_sockets"):
            records_ok, errors = False, errors + [f"{name}:metadata"]
    add(checks, "artifact_records", records_ok, ",".join(errors[:10]) if errors else "all records valid")

    blend = manifest.get("blend", {})
    blend_path = ROOT / str(blend.get("path", ""))
    blend_ok = (
        blend_path.is_file()
        and blend_path.stat().st_size == blend.get("bytes")
        and sha256_file(blend_path) == blend.get("sha256")
    )
    add(checks, "artifact_master_blend", blend_ok, rel(blend_path))
    return ("PASS" if all(item["passed"] for item in checks) else "FAIL"), checks


def evaluate(contract_path: Path = CONTRACT_PATH, generator_path: Path = GENERATOR_PATH) -> dict:
    contract = load_json(contract_path)
    generator_text = generator_path.read_text(encoding="utf-8")
    checks = source_checks(contract, generator_text)
    source_status = "PASS" if all(item["passed"] for item in checks) else "FAIL"
    manifest_path = ROOT / contract.get("outputs", {}).get(
        "manifest", "Saved/Reports/BLD_M01_COAST_PROD_001_MANIFEST.json"
    )
    artifact_status, generated_checks = artifact_checks(contract, manifest_path)
    return {
        "schema": "skyguard.bld-m01-coast-prod-001.source-audit.v1",
        "build_id": BUILD_ID,
        "source_status": source_status,
        "artifact_status": artifact_status,
        "quality_claim": "production_direction_candidate_not_aaa",
        "contract": rel(contract_path),
        "generator": rel(generator_path),
        "source_checks": checks,
        "artifact_checks": generated_checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-artifacts", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    if not args.no_write:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["source_status"] != "PASS":
        return 2
    if args.require_artifacts and result["artifact_status"] == "NOT_RUN":
        return 3
    if result["artifact_status"] == "FAIL":
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
