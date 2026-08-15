from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "core-rifle-method05-stagea"
AUTHORITY = ROOT / "Saved" / "Reports" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_EXECUTION_AUTHORITY.json"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_CONTRACT.json"
POLICY = ROOT / "Docs" / "AAA_Review" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_REFERENCE_POLICY.json"
CAMERAS = ROOT / "Docs" / "AAA_Review" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_CAMERAS.json"
RUBRIC = ROOT / "Docs" / "AAA_Review" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_VISUAL_RUBRIC.json"
WORKER = ROOT / "Scripts" / "Workers" / "worker_core_rifle_method05_deterministic_stagea.py"
SUPERVISOR = ROOT / "Scripts" / "invoke_p0_core_rifle_method05_deterministic_stagea_once.ps1"
CONTROLLER = ROOT / "Scripts" / "skyguard_production.py"
MANIFEST = ROOT / "Production" / "production_manifest.json"
FUTURE_ATTEMPT_ROOT = ROOT / "Production" / "Attempts" / ASSET_ID
FUTURE_TERMINAL = ROOT / "Saved" / "Reports" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_SUPERVISOR_TERMINAL.json"
FUTURE_EMERGENCY = ROOT / "Saved" / "Reports" / "P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_SUPERVISOR_EMERGENCY_RECEIPT.jsonl"
RAIL_RECEIPT = ROOT / "Production" / "Attempts" / "support-rail-coupon" / "attempt_20260807T221818127741Z" / "output" / "dimension_receipt.json"
RAIL_REVIEW = ROOT / "Production" / "Attempts" / "support-rail-coupon" / "attempt_20260807T221818127741Z" / "visual_review.json"

EXPECTED_RAIL = {
    "top_width": 0.021209,
    "profile_minimum_height": 0.009322,
    "dovetail_width": 0.018999,
    "groove_width": 0.005232,
    "pitch": 0.010008,
}
EXPECTED_SOCKETS = {
    "SOCKET_Rail_Origin",
    "SOCKET_Muzzle",
    "SOCKET_Receiver_Interface",
    "SOCKET_SupportHand",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


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
    require(path.is_file(), f"Missing immutable authority: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"Byte mismatch: {path}")
    require(sha256(path) == record["sha256"], f"SHA-256 mismatch: {path}")


def load_worker_module() -> Any:
    specification = importlib.util.spec_from_file_location("skyguard_rifle_method05_stagea", WORKER)
    require(specification is not None and specification.loader is not None, "Could not create worker import specification")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def polygon_area(vertices: list[tuple[float, float, float]], face: tuple[int, ...]) -> float:
    nx = ny = nz = 0.0
    for index, current_index in enumerate(face):
        next_index = face[(index + 1) % len(face)]
        current = vertices[current_index]
        following = vertices[next_index]
        nx += (current[1] - following[1]) * (current[2] + following[2])
        ny += (current[2] - following[2]) * (current[0] + following[0])
        nz += (current[0] - following[0]) * (current[1] + following[1])
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)


def check_pure_topology(module: Any) -> dict[str, Any]:
    vertices, faces, solid = module.build_handguard_shell_geometry()
    require(vertices and faces, "Pure handguard builder returned no geometry")
    require(sum(1 for value in solid.values() if not value) > 0, "Handguard has no real omitted window cells")
    edge_incidence: Counter[tuple[int, int]] = Counter()
    edge_direction: Counter[tuple[int, int]] = Counter()
    used_vertices: set[int] = set()
    minimum_area = float("inf")
    for face in faces:
        require(len(face) >= 3, "Topology contains a face with fewer than three vertices")
        require(len(set(face)) == len(face), "Topology contains a repeated-index face")
        require(all(0 <= index < len(vertices) for index in face), "Topology contains an invalid vertex index")
        used_vertices.update(face)
        minimum_area = min(minimum_area, polygon_area(vertices, face))
        for first, second in zip(face, face[1:] + face[:1]):
            edge_incidence[tuple(sorted((first, second)))] += 1
            edge_direction[(first, second)] += 1
    bad_incidence = [edge for edge, count in edge_incidence.items() if count != 2]
    require(not bad_incidence, f"Pure handguard topology has {len(bad_incidence)} non-manifold boundary edges")
    orientation_errors = [
        edge
        for edge in edge_incidence
        if edge_direction[(edge[0], edge[1])] != 1 or edge_direction[(edge[1], edge[0])] != 1
    ]
    require(not orientation_errors, f"Pure handguard topology has {len(orientation_errors)} inconsistent edge orientations")
    require(len(used_vertices) == len(vertices), "Pure handguard topology contains loose vertices")
    require(minimum_area > 1e-12, "Pure handguard topology contains a zero-area face")
    estimated_python_geometry_bytes = len(vertices) * 96 + len(faces) * 128 + len(edge_incidence) * 128
    require(estimated_python_geometry_bytes < 16 * 1024 * 1024, "Pure geometry estimate exceeds the 16 MiB offline bound")
    return {
        "vertices": len(vertices),
        "faces": len(faces),
        "edges": len(edge_incidence),
        "solid_cells": sum(1 for value in solid.values() if value),
        "void_cells": sum(1 for value in solid.values() if not value),
        "loose_vertices": 0,
        "non_manifold_edges": 0,
        "orientation_errors": 0,
        "minimum_face_area": minimum_area,
        "estimated_python_geometry_bytes": estimated_python_geometry_bytes,
    }


def check_worker() -> dict[str, Any]:
    source = WORKER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(WORKER))
    top_level_imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported_names = {
        alias.name.split(".")[0]
        for node in top_level_imports
        for alias in node.names
    }
    require("bpy" not in imported_names and "bmesh" not in imported_names and "mathutils" not in imported_names, "Worker imports Blender modules at module scope")
    forbidden = [
        "numpy",
        "np.repeat",
        "np.tile",
        "requests.",
        "openai",
        "anthropic",
        "grok",
        "blender-mcp",
        "three.js",
        "bpy.ops.wm.open_mainfile",
        "Method01",
        "Method02",
        "Method03",
        'empty_display_type = "CROSS"',
    ]
    for token in forbidden:
        require(token.lower() not in source.lower(), f"Worker contains forbidden token: {token}")
    required = [
        "build_handguard_shell_geometry",
        "explicit outer and inner superellipse cage",
        "real omitted shell cells",
        'empty_display_type = "PLAIN_AXES"',
        "SOCKET_Rail_Origin",
        "SOCKET_Muzzle",
        "SOCKET_Receiver_Interface",
        "SOCKET_SupportHand",
        "UCX_M05A_ForwardAssembly",
        "stageA_topology_inventory.json",
        "stageA_manifold_intersection_validation.json",
        "stageA_terminal_receipt.json",
        "BLENDER_EEVEE",
        "export_apply=True",
    ]
    for token in required:
        require(token in source, f"Worker is missing required contract token: {token}")
    module = load_worker_module()
    actual_rail = {
        "top_width": module.RAIL_TOP_WIDTH_M,
        "profile_minimum_height": module.RAIL_PROFILE_HEIGHT_M,
        "dovetail_width": module.RAIL_DOVETAIL_WIDTH_M,
        "groove_width": module.RAIL_GROOVE_WIDTH_M,
        "pitch": module.RAIL_PITCH_M,
    }
    require(actual_rail == EXPECTED_RAIL, f"Worker rail constants differ: {actual_rail}")
    require(set(module.REQUIRED_SOCKETS) == EXPECTED_SOCKETS, "Worker socket set differs")
    require(module.REQUIRED_COLLISION == "UCX_M05A_ForwardAssembly", "Worker collision name differs")
    checkpoints = module.checkpoint_views()
    finals = module.final_views()
    require(len(checkpoints) == 3, "Worker checkpoint group count is not three")
    require(sum(len(views) for views in checkpoints.values()) == 15, "Worker checkpoint render count is not fifteen")
    require(len(finals) == 12, "Worker final render count is not twelve")
    require(tuple(module.CHECKPOINT_RESOLUTION) == (1600, 900), "Worker checkpoint resolution differs")
    require(tuple(module.FINAL_RESOLUTION) == (2560, 1440), "Worker final resolution differs")
    topology = check_pure_topology(module)
    return {
        "bytes": WORKER.stat().st_size,
        "sha256": sha256(WORKER),
        "rail_dimensions": actual_rail,
        "checkpoint_groups": len(checkpoints),
        "checkpoint_renders": sum(len(views) for views in checkpoints.values()),
        "final_renders": len(finals),
        "topology": topology,
        "module_scope_blender_imports": 0,
        "numpy_usage": False,
    }


def check_contracts(module: Any) -> dict[str, Any]:
    contract = load_json(CONTRACT)
    policy = load_json(POLICY)
    cameras = load_json(CAMERAS)
    rubric = load_json(RUBRIC)
    require(contract["asset_id"] == ASSET_ID, "Contract asset id differs")
    require(contract["accepted_rail_dimensions_m"] == EXPECTED_RAIL, "Contract rail dimensions differ")
    required_outputs = contract["required_outputs"]
    require(required_outputs["checkpoint_groups"] == 3, "Contract checkpoint group count differs")
    require(required_outputs["checkpoint_render_count"] == 15, "Contract checkpoint render count differs")
    require(required_outputs["checkpoint_resolution"] == [1600, 900], "Contract checkpoint resolution differs")
    require(required_outputs["final_render_count"] == 12, "Contract final render count differs")
    require(required_outputs["final_resolution"] == [2560, 1440], "Contract final resolution differs")
    require(contract["automatic_acceptance"] is False, "Contract permits automatic acceptance")
    require(contract["unreal_import_authorized"] is False, "Contract permits Unreal import")
    require(policy["failed_geometry_policy"]["mesh_reuse_allowed"] is False, "Reference policy permits failed mesh reuse")
    require(policy["failed_geometry_policy"]["topology_reuse_allowed"] is False, "Reference policy permits failed topology reuse")
    checkpoint_names = [name for values in cameras["checkpoint_groups"].values() for name in values]
    module_checkpoint_names = [view["name"] for values in module.checkpoint_views().values() for view in values]
    require(checkpoint_names == module_checkpoint_names, "Checkpoint camera names differ from worker")
    final_names = [item["name"] for item in cameras["final_views"]]
    require(final_names == [item["name"] for item in module.final_views()], "Final camera names differ from worker")
    require(cameras["checkpoint_resolution"] == [1600, 900], "Camera checkpoint resolution differs")
    require(cameras["final_resolution"] == [2560, 1440], "Camera final resolution differs")
    require(rubric["automatic_pass_is_not_visual_acceptance"] is True, "Rubric permits automatic visual acceptance")
    require(len(rubric["reject_if_any"]) >= 10, "Visual rubric is not sufficiently bounded")
    return {
        "contract": CONTRACT.name,
        "reference_policy": POLICY.name,
        "checkpoint_views": len(checkpoint_names),
        "final_views": len(final_names),
        "visual_reject_rules": len(rubric["reject_if_any"]),
    }


def check_rail_authority() -> dict[str, Any]:
    receipt = load_json(RAIL_RECEIPT)
    review = load_json(RAIL_REVIEW)
    dimensions = receipt["dimension_validation"]["authoritative_dimensions_m"]
    mapped = {
        "top_width": float(dimensions["top_width"]),
        "profile_minimum_height": float(dimensions["profile_height_min"]),
        "dovetail_width": float(dimensions["dovetail_width"]),
        "groove_width": float(dimensions["groove_width"]),
        "pitch": float(dimensions["pitch"]),
    }
    require(mapped == EXPECTED_RAIL, f"Accepted rail receipt differs: {mapped}")
    require(receipt["dimension_validation"]["all_passed"] is True, "Rail dimension receipt is not passing")
    require(review["decision"] == "accept", "Rail coupon visual review is not accepted")
    require(review["terminal_sha256"] == sha256(RAIL_REVIEW.parent / "terminal.json"), "Rail review terminal binding differs")
    return {"dimensions": mapped, "review_decision": review["decision"]}


def check_manifest(authority: dict[str, Any]) -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    assets = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
    require(len(assets) == 1, "Manifest must contain exactly one Method05 StageA entry")
    asset = assets[0]
    binding = authority["mutable_manifest_binding"]
    require(asset["status"] == binding["expected_status"], f"Unexpected Method05 StageA state: {asset['status']}")
    require(asset["worker"]["script"] == binding["expected_worker_script"], "Manifest worker script differs")
    require(asset["worker"]["arguments"] == binding["expected_worker_arguments"], "Manifest worker arguments differ")
    require(int(asset["worker"]["minimum_renders"]) == int(binding["expected_minimum_renders"]), "Manifest render requirement differs")
    require(asset["supersedes_only_after_acceptance"] == "core-rifle", "Manifest supersession boundary differs")
    legacy = [item for item in manifest["assets"] if item["id"] == "core-rifle"]
    require(len(legacy) == 1 and legacy[0]["status"] == "failed", "Legacy failed core-rifle evidence was changed")
    require(legacy[0]["worker"]["script"] == "Scripts\\Workers\\worker_core_rifle_artist_grade.py", "Legacy rifle worker was changed")
    return {
        "asset_count": len(manifest["assets"]),
        "status": asset["status"],
        "worker": asset["worker"]["script"],
        "minimum_renders": asset["worker"]["minimum_renders"],
        "legacy_status": legacy[0]["status"],
    }


def check_supervisor() -> dict[str, Any]:
    source = SUPERVISOR.read_text(encoding="utf-8")
    required = [
        "AuthorizeSingleBlender",
        "OfflineContractTest",
        "Get-Sha256Lower",
        "Assert-ManifestBinding",
        "Assert-FutureNamespacesAbsent",
        "Get-HeavyProcesses",
        "run $AssetId",
        "PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW",
        "SUPERVISOR_TERMINAL.json",
        "SUPERVISOR_EMERGENCY_RECEIPT.jsonl",
    ]
    for token in required:
        require(token in source, f"Supervisor is missing token: {token}")
    require(source.count("run $AssetId") == 1, "Supervisor does not contain exactly one controller run path")
    forbidden = ["Start-Process", "UnrealEditor.exe", "UnrealEditor-Cmd.exe", "grok", "blender-mcp", "while (", "for (;;", "--restore", "retry"]
    lowered = source.lower()
    for token in forbidden:
        if token == "retry":
            require("retry_count = 0" in lowered and lowered.count("retry") == 1, "Supervisor contains a retry path")
        else:
            require(token.lower() not in lowered, f"Supervisor contains forbidden construct: {token}")
    require("[Environment]::Exit([int]3)" in source, "Supervisor lacks exact conflict exit 3")
    require("[Environment]::Exit([int]2)" in source, "Supervisor lacks exact refusal exit 2")
    return {"bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR), "controller_run_paths": 1}


def heavy_processes() -> list[dict[str, str]]:
    completed = subprocess.run(
        ["tasklist.exe", "/fo", "csv", "/nh"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(completed.returncode == 0, f"tasklist failed: {completed.stderr.strip()}")
    names = {"blender", "unrealeditor", "unrealeditor-cmd", "shadercompileworker", "automationtool", "unrealbuildtool", "cl", "link"}
    records: list[dict[str, str]] = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and Path(row[0]).stem.lower() in names:
            records.append({"name": row[0], "pid": row[1]})
    return records


def check_controller_audit() -> dict[str, Any]:
    completed = subprocess.run(
        ["python", str(CONTROLLER), "audit"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(completed.returncode == 0, f"Production controller audit failed: {completed.stderr.strip()}")
    payload = json.loads(completed.stdout)
    require(payload.get("pass") is True, f"Production audit is not passing: {payload.get('errors')}")
    require(ASSET_ID in payload.get("executable_worker_assets", []), "Method05 StageA is absent from executable workers")
    return {"pass": True, "asset_count": payload["asset_count"], "heavy_processes": payload["heavy_processes"]}


def verify(require_future_namespaces_absent: bool = True) -> dict[str, Any]:
    authority = load_json(AUTHORITY)
    require(authority["asset_id"] == ASSET_ID, "Execution authority asset id differs")
    for record in authority["immutable_authorities"]:
        verify_record(record)
    module = load_worker_module()
    rail = check_rail_authority()
    worker = check_worker()
    contracts = check_contracts(module)
    manifest = check_manifest(authority)
    supervisor = check_supervisor()
    active = heavy_processes()
    require(not active, f"Heavy processes are active: {active}")
    if require_future_namespaces_absent:
        require(not FUTURE_ATTEMPT_ROOT.exists(), f"Future attempt root already exists: {FUTURE_ATTEMPT_ROOT}")
        require(not FUTURE_TERMINAL.exists(), f"Future supervisor terminal already exists: {FUTURE_TERMINAL}")
        require(not FUTURE_EMERGENCY.exists(), f"Future emergency receipt already exists: {FUTURE_EMERGENCY}")
    controller_audit = check_controller_audit()
    return {
        "schema": "skyguard.p0.core-rifle.method05-deterministic-stagea.offline-verification.v1",
        "classification": "PASS",
        "authority_records": len(authority["immutable_authorities"]),
        "rail_authority": rail,
        "worker": worker,
        "contracts": contracts,
        "manifest": manifest,
        "supervisor": supervisor,
        "controller_audit": controller_audit,
        "heavy_process_count": 0,
        "future_namespaces_absent": not any(path.exists() for path in (FUTURE_ATTEMPT_ROOT, FUTURE_TERMINAL, FUTURE_EMERGENCY)),
        "blender_launched": False,
        "unreal_launched": False,
        "external_model_launched": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-existing-future-namespaces", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(require_future_namespaces_absent=not args.allow_existing_future_namespaces)
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
