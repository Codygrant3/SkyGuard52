"""Recovery02 UE 5.8 import re-probe with executable offline transformation validation."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_import_probe01\probe_visible_kit_import01.py"
EXPECTED_ORIGINAL = "20cf9b0fd2a2d8a9b60939b5b63a29527d66569d695b01c6dc9620b04d3d1955"


def replace_exact(source: str, old: str, new: str, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} occurrences of {old!r}; found {actual}")
    return source.replace(old, new)


def build_transformed_source() -> str:
    raw = ORIGINAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ORIGINAL:
        raise RuntimeError("Frozen ImportProbe01 source hash mismatch")
    source = raw.decode("utf-8")
    source = replace_exact(
        source,
        r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb",
        r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\exports\SM_M01_Apartment_Production_A_UNREAL_READY.glb",
    )
    source = replace_exact(source, 'DESTINATION = "/Game/ToolchainWave08/Environment/VisibleKitImportProbe01"', 'DESTINATION = "/Game/ToolchainWave08/Environment/VisibleKitImportReprobe02"')
    source = replace_exact(source, r'Content\ToolchainWave08\Environment\VisibleKitImportProbe01"', r'Content\ToolchainWave08\Environment\VisibleKitImportReprobe02"')
    source = replace_exact(source, r'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01\attempt_01"', r'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02\attempt_01"')
    source = replace_exact(source, 'SOURCE_BYTES = 45451472', 'SOURCE_BYTES = 23710548')
    source = replace_exact(source, 'SOURCE_SHA256 = "5c09c9eb7bf17057ec277b958165005e71e3ecac6a9430df47eddeceab9a7849"', 'SOURCE_SHA256 = "c1ecb14007710c4aaa4dd0c363177cba6ea4411eeeae495b56ca2e89a0f5e09a"')
    source = replace_exact(source, 'skyguard.m01-visible-environment-kit-import-probe01.receipt.v1', 'skyguard.m01-visible-environment-kit-import-reprobe02.receipt.v1')
    source = replace_exact(source, 'require(static_mesh_count >= 1, "Interchange import produced no StaticMesh assets")', 'require(2 <= static_mesh_count <= 4, f"Consolidated StaticMesh budget failed: {static_mesh_count}")')
    source = replace_exact(
        source,
        'PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN',
        'PASSED_CONSOLIDATED_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT_DESIGN',
        count=1,
    )
    source = replace_exact(source, 'Accepted apartment GLB authority changed', 'Metadata-normalized apartment GLB authority changed')
    return source


def offline_contract_test() -> int:
    source = build_transformed_source()
    compile(source, str(ORIGINAL) + "::ImportReprobe02Offline", "exec")
    required = (
        "VisibleKitImportReprobe02",
        "M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02",
        "2 <= static_mesh_count <= 4",
        "PASSED_CONSOLIDATED_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT_DESIGN",
    )
    if not all(token in source for token in required):
        raise RuntimeError("Recovery02 transformed source is incomplete")
    if "VisibleKitImportProbe01" in source or "M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01" in source:
        raise RuntimeError("Recovery02 transformed source retains an old governed namespace")
    print("PASS_TRANSFORMATION_COMPILE")
    return 0


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

transformed = build_transformed_source()
code = compile(transformed, str(ORIGINAL) + "::ImportReprobe02", "exec")
namespace = {"__name__": "__main__", "__file__": str(ORIGINAL)}
exec(code, namespace, namespace)
