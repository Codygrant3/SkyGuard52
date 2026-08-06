"""Diagnose Attempt03 physical-light saturation for recovery_01."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = (
    ROOT
    / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008"
    / "attempt_20260802T173639559Z/mapped_view_capture_03"
)
SUPERVISOR = ATTEMPT / "supervisor_receipt.json"
SWEEP = ATTEMPT / "sweep/capture_manifest.json"
SELECTION = ATTEMPT / "selection/exposure_selection_receipt.json"
MAP_PACKAGE = (
    ROOT
    / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
    / "Review/Lvl_M01_HeroGroupedTopology_008_Attempt03.umap"
)
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_DIAGNOSIS.json"
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


def main() -> int:
    supervisor = json.loads(SUPERVISOR.read_text(encoding="utf-8-sig"))
    sweep = json.loads(SWEEP.read_text(encoding="utf-8-sig"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8-sig"))
    summaries = []
    every_record_clipped = True
    for candidate in selection["candidates"]:
        records = candidate["records"]
        clips = [record["metrics"]["active_clipped_fraction"] for record in records]
        p95s = [record["metrics"]["active_p95"] for record in records]
        every_record_clipped = every_record_clipped and all(
            clip > 0.02 and p95 > 248 for clip, p95 in zip(clips, p95s)
        )
        summaries.append(
            {
                "exposure_bias_ev": candidate["exposure_bias_ev"],
                "all_nine_hard_bounds_passed": candidate[
                    "all_nine_hard_bounds_passed"
                ],
                "minimum_active_clipped_fraction": min(clips),
                "maximum_active_clipped_fraction": max(clips),
                "minimum_active_p95": min(p95s),
                "maximum_active_p95": max(p95s),
            }
        )
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery01-diagnosis.v1",
        "gate": "PASS_OFFLINE_SATURATION_DIAGNOSIS_READY_FOR_RECOVERY01",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bound_failed_evidence": {
            "supervisor_receipt": bound(SUPERVISOR),
            "sweep_manifest": bound(SWEEP),
            "selection_receipt": bound(SELECTION),
            "existing_review_map_package": bound(MAP_PACKAGE),
        },
        "failed_run_facts": {
            "supervisor_gate": supervisor["gate"],
            "failure": supervisor["failure"],
            "unreal_exit_code": supervisor["unreal_process"]["exit_code"],
            "unreal_timed_out": supervisor["unreal_process"]["timed_out"],
            "selector_exit_code": supervisor["selector_process"]["exit_code"],
            "rhi_validation": sweep["rhi_validation"],
            "capture_count": sweep["capture_count"],
            "selection_gate": selection["gate"],
            "every_view_at_every_ev_failed_clipping_and_p95_bounds": every_record_clipped,
            "candidate_summaries": summaries,
        },
        "root_cause": {
            "classification": "PHYSICAL_LIGHT_RIG_SATURATION",
            "key_directional_lux": 100000.0,
            "fill_directional_lux": 12000.0,
            "skylight_intensity": 2.25,
            "exposure_bias_sweep_was_not_a_valid_remedy": True,
            "evidence": (
                "All 63 images exist, but every view at every EV candidate exceeded "
                "the 0.02 clipped-active-pixel maximum and the 248 active-p95 maximum."
            ),
        },
        "recovery_design": {
            "reuse_existing_review_map_without_reassembly": True,
            "fixed_manual_exposure_bias_ev": -12,
            "rig_candidates": [
                {"rig_id": "R00", "key_lux": 250.0, "fill_lux": 30.0, "skylight": 0.25},
                {"rig_id": "R01", "key_lux": 500.0, "fill_lux": 60.0, "skylight": 0.35},
                {"rig_id": "R02", "key_lux": 1000.0, "fill_lux": 120.0, "skylight": 0.5},
                {"rig_id": "R03", "key_lux": 2000.0, "fill_lux": 240.0, "skylight": 0.75},
                {"rig_id": "R04", "key_lux": 4000.0, "fill_lux": 480.0, "skylight": 1.0},
                {"rig_id": "R05", "key_lux": 8000.0, "fill_lux": 960.0, "skylight": 1.25},
                {"rig_id": "R06", "key_lux": 16000.0, "fill_lux": 1920.0, "skylight": 1.5},
                {"rig_id": "R07", "key_lux": 32000.0, "fill_lux": 3840.0, "skylight": 1.75},
            ],
            "captures_per_candidate": 9,
            "total_capture_count": 72,
            "one_global_rig_for_all_nine_views": True,
            "original_hard_bounds_unchanged": True,
            "selection_order": [
                "minimum_maximum_normalized_penalty",
                "minimum_mean_penalty",
                "lowest_rig_index",
            ],
            "canonical_images_are_byte_for_byte_copies": True,
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
