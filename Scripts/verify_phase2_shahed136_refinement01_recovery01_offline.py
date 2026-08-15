from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ORIGINAL_FREEZE = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_OFFLINE_DESIGN_FREEZE.json"
ORIGINAL_FREEZE_BYTES = 3858
ORIGINAL_FREEZE_SHA256 = "6055936112b5dc261dfdc2c104ca9bc6104468f49805508c3f3e1991157bd4a5"
AUTHORITY = ROOT / "Saved" / "Reports" / "PHASE2_SHAHED136_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json"
COMPATIBILITY = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_RECOVERY01_COMPATIBILITY_CONTRACT.json"
ORIGINAL_WORKER = ROOT / "Scripts" / "Workers" / "worker_core_shahed136_refinement01.py"
WRAPPER = ROOT / "Scripts" / "Workers" / "worker_core_shahed136_refinement01_recovery01.py"
SUPERVISOR = ROOT / "Scripts" / "invoke_phase2_shahed136_refinement01_recovery01_once.ps1"
MANIFEST = ROOT / "Production" / "production_manifest.json"
FUTURE_ATTEMPT_ROOT = ROOT / "Production" / "Attempts" / "core-shahed136"


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise VerificationError(f"JSON root is not an object: {path}")
    return payload


def verify_record(record: dict[str, Any]) -> None:
    path = Path(record["path"])
    if not path.is_file():
        raise VerificationError(f"Missing authority: {path}")
    if path.stat().st_size != int(record["bytes"]):
        raise VerificationError(f"Byte mismatch: {path}")
    if sha256(path) != record["sha256"]:
        raise VerificationError(f"Hash mismatch: {path}")


def verify_original_freeze() -> int:
    if ORIGINAL_FREEZE.stat().st_size != ORIGINAL_FREEZE_BYTES or sha256(ORIGINAL_FREEZE) != ORIGINAL_FREEZE_SHA256:
        raise VerificationError("Original Refinement01 offline freeze changed.")
    payload = load_json(ORIGINAL_FREEZE)
    members = payload.get("members", [])
    if len(members) != 16:
        raise VerificationError(f"Expected 16 original freeze members, found {len(members)}.")
    for record in members:
        verify_record(record)
    return len(members)


def check_compatibility_binding() -> dict[str, Any]:
    source = WRAPPER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(WRAPPER))
    required = [
        "EXPECTED_SHA256",
        "LEGACY_ACTION_BLOCK",
        "BLENDER52_ACTION_BLOCK",
        "source.count(LEGACY_ACTION_BLOCK) != 1",
        "rig.animation_data.action.fcurves",
        "load_patched_namespace",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Compatibility wrapper is missing token: {token}")
    if source.count("source.replace(LEGACY_ACTION_BLOCK, BLENDER52_ACTION_BLOCK, 1)") != 1:
        raise VerificationError("Compatibility wrapper does not apply exactly one bounded replacement.")
    if ORIGINAL_WORKER.stat().st_size != 31801 or sha256(ORIGINAL_WORKER) != "7a845f941788c47cb2baab863bc17ce6606f626d7257170eb802f1f4a40c283b":
        raise VerificationError("Frozen original worker changed.")
    specification = importlib.util.spec_from_file_location("shahed_recovery01_wrapper", WRAPPER)
    if specification is None or specification.loader is None:
        raise VerificationError("Could not load compatibility wrapper.")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    namespace = module.load_patched_namespace()
    if not callable(namespace.get("main")):
        raise VerificationError("Patched worker exposes no callable main.")
    patched_main = namespace["create_asset"].__code__.co_names
    if "fcurves" in patched_main:
        raise VerificationError("Patched create_asset bytecode still contains direct fcurves access.")
    contract = load_json(COMPATIBILITY)
    if contract["permitted_runtime_patch"]["count"] != 1:
        raise VerificationError("Compatibility contract permits more than one patch.")
    return {
        "wrapper_bytes": WRAPPER.stat().st_size,
        "wrapper_sha256": sha256(WRAPPER),
        "patched_main_callable": True,
        "direct_action_fcurves_removed": True,
    }


def check_supervisor() -> dict[str, Any]:
    source = SUPERVISOR.read_text(encoding="utf-8")
    required = [
        "AuthorizeSingleBlender",
        "OfflineContractTest",
        "PHASE2_SHAHED136_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json",
        "worker_core_shahed136_refinement01_recovery01.py",
        "run $AssetId",
        "Get-Sha256Lower",
        "Get-HeavyProcesses",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Recovery01 supervisor is missing token: {token}")
    if source.count("run $AssetId") != 1:
        raise VerificationError("Recovery01 supervisor has more than one controller run path.")
    for forbidden in ("while (", "for (;;", "Start-Process", "UnrealEditor.exe"):
        if forbidden in source:
            raise VerificationError(f"Recovery01 supervisor contains forbidden construct: {forbidden}")
    return {"bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR)}


def check_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    assets = [asset for asset in manifest["assets"] if asset["id"] == "core-shahed136"]
    if len(assets) != 1:
        raise VerificationError("Expected one Shahed-136 registry entry.")
    asset = assets[0]
    if asset.get("status") != "ready":
        raise VerificationError(f"Shahed-136 is not ready: {asset.get('status')}")
    worker = asset.get("worker", {})
    if worker.get("script") != "Scripts\\Workers\\worker_core_shahed136_refinement01_recovery01.py":
        raise VerificationError("Manifest does not bind the Recovery01 compatibility worker.")
    if int(worker.get("minimum_renders", 0)) != 8:
        raise VerificationError("Manifest render requirement is not eight.")
    return {"status": asset["status"], "worker": worker["script"], "minimum_renders": 8}


def heavy_processes() -> list[dict[str, str]]:
    completed = subprocess.run(
        ["tasklist.exe", "/fo", "csv", "/nh"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    names = {"blender", "unrealeditor", "unrealeditor-cmd", "shadercompileworker", "automationtool", "unrealbuildtool", "cl", "link"}
    return [
        {"name": row[0], "pid": row[1]}
        for row in csv.reader(completed.stdout.splitlines())
        if len(row) >= 2 and Path(row[0]).stem.lower() in names
    ]


def verify(require_future_namespace_absent: bool = True) -> dict[str, Any]:
    original_members = verify_original_freeze()
    authority = load_json(AUTHORITY)
    if authority.get("asset_id") != "core-shahed136" or len(authority.get("authorities", [])) != 15:
        raise VerificationError("Recovery01 execution authority is incomplete.")
    for record in authority["authorities"]:
        verify_record(record)
    compatibility = check_compatibility_binding()
    supervisor = check_supervisor()
    manifest = check_manifest()
    active = heavy_processes()
    if active:
        raise VerificationError(f"Heavy processes are active: {active}")
    if require_future_namespace_absent and FUTURE_ATTEMPT_ROOT.exists():
        raise VerificationError(f"Future attempt root already exists: {FUTURE_ATTEMPT_ROOT}")
    return {
        "schema": "skyguard.phase2.shahed136-refinement01-recovery01.offline-verification.v1",
        "classification": "PASS",
        "original_freeze_members": original_members,
        "authority_records": 15,
        "compatibility": compatibility,
        "supervisor": supervisor,
        "manifest": manifest,
        "heavy_process_count": 0,
        "future_attempt_root_absent": not FUTURE_ATTEMPT_ROOT.exists(),
        "blender_launched": False,
        "unreal_launched": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-existing-attempt-root", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(require_future_namespace_absent=not args.allow_existing_attempt_root)
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
