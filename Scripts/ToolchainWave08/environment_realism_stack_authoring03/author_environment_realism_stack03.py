"""Run the frozen Authoring02 geometry correction with an explicit UE Rotator binding."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring02/author_environment_realism_stack02.py"
EXPECTED_BYTES = 11473
EXPECTED_SHA256 = "116adb907c97d125ed349f2aa2d5b703ec6df6418df77a5b81bbe8622c9016fb"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
    raise RuntimeError("Frozen Authoring02 source authority changed")

transformed = SOURCE.read_text(encoding="utf-8")
replacements = (
    (
        'OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02"',
        'OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack03"',
    ),
    (
        'OUTPUT_FILE = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02.umap"',
        'OUTPUT_FILE = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack03.umap"',
    ),
    (
        'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING02/attempt_01"',
        'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING03/attempt_01"',
    ),
    (
        'sun.set_actor_rotation(unreal.Rotator(*TARGET_SUN_ROTATION), False)',
        'sun.set_actor_rotation(unreal.Rotator(roll=TARGET_SUN_ROTATION[2], pitch=TARGET_SUN_ROTATION[0], yaw=TARGET_SUN_ROTATION[1]), False)',
    ),
    (
        'result["lighting_after"] = {"sun_rotation": rotator(sun.get_actor_rotation()), "sun_intensity": float(sun_component.get_editor_property("intensity")), "skylight_intensity": float(sky_component.get_editor_property("intensity"))}',
        'result["lighting_after"] = {"sun_rotation": rotator(sun.get_actor_rotation()), "sun_intensity": float(sun_component.get_editor_property("intensity")), "skylight_intensity": float(sky_component.get_editor_property("intensity"))}\n    require(all(abs(actual - expected) <= 0.01 for actual, expected in zip(result["lighting_after"]["sun_rotation"], TARGET_SUN_ROTATION)), f"Sun rotation mismatch: {result[\'lighting_after\'][\'sun_rotation\']}")',
    ),
    (
        '"schema": "skyguard.m01-environment-realism-stack-authoring02.receipt.v1"',
        '"schema": "skyguard.m01-environment-realism-stack-authoring03.receipt.v1"',
    ),
    (
        'result["classification"] = "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_AUTOMATIC"',
        'result["classification"] = "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_AUTOMATIC"',
    ),
)

for old, new in replacements:
    if transformed.count(old) != 1:
        raise RuntimeError(f"Expected exactly one bounded transformation target: {old}")
    transformed = transformed.replace(old, new, 1)

if "Lvl_M01_T08_EnvironmentRealismStack02.umap" in transformed or "M01_ENVIRONMENT_REALISM_STACK_AUTHORING02/attempt_01" in transformed:
    raise RuntimeError("Authoring03 transformation retained a governed Authoring02 output namespace")

exec(compile(transformed, str(SOURCE) + "::authoring03", "exec"), {"__name__": "__main__"})
