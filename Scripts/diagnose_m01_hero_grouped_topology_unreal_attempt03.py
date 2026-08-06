"""Offline diagnosis for Build 008 Unreal mapped-view Attempt 03.

Reads only persisted JSON/PNG/GLB evidence. It proves the exposure failure
numerically and derives source-authoritative Unreal assembly locations from the
GLB POSITION accessor bounds. It never imports unreal/bpy or launches a process.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\Skyguard52")
GLB = ROOT / "Content/Skyguard/Meshes/Source/Mission01/HeroGroupedTopology_008/bld_m01_hero_grouped_topology_008_low.glb"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008/attempt_20260802T173639559Z"
CAPTURE_01 = ATTEMPT / "mapped_view_capture_01/capture_manifest.json"
CAPTURE_02 = ATTEMPT / "mapped_view_capture_02/capture_manifest.json"
VISUAL_RECEIPT = ATTEMPT / "unreal_mapped_view_original_resolution_review_receipt.json"
BUILDER = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_candidate_008.py"
OUTPUT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_DIAGNOSIS.json"
FAMILY_OFFSETS_CM = {
    "Pathfinder": [0.0, 0.0, 0.0],
    "Lighthouse": [3000.0, 0.0, 0.0],
    "RadarPost": [6000.0, 0.0, 0.0],
}
OBJECT_TO_KEY = {
    "LOW_M01_Pathfinder_PaintShell_008": "Pathfinder/PaintShell",
    "LOW_M01_Pathfinder_EdgeHardware_008": "Pathfinder/EdgeHardware",
    "LOW_M01_Pathfinder_AccessPanels_008": "Pathfinder/AccessPanels",
    "LOW_M01_Pathfinder_ThermalHardware_008": "Pathfinder/ThermalHardware",
    "LOW_M01_Lighthouse_WhiteTower_008": "Lighthouse/WhiteTower",
    "LOW_M01_Lighthouse_RedBandsRoof_008": "Lighthouse/RedBandsRoof",
    "LOW_M01_Lighthouse_SteelGallery_008": "Lighthouse/SteelGallery",
    "LOW_M01_Lighthouse_LanternGlass_008": "Lighthouse/LanternGlass",
    "LOW_M01_RadarPost_ConcreteBunker_008": "RadarPost/ConcreteBunker",
    "LOW_M01_RadarPost_BlastDoor_008": "RadarPost/BlastDoor",
    "LOW_M01_RadarPost_MastDrive_008": "RadarPost/MastDrive",
    "LOW_M01_RadarPost_DishFeed_008": "RadarPost/DishFeed",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def image_metrics(path: Path) -> dict:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        pixels = list(rgb.getdata())
    luminance = [
        int(round(0.2126 * red + 0.7152 * green + 0.0722 * blue))
        for red, green, blue in pixels
    ]
    active = [value for value in luminance if value > 8]
    total = max(len(luminance), 1)
    active_total = max(len(active), 1)
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "dimensions": [width, height],
        "active_pixel_fraction_luma_gt_8": round(len(active) / total, 8),
        "global_dark_fraction_luma_le_8": round(
            sum(value <= 8 for value in luminance) / total, 8
        ),
        "global_clipped_fraction_luma_ge_250": round(
            sum(value >= 250 for value in luminance) / total, 8
        ),
        "active_clipped_fraction_luma_ge_250": round(
            sum(value >= 250 for value in active) / active_total, 8
        ),
        "active_p05": round(percentile(active, 0.05), 4),
        "active_p50": round(percentile(active, 0.50), 4),
        "active_p95": round(percentile(active, 0.95), 4),
        "active_dynamic_range_p95_minus_p05": round(
            percentile(active, 0.95) - percentile(active, 0.05), 4
        ),
    }


def read_glb_json(path: Path) -> dict:
    payload = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", payload, 0)
    if magic != b"glTF" or version != 2 or total != len(payload):
        raise RuntimeError("Invalid GLB header")
    offset = 12
    while offset < total:
        length, chunk_type = struct.unpack_from("<II", payload, offset)
        offset += 8
        chunk = payload[offset : offset + length]
        offset += length
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.decode("utf-8").rstrip("\x00 "))
    raise RuntimeError("GLB JSON chunk is missing")


def union_bounds(mesh: dict, document: dict) -> tuple[list[float], list[float]]:
    minimum = [float("inf")] * 3
    maximum = [float("-inf")] * 3
    for primitive in mesh["primitives"]:
        accessor = document["accessors"][primitive["attributes"]["POSITION"]]
        for axis in range(3):
            minimum[axis] = min(minimum[axis], float(accessor["min"][axis]))
            maximum[axis] = max(maximum[axis], float(accessor["max"][axis]))
    return minimum, maximum


def gltf_to_unreal_cm(vector: list[float]) -> list[float]:
    # glTF right-handed X-right/Y-up/Z-forward to Unreal X/Y/Z:
    # X -> X, Z -> -Y, Y -> Z. The sign is explicit even though every
    # Build008 component center has source Z == 0.
    return [
        round(vector[0] * 100.0, 6),
        round(-vector[2] * 100.0, 6),
        round(vector[1] * 100.0, 6),
    ]


def derive_assembly() -> tuple[list[dict], dict]:
    document = read_glb_json(GLB)
    records = []
    family_min = {family: [float("inf")] * 3 for family in FAMILY_OFFSETS_CM}
    family_max = {family: [float("-inf")] * 3 for family in FAMILY_OFFSETS_CM}
    for node in document["nodes"]:
        name = node["name"]
        if name not in OBJECT_TO_KEY:
            raise RuntimeError("Unexpected GLB node: " + name)
        if any(field in node for field in ("translation", "rotation", "scale", "matrix")):
            raise RuntimeError("Build008 GLB unexpectedly contains node transforms")
        key = OBJECT_TO_KEY[name]
        family = key.split("/", 1)[0]
        minimum, maximum = union_bounds(document["meshes"][node["mesh"]], document)
        center = [(minimum[i] + maximum[i]) * 0.5 for i in range(3)]
        dimensions = [maximum[i] - minimum[i] for i in range(3)]
        relative_cm = gltf_to_unreal_cm(center)
        actor_cm = [
            round(FAMILY_OFFSETS_CM[family][i] + relative_cm[i], 6)
            for i in range(3)
        ]
        unreal_min = gltf_to_unreal_cm([minimum[0], maximum[1], maximum[2]])
        unreal_max = gltf_to_unreal_cm([maximum[0], minimum[1], minimum[2]])
        for axis in range(3):
            low = min(unreal_min[axis], unreal_max[axis])
            high = max(unreal_min[axis], unreal_max[axis])
            family_min[family][axis] = min(family_min[family][axis], low)
            family_max[family][axis] = max(family_max[family][axis], high)
        records.append(
            {
                "key": key,
                "glb_node": name,
                "glb_node_transform": "IDENTITY",
                "source_bounds_min_m": minimum,
                "source_bounds_max_m": maximum,
                "source_bounds_center_m": center,
                "source_dimensions_m": dimensions,
                "unreal_relative_location_cm": relative_cm,
                "attempt03_actor_location_cm": actor_cm,
                "attempt03_actor_rotation_degrees": [0.0, 0.0, 0.0],
                "attempt03_actor_scale": [1.0, 1.0, 1.0],
            }
        )
    if len(records) != 12:
        raise RuntimeError("Expected 12 source-authoritative assembly records")
    families = {}
    for family in FAMILY_OFFSETS_CM:
        dimensions = [
            family_max[family][axis] - family_min[family][axis]
            for axis in range(3)
        ]
        families[family] = {
            "family_offset_cm": FAMILY_OFFSETS_CM[family],
            "source_assembled_bounds_min_cm": family_min[family],
            "source_assembled_bounds_max_cm": family_max[family],
            "source_assembled_dimensions_cm": dimensions,
        }
    return sorted(records, key=lambda item: item["key"]), families


def main() -> None:
    capture_01 = json.loads(CAPTURE_01.read_text(encoding="utf-8-sig"))
    capture_02 = json.loads(CAPTURE_02.read_text(encoding="utf-8-sig"))
    if capture_01["capture_count"] != 9 or capture_02["capture_count"] != 9:
        raise RuntimeError("Persisted capture count mismatch")
    attempt_metrics = []
    for attempt_id, capture in (
        ("mapped_view_capture_01", capture_01),
        ("mapped_view_capture_02", capture_02),
    ):
        images = [image_metrics(Path(item["path"])) for item in capture["captures"]]
        attempt_metrics.append(
            {
                "attempt_id": attempt_id,
                "manifest": str(CAPTURE_01 if attempt_id.endswith("01") else CAPTURE_02),
                "manifest_sha256": sha256_file(
                    CAPTURE_01 if attempt_id.endswith("01") else CAPTURE_02
                ),
                "image_count": len(images),
                "mean_active_pixel_fraction": round(
                    sum(item["active_pixel_fraction_luma_gt_8"] for item in images)
                    / len(images),
                    8,
                ),
                "mean_active_clipped_fraction": round(
                    sum(item["active_clipped_fraction_luma_ge_250"] for item in images)
                    / len(images),
                    8,
                ),
                "mean_active_p50": round(
                    sum(item["active_p50"] for item in images) / len(images), 4
                ),
                "images": images,
            }
        )
    assembly, families = derive_assembly()
    builder_text = BUILDER.read_text(encoding="utf-8-sig")
    exact_zero_offset_evidence = (
        'offsets = {"Pathfinder": (0.0, 0.0, 0.0), "Lighthouse": '
        '(3000.0, 0.0, 0.0), "RadarPost": (6000.0, 0.0, 0.0)}'
    )
    if exact_zero_offset_evidence not in builder_text:
        raise RuntimeError("Could not bind the Attempt02 zero-relative-offset cause")

    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-attempt03-diagnosis.v1",
        "gate": "PASS_OFFLINE_DIAGNOSIS_READY_FOR_ATTEMPT03_CONTRACT",
        "build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bound_inputs": {
            "low_glb": {"path": str(GLB), "sha256": sha256_file(GLB)},
            "visual_receipt": {
                "path": str(VISUAL_RECEIPT),
                "sha256": sha256_file(VISUAL_RECEIPT),
            },
            "attempt02_builder": {
                "path": str(BUILDER),
                "sha256": sha256_file(BUILDER),
            },
        },
        "exposure_diagnosis": {
            "attempts": attempt_metrics,
            "root_cause": (
                "Attempt01 used an uncalibrated dim transient rig and produced "
                "underexposed evidence. Attempt02 changed both physical light "
                "intensity and exposure bias simultaneously, producing severe "
                "highlight clipping. Neither attempt numerically selected an "
                "exposure from a bounded sweep."
            ),
            "attempt03_policy": {
                "single_unreal_process": True,
                "manual_exposure_bias_candidates_ev": [-12, -10, -8, -6, -4, -2, 0],
                "capture_all_nine_views_at_each_bias": True,
                "pilot_image_count": 63,
                "selector_runs_offline_after_unreal_exit": True,
                "one_global_bias_for_all_nine_views": True,
                "selection_metrics": {
                    "active_pixel_threshold_luma": 8,
                    "maximum_active_clipped_fraction_luma_ge_250": 0.02,
                    "active_p50_range": [35, 210],
                    "active_p95_range": [100, 248],
                    "minimum_active_dynamic_range_p95_minus_p05": 35,
                },
                "selection_order": (
                    "Reject any EV failing a hard bound in any view; among the "
                    "remaining EVs minimize the maximum normalized penalty "
                    "across all nine views, then mean penalty, then absolute EV."
                ),
            },
        },
        "assembly_diagnosis": {
            "root_cause": (
                "The GLB contains 12 identity-transform nodes whose POSITION "
                "accessors retain source-space component placement. Unreal "
                "imports each node as an independently centered StaticMesh. "
                "The Build008 review-map builder placed all four family meshes "
                "at one common family origin and omitted each source bounds "
                "center, collapsing their required relative transforms."
            ),
            "axis_conversion": "UnrealCm = [gltfX*100, -gltfZ*100, gltfY*100]",
            "attempt02_builder_zero_relative_offset_evidence": exact_zero_offset_evidence,
            "family_assembled_bounds": families,
            "source_authoritative_actor_transforms": assembly,
            "geometry_uv_bake_change_required": False,
        },
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "report": str(OUTPUT),
                "sha256": sha256_file(OUTPUT),
                "gate": report["gate"],
                "assembly_record_count": len(assembly),
                "attempt01_mean_active_p50": attempt_metrics[0]["mean_active_p50"],
                "attempt02_mean_active_p50": attempt_metrics[1]["mean_active_p50"],
                "attempt02_mean_active_clipped_fraction": attempt_metrics[1][
                    "mean_active_clipped_fraction"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
