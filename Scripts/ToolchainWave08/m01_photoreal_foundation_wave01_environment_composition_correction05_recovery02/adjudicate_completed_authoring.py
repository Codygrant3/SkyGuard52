from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
PROJECT = Path(r"D:\SG52T08_ENV01")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING/attempt_01"
FAILURE_FREEZE = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json"
OFFLINE_FREEZE = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_OFFLINE_DESIGN_FREEZE.json"
INPUT_MAP = PROJECT / "Content/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap"
OUTPUT_MAP = PROJECT / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02.umap"


AUTHORITIES = {
    FAILURE_FREEZE: (3878, "c4a70d766711e237d405aa3a36b63f77c50e8d9476ff43075850d97b424543bf"),
    OFFLINE_FREEZE: (2208, "ba3dc7de559a70d791801cd94f26f53f09557e4d1e5447a7cc610cdf41672f60"),
    INPUT_MAP: (743809, "97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf"),
    OUTPUT_MAP: (781174, "d868fc50959eda83e3e4d9dc495e95ea0fd9d83e34ebdd191a6cd43a5b0c04cd"),
    ATTEMPT / "authoring_receipt.json": (55328, "e9629235dd941f4d7bc687d1735a2e11b0f0e40e598d67a78435f47b8315f14b"),
    ATTEMPT / "terminal.json": (5507, "94b7cbd9e7851db7ea0b53b9f207d92035d7b0c59ca79a7e419e2a1acf017657"),
    ATTEMPT / "unreal.engine.log": (250945, "1ec42cac9030a61e89a68b49580fcfdd88c8b8d620fc078db86c1a529491afd2"),
    ATTEMPT / "unreal.stderr.log": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    ATTEMPT / "unreal.stdout.log": (251853, "5b56158401f862d8d35ccddc51c24d7b8bbf696408fa813d8c7a9a0ed030fb9c"),
}


FATAL_LOG_PATTERN = re.compile(
    r"Fatal error:|Unhandled Exception|Assertion failed|LogPython:\s*Error",
    re.IGNORECASE | re.MULTILINE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def verify_authority(path: Path, expected_bytes: int, expected_hash: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_bytes = path.stat().st_size
    actual_hash = sha256(path)
    if actual_bytes != expected_bytes:
        raise ValueError(f"Byte mismatch for {path}: {actual_bytes} != {expected_bytes}")
    if actual_hash != expected_hash:
        raise ValueError(f"Hash mismatch for {path}: {actual_hash} != {expected_hash}")
    return {"path": str(path), "bytes": actual_bytes, "sha256": actual_hash}


def adjudicate() -> dict[str, Any]:
    inventory = [verify_authority(path, *expected) for path, expected in AUTHORITIES.items()]
    failure = load_json(FAILURE_FREEZE)
    receipt = load_json(ATTEMPT / "authoring_receipt.json")
    terminal = load_json(ATTEMPT / "terminal.json")

    if failure.get("classification") != "FAILED_WITH_EVIDENCE":
        raise ValueError("Failure freeze classification changed")
    if failure.get("failure_scope") != "SUPERVISOR_LOG_READ_HANDLE_RACE_AFTER_SUCCESSFUL_UNREAL_AUTHORING":
        raise ValueError("Failure scope is not the bounded log-handle race")
    if terminal.get("exit_code") != 0 or terminal.get("exit_code_type") != "System.Int32":
        raise ValueError("Unreal child did not provide numeric System.Int32 exit code 0")
    if terminal.get("timeout") is not False:
        raise ValueError("Unreal child timed out")
    if terminal.get("unreal_launch_count") != 1 or terminal.get("retry_count") != 0:
        raise ValueError("Launch or retry counts violate the one-shot contract")

    expected_receipt = {
        "schema": "skyguard.m01-photoreal-foundation.environment-composition-correction05-recovery02.authoring.v1",
        "classification": "PASSED_M01_PHOTOREAL_FOUNDATION_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTOMATIC",
        "input_asset": "/Game/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01",
        "output_asset": "/Game/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02",
        "input_sha256_before": AUTHORITIES[INPUT_MAP][1],
        "input_sha256_after": AUTHORITIES[INPUT_MAP][1],
        "output_sha256": AUTHORITIES[OUTPUT_MAP][1],
        "actor_count_before": 120,
        "actor_count_after": 140,
    }
    for key, expected in expected_receipt.items():
        if receipt.get(key) != expected:
            raise ValueError(f"Receipt mismatch for {key}: {receipt.get(key)!r} != {expected!r}")
    if receipt.get("errors") != []:
        raise ValueError("Authoring receipt contains errors")

    expected_metrics = {
        "actor_count": 140,
        "grounded_cross_streets": 15,
        "matched_water_material_pair": 1,
        "ocean_wave_state_preserved": 1,
        "proxy_tree_count": 0,
        "uv_less_terrain_removed": 4,
        "uv_mapped_beach_modules": 24,
        "varied_building_instances": 27,
    }
    if receipt.get("quality_metrics") != expected_metrics:
        raise ValueError("Quality metrics differ from the frozen correction contract")
    if len(receipt.get("removed_terrain", [])) != 4:
        raise ValueError("Removed-terrain evidence count is not four")
    if len(receipt.get("beach_modules", [])) != 24:
        raise ValueError("Beach-module evidence count is not twenty-four")
    if len(receipt.get("road_corrections", [])) != 15:
        raise ValueError("Road-correction evidence count is not fifteen")
    if len(receipt.get("building_variation", [])) != 27:
        raise ValueError("Building-variation evidence count is not twenty-seven")

    water = receipt.get("water", {})
    if water.get("waves_before") != water.get("waves_after"):
        raise ValueError("Ocean wave state was not preserved")
    if water.get("near_material_after") != "/Water/Materials/WaterSurface/Water_Material_Ocean.Water_Material_Ocean":
        raise ValueError("Near-water material is not the accepted UE ocean material")
    if water.get("far_material_after") != "/Water/Materials/WaterSurface/Water_FarMesh.Water_FarMesh":
        raise ValueError("Far-water material is not the matching UE far material")

    log_results: list[dict[str, Any]] = []
    for name in ("unreal.stdout.log", "unreal.stderr.log", "unreal.engine.log"):
        path = ATTEMPT / name
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = [match.group(0) for match in FATAL_LOG_PATTERN.finditer(text)]
        if matches:
            raise ValueError(f"Fatal/error signatures found in {name}: {matches[:5]}")
        log_results.append({"path": str(path), "fatal_signature_count": 0})

    return {
        "schema": "skyguard.m01-photoreal-foundation.environment-composition-correction05-recovery02.independent-postflight.v1",
        "classification": "PASSED_RECOVERY02_AUTHORING_OUTPUT_ACCEPTED_AFTER_INDEPENDENT_POSTFLIGHT",
        "source_attempt_classification": "FAILED_WITH_EVIDENCE",
        "source_attempt_reused_or_retried": False,
        "unreal_launches_during_adjudication": 0,
        "verified_authorities": inventory,
        "quality_metrics": expected_metrics,
        "water_state": {
            "near_material": water["near_material_after"],
            "far_material": water["far_material_after"],
            "waves_preserved": True,
        },
        "log_scan": log_results,
        "output_map": {
            "path": str(OUTPUT_MAP),
            "bytes": AUTHORITIES[OUTPUT_MAP][0],
            "sha256": AUTHORITIES[OUTPUT_MAP][1],
        },
        "remaining_gate": "D3D12_MAPPED_VISUAL_PROOF_AND_FULL_RESOLUTION_REVIEW",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        result = adjudicate()
        if args.report:
            if args.report.exists():
                raise FileExistsError(f"Refusing to overwrite evidence: {args.report}")
            args.report.parent.mkdir(parents=True, exist_ok=True)
            temporary = args.report.with_suffix(args.report.suffix + ".tmp")
            temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            temporary.replace(args.report)
        print(result["classification"])
        return 0
    except Exception as exc:  # Evidence tooling must emit a clear terminal failure.
        print(f"FAILED_WITH_EVIDENCE: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
