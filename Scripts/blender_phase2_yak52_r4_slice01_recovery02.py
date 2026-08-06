"""Recovery02 entrypoint for Yak-52 R4 Slice 01.

Recovery01 is terminal and immutable. This distinct namespace retains the
frozen authoring implementation but replaces its Blender-5.2-incompatible
datum empty display enum ``CROSS`` with the supported, semantically equivalent
axis datum display ``PLAIN_AXES``.

Importing or compiling this module creates no output.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY02"
DATUM_EMPTY_DISPLAY_TYPE = "PLAIN_AXES"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
FROZEN_SOURCE_PATH = ROOT / "Scripts/blender_phase2_yak52_r4_slice01_silhouette.py"
OUTPUT_CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY02_OUTPUT_CONTRACT.json"
)
DIMENSION_LEDGER_PATH = ROOT / (
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_DIMENSION_LEDGER.json"
)
CAMERA_MANIFEST_PATH = ROOT / (
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_CAMERA_MANIFEST.json"
)
R4_CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/PHASE2_YAK52_R4_OFFLINE_PRODUCTION_CONTRACT.json"
)
OUTPUT_DIR = ROOT / (
    "Content/Skyguard/Meshes/Source/Mission01/"
    "Yak52_FinalArt_R4/Slice01_Recovery02"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY02_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_final_art_r4_s01_recovery02.glb"
MANIFEST_PATH = ROOT / (
    "Saved/Reports/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY02_MANIFEST.json"
)
SCREENSHOT_DIR = ROOT / (
    "Saved/Screenshots/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY02"
)
FROZEN_CONTRACT_KEY_PATHS = (
    "build_id",
    "authority_inputs",
    "authority_inputs[]",
    "authority_inputs[].path",
    "authority_inputs[].bytes",
    "authority_inputs[].sha256",
    "authoring_script",
    "authoring_script.sha256",
    "outputs",
    "outputs.blend",
    "outputs.glb",
    "outputs.manifest",
    "outputs.comparison_directory",
    "claims",
    "claims.silhouette_locked",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def require_contract_path(contract: dict[str, Any], key_path: str) -> None:
    current: Any = contract
    parts = key_path.split(".")
    for index, part in enumerate(parts):
        if part.endswith("[]"):
            key = part[:-2]
            if not isinstance(current, dict) or key not in current:
                raise RuntimeError(f"Recovery02 contract path missing: {key_path}")
            current = current[key]
            if not isinstance(current, list) or not current:
                raise RuntimeError(f"Recovery02 contract list empty: {key_path}")
            remainder = ".".join(parts[index + 1 :])
            if remainder:
                for item in current:
                    if not isinstance(item, dict):
                        raise RuntimeError(f"Recovery02 contract item invalid: {key_path}")
                    require_contract_path(item, remainder)
            return
        if not isinstance(current, dict) or part not in current:
            raise RuntimeError(f"Recovery02 contract path missing: {key_path}")
        current = current[part]


def prove_contract_accesses(contract: dict[str, Any]) -> None:
    for key_path in FROZEN_CONTRACT_KEY_PATHS:
        require_contract_path(contract, key_path)
    policy = contract["output_policy"]["paths"]
    expected = {
        "blend": policy["blend"],
        "glb": policy["glb"],
        "manifest": policy["manifest"],
        "comparison_directory": policy["screenshot_directory"],
    }
    if contract["outputs"] != expected:
        raise RuntimeError("Recovery02 output alias and policy paths disagree")
    if contract["build_id"] != BUILD_ID:
        raise RuntimeError("Recovery02 build id mismatch")


def load_frozen_source() -> Any:
    spec = importlib.util.spec_from_file_location(
        "skyguard_phase2_slice01_frozen_recovery02", FROZEN_SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load frozen Slice 01 source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_datums_blender52(
    frozen: Any, collection: Any, overall_length: float
) -> None:
    half_length = overall_length / 2.0
    for name, location in (
        ("DATUM_R4S01_AircraftOrigin", (0.0, 0.0, 0.0)),
        ("DATUM_R4S01_TailExtreme", (-half_length, 0.0, 0.34)),
        ("DATUM_R4S01_PropellerPlane", (half_length, 0.0, 0.13)),
        ("DATUM_R4S01_WingReference", (0.0, 0.0, 0.0)),
    ):
        obj = frozen.bpy.data.objects.new(name, None)
        obj.empty_display_type = DATUM_EMPTY_DISPLAY_TYPE
        obj.empty_display_size = 0.25
        obj.location = location
        frozen.link_object(obj, collection)


def configure_recovery_namespace(frozen: Any) -> None:
    frozen.BUILD_ID = BUILD_ID
    frozen.OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_PATH
    frozen.DIMENSION_LEDGER_PATH = DIMENSION_LEDGER_PATH
    frozen.CAMERA_MANIFEST_PATH = CAMERA_MANIFEST_PATH
    frozen.R4_CONTRACT_PATH = R4_CONTRACT_PATH
    frozen.SCRIPT_PATH = SCRIPT_PATH
    frozen.OUTPUT_DIR = OUTPUT_DIR
    frozen.BLEND_PATH = BLEND_PATH
    frozen.GLB_PATH = GLB_PATH
    frozen.MANIFEST_PATH = MANIFEST_PATH
    frozen.SCREENSHOT_DIR = SCREENSHOT_DIR
    frozen.create_datums = (
        lambda collection, overall_length: create_datums_blender52(
            frozen, collection, overall_length
        )
    )


def main() -> None:
    contract = read_json(OUTPUT_CONTRACT_PATH)
    prove_contract_accesses(contract)
    frozen = load_frozen_source()
    configure_recovery_namespace(frozen)
    frozen.main()


if __name__ == "__main__":
    main()
