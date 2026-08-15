"""Recovery01 one-shot supervisor binding for Hero Street/Shore Cell01."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell01\invoke_m01_hero_street_shore_cell01_once.py"
)
BASE_BYTES = 5_068
BASE_SHA256 = "6f8b76021fcae58898cb455938c053cbea58d5c5a2b60da5b10a615f3fc3829e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen failed Cell01 supervisor authority changed")

source = BASE.read_text(encoding="utf-8")
replacements = (
    ("m01_hero_street_shore_cell01/author_m01_hero_street_shore_cell01.py", "m01_hero_street_shore_cell01_recovery01/author_m01_hero_street_shore_cell01_recovery01.py"),
    ("AUTHOR_BYTES = 23_887", "AUTHOR_BYTES = 2_396"),
    ("AUTHOR_SHA256 = \"2a818d492c62e9c332e21314a737c92a212b6112c0316a66fff282a33767aed5\"", "AUTHOR_SHA256 = \"29df815ce2184025fe4a5f9bddfd563c7fdcc7610930dc69457509986630f96f\""),
    ("Lvl_M01_HeroStreetShoreCell01.umap", "Lvl_M01_HeroStreetShoreCell01_Recovery01.umap"),
    ("M01_HERO_STREET_SHORE_CELL01/attempt_01", "M01_HERO_STREET_SHORE_CELL01_RECOVERY01/attempt_01"),
    ("M01_HERO_STREET_SHORE_CELL01_TERMINAL_SUPERVISOR", "M01_HERO_STREET_SHORE_CELL01_RECOVERY01_TERMINAL_SUPERVISOR"),
    ("PASS_M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT", "PASS_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_AUTHORING_CONTRACT"),
    ("PASS_M01_HERO_STREET_SHORE_CELL01_SUPERVISOR_OFFLINE_CONTRACT", "PASS_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_SUPERVISOR_OFFLINE_CONTRACT"),
    ("PASSED_M01_HERO_STREET_SHORE_CELL01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF", "PASSED_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"),
    ("skyguard.m01-hero-street-shore-cell01.supervisor.v1", "skyguard.m01-hero-street-shore-cell01-recovery01.supervisor.v1"),
    ("freeze one focused Hero Street/Shore Cell01 D3D12 mapped visual proof", "freeze one focused Hero Street/Shore Cell01 Recovery01 D3D12 mapped visual proof"),
)

for old, new in replacements:
    if old not in source:
        raise RuntimeError(f"Recovery01 supervisor binding token absent: {old}")
    source = source.replace(old, new)

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(source, __file__ + "::bound", "exec"), namespace, namespace)
