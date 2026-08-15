from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = PROJECT_ROOT / "Production" / "ready_blender_output_contracts.json"
MANIFEST_PATH = PROJECT_ROOT / "Production" / "production_manifest.json"
ATTEMPTS_ROOT = PROJECT_ROOT / "Production" / "Attempts"

HEAVY_PROCESS_NAMES = {
    "unrealeditor",
    "unrealeditor-cmd",
    "shadercompileworker",
    "blender",
    "automationtool",
    "unrealbuildtool",
    "cl",
    "link",
}

FORBIDDEN_WORKER_PATTERNS = {
    'bpy.data.images.get("Render Result")': "in-memory Render Result readback",
    "bpy.data.images.get('Render Result')": "in-memory Render Result readback",
    ".pixels.foreach_get": "unbounded Render Result pixel readback",
    "import numpy": "NumPy dependency or allocation",
    "from numpy": "NumPy dependency or allocation",
    "np.repeat": "large repeated NumPy allocation",
    "np.tile": "large tiled NumPy allocation",
    'empty_display_type = "CROSS"': "Blender 5.2-incompatible empty display token",
    "empty_display_type = 'CROSS'": "Blender 5.2-incompatible empty display token",
}


class AdjudicationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AdjudicationError(f"Invalid JSON {path}: {exc}") from exc


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def verify_authority(record: dict[str, Any]) -> dict[str, Any]:
    path = PROJECT_ROOT / str(record["path"])
    if not path.is_file():
        raise AdjudicationError(f"Missing frozen authority: {path}")
    actual = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
    if actual["bytes"] != int(record["bytes"]) or actual["sha256"] != str(record["sha256"]):
        raise AdjudicationError(f"Frozen authority mismatch: {path}")
    return actual


def get_path(payload: Any, dotted: str) -> Any:
    value = payload
    for token in dotted.split("."):
        if not isinstance(value, dict) or token not in value:
            raise AdjudicationError(f"Missing receipt field: {dotted}")
        value = value[token]
    return value


def evaluate_check(payload: Any, check: dict[str, Any]) -> None:
    actual = get_path(payload, str(check["path"]))
    expected = check["value"]
    operator = str(check["op"])
    if operator == "eq":
        passed = actual == expected
    elif operator == "ge":
        passed = isinstance(actual, (int, float)) and not isinstance(actual, bool) and actual >= expected
    elif operator == "contains_all":
        passed = isinstance(actual, list) and all(item in actual for item in expected)
    else:
        raise AdjudicationError(f"Unsupported contract operator: {operator}")
    if not passed:
        raise AdjudicationError(
            f"Receipt check failed for {check['file']}:{check['path']} ({operator}); "
            f"actual={actual!r}, expected={expected!r}"
        )


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise AdjudicationError(f"Invalid PNG header: {path}")
    return struct.unpack(">II", header[16:24])


def glb_json(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise AdjudicationError(f"Truncated GLB header: {path}")
        magic, version, declared_length = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2 or declared_length != path.stat().st_size:
            raise AdjudicationError(f"Invalid GLB identity or length: {path}")
        while stream.tell() < declared_length:
            chunk_header = stream.read(8)
            if len(chunk_header) != 8:
                raise AdjudicationError(f"Truncated GLB chunk header: {path}")
            chunk_length, chunk_type = struct.unpack("<II", chunk_header)
            chunk = stream.read(chunk_length)
            if len(chunk) != chunk_length:
                raise AdjudicationError(f"Truncated GLB chunk: {path}")
            if chunk_type == 0x4E4F534A:
                try:
                    return json.loads(chunk.rstrip(b" \t\r\n\x00").decode("utf-8"))
                except Exception as exc:
                    raise AdjudicationError(f"Invalid GLB JSON chunk: {path}: {exc}") from exc
    raise AdjudicationError(f"GLB has no JSON chunk: {path}")


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "relative_path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]


def inventory_map(records: list[dict[str, Any]]) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for record in records:
        relative = str(record["relative_path"])
        if relative in result:
            raise AdjudicationError(f"Duplicate artifact inventory path: {relative}")
        result[relative] = (int(record["bytes"]), str(record["sha256"]))
    return result


def heavy_processes() -> list[dict[str, str]]:
    completed = subprocess.run(
        ["tasklist.exe", "/fo", "csv", "/nh"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise AdjudicationError(f"tasklist failed: {completed.stderr.strip()}")
    import csv

    found: list[dict[str, str]] = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) < 2:
            continue
        name = Path(row[0]).stem.lower()
        if name in HEAVY_PROCESS_NAMES:
            found.append({"name": name, "pid": row[1]})
    return found


def validate_contracts() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    contracts_payload = load_json(CONTRACT_PATH)
    if contracts_payload.get("schema") != "skyguard.ready-blender-output-contracts.v1":
        raise AdjudicationError("Unexpected ready Blender output-contract schema.")
    contracts = contracts_payload.get("contracts")
    if not isinstance(contracts, dict) or len(contracts) != 5:
        raise AdjudicationError("Exactly five ready Blender lane contracts are required.")

    manifest = load_json(MANIFEST_PATH)
    assets = {str(item["id"]): item for item in manifest.get("assets", [])}
    authority_records: list[dict[str, Any]] = []
    static_records: list[dict[str, Any]] = []
    for asset_id, contract in contracts.items():
        asset = assets.get(asset_id)
        if asset is None:
            raise AdjudicationError(f"Manifest is missing ready Blender asset: {asset_id}")
        if asset.get("status") != "ready":
            raise AdjudicationError(f"{asset_id} is {asset.get('status')}, not ready.")
        if asset.get("worker", {}).get("script") != contract.get("worker_script"):
            raise AdjudicationError(f"Worker binding mismatch for {asset_id}.")
        expected_renders = sum(int(group["count"]) for group in contract["render_groups"])
        if int(asset.get("worker", {}).get("minimum_renders", -1)) != expected_renders:
            raise AdjudicationError(f"Render-count contract mismatch for {asset_id}.")
        for record in contract["authorities"]:
            authority_records.append(verify_authority(record))

        worker_sources = [
            PROJECT_ROOT / str(record["path"])
            for record in contract["authorities"]
            if str(record["path"]).startswith("Scripts\\Workers\\") and str(record["path"]).endswith(".py")
        ]
        merged_source = "\n".join(path.read_text(encoding="utf-8") for path in worker_sources)
        hazards = [description for pattern, description in FORBIDDEN_WORKER_PATTERNS.items() if pattern in merged_source]
        if hazards:
            raise AdjudicationError(f"Known Blender hazard in {asset_id}: {sorted(set(hazards))}")
        if "bpy.ops.render.render(write_still=True)" not in merged_source:
            raise AdjudicationError(f"{asset_id} has no governed write-still render path.")

        supervisor = PROJECT_ROOT / str(contract["supervisor_script"])
        supervisor_source = supervisor.read_text(encoding="utf-8")
        if supervisor_source.count("$ControllerPath run $AssetId") != 1:
            raise AdjudicationError(f"{asset_id} supervisor must expose exactly one controller run path.")
        if "Start-Process" in supervisor_source or "blender.exe" in supervisor_source.lower():
            raise AdjudicationError(f"{asset_id} supervisor has an alternate direct Blender launch path.")
        if "OfflineContractTest" not in supervisor_source or "AuthorizeSingleBlender" not in supervisor_source:
            raise AdjudicationError(f"{asset_id} supervisor lacks offline/authorization separation.")
        future_attempt = ATTEMPTS_ROOT / asset_id
        if future_attempt.exists():
            raise AdjudicationError(f"Future attempt namespace already exists: {future_attempt}")
        static_records.append(
            {
                "asset_id": asset_id,
                "known_hazard_count": 0,
                "controller_run_paths": 1,
                "direct_blender_launch_paths": 0,
                "expected_render_count": expected_renders,
                "future_attempt_absent": True,
            }
        )
    return contracts, authority_records, static_records


def validate_attempt(asset_id: str, attempt: Path, contract: dict[str, Any]) -> dict[str, Any]:
    expected_parent = (ATTEMPTS_ROOT / asset_id).resolve()
    if attempt.parent.resolve() != expected_parent or not attempt.name.startswith("attempt_"):
        raise AdjudicationError(f"Attempt is outside the governed asset namespace: {attempt}")
    terminal_path = attempt / "terminal.json"
    output = attempt / "output"
    if not terminal_path.is_file() or not output.is_dir():
        raise AdjudicationError("Attempt is missing terminal.json or output directory.")
    terminal = load_json(terminal_path)
    required_terminal = {
        "asset_id": asset_id,
        "launch_count": 1,
        "retry_count": 0,
        "timeout": False,
        "status": "awaiting_review",
        "exit_code": 0,
        "exit_code_type": "int",
    }
    for key, expected in required_terminal.items():
        if terminal.get(key) != expected:
            raise AdjudicationError(f"Terminal mismatch {key}: {terminal.get(key)!r} != {expected!r}")

    blends = list(output.rglob("*.blend"))
    glbs = list(output.rglob("*.glb"))
    if [path.name for path in blends] != [contract["blend"]]:
        raise AdjudicationError(f"Unexpected blend set: {[path.name for path in blends]}")
    if [path.name for path in glbs] != [contract["glb"]]:
        raise AdjudicationError(f"Unexpected GLB set: {[path.name for path in glbs]}")
    if blends[0].stat().st_size <= 0 or glbs[0].stat().st_size <= 20:
        raise AdjudicationError("Blend or GLB output is empty/truncated.")

    all_pngs: set[Path] = set()
    render_groups: list[dict[str, Any]] = []
    for group in contract["render_groups"]:
        paths = sorted(output.glob(str(group["glob"])))
        if len(paths) != int(group["count"]):
            raise AdjudicationError(f"Render group {group['glob']} has {len(paths)} files, expected {group['count']}.")
        for path in paths:
            if path in all_pngs:
                raise AdjudicationError(f"Render belongs to multiple groups: {path}")
            all_pngs.add(path)
            dimensions = png_dimensions(path)
            expected_dimensions = (int(group["width"]), int(group["height"]))
            if dimensions != expected_dimensions:
                raise AdjudicationError(f"PNG dimensions mismatch: {path}: {dimensions} != {expected_dimensions}")
        render_groups.append({"glob": group["glob"], "count": len(paths), "dimensions": [group["width"], group["height"]]})
    actual_pngs = set(output.rglob("*.png"))
    if actual_pngs != all_pngs:
        unexpected = sorted(str(path.relative_to(output)) for path in actual_pngs - all_pngs)
        raise AdjudicationError(f"Unexpected or ungoverned PNG renders: {unexpected}")

    receipts: dict[str, Any] = {}
    for relative, schema in contract["required_json"].items():
        path = output / relative
        if not path.is_file():
            raise AdjudicationError(f"Missing required receipt: {relative}")
        payload = load_json(path)
        if payload.get("schema") != schema:
            raise AdjudicationError(f"Receipt schema mismatch: {relative}")
        receipts[relative] = payload
    for check in contract["checks"]:
        evaluate_check(receipts[str(check["file"])], check)

    gltf = glb_json(glbs[0])
    node_names = {str(node.get("name")) for node in gltf.get("nodes", []) if node.get("name") is not None}
    missing_nodes = sorted(set(contract["required_glb_nodes"]) - node_names)
    if missing_nodes:
        raise AdjudicationError(f"GLB is missing required nodes: {missing_nodes}")
    counts = {
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
        "skins": len(gltf.get("skins", [])),
        "animations": len(gltf.get("animations", [])),
    }
    for key in ("meshes", "skins", "animations"):
        if counts[key] < int(contract[f"minimum_{key}"]):
            raise AdjudicationError(f"GLB {key} count {counts[key]} is below {contract[f'minimum_{key}']}.")

    current_inventory = inventory(output)
    recorded_inventory = terminal.get("artifact_inventory")
    if not isinstance(recorded_inventory, list):
        raise AdjudicationError("Controller terminal has no artifact inventory.")
    if inventory_map(current_inventory) != inventory_map(recorded_inventory):
        raise AdjudicationError("Current output inventory differs from the controller terminal inventory.")

    allowed_suffixes = {".blend", ".glb", ".png", ".json"}
    unexpected_suffixes = sorted({path.suffix.lower() for path in output.rglob("*") if path.is_file()} - allowed_suffixes)
    if unexpected_suffixes:
        raise AdjudicationError(f"Unexpected output file suffixes: {unexpected_suffixes}")

    return {
        "attempt": str(attempt),
        "terminal_sha256": sha256(terminal_path),
        "output_file_count": len(current_inventory),
        "blend": current_inventory[[item["relative_path"] for item in current_inventory].index(str(blends[0].relative_to(output)))],
        "glb": current_inventory[[item["relative_path"] for item in current_inventory].index(str(glbs[0].relative_to(output)))],
        "render_groups": render_groups,
        "receipt_count": len(receipts),
        "glb_structure": counts,
        "required_glb_nodes_verified": len(contract["required_glb_nodes"]),
        "inventory_parity": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", choices=[
        "core-yak52-airframe",
        "core-reargunner-character-refinement01",
        "core-reargunner-hand-forearm-refinement01",
        "core-rifle-method05-stagea",
        "core-shahed136",
    ])
    parser.add_argument("--attempt-dir")
    parser.add_argument("--report")
    parser.add_argument("--offline-authority-audit", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report: dict[str, Any] = {
        "schema": "skyguard.ready-blender-attempt-postflight.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "automatic_visual_acceptance": False,
        "unreal_import_authorized": False,
        "errors": [],
    }
    try:
        contracts, authorities, static_records = validate_contracts()
        report["contract_sha256"] = sha256(CONTRACT_PATH)
        report["authority_records"] = authorities
        report["static_lane_audit"] = static_records
        report["heavy_processes"] = heavy_processes()
        if args.offline_authority_audit:
            if args.asset_id or args.attempt_dir:
                raise AdjudicationError("Offline authority audit cannot target an attempt.")
            report["classification"] = "PASSED_READY_BLENDER_LANES_PREVENTIVE_AUDIT_NO_HEAVY_PROCESS_LAUNCHED"
        else:
            if not args.asset_id or not args.attempt_dir or not args.report:
                raise AdjudicationError("Postflight requires --asset-id, --attempt-dir, and --report.")
            attempt = Path(args.attempt_dir).resolve()
            report["attempt_validation"] = validate_attempt(args.asset_id, attempt, contracts[args.asset_id])
            report["asset_id"] = args.asset_id
            report["classification"] = "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW"
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")

    if args.report:
        report_path = Path(args.report).resolve()
        if args.attempt_dir:
            attempt = Path(args.attempt_dir).resolve()
            if report_path == attempt or attempt in report_path.parents:
                report["classification"] = "FAILED_WITH_EVIDENCE"
                report["errors"].append("Postflight report must remain outside the immutable attempt directory.")
            else:
                atomic_json(report_path, report)
        else:
            atomic_json(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["classification"].startswith("PASSED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
