"""Persist the actual Recovery03 window topology signature set before assertion.

This is a diagnostic artifact only. It builds the immutable Recovery03 window
geometry, records every renderable object's provenance signature, produces one
small review render, and exports a diagnostic blend/GLB. It does not authorize
Unreal import or alter the production implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKERS = ROOT / "Scripts" / "Workers"
for candidate in (ROOT, WORKERS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import bpy
from Scripts.Workers import worker_m01_hero_prewar_window_bay_a01_recovery03 as implementation


ASSET_ID = "m01-prewar-window-r03-topology-signature-diagnostic-a01"
GATE = "M01-PREWAR-WINDOW-R03-TOPOLOGY-SIGNATURE-DIAGNOSTIC-A01"
EXPECTED_SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(values)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.asset_id != ASSET_ID:
        raise RuntimeError(f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output}")
    if implementation.SIGNATURE != EXPECTED_SIGNATURE:
        raise RuntimeError("Immutable Recovery03 signature authority changed")
    if not implementation.PROVENANCE.is_file() or not implementation.COUPON_FREEZE.is_file():
        raise RuntimeError("Required provenance authority is missing")
    if sha256(implementation.COUPON_FREEZE) != "221354359165758bf92cb8fb35a05f59814457b366968a7d59e26f9d756a0389":
        raise RuntimeError("Accepted glazing coupon freeze changed")
    for family in implementation.legacy.PBR.values():
        for source in family.values():
            if not source.is_file():
                raise RuntimeError(f"Texture authority missing: {source}")

    implementation.base.ASSET_ID = ASSET_ID
    implementation.base.clear_scene()
    scene = bpy.context.scene
    implementation.configure_scene(scene)
    visible = implementation.base.get_collection("M01_PREWAR_WINDOW_R03_DIAGNOSTIC_VISIBLE")
    collision = implementation.base.get_collection("M01_PREWAR_WINDOW_R03_DIAGNOSTIC_COLLISION")
    sockets = implementation.base.get_collection("M01_PREWAR_WINDOW_R03_DIAGNOSTIC_SOCKETS")
    review = implementation.base.get_collection("M01_PREWAR_WINDOW_R03_DIAGNOSTIC_REVIEW_ONLY")
    materials = implementation.build_materials()
    design = implementation.build_window(materials, visible, collision)
    implementation.base.add_empty("SOCKET_M01_PrewarWindowR03_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    implementation.base.add_empty("SOCKET_M01_PrewarWindowR03_Center", (0.0, 0.0, 2.12), sockets, "unreal_socket")
    implementation.base.add_empty("SOCKET_M01_PrewarWindowR03_Latch", (0.050, -0.052, 2.00), sockets, "unreal_socket")

    topology = implementation.topology_receipt((visible, collision, sockets))
    renderable = [
        record
        for record in topology["objects"]
        if record["type"] == "MESH" and record["role"] != "unreal_collision"
    ]
    signature_counts: dict[str, int] = {}
    for record in renderable:
        key = str(record.get("signature")) if record.get("signature") is not None else "<missing>"
        signature_counts[key] = signature_counts.get(key, 0) + 1
    mismatches = [
        {"name": record["name"], "role": record["role"], "signature": record.get("signature")}
        for record in renderable
        if record.get("signature") != EXPECTED_SIGNATURE
    ]
    signature_receipt = {
        "schema": "skyguard.m01-prewar-window-r03-topology-signature-diagnostic-a01.signature-receipt.v1",
        "asset_id": ASSET_ID,
        "diagnostic_complete": True,
        "expected_signature": EXPECTED_SIGNATURE,
        "distinct_building_signatures": topology["distinct_building_signatures"],
        "signature_counts_including_missing": dict(sorted(signature_counts.items())),
        "renderable_mesh_count": len(renderable),
        "mismatch_count": len(mismatches),
        "mismatch_objects": mismatches,
        "matches_expected": topology["distinct_building_signatures"] == [EXPECTED_SIGNATURE] and not mismatches,
        "unreal_import_authorized": False,
        "passed": True,
    }
    write_json(output / "signature_diagnostic_receipt.json", signature_receipt)
    topology["schema"] = "skyguard.m01-prewar-window-r03-topology-signature-diagnostic-a01.topology-material.v1"
    topology["asset_id"] = ASSET_ID
    write_json(output / "topology_material_receipt.json", topology)

    rig = implementation.setup_review(scene, review, materials)
    implementation.set_condition(scene, rig, "daylight")
    renders_dir = output / "renders"
    renders_dir.mkdir()
    render_record = implementation.base.render_one(
        scene,
        rig["camera"],
        renders_dir / "topology_signature_diagnostic.png",
        (0.0, -7.25, 2.02),
        (0.0, 0.18, 2.00),
        64.0,
        (512, 512),
    )

    blend_path = output / "M01_Prewar_Window_R03_Topology_Signature_Diagnostic_A01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Prewar_Window_R03_Topology_Signature_Diagnostic_A01.glb"
    implementation.base.export_glb(glb_path, (visible, collision, sockets))
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-r03-topology-signature-diagnostic-a01.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "render_count": 1,
            "render_dimensions": [512, 512],
            "render_record": render_record,
            "design": design,
            "diagnostic_only": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_DIAGNOSTIC_AWAITING_POSTFLIGHT", "actual_signatures": topology["distinct_building_signatures"], "mismatch_count": len(mismatches)}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
