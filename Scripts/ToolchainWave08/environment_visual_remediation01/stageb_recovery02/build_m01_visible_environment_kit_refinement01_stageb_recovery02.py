from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_RECOVERY02"
BASE_SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stageb.py")
BASE_BYTES = 37220
BASE_SHA256 = "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a"
STAGEA_RECOVERY02_WRAPPER = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery02\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py")
STAGEA_RECOVERY02_WRAPPER_BYTES = 6111
STAGEA_RECOVERY02_WRAPPER_SHA256 = "ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61"
CORRECTED_STAGEA_HELPER_BYTES = 42844
CORRECTED_STAGEA_HELPER_SHA256 = "f2e260121feca175b62464883ae1933f25c5a02eb5fd538ddd946dd6149a800d"

MEMORY_REPLACEMENTS = (
    (
        "    base = np.repeat(base, size, axis=1)\n",
        "    require(base.shape == (size, size, 3), f\"Base-color texture shape drift: {base.shape}\")\n",
    ),
    (
        "    rough = np.repeat(rough, size, axis=1)\n",
        "    require(rough.shape == (size, size, 1), f\"Roughness texture shape drift: {rough.shape}\")\n",
    ),
)
OLD_HELPER_BLOCK = '''STAGEA_HELPER = Path(
    r"D:\\Skyguard52\\Scripts\\ToolchainWave08\\environment_visual_remediation01\\build_m01_visible_environment_kit_refinement01_stagea.py"
)
STAGEA_HELPER_SHA256 = "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12"
'''


def require(value, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive_stagea_helper() -> tuple[str, dict[str, object]]:
    raw = STAGEA_RECOVERY02_WRAPPER.read_bytes()
    require(len(raw) == STAGEA_RECOVERY02_WRAPPER_BYTES, "StageA Recovery02 wrapper byte mismatch")
    require(sha256_bytes(raw) == STAGEA_RECOVERY02_WRAPPER_SHA256, "StageA Recovery02 wrapper hash mismatch")
    spec = importlib.util.spec_from_file_location("skyguard_stagea_recovery02_derivation", STAGEA_RECOVERY02_WRAPPER)
    require(spec is not None and spec.loader is not None, "Unable to load StageA Recovery02 derivation module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, "load_bounded_source", None)
    require(callable(function), "StageA Recovery02 derivation function is unavailable")
    corrected, upstream_receipt = function()
    encoded = corrected.encode("utf-8")
    require(len(encoded) == CORRECTED_STAGEA_HELPER_BYTES, "Corrected StageA helper byte mismatch")
    require(sha256_bytes(encoded) == CORRECTED_STAGEA_HELPER_SHA256, "Corrected StageA helper hash mismatch")
    require("Saved render is missing or empty" in corrected, "Saved-PNG measurement correction is absent")
    require('bpy.data.images.get("Render Result")' not in corrected, "Empty Render Result path remains in corrected helper")
    return corrected, upstream_receipt


def derive_stageb_source(helper_path: Path) -> tuple[str, dict[str, object]]:
    raw = BASE_SOURCE.read_bytes()
    require(len(raw) == BASE_BYTES, "Frozen StageB source byte mismatch")
    require(sha256_bytes(raw) == BASE_SHA256, "Frozen StageB source hash mismatch")
    corrected = raw.decode("utf-8")
    changes: list[dict[str, object]] = []
    for old, new in MEMORY_REPLACEMENTS:
        count = corrected.count(old)
        require(count == 1, f"StageB memory-fix token cardinality differs: {old.strip()} => {count}")
        corrected = corrected.replace(old, new, 1)
        require(old not in corrected and corrected.count(new) == 1, "StageB memory fix did not apply exactly once")
        changes.append({"removed": old.strip(), "added": new.strip()})
    require(corrected.count(OLD_HELPER_BLOCK) == 1, "StageB helper authority block cardinality differs")
    new_helper_block = (
        f'STAGEA_HELPER = Path(r"{helper_path}")\n'
        f'STAGEA_HELPER_SHA256 = "{CORRECTED_STAGEA_HELPER_SHA256}"\n'
    )
    corrected = corrected.replace(OLD_HELPER_BLOCK, new_helper_block, 1)
    require(OLD_HELPER_BLOCK not in corrected and corrected.count(new_helper_block) == 1, "StageB corrected helper binding did not apply exactly once")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb-recovery02.in-memory-patch.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "stagea_recovery02_wrapper": str(STAGEA_RECOVERY02_WRAPPER),
        "stagea_recovery02_wrapper_sha256": STAGEA_RECOVERY02_WRAPPER_SHA256,
        "corrected_stagea_helper": str(helper_path),
        "corrected_stagea_helper_bytes": CORRECTED_STAGEA_HELPER_BYTES,
        "corrected_stagea_helper_sha256": CORRECTED_STAGEA_HELPER_SHA256,
        "memory_replacements": changes,
        "helper_binding_replacements": 1,
        "geometry_material_camera_render_export_receipt_changes": 0,
        "passed": True,
    }
    return corrected, receipt


def main() -> int:
    wrapper_path = Path(__file__).resolve()
    helper_path = wrapper_path.with_name("build_m01_visible_environment_kit_refinement01_stagea_recovery02_helper.py")
    require(not helper_path.exists(), f"Generated StageA helper already exists: {helper_path}")
    helper_text, upstream_receipt = derive_stagea_helper()
    with helper_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(helper_text)
    require(helper_path.stat().st_size == CORRECTED_STAGEA_HELPER_BYTES, "Written StageA helper byte mismatch")
    require(sha256_bytes(helper_path.read_bytes()) == CORRECTED_STAGEA_HELPER_SHA256, "Written StageA helper hash mismatch")
    corrected, receipt = derive_stageb_source(helper_path)
    receipt["stagea_upstream_receipt"] = upstream_receipt
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stageb_recovery02_embedded",
        "__file__": str(wrapper_path),
        "__package__": None,
    }
    exec(compile(corrected, str(wrapper_path), "exec"), namespace)
    embedded_main = namespace.get("main")
    require(callable(embedded_main), "Frozen StageB main() was not recovered")
    return int(embedded_main())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": GATE, "status": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True), file=sys.stderr)
        raise
