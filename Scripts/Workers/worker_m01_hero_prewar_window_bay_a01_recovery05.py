"""Blender compatibility wrapper preserving Recovery03's internal design signature.

Recovery04 proved package imports and Blender argument parsing were corrected, but
it versioned the internal building signature before Recovery03's immutable
topology self-check. This wrapper keeps that internal provenance identity intact
and versions only the fresh external asset identity, filenames and receipts.
Geometry, materials, lighting, cameras and acceptance thresholds remain owned by
the immutable Recovery03 implementation.
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


ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery05"
GATE = "M01-HERO-PREWAR-WINDOW-BAY-A01-RECOVERY05"
IMMUTABLE_INTERNAL_SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"


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


def rewrite_receipts(output: Path) -> None:
    for receipt in output.glob("*_receipt.json"):
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["asset_id"] = ASSET_ID
        schema = payload.get("schema")
        if isinstance(schema, str):
            payload["schema"] = schema.replace("recovery03", "recovery05")
        receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_blend = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.blend"
    old_glb = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.glb"
    new_blend = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery05.blend"
    new_glb = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery05.glb"
    if old_blend.is_file():
        old_blend.replace(new_blend)
    if old_glb.is_file():
        old_glb.replace(new_glb)

    artifact_path = output / "artifact_receipt.json"
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    payload["asset_id"] = ASSET_ID
    payload["schema"] = "skyguard.m01-hero-prewar-window-bay-a01-recovery05.artifacts.v1"
    payload["blend"] = {"path": str(new_blend), "bytes": new_blend.stat().st_size, "sha256": sha256(new_blend)}
    payload["glb"] = {"path": str(new_glb), "bytes": new_glb.stat().st_size, "sha256": sha256(new_glb)}
    payload["recovery05_preserved_internal_signature"] = True
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_blender_args()
    if args.asset_id != ASSET_ID:
        raise RuntimeError(f"Unexpected asset id: {args.asset_id}")
    if implementation.SIGNATURE != IMMUTABLE_INTERNAL_SIGNATURE:
        raise RuntimeError("Immutable Recovery03 internal signature changed")
    output = Path(args.output).resolve()

    implementation.ASSET_ID = ASSET_ID
    implementation.GATE = GATE
    implementation.base.ASSET_ID = ASSET_ID
    implementation.parse_args = parse_blender_args

    result = int(implementation.main())
    if result != 0:
        return result
    rewrite_receipts(output)
    print(json.dumps({"gate": GATE, "classification": "PASSED_RECOVERY05_COMPATIBILITY_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW"}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
