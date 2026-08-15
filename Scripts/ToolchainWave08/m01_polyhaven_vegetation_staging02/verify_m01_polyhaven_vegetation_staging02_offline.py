from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
NS = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02"
CONTRACT = NS / "vegetation_staging02_contract.json"
WORKER = NS / "author_m01_polyhaven_vegetation_staging02.py"
SUPERVISOR = NS / "invoke_m01_polyhaven_vegetation_staging02_once.ps1"
MATERIAL_SOURCE = ROOT / "Saved/SourceQuarantine/M01_POLYHAVEN_VEGETATION_MATERIAL_SOURCE01/material_source_manifest.json"
BOUNDS = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY.json"
FAILURE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def verify_record(row: dict[str, object]) -> None:
    path = Path(str(row["path"]))
    require(path.is_file(), f"Missing source: {path}")
    require(path.stat().st_size == int(row["bytes"]), f"Byte mismatch: {path}")
    require(sha(path) == str(row["sha256"]), f"Hash mismatch: {path}")


def main() -> int:
    require(BOUNDS.stat().st_size == 7858 and sha(BOUNDS) == "3528b8c143d6f77f383a13787519d491fc32a5b92cc9d9e882ee0883334c67ab", "Exact bounds authority changed")
    require(FAILURE.stat().st_size == 11832 and sha(FAILURE) == "5c3fe5c76696f2e2b0052315ce4f02994fdd2071839db24655ca82ba9dc94ae3", "Recovery02 failure changed")
    require(MATERIAL_SOURCE.stat().st_size == 3599 and sha(MATERIAL_SOURCE) == "89200fcd07b3bf69837f77609d41eb62d3234ae758e057f42899377e28660e79", "Material-source manifest changed")
    source_manifest = json.loads(MATERIAL_SOURCE.read_text(encoding="utf-8"))
    require(source_manifest["classification"] == "PASSED_SOURCE_ACQUISITION_AND_HASH_VALIDATION", "Material-source classification changed")
    for row in source_manifest["files"]:
        verify_record(row)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    bounds = {row["asset_id"]: row for row in json.loads(BOUNDS.read_text(encoding="utf-8"))["assets"]}
    compile(WORKER.read_text(encoding="utf-8"), str(WORKER), "exec")
    worker = WORKER.read_text(encoding="utf-8")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require(contract["contract_id"] == "M01-POLYHAVEN-VEGETATION-STAGING02", "Contract ID changed")
    require(contract["material_method"]["generic_gltf_material_translator_forbidden"] is True, "Translator prohibition changed")
    require('set_editor_property("import_materials", False)' in worker, "Geometry-only material import is absent")
    require('set_editor_property("import_textures", False)' in worker, "Geometry-only texture import is absent")
    require('unreal.MaterialProperty.MP_OPACITY_MASK' in worker, "Opacity-mask connection is absent")
    require('unreal.MaterialProperty.MP_AMBIENT_OCCLUSION' in worker, "AO channel connection is absent")
    require('unreal.MaterialProperty.MP_ROUGHNESS' in worker, "Roughness channel connection is absent")
    require('unreal.MaterialProperty.MP_METALLIC' in worker, "Metallic channel connection is absent")
    require('set_editor_property("flip_green_channel", True)' in worker, "OpenGL-normal correction is absent")
    require(sum(len(asset["materials"]) for asset in contract["assets"]) == 7, "Explicit material count changed")
    for asset in contract["assets"]:
        expected = bounds[asset["id"]]["dimensions_cm"]
        require(all(abs(float(a) - float(b)) < 1e-9 for a, b in zip(asset["expected_dimensions_cm"], expected)), f"Bounds mismatch: {asset['id']}")
        for material in asset["materials"]:
            roles = {texture["role"] for texture in material["textures"]}
            require({"diff", "normal", "arm"}.issubset(roles), f"PBR source contract incomplete: {material['id']}")
            if material["masked"]:
                require("alpha" in roles, f"Alpha authority absent: {material['id']}")
            for texture in material["textures"]:
                verify_record(texture)
    require(supervisor.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "One-launch contract failed")
    require("Remove-Item" not in supervisor and "retry_count = 0" in supervisor, "Preservation rule failed")
    for key in ("asset_disk_root", "map_path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(contract["fresh_outputs"][key]).exists(), f"Fresh Stage02 namespace exists: {key}")
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", f"$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('{SUPERVISOR}',[ref]$null,[ref]$e)|Out-Null;if($e.Count){{$e|ForEach-Object{{$_.Message}};exit 1}}"],
        capture_output=True, text=True, check=False,
    )
    require(result.returncode == 0, f"PowerShell parse failed: {result.stdout} {result.stderr}")
    print(json.dumps({
        "classification": "PASS",
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha(CONTRACT)},
        "worker": {"bytes": WORKER.stat().st_size, "sha256": sha(WORKER)},
        "supervisor": {"bytes": SUPERVISOR.stat().st_size, "sha256": sha(SUPERVISOR)},
        "source_alpha_files": len(source_manifest["files"]),
        "explicit_materials": 7,
        "fresh_namespaces_absent": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
