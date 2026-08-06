from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PLUGINS = ROOT / "Plugins"
INVENTORY = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_PLUGIN_ROOT_INVENTORY.json"
COLLISIONS = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_COLLISION_REPORT.json"
ACTIVE = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_SELECTED_ACTIVE_ROOT_AUTHORITY.json"
CONTRACT = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_MIGRATION_CONTRACT.json"
ROLLBACK_CONTRACT = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_ROLLBACK_CONTRACT.json"
PATHS = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_PROJECTED_PATH_REPORT.json"
SUPERVISOR = ROOT / "Scripts/invoke_phase4_m01_recovery05_active_plugin_root_migration01_once.ps1"
ROLLBACK = ROOT / "Scripts/rollback_phase4_m01_recovery05_active_plugin_root_migration01_once.ps1"
TERMINAL_FREEZE = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json"

AUTHORITIES: dict[Path, tuple[int, str]] = {
    TERMINAL_FREEZE: (5005, "f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5"),
    INVENTORY: (5457, "a8c6e995807a94d6074f2ad6611f6a98e6d7340dd4892498db855077dc574fe2"),
    COLLISIONS: (2363, "14b0e44c406c4fb20507b9345967878943ed761368663e13d9d990b0953dee04"),
    ACTIVE: (2109, "f3a9ae0774a2e77fa6b59588449b44315c6d9d23c08d404b936f2f2a4bd7abaa"),
    CONTRACT: (2938, "4a1a728ed11ebc9eda69b5be92ad1cb3729eb5ca6d2c87681acd662d88b58a02"),
    ROLLBACK_CONTRACT: (1928, "3f9ea27aed285045ea0c9f1f2f18a8c0c7f5a1fc70c24d9cd3619cf4a9de00a8"),
    PATHS: (928, "dfd4c45d4c62d2b7508b6eb25d63b53922c72c67331af75cc254c85818d9a758"),
}

FUTURE_PATHS = (
    ROOT / "Saved/PluginQuarantine/PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01",
    ROOT / "Saved/MigrationAttempts/PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01/attempt_01",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_MANIFEST.json",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_EMERGENCY_RECEIPT.jsonl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_file(path: Path, size: int, digest: str) -> None:
    if not path.is_file():
        raise AssertionError(f"missing: {path}")
    if path.stat().st_size != size:
        raise AssertionError(f"byte mismatch: {path}")
    if sha256(path) != digest:
        raise AssertionError(f"hash mismatch: {path}")


def verify_inventory() -> int:
    data = json.loads(INVENTORY.read_text(encoding="utf-8-sig"))
    records = data["records"]
    if len(records) != 23:
        raise AssertionError("plugin inventory must contain 23 files")
    expected: set[str] = set()
    for record in records:
        relative = record["relative_path"]
        expected.add(relative.casefold())
        assert_file(
            PLUGINS / Path(relative.replace("/", "\\")),
            int(record["bytes"]),
            record["sha256"],
        )
    actual = {
        str(path.relative_to(PLUGINS)).replace("\\", "/").casefold()
        for path in PLUGINS.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        raise AssertionError("undeclared or missing plugin file")
    roots = sorted(path.name for path in PLUGINS.iterdir() if path.is_dir())
    expected_roots = sorted(
        [
            "SkyguardRecovery03",
            "SkyguardRecovery03NativeRecovery01",
            "SkyguardRecovery03NativeRecovery04",
            "SkyguardRecovery03NativeRecovery05",
        ]
    )
    if roots != expected_roots:
        raise AssertionError("initial plugin discovery roots differ")
    return len(records)


def verify_contracts() -> None:
    collisions = json.loads(COLLISIONS.read_text(encoding="utf-8-sig"))
    if len(collisions["duplicate_module_identities"]) != 1:
        raise AssertionError("expected one duplicate module identity")
    if len(collisions["duplicate_module_rules_classes"]) != 1:
        raise AssertionError("expected one duplicate ModuleRules class")
    active = json.loads(ACTIVE.read_text(encoding="utf-8-sig"))
    if active["plugin_identity"] != "SkyguardRecovery03NativeRecovery05":
        raise AssertionError("wrong selected plugin")
    if active["enabled_by_default"]:
        raise AssertionError("selected plugin must remain disabled")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    if len(contract["moves"]) != 3:
        raise AssertionError("migration must contain exactly three moves")
    if contract["required_final_discovery_set"] != ["SkyguardRecovery03NativeRecovery05"]:
        raise AssertionError("wrong future plugin discovery set")
    if not all(
        contract["rules"][key]
        for key in (
            "no_delete",
            "no_overwrite",
            "no_merge",
            "no_copy",
            "no_retry",
            "no_partial_success",
            "atomic_directory_moves_only",
            "rollback_completed_moves_on_failure",
        )
    ):
        raise AssertionError("migration safety rule missing")
    path_report = json.loads(PATHS.read_text(encoding="utf-8-sig"))
    if path_report["longest_projected_destination_characters"] != len(
        path_report["longest_projected_destination"]
    ):
        raise AssertionError("projected path length mismatch")
    if path_report["longest_projected_destination_characters"] > 240:
        raise AssertionError("projected path exceeds contract")


def verify_script(path: Path, kind: str) -> dict[str, int]:
    text = path.read_text(encoding="utf-8-sig")
    for forbidden in (
        "Start-Process",
        "Remove-Item",
        "Copy-Item",
        "Move-Item",
        "UnrealEditor.exe",
        "UnrealEditor-Cmd.exe",
        "UnrealBuildTool.dll",
        "AutomationTool.dll",
        "blender.exe",
        "dotnet.exe",
    ):
        if forbidden.casefold() in text.casefold():
            raise AssertionError(f"{kind} contains forbidden launcher or cmdlet: {forbidden}")
    if text.count("[System.IO.Directory]::Move(") != 2:
        raise AssertionError(f"{kind} must contain one forward and one rollback Directory.Move path")
    if re.search(r"(?mi)^\s*(?:Remove|Copy|Move)-Item\b", text):
        raise AssertionError(f"{kind} contains mutating PowerShell cmdlet")
    if re.search(r"(?mi)^\s*\w+\s*=\s*(?:true|false|null)\s*$", text):
        raise AssertionError(f"{kind} contains bare PowerShell literal")
    for required in (
        "retry_count = 0",
        "delete_count = 0",
        "overwrite_count = 0",
        "copy_count = 0",
        "build_launch_count = 0",
        "unreal_launch_count = 0",
        "blender_launch_count = 0",
    ):
        if required not in text:
            raise AssertionError(f"{kind} missing invariant: {required}")
    return {"directory_move_call_sites": 2}


def main() -> int:
    for path, (size, digest) in AUTHORITIES.items():
        assert_file(path, size, digest)
    record_count = verify_inventory()
    verify_contracts()
    for path in FUTURE_PATHS:
        if path.exists():
            raise AssertionError(f"future governed path exists: {path}")
    migration_static = verify_script(SUPERVISOR, "migration supervisor")
    rollback_static = verify_script(ROLLBACK, "rollback supervisor")
    result = {
        "classification": "PASS",
        "authority_count": len(AUTHORITIES),
        "plugin_records_verified": record_count,
        "future_paths_absent": True,
        "migration_static": migration_static,
        "rollback_static": rollback_static,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": str(exc)}), file=sys.stderr)
        raise
