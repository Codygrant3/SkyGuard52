from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT_DEFAULT = Path(__file__).resolve().parents[1]
BASE_VERIFIER_PATH = (
    ROOT_DEFAULT / "Scripts" / "verify_skyguard_m01_hero_high_to_low_bake.py"
)
SPEC = importlib.util.spec_from_file_location(
    "skyguard_hilo_base_verifier",
    BASE_VERIFIER_PATH,
)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(BASE)

CONTRACT_SCHEMA = (
    "skyguard.m01.hero-high-to-low-bake.corrective.contract.v1"
)
REPORT_SCHEMA = (
    "skyguard.m01.hero-high-to-low-bake.corrective-verification.v1"
)
BUILD_ID = "BLD_M01_HERO_HILO_002"


def evaluate(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    root: Path,
    contract_path: Path,
    generator_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    checks["contract_schema"] = contract.get("schema") == CONTRACT_SCHEMA
    checks["build_id"] = contract.get("build_id") == BUILD_ID
    checks["immutable_002_outputs"] = all(
        "002" in str(raw)
        for raw in contract.get("outputs", {}).values()
    )
    checks["correction_basis"] = (
        contract.get("correction_basis")
        == "Docs/AAA_Review/M01_HERO_HIGH_TO_LOW_MAP_VISUAL_REVIEW_2026-08-02.md"
    )
    checks["three_corrective_assets"] = (
        isinstance(contract.get("assets"), list)
        and len(contract["assets"]) == 3
        and all(
            isinstance(asset.get("corrections"), list)
            and len(asset["corrections"]) >= 4
            and isinstance(asset.get("ao_remap"), dict)
            and 0.0 < float(asset["ao_remap"].get("minimum", -1.0)) < 1.0
            and 0.0 < float(asset["ao_remap"].get("strength", -1.0)) < 1.0
            for asset in contract["assets"]
        )
    )
    try:
        source_text = generator_path.read_text(encoding="utf-8-sig")
        ast.parse(source_text)
        checks["generator_parses"] = True
    except (OSError, SyntaxError) as exc:
        source_text = ""
        checks["generator_parses"] = False
        errors.append(f"generator parse failed: {exc}")
    for name, token in {
        "contract_argument": "contract_path_from_argv()",
        "ao_remap": "def remap_ao(",
        "pathfinder_outline": "HILO_Pathfinder_HatchSeam_Front",
        "lighthouse_surface_radii": "tower_seam_major_radii_m",
        "radar_turntable_mount": "0.82 * math.cos(angle)",
    }.items():
        checks[f"generator_{name}"] = token in source_text

    artifact = BASE.evaluate_artifacts(contract, manifest, root)
    checks["base_artifact_gate"] = artifact["gate"] == "PASS"
    integrity_errors: list[str] = []
    checks["contract_integrity"] = BASE.verify_file_evidence(
        manifest.get("contract"),
        root,
        "contract",
        integrity_errors,
    ) and (
        Path(manifest["contract"]["path"]).resolve() == contract_path.resolve()
    )
    checks["generator_integrity"] = BASE.verify_file_evidence(
        manifest.get("generator"),
        root,
        "generator",
        integrity_errors,
    ) and (
        Path(manifest["generator"]["path"]).resolve()
        == generator_path.resolve()
    )

    records = {
        item.get("id"): item
        for item in manifest.get("assets", [])
        if isinstance(item, dict)
    }
    ao_contract_match = True
    for asset in contract.get("assets", []):
        record = records.get(asset["id"], {})
        maps = {
            item.get("type"): item
            for item in record.get("maps", [])
            if isinstance(item, dict)
        }
        ao_contract_match &= (
            maps.get("AO", {}).get("ao_remap") == asset["ao_remap"]
            and maps.get("Normal", {}).get("ao_remap") is None
        )
    checks["ao_remap_manifest_contract"] = bool(ao_contract_match)

    for check, passed in checks.items():
        if not passed:
            errors.append(f"corrective check failed: {check}")
    errors.extend(integrity_errors)
    errors.extend(artifact["errors"])
    return {
        "schema": REPORT_SCHEMA,
        "build_id": BUILD_ID,
        "gate": "PASS" if not errors else "FAIL",
        "terminal_state": (
            "ARTIFACTS_VERIFIED_AWAITING_MAP_VISUAL_REVIEW"
            if not errors
            else "CORRECTIVE_ARTIFACT_VERIFICATION_FAILED"
        ),
        "checks": checks,
        "base_artifact_verification": artifact,
        "errors": errors,
        "map_visual_gate": "NOT_REVIEWED",
        "p3_4_closed": False,
        "promotion": contract.get("promotion"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify immutable M01 high-to-low corrective build 002."
    )
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT_DEFAULT
        / "Docs"
        / "AAA_Review"
        / "M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002_CONTRACT.json",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=ROOT_DEFAULT
        / "Scripts"
        / "blender_m01_hero_high_to_low_bake.py",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT_DEFAULT
        / "Saved"
        / "Reports"
        / "M01_HERO_HIGH_TO_LOW_BAKE_MANIFEST_002.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    report = evaluate(
        contract,
        manifest,
        args.root.resolve(),
        args.contract,
        args.generator,
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
