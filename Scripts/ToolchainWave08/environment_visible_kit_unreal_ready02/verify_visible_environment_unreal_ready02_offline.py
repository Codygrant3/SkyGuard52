"""Offline prevention checks for material-preserving UnrealReady02."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GENERATOR = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready02\build_visible_environment_unreal_ready02.py"
ADJUDICATOR = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready02\adjudicate_visible_environment_unreal_ready02.py"
AUTHORITIES = {
    GENERATOR: "4a2c33e2e1ab656343996b0d17e17a3eb50058c0c8621c927916fc3320d1d158",
    ADJUDICATOR: "a09eb76c72481b2bb74ff2006ee453c555198fb138bc6ca3d39abcc1398e6233",
    ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady02\execution_contract.json": "0dee50e3e3eedc992f2ef89bf3d75469f38ba169f8def1878791f411898b3866",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02_ACCEPTANCE_FREEZE.json": "88b2ac171f48bca55b0643599c7e17137f740b3db15d4c708c42b7838916b202",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json": "efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend": "0ef89cd08cb224f1d21015cfb1c968c1b66d8916c29c4702e129766a215093eb",
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"): "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7",
}
FUTURE = (
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02",
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_TERMINAL_SUPERVISOR.json",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_POSTFLIGHT.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_offline(path: Path) -> None:
    result = subprocess.run([sys.executable, str(path), "--offline-contract-test"], check=False, capture_output=True, text=True)
    require(result.returncode == 0 and "PASS_TRANSFORMATION_COMPILE" in result.stdout, f"Offline transformation failed for {path}: {result.stdout} {result.stderr}")


def main() -> int:
    for path, expected in AUTHORITIES.items():
        require(path.is_file() and sha256(path) == expected, f"Authority mismatch: {path}")
    for path in FUTURE:
        require(not path.exists(), f"Fresh namespace exists: {path}")
    run_offline(GENERATOR)
    run_offline(ADJUDICATOR)
    contract = json.loads((ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady02\execution_contract.json").read_text(encoding="utf-8"))
    require(contract["material_preservation"]["used_material_indices_must_equal_slot_range"] is True, "Material-index gate changed")
    require(contract["execution"]["automatic_retries"] == 0, "Retry contract changed")
    require(contract["mesh_contract"]["total_render_groups"] == 14, "Mesh-group contract changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
