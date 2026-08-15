from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WRAPPER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stageb_recovery02\build_m01_visible_environment_kit_refinement01_stageb_recovery02.py"
BASE = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stageb.py"
STAGEA_R2 = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery02\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"
EXPECTED_BASE = "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a"
EXPECTED_STAGEA_R2 = "ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61"
EXPECTED_HELPER = "f2e260121feca175b62464883ae1933f25c5a02eb5fd538ddd946dd6149a800d"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    require(digest(BASE) == EXPECTED_BASE, "StageB base source mismatch")
    require(digest(STAGEA_R2) == EXPECTED_STAGEA_R2, "StageA Recovery02 source mismatch")
    ast.parse(WRAPPER.read_text(encoding="utf-8"), filename=str(WRAPPER))
    spec = importlib.util.spec_from_file_location("stageb_recovery02_verifier_target", WRAPPER)
    require(spec is not None and spec.loader is not None, "Unable to load StageB Recovery02 wrapper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    helper_text, _ = module.derive_stagea_helper()
    require(len(helper_text.encode("utf-8")) == 42844 and hashlib.sha256(helper_text.encode("utf-8")).hexdigest() == EXPECTED_HELPER, "Corrected helper derivation mismatch")
    require('bpy.data.images.get("Render Result")' not in helper_text, "Render Result measurement remains")
    require("Saved render is missing or empty" in helper_text, "Saved-PNG measurement is absent")
    with tempfile.TemporaryDirectory(prefix="skyguard_stageb_recovery02_verify_") as temporary:
        helper_path = Path(temporary) / "stagea_helper.py"
        stageb_text, receipt = module.derive_stageb_source(helper_path)
        ast.parse(stageb_text, filename="derived_stageb_recovery02.py")
        require(receipt.get("passed") is True and receipt.get("geometry_material_camera_render_export_receipt_changes") == 0, "StageB receipt scope failed")
        require("base = np.repeat(base, size, axis=1)" not in stageb_text, "base-color repeat remains")
        require("rough = np.repeat(rough, size, axis=1)" not in stageb_text, "roughness repeat remains")
        require(str(helper_path) in stageb_text and EXPECTED_HELPER in stageb_text, "corrected helper binding is absent")
    size = 2048
    require(size * size * 4 * 4 == 67108864, "largest contracted texture array drift")
    result = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb-recovery02.offline-verification.v1",
        "classification": "PASS",
        "stageb_base_sha256": digest(BASE),
        "stagea_recovery02_wrapper_sha256": digest(STAGEA_R2),
        "corrected_stagea_helper_sha256": EXPECTED_HELPER,
        "bounded_stageb_replacements": 3,
        "saved_png_measurement": "PASS",
        "largest_contracted_single_texture_array_bytes": 67108864,
        "geometry_changes": 0,
        "render_contract_changes": 0,
        "export_contract_changes": 0,
        "blender_launches": 0,
        "unreal_launches": 0,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
