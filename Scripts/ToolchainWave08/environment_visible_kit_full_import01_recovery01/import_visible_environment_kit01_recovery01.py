"""Bounded Recovery01 binding for the proven full-kit Unreal import logic."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_full_import01\import_visible_environment_kit01.py"
EXPECTED_ORIGINAL = "5db48b5f2862a6406b12534e85137f2a98021058816976f1f2e1f94d5191e3df"


def replace_exact(source: str, old: str, new: str, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} occurrences of {old!r}; found {actual}")
    return source.replace(old, new)


def build_transformed_source() -> str:
    raw = ORIGINAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ORIGINAL:
        raise RuntimeError("Frozen full-import source hash mismatch")
    source = raw.decode("utf-8")
    replacements = (
        (r"VisibleEnvironmentProductionReset01_UnrealReady02\exports", r"VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports"),
        ('DESTINATION = "/Game/ToolchainWave08/Environment/VisibleEnvironmentKit01"', 'DESTINATION = "/Game/M01/EnvKit02"'),
        (r'Content\ToolchainWave08\Environment\VisibleEnvironmentKit01"', r'Content\M01\EnvKit02"'),
        (r'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01"', r'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01\attempt_01"'),
        ('"SM_M01_Apartment_Production_A_CONSOLIDATED.glb": (45826976, "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080")', '"M01_APARTMENT_A.glb": (45826868, "62f117c58a9cbe02e57ffe7ebcdc4d1b7ad7401635ecc5ef0ad1f2f07281b33a")'),
        ('"SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb": (57221668, "7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a")', '"M01_COASTAL_DISTRICT_A.glb": (57221528, "7c42cd930495aa39ef58a4e7f80b02b2b3af7f345f5477bff3130fd0bd6d7b34")'),
        ('"SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb": (61796036, "6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8")', '"M01_CORNER_RESIDENCE_C.glb": (61795848, "809aeb6e36256279320ed7688e81f9f14eb4553b027a711c277309cda6e24702")'),
        ('"SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb": (35550616, "50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301")', '"M01_LIGHTHOUSE_A.glb": (35550508, "e0502f12494a031a1187ea85defa11ac8038910301cd0bb4bf743dca17f7ba0a")'),
        ('"SM_M01_Midrise_Production_B_CONSOLIDATED.glb": (62233232, "6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155")', '"M01_MIDRISE_B.glb": (62233124, "5d93c46206631953b8affacee6bb757ef7bab674476276df08b61ff684cbc794")'),
        ('"SM_M01_Apartment_Production_A_DETAILS"', '"SM_M01_ApartmentA_DETAILS"'),
        ('"SM_M01_Apartment_Production_A_GLAZING"', '"SM_M01_ApartmentA_GLAZING"'),
        ('"SM_M01_Apartment_Production_A_STRUCTURAL"', '"SM_M01_ApartmentA_STRUCTURAL"'),
        ('"SM_M01_CoastalDistrict_Production_A_HARDSCAPE"', '"SM_M01_CoastalA_HARDSCAPE"'),
        ('"SM_M01_CoastalDistrict_Production_A_TERRAIN"', '"SM_M01_CoastalA_TERRAIN"'),
        ('"SM_M01_CornerResidence_Production_C_DETAILS"', '"SM_M01_CornerC_DETAILS"'),
        ('"SM_M01_CornerResidence_Production_C_GLAZING"', '"SM_M01_CornerC_GLAZING"'),
        ('"SM_M01_CornerResidence_Production_C_STRUCTURAL"', '"SM_M01_CornerC_STRUCTURAL"'),
        ('"SM_M01_Lighthouse_Production_A_DETAILS"', '"SM_M01_LighthouseA_DETAILS"'),
        ('"SM_M01_Lighthouse_Production_A_GLAZING"', '"SM_M01_LighthouseA_GLAZING"'),
        ('"SM_M01_Lighthouse_Production_A_STRUCTURAL"', '"SM_M01_LighthouseA_STRUCTURAL"'),
        ('"SM_M01_Midrise_Production_B_DETAILS"', '"SM_M01_MidriseB_DETAILS"'),
        ('"SM_M01_Midrise_Production_B_GLAZING"', '"SM_M01_MidriseB_GLAZING"'),
        ('"SM_M01_Midrise_Production_B_STRUCTURAL"', '"SM_M01_MidriseB_STRUCTURAL"'),
        ("skyguard.m01-visible-environment-kit-full-import01.receipt.v1", "skyguard.m01-visible-environment-kit-full-import01-recovery01.receipt.v1"),
        ("PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_READY_FOR_REVERSIBLE_MAP_ASSEMBLY_DESIGN", "PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_RECOVERY01_READY_FOR_REVERSIBLE_MAP_ASSEMBLY"),
    )
    for old, new in replacements:
        source = replace_exact(source, old, new)
    forbidden = (
        "VisibleEnvironmentKit01",
        "M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\\attempt_01",
        "SM_M01_CoastalDistrict_Production_A_HARDSCAPE",
        "SM_M01_CornerResidence_Production_C_STRUCTURAL",
    )
    if any(token in source for token in forbidden):
        raise RuntimeError("Recovery01 transformed source retains a failed namespace or long identity")
    compile(source, str(ORIGINAL) + "::FullImportRecovery01Compile", "exec")
    return source


transformed = build_transformed_source()
namespace = {"__name__": "__main__", "__file__": str(Path(__file__))}
exec(compile(transformed, str(ORIGINAL) + "::FullImportRecovery01", "exec"), namespace, namespace)
