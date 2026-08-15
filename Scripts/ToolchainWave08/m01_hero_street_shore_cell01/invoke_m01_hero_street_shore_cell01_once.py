"""One-shot supervisor binding for Mission 1 Hero Street/Shore Cell01.

The proven Assembly03 supervisor lifecycle is reused byte-for-byte, then
bound to a fresh author, map and evidence namespace.  No retry path exists.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_accepted_candidate_assembly03\invoke_m01_accepted_candidate_assembly03_once.py"
)
BASE_BYTES = 12_561
BASE_SHA256 = "f526c03dc0f822054713e2e6796254623cb1e339068a7bd358cdc9b595787838"
AUTHOR_BYTES = 23_887
AUTHOR_SHA256 = "2a818d492c62e9c332e21314a737c92a212b6112c0316a66fff282a33767aed5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen Assembly03 supervisor lifecycle authority changed")

source = BASE.read_text(encoding="utf-8")

old_input = '''INPUT_MAP = ISOLATED / (
    "Content/M01/"
    "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_"
    "PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_"
    "StormDrains01_LitterBins01.umap"
)
INPUT_MAP_BYTES = 813_648
INPUT_MAP_SHA256 = "3bc0fdb85429de7cd471a1ba5d305caab9d8e6f554e52d4f7cf4ef138c741ce2"'''
new_input = '''INPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_AcceptedCandidateAssembly03_Recovery01.umap"
INPUT_MAP_BYTES = 751_687
INPUT_MAP_SHA256 = "73097ef783735e2c3dd72b1ea17f9e0240b98d7e5e30d0df4d54bb2468550aba"'''

replacements = (
    (old_input, new_input),
    (
        'AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03/author_m01_accepted_candidate_assembly03.py"',
        'AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell01/author_m01_hero_street_shore_cell01.py"\nAUTHOR_BYTES = 23_887\nAUTHOR_SHA256 = "2a818d492c62e9c332e21314a737c92a212b6112c0316a66fff282a33767aed5"',
    ),
    (
        'OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_AcceptedCandidateAssembly03.umap"',
        'OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell01.umap"',
    ),
    (
        'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01"',
        'ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01/attempt_01"',
    ),
    (
        'TERMINAL = ROOT / "Saved/Reports/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_TERMINAL_SUPERVISOR.json"',
        'TERMINAL = ROOT / "Saved/Reports/M01_HERO_STREET_SHORE_CELL01_TERMINAL_SUPERVISOR.json"',
    ),
    ('author_record = record(AUTHOR)', 'author_record = require_authority(AUTHOR, AUTHOR_BYTES, AUTHOR_SHA256)'),
    (
        'PASS_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_OFFLINE_CONTRACT',
        'PASS_M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT',
    ),
    (
        'PASS_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_SUPERVISOR_OFFLINE_CONTRACT',
        'PASS_M01_HERO_STREET_SHORE_CELL01_SUPERVISOR_OFFLINE_CONTRACT',
    ),
    (
        'PASSED_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_READY_FOR_STRUCTURAL_ADJUDICATION',
        'PASSED_M01_HERO_STREET_SHORE_CELL01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF',
    ),
    ('receipt.get("actor_count_before") != 148 or receipt.get("actor_count_after") != 119',
     'receipt.get("actor_count_before") != 119 or receipt.get("actor_count_after") != 120'),
    ('if len(receipt.get("city_placements", [])) != 18:\n            raise RuntimeError("Assembly03 city-placement contract failed")',
     'if len(receipt.get("window_modules", [])) != 12 or len(receipt.get("prop_copies", [])) != 11:\n            raise RuntimeError("Hero-cell bounded-content contract failed")'),
    (
        'PASSED_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_READY_FOR_MAPPED_VISUAL_PROOF_DESIGN',
        'PASSED_M01_HERO_STREET_SHORE_CELL01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF',
    ),
    ('skyguard.m01-accepted-candidate-assembly03.supervisor.v1',
     'skyguard.m01-hero-street-shore-cell01.supervisor.v1'),
    ('offline design for one fresh Assembly03 D3D12 mapped visual proof',
     'freeze one focused Hero Street/Shore Cell01 D3D12 mapped visual proof'),
    ('Assembly03 output map is absent', 'Hero Street/Shore Cell01 output map is absent'),
    ('Accepted input map changed during authoring', 'Accepted Assembly03 source map changed during authoring'),
)

for old, new in replacements:
    if old not in source:
        raise RuntimeError(f"Hero-cell supervisor binding token absent: {old[:120]}")
    source = source.replace(old, new)

for forbidden in (
    "Lvl_M01_AcceptedCandidateAssembly03.umap",
    "M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01",
    "author_m01_accepted_candidate_assembly03.py",
):
    if forbidden in source:
        raise RuntimeError(f"Hero-cell supervisor retains stale namespace: {forbidden}")

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(source, __file__ + "::bound", "exec"), namespace, namespace)
