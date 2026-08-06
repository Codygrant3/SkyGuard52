"""Select one global Attempt03 EV from a completed 63-image sweep.

The selector runs only after Unreal exits. It computes bounded luminance metrics
with Pillow, rejects any EV that fails a hard bound in any of the nine views,
then deterministically ranks the remaining global EVs. The nine canonical PNGs
are byte-for-byte copies of the selected pilot images.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
BLENDER_RECEIPT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_008/attempt_20260802T161843676Z/mapped_mesh_grazing_angle_review_receipt.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: list[int], fraction: float) -> float:
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def image_metrics(path: Path, threshold: int) -> dict:
    with Image.open(path) as image:
        luminance = list(image.convert("L").getdata())
        dimensions = list(image.size)
    active = [value for value in luminance if value > threshold]
    if not active:
        return {
            "dimensions": dimensions,
            "active_pixel_fraction": 0.0,
            "active_clipped_fraction": 1.0,
            "active_p05": 0.0,
            "active_p50": 0.0,
            "active_p95": 0.0,
            "active_dynamic_range": 0.0,
        }
    p05 = percentile(active, 0.05)
    p50 = percentile(active, 0.50)
    p95 = percentile(active, 0.95)
    return {
        "dimensions": dimensions,
        "active_pixel_fraction": round(len(active) / len(luminance), 8),
        "active_clipped_fraction": round(
            sum(value >= 250 for value in active) / len(active), 8
        ),
        "active_p05": round(p05, 4),
        "active_p50": round(p50, 4),
        "active_p95": round(p95, 4),
        "active_dynamic_range": round(p95 - p05, 4),
    }


def metric_result(metrics: dict, policy: dict) -> tuple[bool, list[str], float]:
    failures = []
    if metrics["active_clipped_fraction"] > policy["maximum_active_clipped_fraction_luma_ge_250"]:
        failures.append("active_clipped_fraction")
    if not policy["active_p50_range"][0] <= metrics["active_p50"] <= policy["active_p50_range"][1]:
        failures.append("active_p50")
    if not policy["active_p95_range"][0] <= metrics["active_p95"] <= policy["active_p95_range"][1]:
        failures.append("active_p95")
    if metrics["active_dynamic_range"] < policy["minimum_active_dynamic_range_p95_minus_p05"]:
        failures.append("active_dynamic_range")
    penalty = (
        metrics["active_clipped_fraction"]
        / policy["maximum_active_clipped_fraction_luma_ge_250"]
        + abs(metrics["active_p50"] - 120.0) / 120.0
        + abs(metrics["active_p95"] - 220.0) / 220.0
        + max(0.0, 100.0 - metrics["active_dynamic_range"]) / 100.0
    )
    return not failures, failures, round(penalty, 8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    output = Path(args.output)
    if output.exists():
        raise RuntimeError("Immutable selector output already exists")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("gate") != "PASS_ATTEMPT03_SWEEP_AWAITING_OFFLINE_GLOBAL_EV_SELECTION":
        raise RuntimeError("Sweep manifest gate is not ready for selection")
    if manifest.get("capture_count") != contract["exposure_sweep"]["pilot_capture_count"]:
        raise RuntimeError("Sweep manifest does not contain exact pilot count")
    policy = contract["exposure_sweep"]["selector"]
    expected_resolution = contract["exposure_sweep"]["capture_resolution"]
    evaluations = {}
    for record in manifest["captures"]:
        path = Path(record["path"])
        if sha256_file(path) != record["sha256"]:
            raise RuntimeError("Pilot capture hash changed: " + str(path))
        metrics = image_metrics(path, int(policy["active_pixel_threshold_luma"]))
        if metrics["dimensions"] != expected_resolution:
            raise RuntimeError("Pilot capture resolution changed")
        passed, failures, penalty = metric_result(metrics, policy)
        enriched = dict(record)
        enriched["metrics"] = metrics
        enriched["hard_bounds_passed"] = passed
        enriched["hard_bound_failures"] = failures
        enriched["penalty"] = penalty
        evaluations.setdefault(int(record["exposure_bias_ev"]), []).append(enriched)
    expected_biases = contract["exposure_sweep"]["manual_exposure_bias_candidates_ev"]
    if sorted(evaluations) != sorted(expected_biases):
        raise RuntimeError("Sweep EV set differs from contract")

    candidates = []
    for bias in expected_biases:
        records = evaluations[int(bias)]
        if len(records) != 9:
            raise RuntimeError("Each EV must contain exactly nine views")
        all_passed = all(record["hard_bounds_passed"] for record in records)
        maximum_penalty = max(record["penalty"] for record in records)
        mean_penalty = sum(record["penalty"] for record in records) / len(records)
        candidates.append(
            {
                "exposure_bias_ev": int(bias),
                "all_nine_hard_bounds_passed": all_passed,
                "maximum_penalty": round(maximum_penalty, 8),
                "mean_penalty": round(mean_penalty, 8),
                "records": records,
            }
        )
    eligible = [candidate for candidate in candidates if candidate["all_nine_hard_bounds_passed"]]
    output.mkdir(parents=True, exist_ok=False)
    if not eligible:
        report = {
            "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-exposure-selection.v1",
            "gate": "FAIL_CLOSED_NO_GLOBAL_EV_PASSED_ALL_NINE_HARD_BOUNDS",
            "build_id": contract["build_id"],
            "selected_exposure_bias_ev": None,
            "sweep_manifest": str(manifest_path),
            "sweep_manifest_sha256": sha256_file(manifest_path),
            "candidates": candidates,
            "canonical_capture_count": 0,
            "promotion_allowed": False,
            "p3_4_closed": False,
        }
        receipt = output / "exposure_selection_receipt.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"gate": report["gate"], "receipt": str(receipt)}, indent=2))
        return 2
    selected = min(
        eligible,
        key=lambda item: (
            item["maximum_penalty"],
            item["mean_penalty"],
            abs(item["exposure_bias_ev"]),
            item["exposure_bias_ev"],
        ),
    )
    blender = json.loads(BLENDER_RECEIPT.read_text(encoding="utf-8-sig"))
    reference_by_key = {
        (record["asset"], record["view"]): record for record in blender["previews"]
    }
    canonical_dir = output / "canonical"
    canonical_dir.mkdir()
    canonical = []
    for record in sorted(selected["records"], key=lambda item: (item["family"], item["view"])):
        source = Path(record["path"])
        destination = canonical_dir / f"Unreal_{record['family']}_{record['view']}_008_Attempt03.png"
        shutil.copyfile(source, destination)
        if sha256_file(destination) != record["sha256"]:
            raise RuntimeError("Canonical byte-for-byte copy verification failed")
        reference = reference_by_key[(record["family"], record["view"])]
        canonical.append(
            {
                "family": record["family"],
                "view": record["view"],
                "selected_exposure_bias_ev": selected["exposure_bias_ev"],
                "path": str(destination),
                "sha256": record["sha256"],
                "dimensions": record["dimensions"],
                "metrics": record["metrics"],
                "blender_reference_sha256": reference["sha256"],
            }
        )
    if len(canonical) != policy["canonical_capture_count"]:
        raise RuntimeError("Canonical capture count differs from contract")
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-exposure-selection.v1",
        "gate": "PASS_ATTEMPT03_EXPOSURE_SELECTED_AWAITING_ORIGINAL_RESOLUTION_REVIEW",
        "build_id": contract["build_id"],
        "selected_utc": datetime.now(timezone.utc).isoformat(),
        "selected_exposure_bias_ev": selected["exposure_bias_ev"],
        "selection_key": {
            "maximum_penalty": selected["maximum_penalty"],
            "mean_penalty": selected["mean_penalty"],
            "absolute_ev": abs(selected["exposure_bias_ev"]),
            "numeric_ev": selected["exposure_bias_ev"],
        },
        "sweep_manifest": str(manifest_path),
        "sweep_manifest_sha256": sha256_file(manifest_path),
        "candidates": candidates,
        "canonical_capture_count": len(canonical),
        "canonical_captures": canonical,
        "files_are_byte_for_byte_selected_pilot_copies": True,
        "original_resolution_review_required": True,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    receipt = output / "exposure_selection_receipt.json"
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "gate": report["gate"],
                "selected_exposure_bias_ev": report["selected_exposure_bias_ev"],
                "canonical_capture_count": len(canonical),
                "receipt": str(receipt),
                "receipt_sha256": sha256_file(receipt),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
