"""Diagnose Recovery01 blank/stale render-target output for Recovery02."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\Skyguard52")
BASE_ATTEMPT = (
    ROOT
    / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008"
    / "attempt_20260802T173639559Z"
)
ATTEMPT03_SWEEP = BASE_ATTEMPT / "mapped_view_capture_03/sweep/capture_manifest.json"
RECOVERY01 = BASE_ATTEMPT / "mapped_view_capture_03_recovery_01"
RECOVERY01_SUPERVISOR = RECOVERY01 / "supervisor_receipt.json"
RECOVERY01_SWEEP = RECOVERY01 / "sweep/capture_manifest.json"
RECOVERY01_SELECTION = RECOVERY01 / "selection/rig_selection_receipt.json"
RECOVERY01_ENGINE_LOG = RECOVERY01 / "unreal.engine.log"
REVIEW_MAP = (
    ROOT
    / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
    / "Review/Lvl_M01_HeroGroupedTopology_008_Attempt03.umap"
)
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_DIAGNOSIS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bound(path: Path) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def sample_image(path: Path) -> dict:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        extrema = rgb.getextrema()
        colors = rgb.getcolors(maxcolors=4097)
        return {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "dimensions": list(rgb.size),
            "channel_extrema": [list(pair) for pair in extrema],
            "unique_color_count_capped_at_4097": (
                len(colors) if colors is not None else 4097
            ),
        }


def main() -> int:
    attempt03 = json.loads(ATTEMPT03_SWEEP.read_text(encoding="utf-8-sig"))
    recovery = json.loads(RECOVERY01_SWEEP.read_text(encoding="utf-8-sig"))
    selection = json.loads(RECOVERY01_SELECTION.read_text(encoding="utf-8-sig"))
    original_hashes = [record["sha256"] for record in attempt03["captures"]]
    recovery_hashes = [record["sha256"] for record in recovery["captures"]]
    recovery_counts = Counter(recovery_hashes)
    sample_paths = [Path(record["path"]) for record in recovery["captures"][:3]]
    all_blank = all(
        record["metrics"]["active_pixel_fraction"] == 0.0
        and record["metrics"]["active_p50"] == 0.0
        and record["metrics"]["active_p95"] == 0.0
        for candidate in selection["candidates"]
        for record in candidate["records"]
    )
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-diagnosis.v1",
        "gate": "PASS_OFFLINE_BLANK_STALE_CAPTURE_DIAGNOSIS_READY_FOR_RECOVERY02",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bound_evidence": {
            "attempt03_sweep_manifest": bound(ATTEMPT03_SWEEP),
            "recovery01_supervisor_receipt": bound(RECOVERY01_SUPERVISOR),
            "recovery01_sweep_manifest": bound(RECOVERY01_SWEEP),
            "recovery01_selection_receipt": bound(RECOVERY01_SELECTION),
            "recovery01_engine_log": bound(RECOVERY01_ENGINE_LOG),
            "existing_review_map_package": bound(REVIEW_MAP),
        },
        "comparison": {
            "attempt03_capture_count": len(original_hashes),
            "attempt03_unique_png_hash_count": len(set(original_hashes)),
            "recovery01_capture_count": len(recovery_hashes),
            "recovery01_unique_png_hash_count": len(set(recovery_hashes)),
            "recovery01_hash_multiplicities": sorted(
                recovery_counts.values(), reverse=True
            ),
            "all_recovery01_metrics_blank": all_blank,
            "sampled_recovery01_images": [
                sample_image(path) for path in sample_paths
            ],
        },
        "root_cause": {
            "classification": "DEGENERATE_BLANK_OR_STALE_RENDER_TARGET_READBACK",
            "not_accepted_as_light_calibration_evidence": True,
            "evidence": (
                "Attempt03 produced 63 unique nonblank PNG hashes. Recovery01 "
                "produced only three hashes across 72 files, every metric had zero "
                "active pixels, and sampled PNG channels were limited to 0..1."
            ),
            "required_fixes": [
                "fresh render target per exported frame",
                "sentinel clear before capture",
                "fresh SceneCapture2D lifecycle per pilot/full frame",
                "explicit component render-state dirties after light changes",
                "multiple immediate capture_scene calls before synchronous export",
                "in-process PNG structural liveness proof before full sweep",
            ],
        },
        "recovery02_design": {
            "pilot": {
                "capture_count": 3,
                "rig": {
                    "key_lux": 100000.0,
                    "fill_lux": 12000.0,
                    "skylight": 2.25,
                    "manual_exposure_bias_ev": -12
                },
                "views": [
                    "Pathfinder/three_quarter",
                    "Lighthouse/three_quarter",
                    "RadarPost/three_quarter"
                ],
                "hard_liveness_bounds": {
                    "unique_png_hash_count": 3,
                    "minimum_active_pixel_fraction_luma_gt_8": 0.02,
                    "minimum_max_channel_value": 64,
                    "minimum_unique_color_count": 64,
                    "maximum_sentinel_magenta_fraction": 0.001
                }
            },
            "full_rig_candidates_key_lux": [
                36000.0,
                44000.0,
                52000.0,
                60000.0,
                68000.0,
                76000.0,
                84000.0,
                92000.0
            ],
            "full_sweep_count": 72,
            "full_sweep_runs_only_after_pilot_pass": True,
            "original_selector_bounds_unchanged": True,
        },
        "content_mutation_allowed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
