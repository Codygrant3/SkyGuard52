from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08" / "M01EnvironmentRealismStackPivot01" / "pivot_contract.json"
INVENTORY = ROOT / "Docs" / "Toolchain" / "ToolchainWave08" / "M01EnvironmentRealismStackPivot01" / "source_inventory.json"
PROBE = ROOT / "Scripts" / "ToolchainWave08" / "environment_realism_stack_pivot01" / "probe_environment_realism_stack_pivot01.py"
SUPERVISOR = ROOT / "Scripts" / "ToolchainWave08" / "environment_realism_stack_pivot01" / "invoke_asset_map_probe_once.ps1"
ATTEMPT = ROOT / "Saved" / "BuildAttempts" / "M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE" / "attempt_01"
TERMINAL = ROOT / "Saved" / "Reports" / "M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved" / "Reports" / "M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE_EMERGENCY_RECEIPT.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    require(contract.get("classification") == "OFFLINE_CONTRACT_READY_FOR_READ_ONLY_ASSET_MAP_PROBE", "contract classification mismatch", errors)
    members = inventory.get("members")
    require(isinstance(members, list) and len(members) == 24, "source inventory must contain exactly 24 members", errors)
    verified = 0
    if isinstance(members, list):
        for member in members:
            path = Path(str(member["path"]))
            if not path.is_file():
                errors.append(f"missing inventory member: {path}")
                continue
            if path.stat().st_size != int(member["bytes"]):
                errors.append(f"byte mismatch: {path}")
                continue
            if sha256(path) != str(member["sha256"]):
                errors.append(f"SHA-256 mismatch: {path}")
                continue
            verified += 1

    probe_source = PROBE.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    for forbidden in ("save_asset(", "save_loaded_asset(", "new_level", "spawn_actor", "set_actor_location", "set_actor_scale3d"):
        require(forbidden not in probe_source, f"read-only probe contains forbidden mutation token: {forbidden}", errors)
    for required in ("load_level(MAP_ASSET)", "map_unchanged", "get_all_level_actors", "static_mesh_assets", "material_assets"):
        require(required in probe_source, f"read-only probe is missing token: {required}", errors)
    require(supervisor_source.count("Start-Process") == 1, "supervisor must contain exactly one Start-Process", errors)
    require("-NullRHI" in supervisor_source, "supervisor lacks NullRHI", errors)
    require("-NoSaveOnExit" in supervisor_source, "supervisor lacks no-save guard", errors)
    require("retry_count = 0" in supervisor_source, "supervisor lacks zero-retry evidence", errors)
    require("while (-not $process.HasExited" in supervisor_source, "supervisor lacks bounded wait", errors)
    require(not ATTEMPT.exists(), "future attempt namespace already exists", errors)
    require(not TERMINAL.exists(), "future terminal manifest already exists", errors)
    require(not EMERGENCY.exists(), "future emergency receipt already exists", errors)

    report = {
        "schema": "skyguard.m01-environment-realism-stack-pivot01.offline-verification.v1",
        "classification": "PASS" if not errors else "FAILED_WITH_EVIDENCE",
        "errors": errors,
        "inventory_verified": verified,
        "inventory_total": len(members) if isinstance(members, list) else 0,
        "future_attempt_absent": not ATTEMPT.exists(),
        "future_terminal_absent": not TERMINAL.exists(),
        "unreal_launch_count": 0,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
