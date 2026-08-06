"""Classify Build 007 direct-map failures without launching a DCC.

This script reads only the immutable Build 007 manifest and direct-review
receipt.  It verifies their hashes, checks the exact six-map failure set, and
emits the governed Build 008 correction and reuse plan.  It imports neither
Blender nor Unreal and never starts a subprocess.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_FAILED_MAPS = {
    "Pathfinder/PaintShell/Normal",
    "Pathfinder/PaintShell/AO",
    "Pathfinder/EdgeHardware/Normal",
    "Lighthouse/WhiteTower/Normal",
    "Lighthouse/WhiteTower/AO",
    "RadarPost/MastDrive/Normal",
}

CORRECTIVE_POLICIES = {
    "Pathfinder/PaintShell": {
        "normal_projection_policy": (
            "component_exploded_selected_to_active_tangent_normal"
        ),
        "ao_projection_policy": (
            "component_exploded_selected_to_active_from_dedicated_bounded_ao_occluder"
        ),
        "component_spacing_multiplier": 3.0,
        "cage_extrusion_m": 0.0030,
        "max_ray_distance_m": 0.0045,
        "bevel_width_m": 0.0010,
        "diagnosis": (
            "Disconnected repaired shell components remain close enough for "
            "group-wide normal and AO projection rays to cross components."
        ),
    },
    "Pathfinder/EdgeHardware": {
        "normal_projection_policy": (
            "component_exploded_selected_to_active_tangent_normal"
        ),
        "component_spacing_multiplier": 3.0,
        "cage_extrusion_m": 0.0025,
        "max_ray_distance_m": 0.0035,
        "bevel_width_m": 0.0010,
        "diagnosis": (
            "Thin repeated hardware components contaminate one another inside "
            "the previous group-wide normal cage."
        ),
    },
    "Lighthouse/WhiteTower": {
        "normal_projection_policy": (
            "component_exploded_selected_to_active_tangent_normal"
        ),
        "ao_projection_policy": (
            "component_exploded_selected_to_active_from_dedicated_bounded_ao_occluder"
        ),
        "component_spacing_multiplier": 3.0,
        "cage_extrusion_m": 0.0030,
        "max_ray_distance_m": 0.0045,
        "bevel_width_m": 0.0015,
        "diagnosis": (
            "Nested closed tower components cross-project normals, while "
            "whole-group direct self-occlusion blackens interior-facing islands."
        ),
    },
    "RadarPost/MastDrive": {
        "normal_projection_policy": (
            "component_exploded_selected_to_active_tangent_normal"
        ),
        "component_spacing_multiplier": 3.0,
        "cage_extrusion_m": 0.0025,
        "max_ray_distance_m": 0.0035,
        "bevel_width_m": 0.0010,
        "diagnosis": (
            "Repeated drive strips and nearby mast components produce isolated "
            "high-contrast projection ticks under the group-wide cage."
        ),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def manifest_maps(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for asset in manifest.get("assets", []):
        for group in asset.get("groups", []):
            for map_item in group.get("maps", []):
                key = f"{asset['id']}/{group['id']}/{map_item['type']}"
                records[key] = map_item
    return records


def analyze(
    root: Path,
    manifest_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    receipt = load_json(receipt_path)
    maps = manifest_maps(manifest)
    receipt_maps = {
        f"{item['asset']}/{item['group']}/{item['map_type']}": item
        for item in receipt.get("maps", [])
    }
    failures: list[str] = []

    if manifest.get("build_id") != "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
        failures.append("manifest build id is not Build 007")
    if receipt.get("build_id") != "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
        failures.append("review receipt build id is not Build 007")
    if receipt.get("overall_gate") != "FAIL":
        failures.append("Build 007 review receipt is not fail-closed")
    if len(maps) != 24 or len(receipt_maps) != 24:
        failures.append("expected exactly 24 manifest and receipt maps")

    actual_failed = {
        key
        for key, item in receipt_maps.items()
        if item.get("result") == "FAIL"
    }
    if actual_failed != EXPECTED_FAILED_MAPS:
        failures.append(
            "failed-map set differs from the governed six-map correction set"
        )

    accepted: list[dict[str, Any]] = []
    rebake: list[dict[str, Any]] = []
    for key in sorted(maps):
        map_item = maps[key]
        receipt_item = receipt_maps.get(key, {})
        source_path = Path(map_item.get("path", ""))
        if not source_path.is_absolute():
            source_path = root / source_path
        if not source_path.is_file():
            failures.append(f"missing map: {key}")
            continue
        actual_hash = sha256(source_path)
        expected_hash = map_item.get("sha256")
        if actual_hash != expected_hash:
            failures.append(f"map hash mismatch: {key}")
        record = {
            "key": key,
            "source_path": str(source_path),
            "sha256": actual_hash,
        }
        if key in EXPECTED_FAILED_MAPS:
            group_key = key.rsplit("/", 1)[0]
            record["reason"] = receipt_item.get("observation")
            record["policy"] = CORRECTIVE_POLICIES[group_key]
            rebake.append(record)
        elif receipt_item.get("result") == "PASS":
            accepted.append(record)
        else:
            failures.append(f"map is neither governed PASS nor FAIL: {key}")

    checks = {
        "analysis_mode_offline": True,
        "source_build_007": (
            manifest.get("build_id")
            == receipt.get("build_id")
            == "BLD_M01_HERO_GROUPED_TOPOLOGY_007"
        ),
        "manifest_map_count_24": len(maps) == 24,
        "receipt_map_count_24": len(receipt_maps) == 24,
        "exact_failed_map_count_6": len(rebake) == 6,
        "exact_reused_map_count_18": len(accepted) == 18,
        "failed_set_matches": actual_failed == EXPECTED_FAILED_MAPS,
        "all_map_hashes_verified": not any(
            item.startswith(("missing map:", "map hash mismatch:"))
            for item in failures
        ),
        "four_corrective_group_policies": (
            set(CORRECTIVE_POLICIES)
            == {
                "Pathfinder/PaintShell",
                "Pathfinder/EdgeHardware",
                "Lighthouse/WhiteTower",
                "RadarPost/MastDrive",
            }
        ),
    }
    for name, passed in checks.items():
        if not passed:
            failures.append(f"check failed: {name}")

    return {
        "schema": (
            "skyguard.m01.hero-grouped-topology-bake."
            "visual-failure-classification.v1"
        ),
        "source_build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
        "target_build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
        "analysis_mode": "offline_json_and_hash_only_no_blender_no_unreal",
        "manifest": {
            "path": str(manifest_path),
            "sha256": sha256(manifest_path),
        },
        "direct_review_receipt": {
            "path": str(receipt_path),
            "sha256": sha256(receipt_path),
        },
        "checks": checks,
        "failed_map_count": len(rebake),
        "reused_accepted_map_count": len(accepted),
        "rebake_targets": rebake,
        "reused_accepted_maps": accepted,
        "group_policies": CORRECTIVE_POLICIES,
        "gate": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(r"D:\Skyguard52"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest or (
        root
        / "Saved"
        / "Reports"
        / "M01_HERO_GROUPED_TOPOLOGY_BAKE_MANIFEST_007.json"
    )
    receipt = args.receipt or (
        root
        / "Saved"
        / "BuildAttempts"
        / "M01_HERO_GROUPED_TOPOLOGY_007"
        / "attempt_20260802T153804154Z"
        / "direct_original_resolution_map_review_receipt.json"
    )
    report = analyze(root, manifest.resolve(), receipt.resolve())
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
