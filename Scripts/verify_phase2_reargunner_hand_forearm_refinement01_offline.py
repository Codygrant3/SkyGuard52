from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(r"D:\Skyguard52")
AUTHORITY = ROOT / "Saved" / "Reports" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_EXECUTION_AUTHORITY.json"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_CONTRACT.json"
POLICY = ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_CAMERAS.json"
RUBRIC = ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_VISUAL_RUBRIC.json"
WORKER = ROOT / "Scripts" / "Workers" / "worker_core_reargunner_hand_forearm_refinement01.py"
SUPERVISOR = ROOT / "Scripts" / "invoke_phase2_reargunner_hand_forearm_refinement01_once.ps1"
MANIFEST = ROOT / "Production" / "production_manifest.json"
BLOCKOUT_FREEZE = ROOT / "Docs" / "AAA_Review" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json"
ANTHROPOMETRIC = (
    ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "reports"
    / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_CHARACTER_ANTHROPOMETRIC_CONTRACT.json"
)
OLD_WORKER = ROOT / "Scripts" / "Workers" / "worker_core_hand_forearm.py"
FUTURE_ATTEMPT_ROOT = ROOT / "Production" / "Attempts" / "core-reargunner-hand-forearm-refinement01"
ASSET_ID = "core-reargunner-hand-forearm-refinement01"


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
    if sha256(path) != str(record["sha256"]):
        raise VerificationError(f"Hash mismatch: {path}")


def verify_freeze_members(path: Path) -> int:
    payload = load_json(path)
    members = payload.get("members", payload.get("files", []))
    if not isinstance(members, list) or not members:
        raise VerificationError(f"Freeze has no members: {path}")
    for original in members:
        record = dict(original)
        candidate = record.get("path", record.get("file", record.get("absolute_path")))
        if not candidate:
            raise VerificationError(f"Freeze member has no path: {path}")
        candidate_path = Path(candidate)
        if not candidate_path.is_absolute():
            candidate_path = ROOT / candidate_path
        record["path"] = str(candidate_path)
        verify_record(record)
    return len(members)


def heavy_processes() -> list[dict[str, str]]:
    completed = subprocess.run(
        ["tasklist.exe", "/fo", "csv", "/nh"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    governed = {
        "blender",
        "unrealeditor",
        "unrealeditor-cmd",
        "shadercompileworker",
        "automationtool",
        "unrealbuildtool",
        "cl",
        "link",
    }
    rows = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and Path(row[0]).stem.lower() in governed:
            rows.append({"name": row[0], "pid": row[1]})
    return rows


def check_contracts() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    policy = load_json(POLICY)
    cameras = load_json(CAMERAS)
    rubric = load_json(RUBRIC)
    if contract["asset_id"] != ASSET_ID:
        raise VerificationError("Wrong contract asset id.")
    dimensions = contract["provisional_dimensions"]
    expected = {"hand_length_m": 0.19, "hand_breadth_m": 0.085, "forearm_plus_hand_m": 0.46}
    for name, value in expected.items():
        if float(dimensions[name]["target"]) != value:
            raise VerificationError(f"Wrong provisional dimension: {name}")
    if dimensions["claim"] != "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE":
        raise VerificationError("The project-provisional dimension label is missing.")
    if contract["topology_and_uv"]["visible_triangle_budget_both_hands"] != 90000:
        raise VerificationError("Wrong visible triangle budget.")
    if contract["topology_and_uv"]["minimum_visible_vertices_both_hands"] != 12000:
        raise VerificationError("Wrong minimum visible vertex count.")
    if contract["required_rig"]["minimum_deform_bones_per_side"] != 18:
        raise VerificationError("Wrong deform-bone minimum.")
    if contract["required_outputs"]["render_count"] != 12:
        raise VerificationError("Wrong governed render count.")
    if len(cameras["views"]) != 12 or cameras["resolution"] != [2048, 2048]:
        raise VerificationError("Camera contract is not twelve 2048-square views.")
    lighting = {view.get("lighting") for view in cameras["views"]}
    if lighting != {"daylight", "overcast", "night", "wet", "cockpit"}:
        raise VerificationError(f"Incomplete governed lighting coverage: {sorted(lighting)}")
    frames = {int(view["frame"]) for view in cameras["views"]}
    if frames != {1, 20, 40, 60}:
        raise VerificationError(f"Wrong pose-frame coverage: {sorted(frames)}")
    if policy["geometry_rule"].find("must never be imported") < 0:
        raise VerificationError("Reference policy does not prohibit blockout geometry import.")
    if not rubric["automatic_pass_is_not_visual_acceptance"]:
        raise VerificationError("Rubric permits automatic visual acceptance.")
    return {
        "cameras": len(cameras["views"]),
        "lighting": sorted(lighting),
        "reject_rules": len(rubric["reject_if_any"]),
    }


def check_worker() -> dict[str, Any]:
    source = WORKER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(WORKER))
    required = [
        "SOURCE_HIGH",
        "bpy.data.metaballs.new",
        "fresh_metaball_anatomical_field_no_blockout_import",
        "RIG_RearGunnerHands_R01",
        "ACT_RifleTriggerADS",
        "export_animation_mode=\"ACTIONS\"",
        "minimum_vertices=6200",
        "target_triangles=27000",
        "VISIBLE_TRIANGLE_BUDGET = 90000",
        "geometry_rig_receipt.json",
        "pose_deformation_receipt.json",
        "source_parity_receipt.json",
        "blockout_geometry_imported\": False",
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Worker is missing contract token: {token}")
    forbidden = [
        "bpy.ops.import_",
        "bpy.data.libraries.load",
        "primitive_cube_add",
        "primitive_cylinder_add",
        "primitive_uv_sphere_add",
        "requests.",
        "openai",
        "anthropic",
        "grok",
        "three.js",
        "subprocess.",
    ]
    for token in forbidden:
        if token.lower() in source.lower():
            raise VerificationError(f"Worker contains forbidden dependency or donor path: {token}")
    if OLD_WORKER.read_bytes() == WORKER.read_bytes():
        raise VerificationError("Refinement01 worker is not independent from the failed worker.")
    return {"bytes": WORKER.stat().st_size, "sha256": sha256(WORKER)}


def check_supervisor() -> dict[str, Any]:
    source = SUPERVISOR.read_text(encoding="utf-8")
    required = [
        "AuthorizeSingleBlender",
        "OfflineContractTest",
        "Get-Sha256Lower",
        "Get-HeavyProcesses",
        "skyguard_production.py",
        "run $AssetId",
        ASSET_ID,
    ]
    for token in required:
        if token not in source:
            raise VerificationError(f"Supervisor is missing token: {token}")
    if source.count("run $AssetId") != 1:
        raise VerificationError("Supervisor must contain exactly one controller-run path.")
    for forbidden in ("Start-Process", "while (", "for (;;", "Blender MCP"):
        if forbidden.lower() in source.lower():
            raise VerificationError(f"Supervisor contains forbidden execution construct: {forbidden}")
    return {"bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR)}


def check_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    assets = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
    if len(assets) != 1:
        raise VerificationError("Expected one Refinement01 manifest entry.")
    asset = assets[0]
    if asset["status"] != "ready":
        raise VerificationError(f"Refinement01 registry state is not ready: {asset['status']}")
    worker = asset.get("worker", {})
    if worker.get("script") != "Scripts\\Workers\\worker_core_reargunner_hand_forearm_refinement01.py":
        raise VerificationError("Manifest does not bind the Refinement01 worker.")
    if int(worker.get("minimum_renders", 0)) != 12:
        raise VerificationError("Manifest render requirement is not twelve.")
    old_assets = [item for item in manifest["assets"] if item["id"] == "core-hand-forearm"]
    if len(old_assets) != 1 or old_assets[0]["status"] != "failed":
        raise VerificationError("The failed segmented-mannequin lane was not preserved.")
    return {"status": asset["status"], "worker": worker["script"], "old_lane": old_assets[0]["status"]}


def check_anthropometric_boundary() -> dict[str, Any]:
    payload = load_json(ANTHROPOMETRIC)
    envelope = payload["accommodation_envelope_mm"]
    selected = {"hand_length": 190, "hand_breadth": 85, "forearm_hand_length": 460}
    for name, value in selected.items():
        lower, upper = envelope[name]
        if not lower <= value <= upper:
            raise VerificationError(f"Selected project-provisional {name} is outside the frozen envelope.")
    if payload["classification"] != "READY_FOR_BLOCKOUT_ONLY":
        raise VerificationError("Anthropometric authority was overstated.")
    return {"selected_mm": selected, "classification": payload["classification"]}


def verify(require_future_namespace_absent: bool = True) -> dict[str, Any]:
    authority = load_json(AUTHORITY)
    if authority["classification"] != "PASSED_READY_FOR_EXPLICIT_SINGLE_REARGUNNER_HAND_FOREARM_REFINEMENT01_BLENDER_AUTHORIZATION":
        raise VerificationError("Execution authority is not ready.")
    for record in authority["authorities"]:
        verify_record(record)
    prior_members = verify_freeze_members(BLOCKOUT_FREEZE)
    contracts = check_contracts()
    worker = check_worker()
    supervisor = check_supervisor()
    manifest = check_manifest()
    anthropometric = check_anthropometric_boundary()
    active = heavy_processes()
    if active:
        raise VerificationError(f"Heavy processes are active: {active}")
    if require_future_namespace_absent and FUTURE_ATTEMPT_ROOT.exists():
        raise VerificationError(f"Future attempt namespace already exists: {FUTURE_ATTEMPT_ROOT}")
    return {
        "schema": "skyguard.phase2.reargunner-hand-forearm-refinement01.offline-verification.v1",
        "classification": "PASS",
        "authority_members": len(authority["authorities"]),
        "prior_freeze_members": prior_members,
        "contracts": contracts,
        "worker": worker,
        "supervisor": supervisor,
        "manifest": manifest,
        "anthropometric": anthropometric,
        "future_attempt_absent": not FUTURE_ATTEMPT_ROOT.exists(),
        "heavy_process_count": len(active),
        "blender_launch_count": 0,
        "unreal_launch_count": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--allow-existing-future-namespace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = verify(require_future_namespace_absent=not args.allow_existing_future_namespace)
    except Exception as exc:
        result = {
            "schema": "skyguard.phase2.reargunner-hand-forearm-refinement01.offline-verification.v1",
            "classification": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        }
        code = 1
    else:
        code = 0
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
