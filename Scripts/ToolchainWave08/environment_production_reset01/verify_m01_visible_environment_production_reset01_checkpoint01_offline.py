"""Fail-closed offline verifier for Production Reset01 Checkpoint01."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01"
GENERATOR = HERE / "build_m01_visible_environment_production_reset01_checkpoint01.py"
ADJUDICATOR = HERE / "adjudicate_m01_visible_environment_production_reset01_checkpoint01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentProductionReset01Checkpoint01\execution_contract.json"
AUTH = ROOT / r"Production\standing_heavy_process_authorization.json"
PROVENANCE = ROOT / r"Content\Skyguard\Textures\PolyHaven\polyhaven-provenance-manifest.json"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01\attempt_01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path in (GENERATOR, ADJUDICATOR, CONTRACT, AUTH, PROVENANCE):
        assert path.is_file(), path
    ast.parse(GENERATOR.read_text(encoding="utf-8"), filename=str(GENERATOR))
    ast.parse(ADJUDICATOR.read_text(encoding="utf-8"), filename=str(ADJUDICATOR))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    authorization = json.loads(AUTH.read_text(encoding="utf-8"))
    assert authorization["status"] == "ACTIVE"
    assert authorization["execution_policy"]["per_run_user_authorization_required"] is False
    assert contract["source_policy"]["failed_stagea_geometry_reuse"] is False
    assert contract["source_policy"]["external_model_import"] is False
    assert contract["execution"]["blender_launch_count"] == 1
    assert contract["execution"]["automatic_retry_count"] == 0
    assert contract["execution"]["unreal_launch_count"] == 0
    assert not OUTPUT.exists(), OUTPUT
    assert not ATTEMPT.exists(), ATTEMPT
    source = GENERATOR.read_text(encoding="utf-8")
    forbidden = [
        "VisibleEnvironmentKit_Refinement01_StageA",
        "bpy.ops.wm.open_mainfile",
        "bpy.ops.import_scene",
        "subprocess",
        "requests",
        "urllib",
    ]
    for token in forbidden:
        assert token not in source, token
    required = [
        "deep glazing",
        "build_building",
        "build_coastal_district",
        "build_lighthouse",
        "build_tree",
        "SOCKET_",
        "UCX_",
        "bpy.ops.export_scene.gltf",
        "bpy.ops.file.pack_all",
    ]
    for token in required:
        assert token in source, token
    texture_dirs = [
        "coast_sand_01", "asphalt_02", "concrete_wall_006", "concrete_floor_painted",
        "blue_plaster_weathered", "painted_plaster_wall", "brick_wall_006", "roof_07",
        "metal_plate", "green_metal_rust", "wood_cabinet_worn_long",
    ]
    texture_root = ROOT / r"Content\Skyguard\Textures\PolyHaven"
    for name in texture_dirs:
        directory = texture_root / name
        assert directory.is_dir(), directory
        names = [path.name.lower() for path in directory.iterdir() if path.is_file()]
        assert any("diff" in name for name in names), directory
        assert any("nor_gl" in name for name in names), directory
        assert any("rough" in name for name in names), directory
    print(json.dumps({
        "classification": "PASS_OFFLINE_READY_FOR_SINGLE_BLENDER",
        "generator": {"bytes": GENERATOR.stat().st_size, "sha256": sha256(GENERATOR)},
        "adjudicator": {"bytes": ADJUDICATOR.stat().st_size, "sha256": sha256(ADJUDICATOR)},
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)},
        "standing_authorization": {"bytes": AUTH.stat().st_size, "sha256": sha256(AUTH)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
