"""Verify that empty Poly Haven placeholders are excluded from runtime use.

This verifier is offline and read-only. It does not delete directories, edit
contracts, import assets, or launch Unreal or Blender.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("metal_walkway_01", "painted_metal_02", "ship_hull")
RUNTIME_ROOTS = ("Source", "Config", "Plugins", "Content")
CONTRACT = Path(
    "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT.json"
)


def contains_ascii_marker(path: Path, marker: bytes) -> bool:
    overlap = max(0, len(marker) - 1)
    carry = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                return False
            data = carry + chunk
            if marker in data.lower():
                return True
            carry = data[-overlap:] if overlap else b""


def verify(project_root: Path) -> dict:
    project_root = project_root.resolve()
    failures: list[dict[str, object]] = []
    family_results: list[dict[str, object]] = []
    runtime_files: list[Path] = []
    for relative_root in RUNTIME_ROOTS:
        root = project_root / relative_root
        if not root.is_dir():
            failures.append({
                "code": "MISSING_RUNTIME_ROOT",
                "path": str(root),
            })
            continue
        runtime_files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
    runtime_files = sorted(set(runtime_files), key=lambda path: path.as_posix())

    contract_path = project_root / CONTRACT
    excluded: set[str] = set()
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        excluded = set(contract["provenance"]["excluded"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        failures.append({
            "code": "INVALID_EXCLUSION_CONTRACT",
            "path": str(contract_path),
            "detail": str(exc),
        })

    for family in FAMILIES:
        source_dir = (
            project_root
            / "Content"
            / "Skyguard"
            / "Textures"
            / "PolyHaven"
            / family
        )
        source_files = (
            sorted(path for path in source_dir.rglob("*") if path.is_file())
            if source_dir.is_dir()
            else []
        )
        marker = family.encode("ascii").lower()
        matches: list[str] = []
        for path in runtime_files:
            try:
                if contains_ascii_marker(path, marker):
                    matches.append(path.relative_to(project_root).as_posix())
            except OSError as exc:
                failures.append({
                    "code": "RUNTIME_FILE_UNREADABLE",
                    "path": str(path),
                    "detail": str(exc),
                })
        exclusion_token = f"{family}_empty_unverified_placeholder"
        result = {
            "family": family,
            "source_directory":
                source_dir.relative_to(project_root).as_posix(),
            "directory_exists": source_dir.is_dir(),
            "source_file_count": len(source_files),
            "runtime_marker_match_count": len(matches),
            "runtime_marker_matches": matches,
            "contract_exclusion_token": exclusion_token,
            "contract_exclusion_present": exclusion_token in excluded,
        }
        family_results.append(result)
        if not source_dir.is_dir():
            failures.append({
                "code": "PLACEHOLDER_DIRECTORY_MISSING",
                "family": family,
            })
        if source_files:
            failures.append({
                "code": "PLACEHOLDER_NOT_EMPTY",
                "family": family,
                "files": [
                    path.relative_to(project_root).as_posix()
                    for path in source_files
                ],
            })
        if matches:
            failures.append({
                "code": "RUNTIME_REFERENCE_DETECTED",
                "family": family,
                "matches": matches,
            })
        if exclusion_token not in excluded:
            failures.append({
                "code": "CONTRACT_EXCLUSION_MISSING",
                "family": family,
                "token": exclusion_token,
            })

    uasset_count = sum(
        1
        for path in runtime_files
        if path.suffix.lower() == ".uasset"
    )
    passed = not failures
    return {
        "schema": "skyguard52.polyhaven-empty-placeholder-exclusion.v1",
        "classification": (
            "PASSED_OFFLINE_EXCLUDED_FROM_CURRENT_CANDIDATE"
            if passed
            else "FAILED_WITH_EVIDENCE"
        ),
        "project_root": str(project_root),
        "runtime_roots": list(RUNTIME_ROOTS),
        "runtime_file_count": len(runtime_files),
        "uasset_count": uasset_count,
        "contract": CONTRACT.as_posix(),
        "families": family_results,
        "failures": failures,
        "policy_note": (
            "Passing proves only current offline exclusion. Final packaged "
            "dependency and Asset Registry validation must reconfirm absence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.project_root)
    print(json.dumps(result, indent=2))
    return 0 if not result["failures"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
