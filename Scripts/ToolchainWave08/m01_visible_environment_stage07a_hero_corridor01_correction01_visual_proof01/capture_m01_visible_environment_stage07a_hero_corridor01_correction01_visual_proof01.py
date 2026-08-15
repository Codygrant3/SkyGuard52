"""Bind the proven Stage07A D3D12 proof to Correction01 without changing cameras."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_visual_proof01\capture_m01_visible_environment_stage07a_hero_corridor01_visual_proof01.py")
EXPECTED_BYTES = 11_679
EXPECTED_SHA256 = "75cb6ed1ab46086820eb6e41a69d11b76f2ea63d6fe1b4644c2012c5b4fe20e5"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage07A capture binder changed")
    namespace = {"__name__": "stage07a_capture_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage07AHeroCorridor01VisualProof01.csv", "M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01.csv"),
        ("m01_visible_environment_stage07a_hero_corridor01_visual_proof01", "m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01"),
        ("visible-environment-stage07a-hero-corridor01-visual-proof01", "visible-environment-stage07a-hero-corridor01-correction01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01", "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01"),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Correction01 capture token absent: {old}")
        transformed = transformed.replace(old, new)

    old_start = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_AUTHORING01/attempt_01/authoring_receipt.json"'''
    old_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01.umap"
        )'''
    start = transformed.find(old_start)
    end = transformed.find(old_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Correction01 authoring authority anchor changed")
    new_authority = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01/attempt_01/authoring_receipt.json"
        verify_record({"absolute_path": str(authoring_path), "bytes": 49025, "sha256": "47e2d80df84c28e0d5c1961f9ea51f7326f2aeb8d5287d0f33afba421e7bf726"})
        authoring = read_json(authoring_path)
        if authoring.get("classification") != "PASSED_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING_AWAITING_FINAL_VISUAL":
            raise RuntimeError("Correction01 authoring classification changed")
        if int(authoring.get("actor_count_before_governed", 0)) != 301 or int(authoring.get("actor_count_after_governed", 0)) != 301:
            raise RuntimeError("Correction01 actor-count contract changed")
        if len(authoring.get("vegetation_corrections", [])) != 48 or len(authoring.get("building_corrections", [])) != 39:
            raise RuntimeError("Correction01 bounded-correction counts changed")
        if not str(authoring.get("terrain_material_binding", {}).get("after", "")).startswith("/Game/M01/CoastalCorridorC06R01/"):
            raise RuntimeError("Correction01 planting-soil binding changed")
        if authoring.get("runtime_promotion_performed") is not False or authoring.get("error") is not None:
            raise RuntimeError("Correction01 authoring safety state changed")
        terminal_path = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01_TERMINAL_MANIFEST.json"
        verify_record({"absolute_path": str(terminal_path), "bytes": 11721, "sha256": "9cf197a91501d67d1a17cede6c2c593150b9c207d45899ff1f77e90651becff7"})
        terminal = read_json(terminal_path)
        if terminal.get("classification") != "PASSED_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING_AWAITING_FINAL_VISUAL" or terminal.get("exit_code") != 0:
            raise RuntimeError("Correction01 terminal authority changed")
'''
    transformed = transformed[:start] + new_authority + transformed[end:]
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage07a-correction01", "exec"), globals(), globals())
