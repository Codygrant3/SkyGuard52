#!/usr/bin/env python3
"""Offline verifier for the pre-authorized StageB Blender production source."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOC_ROOT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08" / "EnvironmentVisibleKitRefinement01StageB"
SOURCE = ROOT / "Scripts" / "ToolchainWave08" / "environment_visual_remediation01" / "build_m01_visible_environment_kit_refinement01_stageb.py"
STAGEA_SOURCE = ROOT / "Scripts" / "ToolchainWave08" / "environment_visual_remediation01" / "build_m01_visible_environment_kit_refinement01_stagea.py"
CONTRACT = DOC_ROOT / "source_preparation_contract.json"
BINDING = DOC_ROOT / "post_stagea_binding_requirements.json"

AUTHORITIES = {
    ROOT / "Docs" / "AAA_Review" / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_VISUAL_REMEDIATION01_OFFLINE_DESIGN_FREEZE.json": (
        3795,
        "f3ebd6d89b0901ec8f5f56bb47fbd9e0c8bad9c53ee1643ddfc892b2a37d0761",
    ),
    ROOT / "Docs" / "AAA_Review" / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_OFFLINE_DESIGN_FREEZE.json": (
        4304,
        "aad4d3481cf7d18f4576ef9493101e2bd5219e0abd3cbe6f3c0fa458dc71f1d6",
    ),
    STAGEA_SOURCE: (
        42238,
        "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12",
    ),
    ROOT / "Docs" / "AAA_Review" / "M01_LANDSCAPE_GROUNDING_BRIDGE01_OFFLINE_SOURCE_FREEZE.json": (
        4227,
        "b5a0b8a2468ff9a1f3645ee5f3d5d5c666131480f331bbfd8e2f77b44c796a8f",
    ),
    SOURCE: (
        37220,
        "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a",
    ),
}

FUTURE_PATHS = [
    ROOT / "Saved" / "BuildAttempts" / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB" / "attempt_01",
    ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "VisibleEnvironmentKit_Refinement01_StageB",
    ROOT / "Saved" / "Reports" / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_TERMINAL_SUPERVISOR.json",
    ROOT / "Saved" / "Reports" / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_EMERGENCY_RECEIPT.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def verify(output: Path | None = None) -> dict:
    failures: list[str] = []
    authority_records = []
    for path, (expected_bytes, expected_hash) in AUTHORITIES.items():
        if not path.is_file():
            failures.append(f"Missing authority: {path}")
            authority_records.append({"path": str(path), "exists": False})
            continue
        record = {"path": str(path), "exists": True, "bytes": path.stat().st_size, "sha256": sha256(path)}
        authority_records.append(record)
        require(record["bytes"] == expected_bytes, f"Byte mismatch: {path}", failures)
        require(record["sha256"] == expected_hash, f"SHA-256 mismatch: {path}", failures)

    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except Exception as error:
        contract = {}
        failures.append(f"Invalid StageB contract: {error}")
    try:
        binding = json.loads(BINDING.read_text(encoding="utf-8"))
    except Exception as error:
        binding = {}
        failures.append(f"Invalid binding requirements: {error}")

    require(
        contract.get("classification") == "OFFLINE_SOURCE_PREPARED_AWAITING_STAGEA_ACCEPTANCE_BINDING",
        "StageB source contract classification mismatch",
        failures,
    )
    require(
        binding.get("classification") == "BIND_ONLY_AFTER_ACCEPTED_STAGEA_OUTPUT_EXISTS",
        "StageB binding requirements classification mismatch",
        failures,
    )
    require(contract.get("stagea_dependency", {}).get("stageb_must_not_launch_before_dependency") is True, "StageA execution dependency is not enforced", failures)

    source = SOURCE.read_text(encoding="utf-8") if SOURCE.is_file() else ""
    helper = STAGEA_SOURCE.read_text(encoding="utf-8") if STAGEA_SOURCE.is_file() else ""
    try:
        tree = ast.parse(source, filename=str(SOURCE))
    except SyntaxError as error:
        tree = ast.Module(body=[], type_ignores=[])
        failures.append(f"StageB source syntax error: {error}")
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    required_functions = {
        "build_lighthouse",
        "build_radar",
        "build_street_furniture",
        "build_vegetation",
        "build_damage_and_variants",
        "create_texture_atlas",
        "render_suite",
        "main",
    }
    require(required_functions.issubset(function_names), f"Missing functions: {sorted(required_functions - function_names)}", failures)

    for token in (
        "STAGEA_HELPER_SHA256",
        "build_lighthouse",
        "parabolic_dish",
        "build_radar",
        "add_beam_between",
        "street_furniture_families",
        "vegetation_species",
        "damage_states",
        "facade_compositions",
        "SOCKET_SM_M01_STAGEB_Lighthouse_Beacon",
        "SOCKET_SM_M01_STAGEB_Radar_DishPivot",
        "UCX_SM_M01_STAGEB_Lighthouse",
        "UCX_SM_M01_STAGEB_Radar",
        "T_M01_STAGEB_Atlas_BaseColor.png",
        "BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW",
    ):
        require(token in source, f"Missing StageB source token: {token}", failures)

    for token in (
        "BLENDER_EEVEE",
        'empty_display_type = "PLAIN_AXES"',
        "export_scene.gltf",
        'export_yup=True',
    ):
        require(token in helper, f"Frozen helper lacks Blender 5.2/export token: {token}", failures)

    for forbidden in (
        "bpy.ops.import_scene",
        "bpy.data.libraries.load",
        "requests.get",
        "urllib.request",
        "VisibleEnvironmentKit_Refinement01_StageA\\",
        "Start-Process",
        "UnrealEditor",
    ):
        require(forbidden not in source, f"Forbidden StageB source token: {forbidden}", failures)

    output_contract = contract.get("output_contract", {})
    require(output_contract.get("blend_count") == 1, "Blend count contract mismatch", failures)
    require(output_contract.get("glb_count") == 6, "GLB count contract mismatch", failures)
    require(output_contract.get("checkpoint_png_count") == 3, "Checkpoint count contract mismatch", failures)
    require(output_contract.get("final_png_count") == 15, "Final render count contract mismatch", failures)
    require(output_contract.get("texture_png_count") == 5, "Texture count contract mismatch", failures)
    require(output_contract.get("final_resolution") == [2560, 1440], "Final resolution mismatch", failures)

    stagea_output = ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "VisibleEnvironmentKit_Refinement01_StageA"
    existing_future = [str(path) for path in FUTURE_PATHS if path.exists()]
    require(not existing_future, f"Future StageB namespaces already exist: {existing_future}", failures)

    result = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb.source-verification.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "PASS" if not failures else "FAIL",
        "failures": failures,
        "authority_records": authority_records,
        "source": {"path": str(SOURCE), "bytes": SOURCE.stat().st_size if SOURCE.is_file() else 0, "sha256": sha256(SOURCE) if SOURCE.is_file() else None},
        "required_function_count": len(required_functions),
        "future_stageb_namespaces_absent": not existing_future,
        "stagea_output_currently_exists": stagea_output.exists(),
        "stageb_execution_authorized": False,
        "build_launches": 0,
        "unreal_launches": 0,
        "blender_launches": 0,
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.output)
    print(result["classification"])
    for failure in result["failures"]:
        print(f"- {failure}")
    return 0 if result["classification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
