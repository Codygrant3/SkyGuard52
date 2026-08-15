"""Material-preserving postflight derived from frozen UnrealReady01 adjudicator."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\adjudicate_visible_environment_unreal_ready01.py"
EXPECTED_SOURCE = "8285d3e8640ed286618f2b37241e56445949b836c1d6dac9c5873e6269876262"


def replace_exact(source: str, old: str, new: str, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} occurrences of {old!r}; found {actual}")
    return source.replace(old, new)


def build_transformed_source() -> str:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE:
        raise RuntimeError("Frozen UnrealReady01 adjudicator hash mismatch")
    source = raw.decode("utf-8")
    source = source.replace("VisibleEnvironmentProductionReset01_UnrealReady01", "VisibleEnvironmentProductionReset01_UnrealReady02")
    source = source.replace("M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_POSTFLIGHT", "M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_POSTFLIGHT")
    source = source.replace("unreal-ready01", "unreal-ready02")
    source = source.replace("UNREAL_READY01.blend", "UNREAL_READY02.blend")
    source = replace_exact(
        source,
        'EXCLUDED = ("_WATER", "_FOAM_", "_WET_CONTACT", "_LEAF_", "_PLANT_", "_TRUNK", "_BRANCH_", "_TREE_", "_SHRUB_", "_FOLIAGE_")\n',
        'EXCLUDED = ("_WATER", "_FOAM_", "_WET_CONTACT", "_LEAF_", "_PLANT_", "_TRUNK", "_BRANCH_", "_TREE_", "_SHRUB_", "_FOLIAGE_")\n'
        'MIN_MATERIALS = {\n'
        '    "SM_M01_Apartment_Production_A": 8,\n'
        '    "SM_M01_Midrise_Production_B": 9,\n'
        '    "SM_M01_CornerResidence_Production_C": 9,\n'
        '    "SM_M01_CoastalDistrict_Production_A": 5,\n'
        '    "SM_M01_Lighthouse_Production_A": 4,\n'
        '}\n',
    )
    source = replace_exact(
        source,
        '            if item["uv_layer_count"] < 1:\n                raise RuntimeError(f"UV layer missing for {asset}:{item[\'group\']}")\n',
        '            if item["group"] != "TERRAIN" and item["uv_layer_count"] < 1:\n'
        '                raise RuntimeError(f"UV layer missing for {asset}:{item[\'group\']}")\n'
        '            if len(item.get("material_names", [])) != item["material_slot_count"]:\n'
        '                raise RuntimeError(f"Material-name receipt mismatch for {asset}:{item[\'group\']}")\n',
    )
    source = replace_exact(
        source,
        '        checks.append({\n',
        '        if len(doc.get("materials", [])) < MIN_MATERIALS[asset]:\n'
        '            raise RuntimeError(f"Material-family preservation failed for {asset}: {len(doc.get(\'materials\', []))}")\n'
        '        checks.append({\n',
    )
    return source


def offline_contract_test() -> int:
    source = build_transformed_source()
    compile(source, str(SOURCE) + "::UnrealReady02PostflightOffline", "exec")
    required = ("MIN_MATERIALS", 'item["group"] != "TERRAIN"', "Material-family preservation failed", "UNREAL_READY02_POSTFLIGHT")
    if not all(token in source for token in required):
        raise RuntimeError("UnrealReady02 postflight transformation incomplete")
    print("PASS_TRANSFORMATION_COMPILE")
    return 0


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

transformed = build_transformed_source()
code = compile(transformed, str(SOURCE) + "::UnrealReady02Postflight", "exec")
namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(code, namespace, namespace)
