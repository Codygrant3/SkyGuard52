from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from typing import Any


ROOT = Path(r"D:\Skyguard52")
AUTHORITY = ROOT / "Saved" / "Reports" / "PHASE2_SHAHED136_REFINEMENT01_EXECUTION_AUTHORITY.json"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_CONTRACT.json"
POLICY = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_CAMERAS.json"
RUBRIC = ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_VISUAL_RUBRIC.json"
WORKER = ROOT / "Scripts" / "Workers" / "worker_core_shahed136_refinement01.py"
SUPERVISOR = ROOT / "Scripts" / "invoke_phase2_shahed136_refinement01_once.ps1"
MANIFEST = ROOT / "Production" / "production_manifest.json"
PRIOR_FREEZE = ROOT / "Docs" / "AAA_Review" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json"
SOURCE_GLB = ROOT / "Blender" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01" / "exports" / "PROVISIONAL_SHAHED136_ENVELOPE.glb"
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


def verify_prior_freeze() -> int:
    payload = load_json(PRIOR_FREEZE)
    if payload.get("classification") != "PASSED_RECOVERY03_PROVISIONAL_BLOCKOUTS_ACCEPTED":
        raise VerificationError("The accepted blockout freeze classification changed.")
    members = payload.get("members", [])
    if len(members) != 24:
        raise VerificationError(f"Expected 24 accepted-blockout members, found {len(members)}.")
    for record in members:
        verify_record(record)
    return len(members)


def inspect_glb(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        magic, version, length = struct.unpack("<III", stream.read(12))
        if magic != 0x46546C67 or version != 2 or length != path.stat().st_size:
            raise VerificationError("Invalid GLB header or length.")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        if chunk_type != 0x4E4F534A:
            raise VerificationError("First GLB chunk is not JSON.")
        payload = json.loads(stream.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\x00"))
    names = [node.get("name") for node in payload.get("nodes", [])]
    required = {
        "SHAHED_OfficialReportedPlanform",
        "SOCKET_Shahed_DamageCore_PROVISIONAL",
        "SOCKET_Shahed_WingL_PROVISIONAL",
        "SOCKET_Shahed_WingR_PROVISIONAL",
    }
    if not required.issubset(set(names)):
        raise VerificationError("The accepted envelope GLB lost governed provisional nodes.")
    return {
        "nodes": len(payload.get("nodes", [])),
        "meshes": len(payload.get("meshes", [])),
        "materials": len(payload.get("materials", [])),
        "skins": len(payload.get("skins", [])),
        "animations": len(payload.get("animations", [])),
        "names": names,
    }


def check_contracts() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    policy = load_json(POLICY)
    cameras = load_json(CAMERAS)
    rubric = load_json(RUBRIC)
    if contract.get("asset_id") != "core-shahed136":
        raise VerificationError("Wrong contract asset id.")
    envelope = contract["primary_envelope_acceptance"]
    if float(envelope["overall_length_m"]["target"]) != 3.3 or float(envelope["wingspan_m"]["target"]) != 3.0:
        raise VerificationError("Wrong primary envelope targets.")
    if policy["project_derived_geometry"]["required_label"] != "PROJECT_DERIVED_NONAUTHORITATIVE":
        raise VerificationError("Derived geometry truth label is not enforced.")
    if len(cameras.get("views", [])) != 8 or cameras.get("resolution") != [2560, 1440]:
        raise VerificationError("Camera contract is not the governed eight-view 2560x1440 set.")
    if not rubric.get("automatic_pass_is_not_visual_acceptance"):
        raise VerificationError("Rubric permits automatic visual acceptance.")
    if not rubric.get("unreal_import_requires_separate_gate"):
        raise VerificationError("Rubric permits ungoverned Unreal import.")
    return {
        "required_geometry": len(contract["required_geometry"]),
        "required_sockets": len(contract["required_sockets"]),
        "required_collision": len(contract["required_collision"]),
        "required_damage_states": len(contract["required_damage_states"]),
        "cameras": len(cameras["views"]),
        "reject_rules": len(rubric["reject_if_any"]),
    }


def check_worker() -> dict[str, Any]:
    source = WORKER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(WORKER))
    required = [
        "PROJECT_DERIVED_NONAUTHORITATIVE",
        "GEO_Shahed_WingShell",
        "GEO_Shahed_Fuselage",
        "GEO_Shahed_NoseCone",
        "RIG_PropellerPivot",
        "ANIM_PropellerPreview_1s",
        "UCX_Shahed_Fuselage",
        "DMG_Shahed_Wing_L",
        "SOCKET_EngineVFX",
        "artifact_receipt.json",
        "export_structure_receipt.json",
        "2560",
        "1440",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Worker is missing contract token: {token}")
    forbidden = ["three.js", "requests.", "openai", "anthropic", "grok", "http://", "https://", "subprocess."]
    for token in forbidden:
        if token.lower() in source.lower():
            raise VerificationError(f"Worker contains forbidden dependency: {token}")
    if source.count("bpy.ops.export_scene.gltf") != 1:
        raise VerificationError("Worker must contain exactly one GLB export path.")
    return {"bytes": WORKER.stat().st_size, "sha256": sha256(WORKER)}


def check_supervisor() -> dict[str, Any]:
    source = SUPERVISOR.read_text(encoding="utf-8")
    required = [
        "AuthorizeSingleBlender",
        "OfflineContractTest",
        "skyguard_production.py",
        "run $AssetId",
        "Get-Sha256Lower",
        "Get-HeavyProcesses",
        "core-shahed136",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Supervisor is missing token: {token}")
    if source.count("run $AssetId") != 1:
        raise VerificationError("Supervisor must contain exactly one controller run path.")
    for forbidden in ("while (", "for (;;", "UnrealEditor.exe", "Start-Process"):
        if forbidden in source:
            raise VerificationError(f"Supervisor contains forbidden execution construct: {forbidden}")
    return {"bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR)}


def check_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    assets = [asset for asset in manifest["assets"] if asset["id"] == "core-shahed136"]
    if len(assets) != 1:
        raise VerificationError("Expected one Shahed-136 registry entry.")
    asset = assets[0]
    if asset.get("status") != "ready":
        raise VerificationError(f"Shahed-136 state is not ready: {asset.get('status')}")
    worker = asset.get("worker", {})
    if worker.get("script") != "Scripts\\Workers\\worker_core_shahed136_refinement01.py":
        raise VerificationError("Manifest does not bind the Refinement01 worker.")
    if int(worker.get("minimum_renders", 0)) != 8:
        raise VerificationError("Manifest render requirement is not eight.")
    if asset.get("blocker") is not None:
        raise VerificationError("Ready Shahed-136 registry entry retains a blocker.")
    return {"status": asset["status"], "worker": worker["script"], "minimum_renders": worker["minimum_renders"]}


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
    rows = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and Path(row[0]).stem.lower() in names:
            rows.append({"name": row[0], "pid": row[1]})
    return rows


def verify(require_future_namespace_absent: bool = True) -> dict[str, Any]:
    authority = load_json(AUTHORITY)
    if authority.get("asset_id") != "core-shahed136":
        raise VerificationError("Execution authority has the wrong asset id.")
    for record in authority["authorities"]:
        verify_record(record)
    accepted_members = verify_prior_freeze()
    glb = inspect_glb(SOURCE_GLB)
    if glb["nodes"] != 6 or glb["meshes"] != 3 or glb["skins"] != 0 or glb["animations"] != 0:
        raise VerificationError("Accepted envelope GLB structure changed.")
    contracts = check_contracts()
    worker = check_worker()
    supervisor = check_supervisor()
    manifest = check_manifest()
    active = heavy_processes()
    if active:
        raise VerificationError(f"Heavy processes are active: {active}")
    if require_future_namespace_absent and FUTURE_ATTEMPT_ROOT.exists():
        raise VerificationError(f"Future attempt root already exists: {FUTURE_ATTEMPT_ROOT}")
    return {
        "schema": "skyguard.phase2.shahed136-refinement01.offline-verification.v1",
        "classification": "PASS",
        "authority_records": len(authority["authorities"]),
        "accepted_blockout_members": accepted_members,
        "accepted_glb": glb,
        "contracts": contracts,
        "worker": worker,
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
