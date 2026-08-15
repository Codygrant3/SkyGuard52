#!/usr/bin/env python3
"""Create the deterministic minimal input inventory for the isolated VFX build."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    files: set[Path] = {ROOT / "Skyguard52.uproject"}
    for directory in (ROOT / "Source", ROOT / "Config"):
        files.update(path for path in directory.rglob("*") if path.is_file())

    plugin = ROOT / "Plugins" / "SkyguardRecovery03NativeRecovery05"
    files.add(plugin / "SkyguardRecovery03NativeRecovery05.uplugin")
    files.update(path for path in (plugin / "Source").rglob("*") if path.is_file())

    pipeline_cache = (
        ROOT
        / "Build"
        / "Windows"
        / "PipelineCaches"
        / "Skyguard52_PCD3D_SM6.stable.upipelinecache"
    )
    files.add(pipeline_cache)

    missing = [str(path) for path in sorted(files) if not path.is_file()]
    if missing:
        raise SystemExit(f"Missing build inputs: {missing}")

    records = []
    for path in sorted(files, key=lambda value: value.relative_to(ROOT).as_posix().lower()):
        relative = path.relative_to(ROOT).as_posix()
        records.append(
            {
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    report = {
        "schema": "skyguard.phase7.combat-vfx-pooling01.native-build-input-inventory.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(ROOT),
        "future_view_root": r"D:\SG52P7VFX01",
        "record_count": len(records),
        "records": records,
        "exclusions": [
            "Content",
            "Binaries",
            "Intermediate",
            "Saved",
            "DerivedDataCache",
            "plugin Binaries",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record_count": len(records), "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
