"""Verify the bounded MapAssembly02 Recovery01 source transformation."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_assembly02/author_visible_environment_kit_map_assembly02.py"
RECOVERY = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_assembly02_recovery01/author_visible_environment_kit_map_assembly02_recovery01.py"


def main() -> int:
    if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() != "3c8d3f1f4d36193c4c24bcdec352a6bce56706f258e45e6c7d3b49bf0f5113f7":
        raise RuntimeError("Original MapAssembly02 authority changed")
    text = RECOVERY.read_text(encoding="utf-8")
    ast.parse(text, filename=str(RECOVERY))
    spec = importlib.util.spec_from_file_location("map_assembly_recovery01", RECOVERY)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery01 source transformer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    transformed = module.build_transformed_source()
    compile(transformed, str(RECOVERY) + "::Transformed", "exec")
    required = (
        'get_editor_property("static_materials")',
        "Lvl_M01_VisibleEnvironmentKit02_Recovery01",
        "M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01/attempt_01",
        "PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01_AUTOMATIC",
    )
    if not all(token in transformed for token in required):
        raise RuntimeError("Recovery01 transformation is incomplete")
    if "get_static_materials()" in transformed:
        raise RuntimeError("Recovery01 retains the invalid UE 5.8 method")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
