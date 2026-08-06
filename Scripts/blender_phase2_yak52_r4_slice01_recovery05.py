"""Recovery05 Blender 5.2 compatibility entrypoint.

This module is import-side-effect free. It preserves the frozen Slice01 source
and replaces only the three proven Blender 5.2 compatibility boundaries plus
the exporter-added temporary ``.glb`` extension.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY05"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
FROZEN = ROOT / "Scripts/blender_phase2_yak52_r4_slice01_silhouette.py"
CONTRACT = (
    ROOT
    / "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY05_OUTPUT_CONTRACT.json"
)
OUTPUT_DIR = (
    ROOT
    / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R4/"
    "Slice01_Recovery05"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY05_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_final_art_r4_s01_recovery05.glb"
MANIFEST_PATH = (
    ROOT / "Saved/Reports/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY05_MANIFEST.json"
)
SCREENSHOT_DIR = (
    ROOT / "Saved/Screenshots/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY05"
)


def load_frozen() -> Any:
    spec = importlib.util.spec_from_file_location(
        "skyguard_slice01_frozen_recovery05", FROZEN
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Frozen Slice01 source could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_datums(module: Any, collection: Any, overall_length: float) -> None:
    half_length = overall_length / 2.0
    datums = (
        ("DATUM_R4S01_AircraftOrigin", (0.0, 0.0, 0.0)),
        ("DATUM_R4S01_TailExtreme", (-half_length, 0.0, 0.34)),
        ("DATUM_R4S01_PropellerPlane", (half_length, 0.0, 0.13)),
        ("DATUM_R4S01_WingReference", (0.0, 0.0, 0.0)),
    )
    for name, location in datums:
        obj = module.bpy.data.objects.new(name, None)
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.25
        obj.location = location
        module.link_object(obj, collection)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    for key in ("build_id", "authority_inputs", "authoring_script", "outputs", "claims"):
        if key not in contract:
            raise RuntimeError(f"Recovery05 contract missing {key}")

    module = load_frozen()
    module.BUILD_ID = BUILD_ID
    module.OUTPUT_CONTRACT_PATH = CONTRACT
    module.SCRIPT_PATH = SCRIPT_PATH
    module.OUTPUT_DIR = OUTPUT_DIR
    module.BLEND_PATH = BLEND_PATH
    module.GLB_PATH = GLB_PATH
    module.MANIFEST_PATH = MANIFEST_PATH
    module.SCREENSHOT_DIR = SCREENSHOT_DIR
    module.create_datums = lambda collection, length: create_datums(
        module, collection, length
    )

    frozen_configure_render = module.configure_render

    def configure_render(camera_manifest: dict[str, Any]) -> None:
        patched = copy.deepcopy(camera_manifest)
        if patched["render_contract"]["engine"] != "BLENDER_EEVEE_NEXT":
            raise RuntimeError("Unexpected frozen render-engine token")
        patched["render_contract"]["engine"] = "BLENDER_EEVEE"
        scene = module.bpy.context.scene
        if scene.world is None:
            scene.world = module.bpy.data.worlds.new("WORLD_R4S01_Recovery05")
        frozen_configure_render(patched)

    frozen_export_glb = module.export_glb

    def export_glb(primary_collection: Any, requested_temp_path: Path) -> None:
        frozen_export_glb(primary_collection, requested_temp_path)
        appended_path = Path(str(requested_temp_path) + ".glb")
        if not requested_temp_path.is_file() and appended_path.is_file():
            appended_path.replace(requested_temp_path)
        if not requested_temp_path.is_file():
            raise RuntimeError(
                "Blender GLB export did not produce the requested temporary file"
            )

    module.configure_render = configure_render
    module.export_glb = export_glb
    module.main()


if __name__ == "__main__":
    main()
