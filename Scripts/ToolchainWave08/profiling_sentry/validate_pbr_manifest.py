#!/usr/bin/env python3
"""Fail-closed validation for Skyguard PBR manifests; no third-party packages."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_SUFFIXES = {"BaseColor", "NormalGL", "ORM"}
TIERS = {"first_person_hero": 4096, "hero": 4096, "midground": 2048, "validation": 1024}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_file(record: object, label: str, errors: list[str], check_files: bool) -> None:
    if not isinstance(record, dict):
        return fail(errors, f"{label}: expected object")
    path = record.get("path")
    size = record.get("bytes")
    digest = record.get("sha256")
    if not isinstance(path, str) or not path:
        fail(errors, f"{label}.path: missing")
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        fail(errors, f"{label}.bytes: expected positive integer")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        fail(errors, f"{label}.sha256: expected lowercase SHA-256")
    if check_files and isinstance(path, str):
        file_path = Path(path)
        if not file_path.is_file():
            fail(errors, f"{label}: file absent: {path}")
        elif isinstance(size, int) and file_path.stat().st_size != size:
            fail(errors, f"{label}: byte mismatch")


def validate(data: object, check_files: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema") != "skyguard.pbr-manifest.v1":
        fail(errors, "schema: unsupported")
    tier = data.get("quality_tier")
    if tier not in TIERS:
        fail(errors, "quality_tier: unsupported")
    method = data.get("bake_method")
    if method not in {"high_to_low", "same_mesh_tangent_detail", "material_only"}:
        fail(errors, "bake_method: unsupported")
    source = data.get("source")
    if not isinstance(source, dict):
        fail(errors, "source: expected object")
    else:
        validate_file(source.get("low"), "source.low", errors, check_files)
        high = source.get("high")
        if high is not None:
            validate_file(high, "source.high", errors, check_files)
        if method == "high_to_low" and high is None:
            fail(errors, "source.high: required for high_to_low")
        if source.get("triangulation_frozen") is not True:
            fail(errors, "source.triangulation_frozen: must be true")
    if data.get("tangent_basis") != "MikkTSpace_OpenGL":
        fail(errors, "tangent_basis: must be MikkTSpace_OpenGL")
    cage = data.get("cage")
    if not isinstance(cage, dict) or cage.get("mode") not in {"named_mesh", "recorded_distance", "not_applicable"}:
        fail(errors, "cage.mode: unsupported")
    elif method == "high_to_low" and cage.get("mode") == "not_applicable":
        fail(errors, "cage.mode: high_to_low requires named_mesh or recorded_distance")
    sets = data.get("texture_sets")
    if not isinstance(sets, list) or not sets:
        fail(errors, "texture_sets: expected nonempty array")
    else:
        for index, item in enumerate(sets):
            if not isinstance(item, dict):
                fail(errors, f"texture_sets[{index}]: expected object")
                continue
            expected = TIERS.get(tier)
            if expected and (item.get("width") != expected or item.get("height") != expected):
                fail(errors, f"texture_sets[{index}]: resolution must be {expected}x{expected} for {tier}")
            maps = item.get("maps")
            if not isinstance(maps, list):
                fail(errors, f"texture_sets[{index}].maps: expected array")
                continue
            suffixes: set[str] = set()
            for map_index, record in enumerate(maps):
                validate_file(record, f"texture_sets[{index}].maps[{map_index}]", errors, check_files)
                if isinstance(record, dict):
                    stem = Path(str(record.get("path", ""))).stem
                    for suffix in REQUIRED_SUFFIXES:
                        if stem.endswith("_" + suffix):
                            suffixes.add(suffix)
            missing = REQUIRED_SUFFIXES - suffixes
            if missing:
                fail(errors, f"texture_sets[{index}]: missing required suffixes {sorted(missing)}")
    if data.get("promotion_state") != "candidate_pending_unreal_review":
        fail(errors, "promotion_state: PBR output cannot self-promote")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "errors": [str(exc)]}, indent=2))
        return 2
    errors = validate(data, args.check_files)
    print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

