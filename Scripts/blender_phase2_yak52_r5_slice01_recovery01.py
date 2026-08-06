"""Yak-52 R5 Slice01 Recovery01 Blender 5.2 compatibility binding.

The frozen R5 authoring source remains unchanged. This wrapper changes only:
1. the new immutable Recovery01 output namespace; and
2. the inherited datum display token from unsupported ``CROSS`` to
   Blender 5.2's supported ``PLAIN_AXES``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK52-R5-SLICE01-RECOVERY01"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
FROZEN_R5 = ROOT / "Scripts/blender_phase2_yak52_r5_slice01.py"
CONTRACT = ROOT / "Docs/AAA_Review/PHASE2_YAK52_R5_SLICE01_RECOVERY01_CONTRACT.json"
OUTPUT_DIR = (
    ROOT
    / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R5/"
    "Slice01_Recovery01"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK52_R5_SLICE01_RECOVERY01_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak52_r5_slice01_recovery01.glb"
MANIFEST_PATH = (
    ROOT / "Saved/Reports/BLD_M01_YAK52_R5_SLICE01_RECOVERY01_MANIFEST.json"
)
SCREENSHOT_DIR = (
    ROOT / "Saved/Screenshots/BLD_M01_YAK52_R5_SLICE01_RECOVERY01"
)


def load_frozen_r5() -> Any:
    spec = importlib.util.spec_from_file_location(
        "skyguard_yak52_r5_slice01_frozen", FROZEN_R5
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load frozen R5 Slice01 source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    frozen = load_frozen_r5()
    frozen.BUILD_ID = BUILD_ID
    frozen.SCRIPT_PATH = SCRIPT_PATH
    frozen.CONTRACT = CONTRACT
    frozen.OUTPUT_DIR = OUTPUT_DIR
    frozen.BLEND_PATH = BLEND_PATH
    frozen.GLB_PATH = GLB_PATH
    frozen.MANIFEST_PATH = MANIFEST_PATH
    frozen.SCREENSHOT_DIR = SCREENSHOT_DIR

    frozen_load_base = frozen.load_base

    def load_base_compatible() -> Any:
        base = frozen_load_base()

        def create_datums(collection: Any, overall_length: float) -> None:
            half_length = overall_length / 2.0
            for name, location in (
                ("DATUM_R4S01_AircraftOrigin", (0.0, 0.0, 0.0)),
                ("DATUM_R4S01_TailExtreme", (-half_length, 0.0, 0.34)),
                ("DATUM_R4S01_PropellerPlane", (half_length, 0.0, 0.13)),
                ("DATUM_R4S01_WingReference", (0.0, 0.0, 0.0)),
            ):
                obj = base.bpy.data.objects.new(name, None)
                obj.empty_display_type = "PLAIN_AXES"
                obj.empty_display_size = 0.25
                obj.location = location
                base.link_object(obj, collection)

        base.create_datums = create_datums
        return base

    frozen.load_base = load_base_compatible
    frozen.main()


if __name__ == "__main__":
    main()

