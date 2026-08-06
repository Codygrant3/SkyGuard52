"""Finalize the Build 008 Unreal mapped-view gate from persisted evidence.

This is a read-only verifier for the candidate packages and capture artifacts.
It records the human original-resolution findings from capture attempts 01/02
and must never launch Unreal, mutate packages, or authorize promotion.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008/attempt_20260802T173639559Z"
CANDIDATE_ROOT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
PERSISTENCE = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_PERSISTENCE.json"
CAPTURE_01 = ATTEMPT / "mapped_view_capture_01/capture_manifest.json"
CAPTURE_02 = ATTEMPT / "mapped_view_capture_02/capture_manifest.json"
SUPERVISOR_02 = ATTEMPT / "mapped_view_capture_02_supervisor_receipt.json"
OUTPUT = ATTEMPT / "unreal_mapped_view_original_resolution_review_receipt.json"
EXPECTED_PERSISTENCE_SHA256 = "2bd9bbaf4750d57d3a3b9ca92dde14995a5b84d4332294a2ce61bfd690d8f185"
EXPECTED_SUPERVISOR_02_GATE = "PASS_CAPTURE_COMPLETE_AWAITING_ORIGINAL_RESOLUTION_REVIEW"

OBSERVATIONS = {
    ("Pathfinder", "three_quarter"): (
        "FAIL",
        "Severe highlight clipping and bloom erase the neutral mapped surface, "
        "normal response, AO response, and most edge detail; the image is not "
        "comparable to the bound Blender three-quarter reference.",
    ),
    ("Pathfinder", "grazing_port"): (
        "FAIL",
        "The port surface and review floor are clipped to white, eliminating "
        "the gradients and thin-hardware evidence required by the contract.",
    ),
    ("Pathfinder", "grazing_starboard"): (
        "FAIL",
        "The starboard surface is clipped to white and cannot demonstrate "
        "stable mapped shading, AO bounds, seams, or thin-hardware response.",
    ),
    ("Lighthouse", "three_quarter"): (
        "FAIL",
        "Severe clipping prevents mapped-surface review; tower, gallery, roof, "
        "and small components also do not read as the continuous assembled "
        "silhouette present in the bound Blender reference.",
    ),
    ("Lighthouse", "grazing_port"): (
        "FAIL",
        "Port highlights are clipped and separated component silhouettes are "
        "visible, so cylindrical gradients, band continuity, and AO cannot be "
        "accepted.",
    ),
    ("Lighthouse", "grazing_starboard"): (
        "FAIL",
        "Starboard highlights are clipped and the assembled lighthouse "
        "silhouette is not reproduced, invalidating the mapped-view comparison.",
    ),
    ("RadarPost", "three_quarter"): (
        "FAIL",
        "Dish/feed, mast, bunker, and floor highlights are clipped; displaced "
        "component silhouettes prevent comparison with the bound assembled "
        "RadarPost reference.",
    ),
    ("RadarPost", "grazing_port"): (
        "FAIL",
        "Port-facing surfaces are clipped and component offsets are visible, "
        "so concentric-ring, mast, AO, and seam behavior cannot be accepted.",
    ),
    ("RadarPost", "grazing_starboard"): (
        "FAIL",
        "Starboard-facing surfaces are clipped and the assembled RadarPost "
        "silhouette is not reproduced; mapped shading is not reviewable.",
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_hashes() -> dict[str, str]:
    records = {}
    for path in sorted(CANDIDATE_ROOT.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".uasset", ".umap"}:
            records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    if len(records) != 49:
        raise RuntimeError(f"Expected 49 candidate packages, found {len(records)}")
    return records


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("Final review receipt already exists")
    if sha256_file(PERSISTENCE) != EXPECTED_PERSISTENCE_SHA256:
        raise RuntimeError("Persistence report hash changed")
    capture_01 = json.loads(CAPTURE_01.read_text(encoding="utf-8-sig"))
    capture_02 = json.loads(CAPTURE_02.read_text(encoding="utf-8-sig"))
    supervisor_02 = json.loads(SUPERVISOR_02.read_text(encoding="utf-8-sig"))
    if supervisor_02.get("gate") != EXPECTED_SUPERVISOR_02_GATE:
        raise RuntimeError("Attempt 02 supervisor capture gate mismatch")
    for capture in (capture_01, capture_02):
        if capture.get("capture_count") != 9:
            raise RuntimeError("Capture manifest does not contain exactly nine views")
        if capture.get("rhi_validation") != "D3D12|SM6":
            raise RuntimeError("Capture manifest is not D3D12|SM6")
        if not capture.get("candidate_packages_unchanged"):
            raise RuntimeError("Capture manifest reports candidate package mutation")
        if capture.get("promotion_allowed") is not False:
            raise RuntimeError("Capture manifest unexpectedly authorizes promotion")

    current = package_hashes()
    expected = capture_02["candidate_package_hashes_after"]
    if current != expected:
        raise RuntimeError("Current candidate package hashes differ from capture 02")

    results = []
    for record in capture_02["captures"]:
        key = (record["family"], record["view"])
        if key not in OBSERVATIONS:
            raise RuntimeError("Unexpected capture record " + repr(key))
        result, observation = OBSERVATIONS[key]
        capture_path = Path(record["path"])
        reference_path = Path(record["blender_reference_path"])
        if sha256_file(capture_path) != record["sha256"]:
            raise RuntimeError("Capture hash changed: " + str(capture_path))
        if sha256_file(reference_path) != record["blender_reference_sha256"]:
            raise RuntimeError("Blender reference hash changed: " + str(reference_path))
        results.append(
            {
                "family": record["family"],
                "view": record["view"],
                "unreal_capture": {
                    "path": str(capture_path),
                    "sha256": record["sha256"],
                    "dimensions": record["dimensions"],
                },
                "blender_reference": {
                    "path": str(reference_path),
                    "sha256": record["blender_reference_sha256"],
                },
                "result": result,
                "observation": observation,
            }
        )
    if len(results) != 9 or any(item["result"] != "FAIL" for item in results):
        raise RuntimeError("Fail-closed result set is incomplete")

    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-review.v1",
        "gate": "FAIL_CLOSED_UNREAL_MAPPED_VIEW_VISUAL_ACCEPTANCE",
        "build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
        "review_completed_utc": datetime.now(timezone.utc).isoformat(),
        "review_mode": "ORIGINAL_RESOLUTION_UNREAL_TO_BOUND_BLENDER_COMPARISON",
        "primary_attempt_path": str(ATTEMPT),
        "capture_attempts": [
            {
                "id": "mapped_view_capture_01",
                "manifest": str(CAPTURE_01),
                "manifest_sha256": sha256_file(CAPTURE_01),
                "capture_count": 9,
                "technical_capture_gate": capture_01["gate"],
                "visual_gate": "FAIL",
                "failure": (
                    "All views are severely underexposed and cannot demonstrate "
                    "mapped normal, AO, material, or silhouette behavior."
                ),
            },
            {
                "id": "mapped_view_capture_02",
                "manifest": str(CAPTURE_02),
                "manifest_sha256": sha256_file(CAPTURE_02),
                "supervisor_receipt": str(SUPERVISOR_02),
                "supervisor_receipt_sha256": sha256_file(SUPERVISOR_02),
                "capture_count": 9,
                "technical_capture_gate": supervisor_02["gate"],
                "visual_gate": "FAIL",
                "failure": (
                    "All views are severely overexposed; Lighthouse and RadarPost "
                    "also fail to reproduce the assembled Blender silhouettes."
                ),
            },
        ],
        "persistence": {
            "path": str(PERSISTENCE),
            "sha256": EXPECTED_PERSISTENCE_SHA256,
            "candidate_package_count": 49,
            "candidate_packages_unchanged": True,
            "current_package_hashes": current,
        },
        "image_count": len(results),
        "pass_count": 0,
        "fail_count": len(results),
        "images": results,
        "fault_classification": [
            "CAPTURE_EXPOSURE_INVALIDATES_MAPPED_SURFACE_COMPARISON",
            "ASSEMBLED_SILHOUETTE_NOT_REPRODUCED_FOR_LIGHTHOUSE_AND_RADARPOST",
        ],
        "runtime_map_changed": False,
        "config_changed": False,
        "candidate_deleted": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
        "next_action": (
            "Preserve the candidate and both failed captures. Any exposure repair, "
            "component-transform repair, recapture, promotion, or P3.4 closure "
            "requires a separate authorized attempt."
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(
        {
            "receipt": str(OUTPUT),
            "sha256": sha256_file(OUTPUT),
            "gate": report["gate"],
            "image_count": report["image_count"],
            "fail_count": report["fail_count"],
            "candidate_packages_unchanged": True,
            "promotion_allowed": False,
            "p3_4_closed": False,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
