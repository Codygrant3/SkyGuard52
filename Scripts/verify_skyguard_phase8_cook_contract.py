"""Offline cook-contract verification for the Skyguard Phase 8 campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAPS_TO_COOK_RE = re.compile(
    r'^\s*\+MapsToCook=\(FilePath="(?P<path>/Game/[^"]+)"\)\s*$',
    re.MULTILINE,
)
MISSION_UMAP_RE = re.compile(rb"(Lvl_M(?:0[1-9]|10)_[A-Za-z0-9_]+\.umap)")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_matrix(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_maps_to_cook(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    return [match.group("path") for match in MAPS_TO_COOK_RE.finditer(text)]


def source_umap(project_root: Path, package_path: str) -> Path:
    if not package_path.startswith("/Game/"):
        raise ValueError(f"Not a /Game package path: {package_path}")
    return project_root / "Content" / f"{package_path.removeprefix('/Game/')}.umap"


def evaluate_preflight(
    project_root: Path, default_game: Path, mission_matrix: Path
) -> dict[str, Any]:
    matrix = read_matrix(mission_matrix)
    missions = matrix.get("missions", [])
    expected = [mission.get("map") for mission in missions]
    configured = parse_maps_to_cook(default_game)
    configured_counts = Counter(configured)
    duplicate_config_paths = sorted(
        path for path, count in configured_counts.items() if count > 1
    )
    missing_from_config = sorted(set(expected) - set(configured))
    stale_config_paths = sorted(set(configured) - set(expected))
    source_files = [
        {
            "map": package_path,
            "path": str(source_umap(project_root, package_path)),
            "exists": source_umap(project_root, package_path).is_file(),
            "sha256": sha256_file(source_umap(project_root, package_path)),
        }
        for package_path in expected
        if isinstance(package_path, str)
    ]
    checks = {
        "required_count_is_ten": matrix.get("required_mission_count") == 10,
        "matrix_has_ten_missions": len(missions) == 10,
        "matrix_paths_are_unique": len(expected) == len(set(expected)),
        "config_has_ten_entries": len(configured) == 10,
        "config_has_no_duplicates": not duplicate_config_paths,
        "config_matches_matrix_exactly_in_order": configured == expected,
        "no_missing_config_paths": not missing_from_config,
        "no_stale_config_paths": not stale_config_paths,
        "all_expected_source_umaps_exist": (
            len(source_files) == 10 and all(item["exists"] for item in source_files)
        ),
    }
    return {
        "schema": "skyguard.phase8.cook-contract-preflight.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "default_game": str(default_game),
        "default_game_sha256": sha256_file(default_game),
        "mission_matrix": str(mission_matrix),
        "mission_matrix_sha256": sha256_file(mission_matrix),
        "expected_maps": expected,
        "configured_maps_to_cook": configured,
        "duplicate_config_paths": duplicate_config_paths,
        "missing_from_config": missing_from_config,
        "stale_config_paths": stale_config_paths,
        "source_files": source_files,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
    }


def evaluate_packaged_maps(
    expected_maps: list[str], archive_root: Path, cooked_asset_registry: Path
) -> dict[str, Any]:
    registry_bytes = (
        cooked_asset_registry.read_bytes() if cooked_asset_registry.is_file() else b""
    )
    utoc_files = sorted(archive_root.rglob("*.utoc")) if archive_root.is_dir() else []
    utoc_bytes = b"".join(path.read_bytes() for path in utoc_files)

    registry_presence = {
        package_path: package_path.encode("utf-8") in registry_bytes
        for package_path in expected_maps
    }
    expected_umaps = {f"{Path(path).name}.umap" for path in expected_maps}
    discovered_umaps = {
        match.decode("utf-8")
        for match in MISSION_UMAP_RE.findall(utoc_bytes)
    }
    missing_from_registry = sorted(
        path for path, present in registry_presence.items() if not present
    )
    missing_from_container = sorted(expected_umaps - discovered_umaps)
    stale_container_maps = sorted(discovered_umaps - expected_umaps)
    checks = {
        "archive_root_exists": archive_root.is_dir(),
        "cooked_asset_registry_exists": cooked_asset_registry.is_file(),
        "utoc_exists": bool(utoc_files),
        "all_expected_maps_in_cooked_registry": not missing_from_registry,
        "all_expected_maps_in_container_index": not missing_from_container,
        "no_stale_mission_maps_in_container_index": not stale_container_maps,
        "container_mission_map_set_is_exact": discovered_umaps == expected_umaps,
    }
    return {
        "schema": "skyguard.phase8.packaged-map-contract.v1",
        "archive_root": str(archive_root),
        "cooked_asset_registry": str(cooked_asset_registry),
        "cooked_asset_registry_sha256": sha256_file(cooked_asset_registry),
        "utoc_files": [str(path) for path in utoc_files],
        "expected_maps": expected_maps,
        "registry_presence": registry_presence,
        "discovered_container_umaps": sorted(discovered_umaps),
        "missing_from_registry": missing_from_registry,
        "missing_from_container": missing_from_container,
        "stale_container_maps": stale_container_maps,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--default-game", required=True, type=Path)
    parser.add_argument("--mission-matrix", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--cooked-asset-registry", type=Path)
    args = parser.parse_args()

    report = evaluate_preflight(
        args.project_root, args.default_game, args.mission_matrix
    )
    if args.archive_root or args.cooked_asset_registry:
        if not args.archive_root or not args.cooked_asset_registry:
            parser.error(
                "--archive-root and --cooked-asset-registry must be supplied together"
            )
        report["packaged_maps"] = evaluate_packaged_maps(
            report["expected_maps"], args.archive_root, args.cooked_asset_registry
        )
        report["gate"] = (
            "PASS"
            if report["gate"] == "PASS"
            and report["packaged_maps"]["gate"] == "PASS"
            else "FAIL"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": report["gate"], "report": str(args.output)}, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
