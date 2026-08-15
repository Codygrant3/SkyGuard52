"""Complete bounded UE 5.8 property-binding correction for MapAssembly02."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_assembly02/author_visible_environment_kit_map_assembly02.py"
EXPECTED_ORIGINAL = "3c8d3f1f4d36193c4c24bcdec352a6bce56706f258e45e6c7d3b49bf0f5113f7"


def replace_exact(source: str, old: str, new: str, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} occurrences of {old!r}; found {actual}")
    return source.replace(old, new, count)


def build_transformed_source() -> str:
    raw = ORIGINAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ORIGINAL:
        raise RuntimeError("Frozen MapAssembly02 source hash mismatch")
    source = raw.decode("utf-8")
    replacements = (
        ('OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02"', 'OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_Recovery02"'),
        ('OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02.umap"', 'OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_Recovery02.umap"'),
        ('ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02/attempt_01"', 'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY02/attempt_01"'),
        ('slots = list(mesh.get_static_materials())', 'slots = list(mesh.get_editor_property("static_materials"))'),
        ('actor.static_mesh_component.get_static_mesh().get_path_name()', 'actor.static_mesh_component.get_editor_property("static_mesh").get_path_name()'),
        ('skyguard.m01-visible-environment-kit-map-assembly02.receipt.v1', 'skyguard.m01-visible-environment-kit-map-assembly02-recovery02.receipt.v1'),
        ('PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_AUTOMATIC', 'PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY02_AUTOMATIC'),
    )
    for old, new in replacements:
        source = replace_exact(source, old, new)
    forbidden = ('get_static_materials()', '.get_static_mesh()', 'Lvl_M01_VisibleEnvironmentKit02.umap"')
    if any(token in source for token in forbidden):
        raise RuntimeError("Recovery02 retained a failed UE 5.8 API or output namespace")
    return source


if __name__ == "__main__":
    transformed = build_transformed_source()
    compile(transformed, str(ORIGINAL) + "::MapAssembly02Recovery02", "exec")
    if "--offline-contract-test" in sys.argv:
        print("PASS_TRANSFORMED_SOURCE")
        raise SystemExit(0)
    namespace = {"__name__": "__main__", "__file__": str(Path(__file__))}
    exec(compile(transformed, str(ORIGINAL) + "::MapAssembly02Recovery02", "exec"), namespace, namespace)
