"""Recovery01 compatibility binding for Hero Street/Shore Cell01 authoring."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell01\author_m01_hero_street_shore_cell01.py"
)
BASE_BYTES = 23_887
BASE_SHA256 = "2a818d492c62e9c332e21314a737c92a212b6112c0316a66fff282a33767aed5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen failed Hero Street/Shore Cell01 author authority changed")

source = BASE.read_text(encoding="utf-8")
replacements = (
    ("/Game/M01/Lvl_M01_HeroStreetShoreCell01", "/Game/M01/Lvl_M01_HeroStreetShoreCell01_Recovery01"),
    ("Content/M01/Lvl_M01_HeroStreetShoreCell01.umap", "Content/M01/Lvl_M01_HeroStreetShoreCell01_Recovery01.umap"),
    ("Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01/attempt_01", "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01_RECOVERY01/attempt_01"),
    ('CELL_PREFIX = "M01_HSSC01_"', 'CELL_PREFIX = "M01_HSSC01R01_"'),
    ("lower_hemisphere_is_solid_color", "lower_hemisphere_is_black"),
    ("PASS_M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT", "PASS_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_AUTHORING_CONTRACT"),
    ("PASSED_M01_HERO_STREET_SHORE_CELL01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF", "PASSED_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"),
    ("skyguard.m01-hero-street-shore-cell01.authoring.v1", "skyguard.m01-hero-street-shore-cell01-recovery01.authoring.v1"),
)

for old, new in replacements:
    count = source.count(old)
    if count == 0:
        raise RuntimeError(f"Recovery01 author binding token absent: {old}")
    if old == "lower_hemisphere_is_solid_color" and count != 1:
        raise RuntimeError(f"Recovery01 compatibility token count changed: {count}")
    source = source.replace(old, new)

if "lower_hemisphere_is_solid_color" in source:
    raise RuntimeError("UE 5.8-incompatible SkyLight property survived Recovery01")

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(source, __file__ + "::bound", "exec"), namespace, namespace)
