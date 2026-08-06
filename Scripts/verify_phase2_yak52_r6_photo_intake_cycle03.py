from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
MANIFEST_PATH = (
    ROOT
    / "Saved"
    / "Reports"
    / "PHASE2_YAK52_R6_PHOTO_INTAKE_CYCLE03_MANIFEST.json"
)
REGISTER_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_R6_REFERENCE_ACQUISITION_REGISTER_CYCLE03_2026-08-04.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a valid PNG header")
    return struct.unpack(">II", header[16:24])


def verify_file(record: dict[str, Any], failures: list[str]) -> None:
    path = Path(record["path"])
    if not path.is_file():
        failures.append(f"missing: {path}")
        return
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    if actual_bytes != record["bytes"]:
        failures.append(
            f"byte mismatch: {path}: expected {record['bytes']}, got {actual_bytes}"
        )
    if actual_sha != record["sha256"]:
        failures.append(
            f"hash mismatch: {path}: expected {record['sha256']}, got {actual_sha}"
        )
    if path.suffix.lower() == ".png":
        width, height = png_dimensions(path)
        if width != record["width"] or height != record["height"]:
            failures.append(
                f"dimension mismatch: {path}: expected "
                f"{record['width']}x{record['height']}, got {width}x{height}"
            )


def run_verification() -> dict[str, Any]:
    failures: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    register = load_json(REGISTER_PATH)

    raw_sources = manifest.get("raw_sources", [])
    frames = manifest.get("derived_frames", [])
    logs = manifest.get("evidence_logs", [])

    if manifest.get("classification") != "PASSED_PHOTOGRAPHIC_REFERENCE_INTAKE_ONLY":
        failures.append("manifest classification mismatch")
    if register.get("classification") != "AWAITING_REFERENCE_INPUT":
        failures.append("R6 must remain in the waiting classification")
    if register.get("blender_authorized") is not False:
        failures.append("Blender must remain unauthorized")
    if register.get("unreal_authorized") is not False:
        failures.append("Unreal must remain unauthorized")
    if len(raw_sources) != 2:
        failures.append(f"expected 2 raw sources, got {len(raw_sources)}")
    if len(frames) != 9:
        failures.append(f"expected 9 derived frames, got {len(frames)}")
    if manifest.get("counts", {}).get(
        "directly_inspected_original_resolution_views"
    ) != 10:
        failures.append("expected 10 directly inspected views")

    for record in raw_sources:
        verify_file(record, failures)
    for record in frames:
        verify_file(record, failures)
    for record in logs:
        verify_file(record, failures)

    rights = manifest.get("rights_policy", {})
    required_rights = {
        "use",
        "redistribution",
        "texture_use",
        "likeness_use",
        "copyright_status",
    }
    if not required_rights.issubset(rights):
        failures.append("rights policy is incomplete")

    minimum_set = register.get("minimum_reference_set_before_blender", [])
    if len(minimum_set) != 6:
        failures.append("minimum technical-reference set must contain six items")

    return {
        "schema": "skyguard52.phase2.yak52-r6-photo-intake-cycle03.verification.v1",
        "gate": "PASS" if not failures else "FAIL",
        "classification": (
            "PASSED_PHOTOGRAPHIC_REFERENCE_INTAKE_R6_STILL_AWAITING_TECHNICAL_REFERENCES"
            if not failures
            else "FAILED_WITH_EVIDENCE"
        ),
        "checks": {
            "raw_source_count": len(raw_sources),
            "derived_frame_count": len(frames),
            "evidence_log_count": len(logs),
            "directly_inspected_view_count": manifest.get("counts", {}).get(
                "directly_inspected_original_resolution_views"
            ),
            "blender_authorized": register.get("blender_authorized"),
            "unreal_authorized": register.get("unreal_authorized"),
            "failure_count": len(failures),
        },
        "failures": failures,
    }


def main() -> int:
    try:
        result = run_verification()
    except Exception as exc:
        result = {
            "schema": "skyguard52.phase2.yak52-r6-photo-intake-cycle03.verification.v1",
            "gate": "FAIL",
            "classification": "FAILED_WITH_EVIDENCE",
            "checks": {},
            "failures": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
