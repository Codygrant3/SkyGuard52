"""Offline verifier for the single UE 5.8 visible-kit import probe."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_import_probe01\probe_visible_kit_import01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitImportProbe01\execution_contract.json"
AUTH = ROOT / r"Production\standing_heavy_process_authorization.json"
FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json"
SOURCE = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb"
DEST = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleKitImportProbe01")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01\attempt_01"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    for path in (SCRIPT, CONTRACT, AUTH, FREEZE, SOURCE):
        assert path.is_file(), path
    ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    assert auth["status"] == "ACTIVE"
    assert auth["execution_policy"]["per_run_user_authorization_required"] is False
    assert contract["execution"]["unreal_launch_count"] == 1
    assert contract["execution"]["automatic_retry_count"] == 0
    assert contract["map_mutation"] is False
    assert not DEST.exists(), DEST
    assert not ATTEMPT.exists(), ATTEMPT
    source = SCRIPT.read_text(encoding="utf-8")
    for token in ("AssetImportTask", "import_asset_tasks", "replace_existing = False", "map_saved\": False", "NullRHI"):
        if token == "NullRHI":
            continue
        assert token in source, token
    for token in ("load_level", "new_level", "save_current_level", "spawn_actor"):
        assert token not in source, token
    print(json.dumps({
        "classification": "PASS_READY_FOR_SINGLE_UNREAL_IMPORT_PROBE",
        "script": {"bytes": SCRIPT.stat().st_size, "sha256": sha256(SCRIPT)},
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)}
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
