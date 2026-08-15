"""Derive the bounded Cell03 Recovery01 sources from immutable Attempt01 sources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03/author_m01_hero_street_shore_cell03.py"
ORIGINAL_SUPERVISOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03/invoke_m01_hero_street_shore_cell03_once.py"
OUTPUT = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03_recovery01/author_m01_hero_street_shore_cell03_recovery01.py"
OUTPUT_SUPERVISOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03_recovery01/invoke_m01_hero_street_shore_cell03_recovery01_once.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_exact(text: str, old: str, new: str, count: int) -> str:
    require(text.count(old) == count, f"Expected {count} occurrences of {old!r}; found {text.count(old)}")
    return text.replace(old, new)


def main() -> int:
    require(ORIGINAL.stat().st_size == 33298 and sha256(ORIGINAL) == "7274a19dc4197cf6c941cec3ce8b13ba9dd99ebaa79fc5f18dfe3af516c6f712", "Attempt01 author authority changed")
    require(ORIGINAL_SUPERVISOR.stat().st_size == 12497 and sha256(ORIGINAL_SUPERVISOR) == "f0a09c8c1abcfa3bed1807721361d7a500f34567b0ad7e10273eb76a46b07838", "Attempt01 supervisor authority changed")
    require(not OUTPUT.exists() and not OUTPUT_SUPERVISOR.exists(), "Recovery01 source namespace is not fresh")

    author = ORIGINAL.read_text(encoding="utf-8")
    author = replace_exact(author, 'OUTPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell03"', 'OUTPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell03Recovery01"', 1)
    author = replace_exact(author, 'OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03.umap"', 'OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03Recovery01.umap"', 1)
    author = replace_exact(author, 'MATERIAL_ROOT = "/Game/M01/HeroStreetShoreCell03/Materials"', 'MATERIAL_ROOT = "/Game/M01/HeroStreetShoreCell03Recovery01/Materials"', 1)
    author = replace_exact(author, 'MATERIAL_DIRECTORY = ISOLATED / "Content/M01/HeroStreetShoreCell03"', 'MATERIAL_DIRECTORY = ISOLATED / "Content/M01/HeroStreetShoreCell03Recovery01"', 1)
    author = replace_exact(author, 'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL03/attempt_01"', 'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL03_RECOVERY01/attempt_01"', 1)
    author = replace_exact(author, '"PASS_M01_HERO_STREET_SHORE_CELL03_AUTHORING_CONTRACT"', '"PASS_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_AUTHORING_CONTRACT"', 1)
    author = replace_exact(author, '"schema": "skyguard.m01-hero-street-shore-cell03.authoring.v1"', '"schema": "skyguard.m01-hero-street-shore-cell03-recovery01.authoring.v1"', 1)
    author = replace_exact(author, '"PASSED_M01_HERO_STREET_SHORE_CELL03_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"', '"PASSED_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"', 1)
    author = replace_exact(author, 'ISOLATED / "Content/M01/HeroStreetShoreCell03/Materials/MI_M01_Cell03_Asphalt_Tiled.uasset"', 'ISOLATED / "Content/M01/HeroStreetShoreCell03Recovery01/Materials/MI_M01_Cell03_Asphalt_Tiled.uasset"', 1)
    old_setter = '''        for parameter in ASPHALT_PARAMETERS:\n            success = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(\n                asphalt, parameter, unreal.LinearColor(*TARGET_ASPHALT_TILING)\n            )\n            require(bool(success), f"Failed to set asphalt tiling parameter: {parameter}")\n        unreal.MaterialEditingLibrary.update_material_instance(asphalt)'''
    new_setter = '''        setter_evidence = []\n        for parameter in ASPHALT_PARAMETERS:\n            reported_return = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(\n                asphalt, parameter, unreal.LinearColor(*TARGET_ASPHALT_TILING)\n            )\n            actual_color = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(asphalt, parameter)\n            actual = rgba(actual_color)\n            require(\n                len(actual) == 4 and all(abs(a - b) <= 0.0005 for a, b in zip(actual, TARGET_ASPHALT_TILING)),\n                f"Asphalt tiling readback mismatch: {parameter}: {actual} != {TARGET_ASPHALT_TILING}",\n            )\n            setter_evidence.append({\n                "parameter": parameter,\n                "known_invalid_ue58_boolean_return": bool(reported_return),\n                "readback": actual,\n                "accepted_by_readback": True,\n            })\n        result["asphalt_parameter_readback"] = setter_evidence\n        unreal.MaterialEditingLibrary.update_material_instance(asphalt)'''
    author = replace_exact(author, old_setter, new_setter, 1)
    author = replace_exact(author, '"created_materials": [],', '"created_materials": [],\n        "asphalt_parameter_readback": [],', 1)
    compile(author, str(OUTPUT), "exec")

    supervisor = ORIGINAL_SUPERVISOR.read_text(encoding="utf-8")
    supervisor = replace_exact(supervisor, 'AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03/author_m01_hero_street_shore_cell03.py"', 'AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell03_recovery01/author_m01_hero_street_shore_cell03_recovery01.py"', 1)
    supervisor = replace_exact(supervisor, 'OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03.umap"', 'OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03Recovery01.umap"', 1)
    supervisor = replace_exact(supervisor, 'MATERIAL_DIRECTORY = ISOLATED / "Content/M01/HeroStreetShoreCell03"', 'MATERIAL_DIRECTORY = ISOLATED / "Content/M01/HeroStreetShoreCell03Recovery01"', 1)
    supervisor = replace_exact(supervisor, 'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL03/attempt_01"', 'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL03_RECOVERY01/attempt_01"', 1)
    supervisor = replace_exact(supervisor, 'TERMINAL = ROOT / "Saved/Reports/M01_HERO_STREET_SHORE_CELL03_TERMINAL_SUPERVISOR.json"', 'TERMINAL = ROOT / "Saved/Reports/M01_HERO_STREET_SHORE_CELL03_RECOVERY01_TERMINAL_SUPERVISOR.json"', 1)
    supervisor = replace_exact(supervisor, 'PASS_M01_HERO_STREET_SHORE_CELL03_AUTHORING_CONTRACT', 'PASS_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_AUTHORING_CONTRACT', 2)
    supervisor = replace_exact(supervisor, 'PASSED_M01_HERO_STREET_SHORE_CELL03_READY_FOR_D3D12_MAPPED_VISUAL_PROOF', 'PASSED_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF', 1)
    supervisor = replace_exact(supervisor, '"schema": "skyguard.m01-hero-street-shore-cell03.supervisor.v1"', '"schema": "skyguard.m01-hero-street-shore-cell03-recovery01.supervisor.v1"', 1)
    compile(supervisor, str(OUTPUT_SUPERVISOR), "exec")

    OUTPUT.write_text(author, encoding="utf-8")
    OUTPUT_SUPERVISOR.write_text(supervisor, encoding="utf-8")
    print(json.dumps({
        "author": {"path": str(OUTPUT), "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
        "supervisor": {"path": str(OUTPUT_SUPERVISOR), "bytes": OUTPUT_SUPERVISOR.stat().st_size, "sha256": sha256(OUTPUT_SUPERVISOR)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
