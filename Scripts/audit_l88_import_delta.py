"""Read-only pass-to-pass contract audit for the L88 source/import slice.

The script deliberately reads a frozen baseline plus the current Blender and
Unreal reports. It never edits a source asset, map, or report supplied as an
input. Only the explicit ``--output`` path is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_BASELINE = Path(r"D:\Skyguard52\Saved\Reports\L88_BASELINE_PASS13.json")
DEFAULT_CURRENT = Path(r"D:\Skyguard52\Saved\Screenshots\AAA_L88_Blockout\L88_SILHOUETTE_REPORT.json")
DEFAULT_IMPORT = Path(r"D:\Skyguard52\Saved\Reports\L88_VALIDATION_IMPORT.json")
DEFAULT_MARKERS = Path(r"D:\Skyguard52\Saved\Reports\L88_MARKERS.json")
DEFAULT_OUTPUT = Path(r"D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS14.json")


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected object in {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close_envelope(left: list[float], right: list[float], tolerance_m: float = 0.01) -> bool:
    return len(left) == len(right) == 3 and all(abs(a - b) <= tolerance_m for a, b in zip(left, right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--import-report", type=Path, default=DEFAULT_IMPORT)
    parser.add_argument("--markers", type=Path, default=DEFAULT_MARKERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--change-reason",
        default="bounded readiness delta",
        help="Explicit human-readable reason for the additive source delta.",
    )
    parser.add_argument(
        "--expected-mesh-delta",
        type=int,
        default=0,
        help="Explicitly authorized Blender/Unreal mesh-count increase from the baseline.",
    )
    args = parser.parse_args()

    baseline = read_json(args.baseline)
    current = read_json(args.current)
    imported = read_json(args.import_report)
    markers = read_json(args.markers)

    source = Path(current["export"])
    current_source_hash = sha256(source)
    current_source_bytes = source.stat().st_size

    checks = {
        "hero_mesh_count_matches_expected_delta": current.get("hero_mesh_objects")
        == baseline.get("hero_mesh_objects", 0) + args.expected_mesh_delta,
        "envelope_unchanged": close_envelope(
            current.get("measured_dimensions_m", []), baseline.get("measured_dimensions_m", [])
        ),
        "unreal_mesh_actor_count_matches_blender": imported.get("validation_mesh_actor_count")
        == current.get("hero_mesh_objects"),
        "unreal_static_mesh_count_matches_blender": imported.get("static_mesh_asset_count")
        == current.get("hero_mesh_objects"),
        "forbidden_labels_empty": not imported.get("forbidden_legacy_labels"),
        "current_glb_hash_matches_import_report": current_source_hash == imported.get("source_glb_sha256"),
        "uv_channel_complete": current.get("uv_layer_name") == "UV_L88_0"
        and current.get("uv_layer_mesh_count") == current.get("hero_mesh_objects"),
        "expected_socket_markers": markers.get("marker_count") == 3
        and markers.get("render_mesh_excluded") is True,
    }

    changed = {
        "source_glb_sha256": {
            "baseline": baseline.get("source_glb_sha256"),
            "current": current_source_hash,
            "allowed_reason": args.change_reason,
        },
        "source_glb_bytes": {
            "baseline": baseline.get("source_glb_bytes"),
            "current": current_source_bytes,
            "allowed_reason": args.change_reason,
        },
        "uv_layer": current.get("uv_layer_name"),
        "expected_mesh_delta": args.expected_mesh_delta,
        "marker_names": [item.get("name") for item in markers.get("markers", [])],
    }
    result = {
        "schema": "skyguard.l88.import-delta.v1",
        "baseline": str(args.baseline),
        "current": str(args.current),
        "import_report": str(args.import_report),
        "markers": str(args.markers),
        "checks": checks,
        "allowed_changes": changed,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "read_only": True,
        "promotion": "readiness_only_not_aaa_acceptance",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["gate"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
