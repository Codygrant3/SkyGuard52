from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(r"D:\Skyguard52")
OUTPUT_ROOT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery02"
ATTEMPT_ROOT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02\attempt_01"
SUPERVISOR_MANIFEST = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_TERMINAL_SUPERVISOR.json"
POSTFLIGHT_REPORT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_POSTFLIGHT.json"
VISUAL_MANIFEST = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_VISUAL_REVIEW_MANIFEST.json"
OFFLINE_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_OFFLINE_DESIGN_FREEZE.json"

EXPECTED_OFFLINE_FREEZE_SHA256 = "d64df63d45acbc893dc5193cdfd8b516682e410159914ecb2e144e4686689e9c"
EXPECTED_SOURCE_SHA256 = "ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61"
SUPERVISOR_SUCCESS = "PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW"
WORKER_SUCCESS = "BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW"
AUTOMATIC_PASS = "PASSED_AUTOMATIC_READY_FOR_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW"
FAILURE = "FAILED_WITH_EVIDENCE"

BLEND = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA.blend"
CHECKPOINTS = (
    "checkpoint_01_cross_section",
    "checkpoint_02_facade_street",
    "checkpoint_03_pbr_composition",
)
CONDITIONS = ("daylight", "overcast", "night", "wet", "storm")
VIEWS = ("close", "route", "aerial")
GLBS = (
    "exports/SM_M01_STAGEA_ShoreStreetDistrict.glb",
    "exports/SM_M01_STAGEA_Midrise5F_A.glb",
    "exports/SM_M01_STAGEA_Midrise7F_B.glb",
    "exports/SM_M01_STAGEA_FacadeCompositions.glb",
)
TEXTURES = (
    "textures/T_M01_STAGEA_Atlas_BaseColor.png",
    "textures/T_M01_STAGEA_Atlas_Normal.png",
    "textures/T_M01_STAGEA_Atlas_Roughness.png",
    "textures/T_M01_STAGEA_Atlas_Metallic.png",
    "textures/T_M01_STAGEA_Atlas_AO.png",
)
RECEIPTS = (
    "dimension_receipt.json",
    "topology_uv_receipt.json",
    "material_texture_receipt.json",
    "checkpoint_receipt.json",
    "render_receipt.json",
    "export_receipt.json",
    "source_parity_receipt.json",
    "artifact_inventory.json",
    "terminal_receipt.json",
)
REQUIRED_SOCKETS = {
    "SOCKET_District_W",
    "SOCKET_District_E",
    "SOCKET_District_S",
    "SOCKET_District_N",
    "SOCKET_SM_M01_STAGEA_Midrise5F_A_Origin",
    "SOCKET_SM_M01_STAGEA_Midrise7F_B_Origin",
}


class ContractError(RuntimeError):
    pass


def require(value: Any, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path, root: Path | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if root is not None:
        result["relative_path"] = path.relative_to(root).as_posix()
    return result


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    require(not temporary.exists(), f"temporary output already exists: {temporary}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def normalized_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    require(normalized and not normalized.startswith("/") and ":" not in normalized, f"invalid relative path: {value}")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    require(normalized, f"invalid relative path: {value}")
    require(".." not in normalized.split("/"), f"parent traversal in relative path: {value}")
    return normalized


def exact_expected_files() -> set[str]:
    paths = {BLEND, *GLBS, *TEXTURES, *RECEIPTS}
    paths.update(f"renders/checkpoints/{name}.png" for name in CHECKPOINTS)
    paths.update(f"renders/final/{condition}_{view}.png" for condition in CONDITIONS for view in VIEWS)
    return paths


def current_files(root: Path) -> dict[str, Path]:
    require(root.is_dir(), f"output root is missing: {root}")
    return {path.relative_to(root).as_posix(): path for path in sorted(root.rglob("*")) if path.is_file()}


def verify_png(path: Path, expected_size: tuple[int, int]) -> dict[str, Any]:
    require(path.is_file() and path.stat().st_size > 0, f"PNG is missing or empty: {path}")
    with Image.open(path) as image:
        observed = tuple(image.size)
        mode = image.mode
        image.verify()
    require(observed == expected_size, f"PNG dimensions differ: {path} => {observed}")
    require(mode in {"RGB", "RGBA", "L", "LA"}, f"unsupported PNG mode: {path} => {mode}")
    return {"width": observed[0], "height": observed[1], "mode": mode}


def parse_glb(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(len(raw) >= 20, f"GLB is too small: {path}")
    magic, version, declared = struct.unpack_from("<4sII", raw, 0)
    require(magic == b"glTF" and version == 2 and declared == len(raw), f"invalid GLB header: {path}")
    offset = 12
    json_chunk: bytes | None = None
    while offset + 8 <= len(raw):
        length, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        require(offset + length <= len(raw), f"truncated GLB chunk: {path}")
        payload = raw[offset : offset + length]
        offset += length
        if kind == 0x4E4F534A:
            require(json_chunk is None, f"multiple GLB JSON chunks: {path}")
            json_chunk = payload
    require(offset == len(raw) and json_chunk is not None, f"missing or malformed GLB JSON chunk: {path}")
    document = json.loads(json_chunk.rstrip(b" \t\r\n\x00").decode("utf-8"))
    require(str((document.get("asset") or {}).get("version")) == "2.0", f"GLB asset version is not 2.0: {path}")
    nodes = document.get("nodes") or []
    meshes = document.get("meshes") or []
    require(nodes and meshes, f"GLB has no nodes or meshes: {path}")
    names = {str(node.get("name")) for node in nodes if node.get("name")}
    return {"node_names": sorted(names), "node_count": len(nodes), "mesh_count": len(meshes)}


def validate_luma(metrics: dict[str, Any], size: tuple[int, int], condition: str | None = None) -> None:
    require((metrics.get("width"), metrics.get("height")) == size, "render-receipt dimensions mismatch")
    mean_luma = float(metrics.get("mean_luma_linear", -1.0))
    black = float(metrics.get("black_fraction_linear_0_01", -1.0))
    maximum = float(metrics.get("max_luma_linear", -1.0))
    minimum_mean = 0.008 if condition == "night" else (0.025 if condition else 0.03)
    maximum_black = 0.70 if condition == "night" else (0.42 if condition else 0.35)
    require(mean_luma >= minimum_mean, f"recorded mean luminance failed: {mean_luma}")
    require(0.0 <= black <= maximum_black, f"recorded black fraction failed: {black}")
    require(maximum >= mean_luma and maximum > 0.0, f"recorded maximum luminance failed: {maximum}")


def verify_freeze() -> None:
    require(OFFLINE_FREEZE.is_file() and sha256(OFFLINE_FREEZE) == EXPECTED_OFFLINE_FREEZE_SHA256, "Recovery02 offline freeze mismatch")
    freeze = load_json(OFFLINE_FREEZE)
    require(freeze.get("classification") == "PASSED_READY_FOR_EXPLICIT_SINGLE_M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_BLENDER_AUTHORIZATION", "Recovery02 offline classification mismatch")
    members = freeze.get("members") or []
    require(freeze.get("member_count") == 12 and len(members) == 12, "Recovery02 freeze cardinality mismatch")
    for member in members:
        path = Path(str(member.get("path", "")))
        require(path.is_file(), f"Recovery02 freeze member is missing: {path}")
        require(path.stat().st_size == member.get("bytes"), f"Recovery02 freeze member byte mismatch: {path}")
        require(sha256(path) == member.get("sha256"), f"Recovery02 freeze member hash mismatch: {path}")


def verify_supervisor(manifest: dict[str, Any]) -> None:
    require(manifest.get("classification") == SUPERVISOR_SUCCESS, "supervisor did not reach automatic success")
    require(manifest.get("terminal") is True and manifest.get("preflight_passed") is True, "supervisor terminal or preflight state failed")
    require(manifest.get("supervisor_launch_count") == 1, "supervisor launch count is not one")
    require(manifest.get("blender_launch_count") == 1, "Blender launch count is not one")
    require(manifest.get("retry_count") == 0 and manifest.get("unreal_launch_count") == 0, "retry or Unreal launch count failed")
    require(manifest.get("exit_code") == 0 and manifest.get("exit_code_type") == "System.Int32", "numeric Blender exit evidence failed")
    require(manifest.get("timeout") is False, "Blender supervisor timed out")
    require(manifest.get("failure_stage") is None and manifest.get("failure_message") is None, "successful supervisor contains failure evidence")
    require(manifest.get("governed_attempt_namespace_created") is True and manifest.get("output_namespace_created") is True, "governed namespaces were not recorded")
    require(manifest.get("native_handle_retained") is True, "native process handle was not retained")
    require(len(manifest.get("process_tree_samples") or []) > 0, "process-tree evidence is absent")
    require(manifest.get("output_counts") == {"blend": 1, "glb": 4, "checkpoint_png": 3, "final_png": 15, "texture_png": 5}, "supervisor output counts differ")
    receipt_states = manifest.get("receipt_states") or {}
    require(set(receipt_states) == {"dimensions", "topology_uv", "materials", "checkpoints", "final_renders", "exports", "source_parity", "terminal"}, "supervisor receipt-state keys differ")
    require(all(value is True for value in receipt_states.values()), "one or more supervisor receipt states failed")


def verify_receipts(root: Path, files: dict[str, Path]) -> dict[str, Any]:
    dimension = load_json(files["dimension_receipt.json"])
    require(dimension.get("passed") is True and dimension.get("district_authority_m") == [100.0, 80.0], "dimension receipt failed")
    bounds = dimension.get("observed_visible_bounds") or {}
    minimum = bounds.get("min_m") or []
    maximum = bounds.get("max_m") or []
    require(len(minimum) == 3 and len(maximum) == 3, "visible bounds are incomplete")
    require(abs(float(minimum[0])) <= 0.01 and abs(float(maximum[0]) - 100.0) <= 0.01, "district X bounds failed")
    require(abs(float(minimum[1])) <= 0.01 and abs(float(maximum[1]) - 80.0) <= 0.01, "district Y bounds failed")

    topology = load_json(files["topology_uv_receipt.json"])
    stats = topology.get("statistics") or {}
    require(topology.get("passed") is True, "topology receipt failed")
    require(int(stats.get("meshes", 0)) > 0 and int(stats.get("vertices", 0)) > 0 and int(stats.get("triangles", 0)) > 0, "topology statistics are empty")
    require(stats.get("uv_failures") == [] and stats.get("unapplied_scales") == [], "UV or transform validation failed")

    materials = load_json(files["material_texture_receipt.json"])
    require(materials.get("passed") is True and materials.get("atlas_resolution") == [2048, 2048], "material receipt failed")
    require(materials.get("maps") == ["BaseColor", "Normal", "Roughness", "Metallic", "AO"], "texture-map contract differs")
    texture_records = {normalized_relative(row["path"]): row for row in materials.get("texture_maps") or []}
    require(set(texture_records) == set(TEXTURES), "material receipt texture paths differ")
    for relative, row in texture_records.items():
        path = files[relative]
        require(path.stat().st_size == row.get("bytes") and sha256(path) == row.get("sha256"), f"material receipt hash mismatch: {relative}")

    checkpoints = load_json(files["checkpoint_receipt.json"])
    rows = checkpoints.get("checkpoints") or []
    require(checkpoints.get("passed") is True and checkpoints.get("count") == 3 and len(rows) == 3, "checkpoint receipt failed")
    require({row.get("id") for row in rows} == set(CHECKPOINTS), "checkpoint identities differ")
    require(sum(bool(row.get("bounded_correction_used")) for row in rows) <= 1, "more than one bounded checkpoint correction was used")
    for row in rows:
        relative = f"renders/checkpoints/{row['id']}.png"
        require(Path(str(row.get("path"))).resolve() == files[relative].resolve(), f"checkpoint path mismatch: {relative}")
        require(row.get("passed") is True, f"checkpoint pass flag failed: {relative}")
        validate_luma(row.get("metrics") or {}, (1280, 720))

    renders = load_json(files["render_receipt.json"])
    rows = renders.get("renders") or []
    expected_pairs = {(condition, view) for condition in CONDITIONS for view in VIEWS}
    require(renders.get("passed") is True and renders.get("count") == 15 and renders.get("resolution") == [2560, 1440], "render receipt failed")
    require({(row.get("condition"), row.get("view")) for row in rows} == expected_pairs, "final render matrix differs")
    for row in rows:
        condition, view = str(row.get("condition")), str(row.get("view"))
        relative = f"renders/final/{condition}_{view}.png"
        require(Path(str(row.get("path"))).resolve() == files[relative].resolve(), f"final render path mismatch: {relative}")
        validate_luma(row.get("metrics") or {}, (2560, 1440), condition)

    exports = load_json(files["export_receipt.json"])
    require(exports.get("passed") is True and exports.get("missing_sockets") == [], "export receipt failed")
    require(set(exports.get("required_sockets") or []) == REQUIRED_SOCKETS, "required socket contract differs")
    collisions = exports.get("collision_objects") or []
    require(len(collisions) >= 5 and all(str(name).startswith("UCX_") for name in collisions), "collision contract failed")
    export_records = {normalized_relative(row["path"]): row for row in exports.get("exports") or []}
    require(set(export_records) == set(GLBS), "export receipt GLB paths differ")
    for relative, row in export_records.items():
        path = files[relative]
        require(path.stat().st_size == row.get("bytes") and sha256(path) == row.get("sha256"), f"export receipt hash mismatch: {relative}")

    source = load_json(files["source_parity_receipt.json"])
    require(source.get("passed") is True and source.get("sha256") == EXPECTED_SOURCE_SHA256 and source.get("expected_sha256") == EXPECTED_SOURCE_SHA256, "source parity receipt failed")

    terminal = load_json(files["terminal_receipt.json"])
    require(terminal.get("status") == WORKER_SUCCESS and terminal.get("automatic_validation_passed") is True, "worker terminal receipt failed")
    require(terminal.get("human_visual_acceptance") == "NOT_PERFORMED", "worker terminal receipt incorrectly claims visual acceptance")
    require((terminal.get("blend_count"), terminal.get("glb_count"), terminal.get("checkpoint_count"), terminal.get("final_render_count"), terminal.get("texture_count")) == (1, 4, 3, 15, 5), "worker terminal counts differ")
    return {"dimensions": dimension, "topology": topology, "materials": materials, "checkpoints": checkpoints, "renders": renders, "exports": exports, "source": source, "terminal": terminal}


def verify_inventories(root: Path, files: dict[str, Path], manifest: dict[str, Any]) -> None:
    artifact = load_json(files["artifact_inventory.json"])
    artifact_records = {normalized_relative(row["relative_path"]): row for row in artifact.get("files") or []}
    expected_artifact_paths = set(files) - {"artifact_inventory.json", "terminal_receipt.json"}
    require(set(artifact_records) == expected_artifact_paths, "worker artifact inventory file set differs")
    for relative, row in artifact_records.items():
        path = files[relative]
        require(path.stat().st_size == row.get("bytes") and sha256(path) == row.get("sha256"), f"worker artifact inventory mismatch: {relative}")

    produced_records = {normalized_relative(row["relative_path"]): row for row in manifest.get("produced_files") or []}
    require(set(produced_records) == set(files), "supervisor produced-file inventory differs")
    for relative, row in produced_records.items():
        path = files[relative]
        require(path.stat().st_size == row.get("bytes") and sha256(path) == row.get("sha256"), f"supervisor produced-file mismatch: {relative}")


def verify_glbs(files: dict[str, Path]) -> list[dict[str, Any]]:
    results = []
    for relative in GLBS:
        details = parse_glb(files[relative])
        names = set(details["node_names"])
        if relative.endswith("ShoreStreetDistrict.glb"):
            require({"SOCKET_District_W", "SOCKET_District_E", "SOCKET_District_S", "SOCKET_District_N"}.issubset(names), "shore GLB lacks district sockets")
            require(any(name.startswith("UCX_SM_M01_STAGEA_TerrainDistrict") for name in names), "shore GLB lacks terrain collision")
        elif relative.endswith("Midrise5F_A.glb"):
            require("SOCKET_SM_M01_STAGEA_Midrise5F_A_Origin" in names, "five-floor GLB lacks origin socket")
            require(any(name.startswith("UCX_SM_M01_STAGEA_Midrise5F_A") for name in names), "five-floor GLB lacks collision")
        elif relative.endswith("Midrise7F_B.glb"):
            require("SOCKET_SM_M01_STAGEA_Midrise7F_B_Origin" in names, "seven-floor GLB lacks origin socket")
            require(any(name.startswith("UCX_SM_M01_STAGEA_Midrise7F_B") for name in names), "seven-floor GLB lacks collision")
        results.append({"relative_path": relative, **details})
    return results


def validate_attempt(attempt_root: Path) -> dict[str, Any]:
    require(attempt_root.is_dir(), f"attempt root is missing: {attempt_root}")
    source = attempt_root / r"source\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"
    contract = attempt_root / "execution_contract.json"
    preflight = attempt_root / "preflight_receipt.json"
    stdout = attempt_root / "blender.stdout.log"
    stderr = attempt_root / "blender.stderr.log"
    require(source.is_file() and sha256(source) == EXPECTED_SOURCE_SHA256, "attempt source parity failed")
    require(contract.is_file() and preflight.is_file() and stdout.is_file() and stderr.is_file(), "attempt evidence is incomplete")
    preflight_data = load_json(preflight)
    require(preflight_data.get("passed") is True and preflight_data.get("retry_count") == 0 and preflight_data.get("heavy_process_count") == 0, "attempt preflight receipt failed")
    require(preflight_data.get("recovery_source_sha256") == EXPECTED_SOURCE_SHA256 and preflight_data.get("recovery01_members_verified") == 13, "attempt preflight authority evidence failed")
    stderr_text = stderr.read_text(encoding="utf-8", errors="replace")
    require("Traceback (most recent call last)" not in stderr_text and "FAILED_WITH_EVIDENCE" not in stderr_text and "zero-size array" not in stderr_text, "Blender stderr contains a governed failure")
    return {"source": record(source), "contract": record(contract), "preflight": record(preflight), "stdout": record(stdout), "stderr": record(stderr)}


def evaluate(output_root: Path, attempt_root: Path, supervisor_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(supervisor_path)
    verify_supervisor(manifest)
    files = current_files(output_root)
    require(set(files) == exact_expected_files(), f"output file set differs; missing={sorted(exact_expected_files()-set(files))}, unexpected={sorted(set(files)-exact_expected_files())}")
    require(files[BLEND].read_bytes()[:7] == b"BLENDER", "governed blend header is invalid")
    png_records = []
    for name in CHECKPOINTS:
        relative = f"renders/checkpoints/{name}.png"
        png_records.append({"relative_path": relative, **verify_png(files[relative], (1280, 720)), **record(files[relative])})
    for condition in CONDITIONS:
        for view in VIEWS:
            relative = f"renders/final/{condition}_{view}.png"
            png_records.append({"relative_path": relative, "condition": condition, "view": view, **verify_png(files[relative], (2560, 1440)), **record(files[relative])})
    for relative in TEXTURES:
        png_records.append({"relative_path": relative, **verify_png(files[relative], (2048, 2048)), **record(files[relative])})
    receipts = verify_receipts(output_root, files)
    verify_inventories(output_root, files, manifest)
    glbs = verify_glbs(files)
    attempt = validate_attempt(attempt_root)
    all_records = [record(path, output_root) for path in files.values()]
    report = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery02.postflight.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": AUTOMATIC_PASS,
        "automatic_validation_passed": True,
        "direct_full_resolution_visual_review_required": True,
        "human_visual_acceptance": "NOT_PERFORMED",
        "output_file_count": len(files),
        "output_inventory": all_records,
        "glb_structure": glbs,
        "attempt_evidence": attempt,
        "supervisor_manifest": record(supervisor_path),
        "worker_terminal_status": receipts["terminal"]["status"],
        "next_gate": "DIRECT_FULL_RESOLUTION_VISUAL_REVIEW_OF_18_ORIGINAL_RENDERS",
    }
    visual = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery02.visual-review-manifest.v1",
        "created_utc": report["created_utc"],
        "classification": "AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "automatic_postflight_report": str(POSTFLIGHT_REPORT),
        "checkpoint_count": 3,
        "final_render_count": 15,
        "render_count": 18,
        "renders": [row for row in png_records if row["relative_path"].startswith("renders/")],
        "reject_if": [
            "flat diagnostic surfaces",
            "plain box-shell buildings",
            "visible module repetition",
            "floating or disconnected geometry",
            "exposed district edges",
            "weak water-beach-seawall transitions",
            "plastic materials",
            "missing facade depth",
            "missing route-visible construction detail",
            "broken UVs, normals, sockets, collision, or dimensions",
        ],
        "accepted_classification": "PASSED_READY_FOR_M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB",
        "rejected_classification": FAILURE,
    }
    return report, visual


def write_minimal_glb(path: Path, node_names: list[str]) -> None:
    document = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": list(range(len(node_names)))}], "nodes": [{"name": name, "mesh": 0} for name in node_names], "meshes": [{"name": "fixture", "primitives": [{}]}]}
    payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
    payload += b" " * ((4 - len(payload) % 4) % 4)
    raw = struct.pack("<4sII", b"glTF", 2, 20 + len(payload)) + struct.pack("<II", len(payload), 0x4E4F534A) + payload
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def make_fixture(root: Path) -> tuple[Path, Path, Path]:
    output = root / "output"
    attempt = root / "attempt"
    manifest_path = root / "supervisor.json"
    output.mkdir(parents=True)
    (output / BLEND).write_bytes(b"BLENDER-v300-fixture")
    glb_nodes = {
        GLBS[0]: ["SM_M01_STAGEA_Terrain", "SOCKET_District_W", "SOCKET_District_E", "SOCKET_District_S", "SOCKET_District_N", "UCX_SM_M01_STAGEA_TerrainDistrict_100x80_00"],
        GLBS[1]: ["SM_M01_STAGEA_Midrise5F_A", "SOCKET_SM_M01_STAGEA_Midrise5F_A_Origin", "UCX_SM_M01_STAGEA_Midrise5F_A_00"],
        GLBS[2]: ["SM_M01_STAGEA_Midrise7F_B", "SOCKET_SM_M01_STAGEA_Midrise7F_B_Origin", "UCX_SM_M01_STAGEA_Midrise7F_B_00"],
        GLBS[3]: ["SM_M01_STAGEA_FacadeCompositions"],
    }
    for relative, nodes in glb_nodes.items():
        write_minimal_glb(output / relative, nodes)
    for name in CHECKPOINTS:
        path = output / f"renders/checkpoints/{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (1280, 720), (90, 110, 130)).save(path)
    for condition in CONDITIONS:
        for view in VIEWS:
            path = output / f"renders/final/{condition}_{view}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (2560, 1440), (45 if condition == "night" else 100, 110, 120)).save(path)
    for relative in TEXTURES:
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (2048, 2048), (128, 128, 128)).save(path)
    checkpoint_rows = [{"id": name, "path": str((output / f"renders/checkpoints/{name}.png").resolve()), "metrics": {"width": 1280, "height": 720, "mean_luma_linear": 0.2, "black_fraction_linear_0_01": 0.0, "max_luma_linear": 0.4}, "passed": True, "bounded_correction_used": False} for name in CHECKPOINTS]
    render_rows = [{"condition": condition, "view": view, "path": str((output / f"renders/final/{condition}_{view}.png").resolve()), "metrics": {"width": 2560, "height": 1440, "mean_luma_linear": 0.05 if condition == "night" else 0.2, "black_fraction_linear_0_01": 0.1, "max_luma_linear": 0.4}} for condition in CONDITIONS for view in VIEWS]
    receipts = {
        "dimension_receipt.json": {"passed": True, "district_authority_m": [100.0, 80.0], "observed_visible_bounds": {"min_m": [0.0, 0.0, 0.0], "max_m": [100.0, 80.0, 25.0]}},
        "topology_uv_receipt.json": {"passed": True, "statistics": {"meshes": 4, "vertices": 100, "triangles": 200, "uv_failures": [], "unapplied_scales": []}},
        "material_texture_receipt.json": {"passed": True, "atlas_resolution": [2048, 2048], "maps": ["BaseColor", "Normal", "Roughness", "Metallic", "AO"], "texture_maps": [{"path": relative, "bytes": (output / relative).stat().st_size, "sha256": sha256(output / relative)} for relative in TEXTURES]},
        "checkpoint_receipt.json": {"passed": True, "count": 3, "checkpoints": checkpoint_rows},
        "render_receipt.json": {"passed": True, "count": 15, "resolution": [2560, 1440], "renders": render_rows},
        "export_receipt.json": {"passed": True, "exports": [{"path": relative, "bytes": (output / relative).stat().st_size, "sha256": sha256(output / relative)} for relative in GLBS], "required_sockets": sorted(REQUIRED_SOCKETS), "missing_sockets": [], "collision_objects": ["UCX_SM_M01_STAGEA_TerrainDistrict_100x80_00", "UCX_SM_M01_STAGEA_Seawall_00", "UCX_SM_M01_STAGEA_RoadCrowned_100m_00", "UCX_SM_M01_STAGEA_Midrise5F_A_00", "UCX_SM_M01_STAGEA_Midrise7F_B_00"]},
        "source_parity_receipt.json": {"passed": True, "sha256": EXPECTED_SOURCE_SHA256, "expected_sha256": EXPECTED_SOURCE_SHA256},
    }
    for name, value in receipts.items():
        write_new_json(output / name, value)
    inventory_paths = current_files(output)
    write_new_json(output / "artifact_inventory.json", {"files": [record(path, output) for path in inventory_paths.values()]})
    write_new_json(output / "terminal_receipt.json", {"status": WORKER_SUCCESS, "automatic_validation_passed": True, "human_visual_acceptance": "NOT_PERFORMED", "blend_count": 1, "glb_count": 4, "checkpoint_count": 3, "final_render_count": 15, "texture_count": 5})
    attempt_source = attempt / r"source\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"
    attempt_source.parent.mkdir(parents=True)
    authoritative_source = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery02\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"
    shutil.copyfile(authoritative_source, attempt_source)
    (attempt / "execution_contract.json").write_text("{}\n", encoding="utf-8")
    write_new_json(attempt / "preflight_receipt.json", {"passed": True, "retry_count": 0, "heavy_process_count": 0, "recovery_source_sha256": EXPECTED_SOURCE_SHA256, "recovery01_members_verified": 13})
    (attempt / "blender.stdout.log").write_text("fixture success\n", encoding="utf-8")
    (attempt / "blender.stderr.log").write_text("", encoding="utf-8")
    produced = [record(path, output) for path in current_files(output).values()]
    write_new_json(manifest_path, {"classification": SUPERVISOR_SUCCESS, "terminal": True, "preflight_passed": True, "supervisor_launch_count": 1, "blender_launch_count": 1, "retry_count": 0, "unreal_launch_count": 0, "exit_code": 0, "exit_code_type": "System.Int32", "timeout": False, "failure_stage": None, "failure_message": None, "governed_attempt_namespace_created": True, "output_namespace_created": True, "native_handle_retained": True, "process_tree_samples": [{"processes": [{"name": "blender.exe"}]}], "output_counts": {"blend": 1, "glb": 4, "checkpoint_png": 3, "final_png": 15, "texture_png": 5}, "receipt_states": {"dimensions": True, "topology_uv": True, "materials": True, "checkpoints": True, "final_renders": True, "exports": True, "source_parity": True, "terminal": True}, "produced_files": produced})
    return output, attempt, manifest_path


def offline_contract_test() -> None:
    with tempfile.TemporaryDirectory(prefix="skyguard_stagea_recovery02_postflight_") as temporary:
        output, attempt, manifest = make_fixture(Path(temporary))
        report, visual = evaluate(output, attempt, manifest)
        require(report["classification"] == AUTOMATIC_PASS and visual["render_count"] == 18, "passing fixture failed")
        tampered = output / TEXTURES[0]
        tampered.write_bytes(tampered.read_bytes() + b"tamper")
        try:
            evaluate(output, attempt, manifest)
        except ContractError:
            pass
        else:
            raise ContractError("tampered fixture did not fail closed")
    print("CLASSIFICATION=PASSED_RECOVERY02_POSTFLIGHT_OFFLINE_CONTRACT_TEST")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--attempt-root", type=Path, default=ATTEMPT_ROOT)
    parser.add_argument("--supervisor-manifest", type=Path, default=SUPERVISOR_MANIFEST)
    parser.add_argument("--postflight-report", type=Path, default=POSTFLIGHT_REPORT)
    parser.add_argument("--visual-manifest", type=Path, default=VISUAL_MANIFEST)
    args = parser.parse_args()
    if args.offline_contract_test:
        offline_contract_test()
        return 0
    require(not args.postflight_report.exists() and not args.visual_manifest.exists(), "future postflight evidence already exists")
    verify_freeze()
    try:
        report, visual = evaluate(args.output_root.resolve(), args.attempt_root.resolve(), args.supervisor_manifest.resolve())
    except Exception as exc:
        failure = {
            "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery02.postflight.v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "classification": FAILURE,
            "automatic_validation_passed": False,
            "failure": f"{type(exc).__name__}: {exc}",
            "direct_full_resolution_visual_review_authorized": False,
        }
        write_new_json(args.postflight_report, failure)
        print(json.dumps(failure, indent=2))
        return 1
    write_new_json(args.postflight_report, report)
    visual["automatic_postflight_report"] = str(args.postflight_report)
    write_new_json(args.visual_manifest, visual)
    print(json.dumps({"classification": report["classification"], "postflight": record(args.postflight_report), "visual_manifest": record(args.visual_manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
