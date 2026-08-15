from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/build_m01_visible_environment_kit_refinement01_stageb.py"
WRAPPER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stageb_recovery01/build_m01_visible_environment_kit_refinement01_stageb_recovery01.py"
BASE_BYTES = 37220
BASE_SHA256 = "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a"
OLD_TOKENS = (
    "    base = np.repeat(base, size, axis=1)\n",
    "    rough = np.repeat(rough, size, axis=1)\n",
)
NEW_TOKENS = (
    "    require(base.shape == (size, size, 3), f\"Base-color texture shape drift: {base.shape}\")\n",
    "    require(rough.shape == (size, size, 1), f\"Roughness texture shape drift: {rough.shape}\")\n",
)
SIZE = 2048
FLOAT_BYTES = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
        failures.append("frozen_stageb_source_mismatch")
    if not WRAPPER.is_file():
        failures.append("recovery_wrapper_missing")
    else:
        text = WRAPPER.read_text(encoding="utf-8")
        try:
            ast.parse(text, filename=str(WRAPPER))
        except SyntaxError as exc:
            failures.append(f"wrapper_syntax:{exc}")
        spec = importlib.util.spec_from_file_location("stageb_recovery01_verification_target", WRAPPER)
        if spec is None or spec.loader is None:
            failures.append("wrapper_import_spec_missing")
        else:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            declared = tuple(module.REPLACEMENTS)
            if tuple(item[0] for item in declared) != OLD_TOKENS:
                failures.append("old_token_contract_mismatch")
            if tuple(item[1] for item in declared) != NEW_TOKENS:
                failures.append("shape_assertion_contract_mismatch")
        if "replace(old_token, new_token, 1)" not in text:
            failures.append("bounded_replace_missing")
        if "geometry_render_export_receipt_changes\": 0" not in text:
            failures.append("behavioral_scope_receipt_missing")

    base_before_repeat_bytes = SIZE * SIZE * 3 * FLOAT_BYTES
    rough_before_repeat_bytes = SIZE * SIZE * FLOAT_BYTES
    base_after_old_repeat_bytes = SIZE * (SIZE * SIZE) * 3 * FLOAT_BYTES
    rough_after_old_repeat_bytes = SIZE * (SIZE * SIZE) * FLOAT_BYTES
    contracted_single_texture_bytes = SIZE * SIZE * 4 * FLOAT_BYTES
    if base_after_old_repeat_bytes != 103079215104:
        failures.append("base_old_repeat_projection_drift")
    if rough_after_old_repeat_bytes != 34359738368:
        failures.append("rough_old_repeat_projection_drift")
    if contracted_single_texture_bytes != 67108864:
        failures.append("contracted_texture_projection_drift")

    result = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb-recovery01.offline-verification.v1",
        "classification": "PASS" if not failures else "FAIL",
        "base_source": str(BASE),
        "base_bytes": BASE.stat().st_size if BASE.exists() else None,
        "base_sha256": sha256(BASE) if BASE.exists() else None,
        "wrapper": str(WRAPPER),
        "wrapper_bytes": WRAPPER.stat().st_size if WRAPPER.exists() else None,
        "wrapper_sha256": sha256(WRAPPER) if WRAPPER.exists() else None,
        "projected_bytes": {
            "base_before_redundant_repeat": base_before_repeat_bytes,
            "roughness_before_redundant_repeat": rough_before_repeat_bytes,
            "base_after_redundant_repeat": base_after_old_repeat_bytes,
            "roughness_after_redundant_repeat": rough_after_old_repeat_bytes,
            "largest_contracted_single_texture_array": contracted_single_texture_bytes,
        },
        "bounded_replacements": 2,
        "blender_launches": 0,
        "unreal_launches": 0,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
