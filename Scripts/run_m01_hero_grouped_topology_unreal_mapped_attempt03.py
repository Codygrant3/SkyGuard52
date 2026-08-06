"""One-process Unreal entrypoint for Build008 mapped-view Attempt03.

The separately authorized PowerShell supervisor launches this script exactly
once in a full D3D12/SM6 Unreal Editor process. It builds the isolated review
map, then captures the complete 63-image exposure sweep in the same process.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
BUILD_SCRIPT = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
CAPTURE_SCRIPT = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
BUILD_REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_BUILD.json"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Run] " + message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("could not load stage module: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    if BUILD_REPORT.exists():
        fail("immutable Attempt03 build report already exists")
    builder = load_module("skyguard_attempt03_builder", BUILD_SCRIPT)
    capture = load_module("skyguard_attempt03_capture", CAPTURE_SCRIPT)

    builder.main()
    if not BUILD_REPORT.is_file():
        fail("builder did not emit its required report")
    build_report = json.loads(BUILD_REPORT.read_text(encoding="utf-8-sig"))
    if build_report.get("gate") != "PASS_ATTEMPT03_MAP_BUILD_REQUIRES_FRESH_TRANSFORM_AUDIT":
        fail("builder gate is not acceptable")
    if build_report.get("promotion_allowed") is not False:
        fail("builder unexpectedly permits promotion")

    capture.main()
    unreal.log(
        "[M01Grouped008Attempt03Run] "
        "PASS_ATTEMPT03_ONE_PROCESS_BUILD_AND_SWEEP_AWAITING_OFFLINE_SELECTION"
    )


if __name__ == "__main__":
    main()
