from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any


ROOT = Path(r"D:\Skyguard52")
AUTHORITY = ROOT / "Saved" / "Reports" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_EXECUTION_AUTHORITY.json"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_CONTRACT.json"
POLICY = ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_CAMERAS.json"
RUBRIC = ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_VISUAL_RUBRIC.json"
WORKER = ROOT / "Scripts" / "Workers" / "worker_core_yak52_airframe_refinement01.py"
SUPERVISOR = ROOT / "Scripts" / "invoke_phase2_yak52_airframe_refinement01_once.ps1"
MANIFEST = ROOT / "Production" / "production_manifest.json"
FUTURE_ATTEMPT_ROOT = ROOT / "Production" / "Attempts" / "core-yak52-airframe"


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
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


def verify_freeze_members(path: Path) -> int:
    payload = load_json(path)
    members = payload.get("files", payload.get("members", []))
    if not isinstance(members, list) or not members:
        raise VerificationError(f"Freeze has no members: {path}")
    for record in members:
        candidate = Path(record["path"])
        if not candidate.is_absolute():
            record = dict(record)
            record["path"] = str(ROOT / candidate)
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
    accessors = payload.get("accessors", [])
    positions = [item for item in accessors if item.get("type") == "VEC3" and "min" in item and "max" in item]
    if not positions:
        raise VerificationError("GLB has no bounded VEC3 accessors.")
    minimum = [min(float(item["min"][axis]) for item in positions) for axis in range(3)]
    maximum = [max(float(item["max"][axis]) for item in positions) for axis in range(3)]
    return {
        "nodes": len(payload.get("nodes", [])),
        "meshes": len(payload.get("meshes", [])),
        "materials": len(payload.get("materials", [])),
        "skins": len(payload.get("skins", [])),
        "animations": len(payload.get("animations", [])),
        "aggregate_local_accessor_extent": [maximum[index] - minimum[index] for index in range(3)],
    }


def check_contracts() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    policy = load_json(POLICY)
    cameras = load_json(CAMERAS)
    rubric = load_json(RUBRIC)
    if contract["asset_id"] != "core-yak52-airframe":
        raise VerificationError("Wrong contract asset id.")
    targets = contract["dimension_acceptance"]
    expected = {"overall_length_m": 7.745, "overall_height_m": 2.7, "wingspan_m": 9.3}
    for name, value in expected.items():
        if float(targets[name]["target"]) != value:
            raise VerificationError(f"Wrong dimension target: {name}")
    if policy["derived_artistic_geometry"]["required_label"] != "PROJECT_DERIVED_NONAUTHORITATIVE":
        raise VerificationError("Derived geometry label is not enforced.")
    if len(cameras["views"]) != 11 or cameras["resolution"] != [2560, 1440]:
        raise VerificationError("Camera contract is not the governed 11-view 2560x1440 set.")
    if not rubric["automatic_pass_is_not_visual_acceptance"]:
        raise VerificationError("Rubric permits automatic visual acceptance.")
    return {"cameras": len(cameras["views"]), "reject_rules": len(rubric["reject_if_any"])}


def check_worker() -> dict[str, Any]:
    source = WORKER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(WORKER))
    required = [
        "PROJECT_DERIVED_NONAUTHORITATIVE",
        "bpy.ops.wm.open_mainfile",
        "GEO_Airframe",
        "SOCKET_Propeller",
        "UCX_Yak52_Fuselage",
        "render_count",
        "2560",
        "1440",
        "source_parity_receipt.json",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Worker is missing contract token: {token}")
    forbidden = ["three.js", "requests.", "openai", "anthropic", "grok", "subprocess."]
    for token in forbidden:
        if token.lower() in source.lower():
            raise VerificationError(f"Worker contains forbidden dependency: {token}")
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
    assets = [asset for asset in manifest["assets"] if asset["id"] == "core-yak52-airframe"]
    if len(assets) != 1:
        raise VerificationError("Expected one airframe registry entry.")
    asset = assets[0]
    if asset["status"] not in {"blocked_reference", "ready"}:
        raise VerificationError(f"Unexpected airframe state: {asset['status']}")
    worker = asset.get("worker", {})
    if worker.get("script") != "Scripts\\Workers\\worker_core_yak52_airframe_refinement01.py":
        raise VerificationError("Manifest does not bind the Refinement01 worker.")
    if int(worker.get("minimum_renders", 0)) != 11:
        raise VerificationError("Manifest render requirement is not 11.")
    return {"status": asset["status"], "worker": worker["script"]}


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
    import csv
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and Path(row[0]).stem.lower() in names:
            rows.append({"name": row[0], "pid": row[1]})
    return rows


def verify(require_future_namespace_absent: bool = True) -> dict[str, Any]:
    authority = load_json(AUTHORITY)
    for record in authority["authorities"]:
        verify_record(record)
    prior_freezes = [
        ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_R6_TECHNICAL_REFERENCE_INTAKE_CYCLE04_FREEZE.json",
        ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_R6_SLICE01_FREEZE.json",
        ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_R6_PHOTO_INTAKE_CYCLE03_FREEZE_2026-08-04.json",
    ]
    member_counts = {path.name: verify_freeze_members(path) for path in prior_freezes}
    glb = inspect_glb(Path(authority["authorities"][4]["path"]))
    if glb["nodes"] < 200 or glb["meshes"] < 200:
        raise VerificationError("R3 source is not the governed full donor candidate.")
    if glb["skins"] != 0 or glb["animations"] != 0:
        raise VerificationError("R3 source unexpectedly contains skeletal or animation authority.")
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
        "schema": "skyguard.phase2.yak52-airframe-refinement01.offline-verification.v1",
        "classification": "PASS",
        "authority_records": len(authority["authorities"]),
        "prior_freeze_members": member_counts,
        "r3_glb": glb,
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
