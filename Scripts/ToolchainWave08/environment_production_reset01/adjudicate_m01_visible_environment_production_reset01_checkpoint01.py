"""Automatic postflight for the fresh Mission 1 environment checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01"
REPORT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_POSTFLIGHT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glb_version(path: Path) -> int:
    with path.open("rb") as stream:
        magic, version, length = struct.unpack("<4sII", stream.read(12))
    if magic != b"glTF" or length != path.stat().st_size:
        raise AssertionError(f"Invalid GLB header: {path}")
    return version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        print("PASS_OFFLINE_CONTRACT")
        return 0

    receipt = json.loads((OUTPUT / "production_checkpoint_receipt.json").read_text(encoding="utf-8"))
    inventory = json.loads((OUTPUT / "artifact_inventory.json").read_text(encoding="utf-8"))
    assert receipt["classification"] == "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW"
    assert receipt["source_policy"]["failed_stagea_geometry_read"] is False
    assert receipt["source_policy"]["external_models_imported"] is False
    assert receipt["scene_stats"]["mesh_object_count"] >= 350
    assert receipt["scene_stats"]["collision_object_count"] >= 5
    assert receipt["scene_stats"]["socket_count"] >= 10
    assert inventory["member_count"] == len(inventory["members"])
    for member in inventory["members"]:
        path = Path(member["path"])
        assert path.is_file(), path
        assert path.stat().st_size == member["bytes"], path
        assert sha256(path) == member["sha256"], path

    renders = sorted((OUTPUT / "renders").glob("*.png"))
    assert len(renders) == 4
    image_metrics = []
    for path in renders:
        with Image.open(path) as image:
            assert image.size == (1920, 1080), (path, image.size)
            rgb = image.convert("RGB").resize((320, 180))
            stat = ImageStat.Stat(rgb)
            mean = sum(stat.mean) / (3 * 255.0)
            extrema = rgb.convert("L").getextrema()
            assert 0.10 < mean < 0.88, (path, mean)
            assert extrema[1] - extrema[0] >= 80, (path, extrema)
            image_metrics.append({"path": str(path), "mean_luminance": mean, "luma_extrema": extrema})

    glbs = sorted((OUTPUT / "exports").glob("*.glb"))
    assert len(glbs) == 5
    glb_metrics = [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path), "glb_version": glb_version(path)} for path in glbs]
    payload = {
        "schema": "skyguard.m01-visible-environment-production-reset01.checkpoint01-postflight.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "image_metrics": image_metrics,
        "glb_metrics": glb_metrics,
        "direct_review_required": True,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
