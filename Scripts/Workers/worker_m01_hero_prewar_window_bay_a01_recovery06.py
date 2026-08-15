"""Surgical production correction for two legacy curtain provenance tags.

The accepted diagnostic proves only the left and right curtain meshes inherit the
material-benchmark signature from legacy.add_curtain. This wrapper retags only
those two returned objects with Recovery03's immutable internal signature, then
runs the unchanged Recovery03 production implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKERS = ROOT / "Scripts" / "Workers"
for candidate in (ROOT, WORKERS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from Scripts.Workers import worker_m01_hero_prewar_window_bay_a01_recovery03 as implementation


ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery06"
GATE = "M01-HERO-PREWAR-WINDOW-BAY-A01-RECOVERY06"
IMMUTABLE_INTERNAL_SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"
CURTAIN_NAMES = ["SM_M01_WindowR03_Curtain_L", "SM_M01_WindowR03_Curtain_R"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_blender_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(values)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rewrite_receipts(output: Path) -> None:
    for receipt in output.glob("*_receipt.json"):
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["asset_id"] = ASSET_ID
        schema = payload.get("schema")
        if isinstance(schema, str):
            payload["schema"] = schema.replace("recovery03", "recovery06")
        receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_blend = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.blend"
    old_glb = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.glb"
    new_blend = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery06.blend"
    new_glb = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery06.glb"
    if old_blend.is_file():
        old_blend.replace(new_blend)
    if old_glb.is_file():
        old_glb.replace(new_glb)

    curtain_records = []
    for name in CURTAIN_NAMES:
        obj = implementation.bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"Corrected curtain object is missing: {name}")
        curtain_records.append({
            "name": name,
            "role": obj.get("SKG_Role"),
            "signature": obj.get("SKG_BuildingSignature"),
            "asset_id": obj.get("SKG_AssetId"),
        })
    if any(record["signature"] != IMMUTABLE_INTERNAL_SIGNATURE for record in curtain_records):
        raise RuntimeError("Curtain signature correction did not persist")
    write_json(
        output / "curtain_signature_correction_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery06.curtain-signature-correction.v1",
            "asset_id": ASSET_ID,
            "diagnostic_authority": "Docs\\AAA_Review\\M01_PREWAR_WINDOW_R03_TOPOLOGY_SIGNATURE_DIAGNOSTIC_A01_ATTEMPT01_ACCEPTANCE_FREEZE.json",
            "correction_scope": "retag_only_two_legacy_curtain_return_objects",
            "corrected_object_count": 2,
            "corrected_objects": curtain_records,
            "geometry_changed": False,
            "materials_changed": False,
            "lighting_changed": False,
            "cameras_changed": False,
            "passed": True,
        },
    )

    artifact_path = output / "artifact_receipt.json"
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    payload["asset_id"] = ASSET_ID
    payload["schema"] = "skyguard.m01-hero-prewar-window-bay-a01-recovery06.artifacts.v1"
    payload["blend"] = {"path": str(new_blend), "bytes": new_blend.stat().st_size, "sha256": sha256(new_blend)}
    payload["glb"] = {"path": str(new_glb), "bytes": new_glb.stat().st_size, "sha256": sha256(new_glb)}
    payload["recovery06_curtain_retag_only"] = True
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_blender_args()
    if args.asset_id != ASSET_ID:
        raise RuntimeError(f"Unexpected asset id: {args.asset_id}")
    if implementation.SIGNATURE != IMMUTABLE_INTERNAL_SIGNATURE:
        raise RuntimeError("Immutable Recovery03 internal signature changed")
    output = Path(args.output).resolve()

    original_add_curtain = implementation.legacy.add_curtain

    def add_curtain_retagged(*curtain_args, **curtain_kwargs):
        obj = original_add_curtain(*curtain_args, **curtain_kwargs)
        implementation.base.tag(obj, "window_interior_textile", IMMUTABLE_INTERNAL_SIGNATURE)
        return obj

    implementation.ASSET_ID = ASSET_ID
    implementation.GATE = GATE
    implementation.base.ASSET_ID = ASSET_ID
    implementation.parse_args = parse_blender_args
    implementation.legacy.add_curtain = add_curtain_retagged
    try:
        result = int(implementation.main())
    finally:
        implementation.legacy.add_curtain = original_add_curtain
    if result != 0:
        return result
    rewrite_receipts(output)
    print(json.dumps({"gate": GATE, "classification": "PASSED_RECOVERY06_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW"}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
