#!/usr/bin/env python3
"""Freeze the exact files copied into the isolated grounding-bridge build view."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DEFAULT_OUTPUT = (
    ROOT
    / "Saved"
    / "Reports"
    / "M01_LANDSCAPE_GROUNDING_BRIDGE01_SOURCE_PARITY_CONTRACT.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def governed_files() -> list[Path]:
    files: set[Path] = {
        ROOT / "Skyguard52.uproject",
        ROOT
        / "Build"
        / "Windows"
        / "PipelineCaches"
        / "Skyguard52_PCD3D_SM6.stable.upipelinecache",
    }
    for directory in (
        ROOT / "Config",
        ROOT / "Source",
        ROOT / "Plugins" / "SkyguardRecovery03NativeRecovery05",
    ):
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing governed directory: {directory}")
        for candidate in directory.rglob("*"):
            if not candidate.is_file():
                continue
            relative_parts = candidate.relative_to(directory).parts
            if any(
                part in {"Binaries", "Intermediate", "Saved", "DerivedDataCache"}
                for part in relative_parts
            ):
                continue
            files.add(candidate)
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing governed files: " + ", ".join(missing))
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix().lower())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    records = []
    for path in governed_files():
        relative = path.relative_to(ROOT).as_posix()
        records.append(
            {
                "relative_path": relative,
                "source": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    payload = {
        "schema": "skyguard.m01-landscape-grounding-bridge01.source-parity.v1",
        "classification": "FROZEN_FOR_FUTURE_ISOLATED_NATIVE_BUILD",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(ROOT),
        "future_view_root": r"D:\SG52M01GROUND01",
        "record_count": len(records),
        "include_roots": [
            "Skyguard52.uproject",
            "Config",
            "Source",
            "Plugins/SkyguardRecovery03NativeRecovery05",
            "Build/Windows/PipelineCaches/Skyguard52_PCD3D_SM6.stable.upipelinecache",
        ],
        "excluded_directory_names": [
            "Binaries",
            "Intermediate",
            "Saved",
            "DerivedDataCache",
            "Content",
        ],
        "copy_back_permitted": False,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": len(records)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
