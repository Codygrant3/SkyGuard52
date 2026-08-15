from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageA/execution_contract.json"
GENERATOR = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/build_m01_visible_environment_kit_refinement01_stagea.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/invoke_m01_visible_environment_kit_refinement01_stagea_once.ps1"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA/attempt_01"
OUTPUT = ROOT / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA"
TERMINAL = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_TERMINAL_SUPERVISOR.json"
EMERGENCY = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_EMERGENCY_RECEIPT.jsonl"


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path: Path, size: int, digest: str) -> None:
    require(path.is_file(), f"missing authority: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(sha256(path) == digest.lower(), f"hash mismatch: {path}")


def parse_powershell(path: Path) -> None:
    command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{str(path).replace("'", "''")}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|%{$_.ToString()};exit 1}else{'PASS'}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    require(result.returncode == 0 and "PASS" in result.stdout, f"PowerShell parse failed: {result.stdout} {result.stderr}")


def validate() -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = GENERATOR.read_text(encoding="utf-8")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    ast.parse(source, filename=str(GENERATOR))
    parse_powershell(SUPERVISOR)

    require(contract["gate"] == "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA", "gate drift")
    require(contract["asset_id"] == "m01-visible-environment-kit-refinement01-stagea", "asset identity drift")
    for authority in contract["authorities"]:
        verify_file(Path(authority["path"]), int(authority["bytes"]), str(authority["sha256"]))
    verify_file(
        Path(contract["execution"]["blender_executable"]),
        int(contract["execution"]["blender_bytes"]),
        str(contract["execution"]["blender_sha256"]),
    )

    output = contract["output_contract"]
    require(output["blend_count"] == 1, "blend count drift")
    require(output["glb_count"] == 4, "GLB count drift")
    require(output["checkpoint_png_count"] == 3, "checkpoint count drift")
    require(output["final_png_count"] == 15, "final render count drift")
    require(output["texture_png_count"] == 5, "texture count drift")
    require(output["checkpoint_resolution"] == [1280, 720], "checkpoint resolution drift")
    require(output["final_resolution"] == [2560, 1440], "final resolution drift")
    require(output["texture_resolution"] == [2048, 2048], "texture resolution drift")
    require(contract["execution"]["blender_launch_count"] == 1, "launch count drift")
    require(contract["execution"]["automatic_retry_count"] == 0, "retry count drift")
    require(contract["execution"]["unreal_launch_count"] == 0, "Unreal launch drift")
    require(contract["execution"]["timeout_seconds"] == 2700, "timeout drift")

    required_source_markers = (
        'scene.render.engine = "BLENDER_EEVEE"',
        'scene.view_settings.look = "AgX - Medium High Contrast"',
        'obj.empty_display_type = "PLAIN_AXES"',
        "build_solid_terrain",
        "build_midrise",
        "create_texture_atlas",
        "render_checkpoints",
        "render_final_views",
        "SOCKET_District_W",
        "UCX_SM_M01_STAGEA_TerrainDistrict_100x80_00",
        '"passed":len(exports)==4 and not missing_sockets and len(collision_objects) >= 5',
    )
    for marker in required_source_markers:
        require(marker in source, f"generator marker missing: {marker}")
    forbidden_source_markers = ("bpy.data.libraries.load", "Coastal_Production_001", "BLENDER_EEVEE_NEXT", 'empty_display_type = "CROSS"')
    for marker in forbidden_source_markers:
        require(marker not in source, f"forbidden generator marker: {marker}")

    require(len(re.findall(r"\bStart-Process\b", supervisor)) == 1, "supervisor must contain exactly one Start-Process")
    require("-AuthorizeSingleBlender" in supervisor and "-OfflineContractTest" in supervisor, "supervisor modes missing")
    require("automatic retry" not in supervisor.lower(), "supervisor contains retry language")
    require("Get-Sha256Lower" in supervisor and "Get-PngDimensions" in supervisor, "self-contained validation missing")
    require("Write-TerminalEvidence" in supervisor and "EmergencyReceipt" in supervisor, "terminal lifecycle missing")
    require("UnrealEditor" not in re.sub(r"Get-GovernedHeavyProcesses[\s\S]*?function Get-PngDimensions", "", supervisor), "unexpected Unreal launch path")

    future = (ATTEMPT, OUTPUT, TERMINAL, EMERGENCY)
    require(not any(path.exists() for path in future), "future governed namespace already exists")

    return {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea.offline-verification.v1",
        "classification": "PASS",
        "authority_count": len(contract["authorities"]) + 1,
        "generator_python_ast": "PASS",
        "supervisor_powershell_5_1_parse": "PASS",
        "one_start_process": True,
        "automatic_retries": 0,
        "future_namespaces_absent": True,
        "heavy_processes_launched": 0,
    }


def main() -> int:
    try:
        print(json.dumps(validate(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
