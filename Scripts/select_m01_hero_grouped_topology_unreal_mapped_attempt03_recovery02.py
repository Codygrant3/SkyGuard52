"""Select one global rig from the pilot-validated Recovery02 sweep."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_CONTRACT.json"
BASE_SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_exposure.py"
BLENDER_RECEIPT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_008/attempt_20260802T161843676Z/mapped_mesh_grazing_angle_review_receipt.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load base selector helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("skyguard_attempt03_selector_helpers_r02", BASE_SELECTOR_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    output = Path(args.output)
    if output.exists():
        raise RuntimeError("immutable Recovery02 selector output already exists")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if (
        manifest.get("gate")
        != "PASS_RECOVERY02_SYNCHRONIZED_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
    ):
        raise RuntimeError("Recovery02 sweep gate is not ready")
    pilot_path = Path(manifest["pilot_receipt"])
    if (
        not pilot_path.is_file()
        or sha256_file(pilot_path) != manifest["pilot_receipt_sha256"]
    ):
        raise RuntimeError("Recovery02 pilot receipt changed")
    pilot = json.loads(pilot_path.read_text(encoding="utf-8-sig"))
    if (
        pilot.get("gate") != "PASS_RECOVERY02_PILOT_LIVE_FULL_SWEEP_ALLOWED"
        or pilot.get("capture_count") != 3
        or pilot.get("unique_png_hash_count") != 3
        or pilot.get("full_sweep_allowed") is not True
    ):
        raise RuntimeError("Recovery02 pilot did not prove live synchronized capture")
    if manifest.get("capture_count") != contract["capture"]["full_sweep_capture_count"]:
        raise RuntimeError("Recovery02 full sweep count differs from contract")

    policy = contract["selector"]
    evaluations: dict[str, list] = {}
    for record in manifest["captures"]:
        path = Path(record["path"])
        if not path.is_file() or sha256_file(path) != record["sha256"]:
            raise RuntimeError("Recovery02 capture hash changed: " + str(path))
        metrics = BASE.image_metrics(
            path, int(policy["active_pixel_threshold_luma"])
        )
        if metrics["dimensions"] != contract["capture"]["resolution"]:
            raise RuntimeError("Recovery02 capture dimensions changed")
        passed, failures, penalty = BASE.metric_result(metrics, policy)
        enriched = dict(record)
        enriched["metrics"] = metrics
        enriched["hard_bounds_passed"] = passed
        enriched["hard_bound_failures"] = failures
        enriched["penalty"] = penalty
        evaluations.setdefault(record["rig_id"], []).append(enriched)

    candidates = []
    for rig in contract["capture"]["rig_candidates"]:
        records = evaluations.get(rig["rig_id"], [])
        if len(records) != 9:
            raise RuntimeError("each Recovery02 rig must contain exactly nine views")
        candidates.append(
            {
                "rig_id": rig["rig_id"],
                "rig_index": rig["rig_index"],
                "key_lux": rig["key_lux"],
                "fill_lux": rig["fill_lux"],
                "skylight": rig["skylight"],
                "all_nine_hard_bounds_passed": all(
                    record["hard_bounds_passed"] for record in records
                ),
                "maximum_penalty": round(
                    max(record["penalty"] for record in records), 8
                ),
                "mean_penalty": round(
                    sum(record["penalty"] for record in records) / len(records), 8
                ),
                "records": records,
            }
        )
    eligible = [
        candidate
        for candidate in candidates
        if candidate["all_nine_hard_bounds_passed"]
    ]
    output.mkdir(parents=True, exist_ok=False)
    if not eligible:
        report = {
            "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-selection.v1",
            "gate": "FAIL_CLOSED_RECOVERY02_NO_GLOBAL_RIG_PASSED_ALL_NINE_HARD_BOUNDS",
            "pilot_receipt_sha256": sha256_file(pilot_path),
            "selected_rig_id": None,
            "sweep_manifest": str(manifest_path),
            "sweep_manifest_sha256": sha256_file(manifest_path),
            "candidates": candidates,
            "canonical_capture_count": 0,
            "promotion_allowed": False,
            "p3_4_closed": False,
        }
        receipt = output / "rig_selection_receipt.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"gate": report["gate"], "receipt": str(receipt)}, indent=2))
        return 2
    selected = min(
        eligible,
        key=lambda item: (
            item["maximum_penalty"],
            item["mean_penalty"],
            item["rig_index"],
        ),
    )
    blender = json.loads(BLENDER_RECEIPT.read_text(encoding="utf-8-sig"))
    reference_by_key = {
        (record["asset"], record["view"]): record for record in blender["previews"]
    }
    canonical_dir = output / "canonical"
    canonical_dir.mkdir()
    canonical = []
    for record in sorted(
        selected["records"], key=lambda item: (item["family"], item["view"])
    ):
        source = Path(record["path"])
        destination = canonical_dir / (
            f"Unreal_{record['family']}_{record['view']}_008_"
            "Attempt03_Recovery02.png"
        )
        shutil.copyfile(source, destination)
        if sha256_file(destination) != record["sha256"]:
            raise RuntimeError("Recovery02 canonical copy verification failed")
        reference = reference_by_key[(record["family"], record["view"])]
        canonical.append(
            {
                "family": record["family"],
                "view": record["view"],
                "selected_rig_id": selected["rig_id"],
                "path": str(destination),
                "sha256": record["sha256"],
                "dimensions": record["dimensions"],
                "metrics": record["metrics"],
                "blender_reference_sha256": reference["sha256"],
            }
        )
    if len(canonical) != policy["canonical_capture_count"]:
        raise RuntimeError("Recovery02 canonical count differs from contract")
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-selection.v1",
        "gate": "PASS_RECOVERY02_GLOBAL_RIG_SELECTED_AWAITING_ORIGINAL_RESOLUTION_REVIEW",
        "selected_utc": datetime.now(timezone.utc).isoformat(),
        "pilot_receipt_sha256": sha256_file(pilot_path),
        "selected_rig_id": selected["rig_id"],
        "selected_rig": {
            "rig_index": selected["rig_index"],
            "key_lux": selected["key_lux"],
            "fill_lux": selected["fill_lux"],
            "skylight": selected["skylight"],
            "fixed_manual_exposure_bias_ev": contract["capture"][
                "fixed_manual_exposure_bias_ev"
            ],
        },
        "selection_key": {
            "maximum_penalty": selected["maximum_penalty"],
            "mean_penalty": selected["mean_penalty"],
            "rig_index": selected["rig_index"],
        },
        "sweep_manifest": str(manifest_path),
        "sweep_manifest_sha256": sha256_file(manifest_path),
        "candidates": candidates,
        "canonical_capture_count": len(canonical),
        "canonical_captures": canonical,
        "files_are_byte_for_byte_selected_rig_copies": True,
        "original_resolution_review_required": True,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    receipt = output / "rig_selection_receipt.json"
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "gate": report["gate"],
                "selected_rig_id": report["selected_rig_id"],
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
