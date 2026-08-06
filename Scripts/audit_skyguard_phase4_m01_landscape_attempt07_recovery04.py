"""Offline-only Recovery04 audit of the immutable Recovery03 PNG evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    decode_png_rgb8,
)


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY04_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def quantize_linear_rgb8(value: float) -> int:
    return max(0, min(255, math.floor(value * 255.0 + 0.5)))


def expected_palette() -> dict[int, tuple[int, int, int]]:
    result = {}
    for y_index in range(2):
        for x_index in range(8):
            component_id = x_index + 8 * y_index
            linear = (
                (x_index + 1) / 9.0,
                (y_index + 1) / 3.0,
                0.25
                + 0.75
                * (
                    component_id * 0.61803398875
                    - math.floor(component_id * 0.61803398875)
                ),
            )
            result[component_id] = tuple(
                quantize_linear_rgb8(channel) for channel in linear
            )
    return result


def four_connected_region_sizes(
    indices: set[int], width: int, height: int
) -> list[int]:
    remaining = set(indices)
    sizes = []
    while remaining:
        queue = deque([remaining.pop()])
        size = 0
        while queue:
            index = queue.popleft()
            size += 1
            x = index % width
            y = index // width
            neighbors = []
            if x > 0:
                neighbors.append(index - 1)
            if x + 1 < width:
                neighbors.append(index + 1)
            if y > 0:
                neighbors.append(index - width)
            if y + 1 < height:
                neighbors.append(index + width)
            for neighbor in neighbors:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def verify_recovery03(contract: dict) -> tuple[Path, dict, dict]:
    immutable = contract["immutable_recovery03"]
    root = ROOT / immutable["root"]
    hashes = {}
    for name, item in immutable["files"].items():
        path = root / item["file"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise RuntimeError(
                "Immutable Recovery03 evidence changed: " + name
            )
        hashes[name] = item["sha256"]
    manifest = read_json(root / "run_manifest.json")
    receipt = read_json(root / "tiny_proof_receipt.json")
    if not (
        manifest.get("terminal_state") == "FAILED"
        and len(manifest.get("stages", [])) == 1
        and manifest["stages"][0].get("exit_code") == 0
        and manifest["stages"][0].get("timed_out") is False
        and manifest.get("build_stage_invoked") is False
        and manifest.get("author_stage_invoked") is False
        and manifest.get("full_capture_invoked") is False
        and manifest.get("profile_invoked") is False
        and receipt.get("gate") == "FAIL"
        and receipt.get("error") is None
    ):
        raise RuntimeError("Recovery03 immutable boundary changed")
    checks = receipt["checks"]
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    if failed_checks != ["all_16_component_ids_visible"]:
        raise RuntimeError(
            "Recovery03 did not fail solely at the palette analyzer"
        )
    if not (
        receipt["component_palette"]["matching_id_count"] == 0
        and receipt["coverage_c05"]["white_pixel_count"] == 72022
        and receipt["coverage_c05"]["white_fraction"]
        > contract["offline_palette_audit"]["coverage_c05_minimum_fraction"]
        and receipt["coverage_c04"]["white_fraction"]
        > contract["offline_palette_audit"]["coverage_c04_minimum_fraction"]
        and receipt["locked_production_packages_unchanged"] is True
        and receipt["recovery01_evidence_unchanged"] is True
        and receipt["deferred_tick_wait_used"] is True
        and receipt["same_stack_compilation_finish_called"] is False
        and receipt["world_saved"] is False
        and receipt["pcg_generation_invoked"] is False
        and receipt["full_capture_invoked"] is False
        and receipt["profile_invoked"] is False
        and receipt["promotion_allowed"] is False
    ):
        raise RuntimeError("Recovery03 prerequisite proof checks changed")
    for phase in (
        "coverage",
        "component_id",
        "governed_restore",
    ):
        audit = receipt["begin_audits"][phase]
        if not (
            audit["success"]
            and audit["landscape_component_count"] == 16
            and audit["generated_material_instance_count"] == 16
            and audit["material_parent_match_count"] == 16
        ):
            raise RuntimeError(
                "Recovery03 begin audit failed for " + phase
            )
    return root, receipt, hashes


def analyze_component_png(
    path: Path, contract: dict, receipt: dict
) -> dict:
    gate = contract["offline_palette_audit"]
    width, height, raw = decode_png_rgb8(path)
    if [width, height] != gate["dimensions"]:
        raise RuntimeError("Recovery03 component PNG dimensions changed")
    pixels = [
        tuple(raw[index : index + 3])
        for index in range(0, len(raw), 3)
    ]
    counts = Counter(pixels)
    palette = expected_palette()
    allowed = {(0, 0, 0), *palette.values()}
    if set(counts) != allowed or len(counts) != 17:
        raise RuntimeError(
            "Expected black plus exactly 16 governed component colors"
        )

    components = {}
    centroids = {}
    areas = []
    for component_id, color in palette.items():
        indices = {
            index for index, pixel in enumerate(pixels) if pixel == color
        }
        area = len(indices)
        if not (
            gate["minimum_pixels_per_id"]
            <= area
            <= gate["maximum_pixels_per_id"]
        ):
            raise RuntimeError(
                f"Component {component_id} area is out of bounds"
            )
        region_sizes = four_connected_region_sizes(
            indices, width, height
        )
        if len(region_sizes) != 1 or region_sizes[0] != area:
            raise RuntimeError(
                f"Component {component_id} is not one connected region"
            )
        xs = [index % width for index in indices]
        ys = [index // width for index in indices]
        bbox = [min(xs), min(ys), max(xs), max(ys)]
        bbox_width = bbox[2] - bbox[0] + 1
        bbox_height = bbox[3] - bbox[1] + 1
        if not (
            gate["minimum_bbox_width"]
            <= bbox_width
            <= gate["maximum_bbox_width"]
            and gate["minimum_bbox_height"]
            <= bbox_height
            <= gate["maximum_bbox_height"]
        ):
            raise RuntimeError(
                f"Component {component_id} bounding box is invalid"
            )
        centroid = [sum(xs) / area, sum(ys) / area]
        centroids[component_id] = centroid
        areas.append(area)
        components[str(component_id)] = {
            "expected_linear_rgb8": list(color),
            "pixel_count": area,
            "four_connected_region_count": 1,
            "bounding_box_xyxy": bbox,
            "centroid_xy": centroid,
        }

    if max(areas) / min(areas) > gate["maximum_area_ratio"]:
        raise RuntimeError("Component areas are not sufficiently uniform")
    for row_start in (0, 8):
        row = [
            centroids[component_id][0]
            for component_id in range(row_start, row_start + 8)
        ]
        gaps = [row[index] - row[index + 1] for index in range(7)]
        if not all(
            gate["minimum_centroid_spacing"]
            <= gap
            <= gate["maximum_centroid_spacing"]
            for gap in gaps
        ):
            raise RuntimeError("Horizontal component ordering failed")
    for component_id in range(8):
        upper = centroids[component_id + 8]
        lower = centroids[component_id]
        if not (
            abs(upper[0] - lower[0])
            <= gate["maximum_paired_x_centroid_delta"]
            and gate["minimum_centroid_spacing"]
            <= lower[1] - upper[1]
            <= gate["maximum_centroid_spacing"]
        ):
            raise RuntimeError("Vertical component ordering failed")

    nonblack = width * height - counts[(0, 0, 0)]
    if (
        nonblack != gate["expected_nonblack_pixel_count"]
        or nonblack != receipt["coverage_c05"]["white_pixel_count"]
    ):
        raise RuntimeError(
            "Component footprint and coverage footprint disagree"
        )
    return {
        "dimensions": [width, height],
        "unique_rgb8_color_count": len(counts),
        "black_background_pixel_count": counts[(0, 0, 0)],
        "nonblack_pixel_count": nonblack,
        "linear_rgb8_direct_match": True,
        "srgb_decode_applied": False,
        "component_id_count": len(components),
        "minimum_component_area": min(areas),
        "maximum_component_area": max(areas),
        "maximum_to_minimum_area_ratio": max(areas) / min(areas),
        "all_components_single_four_connected_regions": True,
        "horizontal_order_valid": True,
        "vertical_pairing_valid": True,
        "components": components,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--authorize-single-recovery04-offline-audit",
        action="store_true",
    )
    args = parser.parse_args()
    if not args.authorize_single_recovery04_offline_audit:
        raise RuntimeError(
            "Recovery04 requires explicit offline-audit authorization"
        )
    contract = read_json(CONTRACT_PATH)
    if (
        contract.get("contract_id")
        != "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-04"
    ):
        raise RuntimeError("Recovery04 contract identity failed")
    output_root = ROOT / contract["offline_audit_execution"]["root"]
    if output_root.exists():
        raise RuntimeError("Recovery04 output namespace already exists")

    recovery03_root, receipt, evidence_hashes = verify_recovery03(
        contract
    )
    component_path = recovery03_root / (
        contract["offline_palette_audit"]["component_capture_file"]
    )
    analysis = analyze_component_png(
        component_path, contract, receipt
    )
    output_root.mkdir(parents=True, exist_ok=False)
    result = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery04-offline-audit.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "gate": "PASS_OFFLINE_COMPONENT_PALETTE_AUDIT",
        "source_recovery": "RECOVERY03_IMMUTABLE",
        "source_evidence_hashes": evidence_hashes,
        "analysis": analysis,
        "recovery03_failure_reclassified": (
            "PALETTE_ANALYZER_COLORSPACE_ASSUMPTION_ONLY"
        ),
        "capture_reused": True,
        "recapture_performed": False,
        "unreal_launched": False,
        "native_build_launched": False,
        "world_saved": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
        "next_gate": (
            "Stop. Independent acceptance is still required; this audit "
            "does not authorize full capture, profiling, or promotion."
        ),
    }
    (output_root / "offline_audit_receipt.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
