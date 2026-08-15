"""Bind the proven D3D12 proof lifecycle to Cell03 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell02_visual_proof01\capture_m01_hero_street_shore_cell02_visual_proof01.py"
)
EXPECTED_BYTES = 6_974
EXPECTED_SHA256 = "c0b540c4b939aa51a21c1e8402bdb8a8c38393567ff5099fa3ee22777d5f34a2"

OLD_PREFIX = "M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01"
NEW_PREFIX = "M01_HERO_STREET_SHORE_CELL03_RECOVERY01_VISUAL_PROOF01"
OLD_ID = "M01-HERO-STREET-SHORE-CELL02-VISUAL-PROOF01"
NEW_ID = "M01-HERO-STREET-SHORE-CELL03-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_HeroStreetShoreCell02"
NEW_MAP = "Lvl_M01_HeroStreetShoreCell03Recovery01"
OLD_CSV = "M01HeroStreetShoreCell02VisualProof01.csv"
NEW_CSV = "M01HeroStreetShoreCell03Recovery01VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Cell02 proof binder changed")
    namespace = {"__name__": "cell02_proof_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in ((OLD_PREFIX, NEW_PREFIX), (OLD_ID, NEW_ID), (OLD_MAP, NEW_MAP), (OLD_CSV, NEW_CSV)):
        if old not in transformed:
            raise RuntimeError(f"Cell03 proof binding token absent: {old}")
        transformed = transformed.replace(old, new)

    old_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", "M01_HSSC01R01_", "M01_HSSC02_"))'
    new_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", "M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_"))'
    if transformed.count(old_fingerprint) != 1:
        raise RuntimeError("Cell03 governed-transform fingerprint anchor changed")
    transformed = transformed.replace(old_fingerprint, new_fingerprint)

    authority_start = '''        cell_freeze_path = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL02_AUTHORING_ATTEMPT01_ACCEPTANCE_FREEZE.json"'''
    authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_HeroStreetShoreCell03Recovery01.umap"
        )'''
    start = transformed.find(authority_start)
    end = transformed.find(authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Cell03 acceptance-authority block anchor changed")
    new_authority = '''        cell_freeze_path = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL03_RECOVERY01_AUTHORING_ATTEMPT01_ACCEPTANCE_FREEZE.json"
        cell_freeze = read_json(cell_freeze_path)
        if cell_freeze.get("classification") != "PASSED_READY_FOR_CELL03_RECOVERY01_D3D12_MAPPED_VISUAL_PROOF":
            raise RuntimeError("Hero Street/Shore Cell03 Recovery01 authoring acceptance changed")
        if cell_freeze.get("runtime_promotion") is not False:
            raise RuntimeError("Hero Street/Shore Cell03 Recovery01 promotion guard changed")
        verify_record({"absolute_path": str(cell_freeze_path), "bytes": 2103, "sha256": "62da518b19ec2d36b272f2982fa4ff749a78a615b58363500da4605bdbf8581d"})
        for cell_record in (cell_freeze.get("terminal"), cell_freeze.get("receipt"), *cell_freeze.get("outputs", [])):
            verify_record({"absolute_path": cell_record["path"], "bytes": cell_record["bytes"], "sha256": cell_record["sha256"]})
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    runtime_start = '''        by_label = {}
        for governed_actor in actors:'''
    runtime_end = '''        transient_pcg = corridor_by_label.get("PCGWorldActor0", [])'''
    start = transformed.find(runtime_start)
    end = transformed.find(runtime_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Cell03 runtime assertion block anchor changed")
    new_runtime = '''        by_label = {}
        for governed_actor in actors:
            by_label.setdefault(governed_actor.get_actor_label(), []).append(governed_actor)
        exact_labels = (
            "M01_C06R01_Corridor_TERRAIN",
            "M01_C06R01_Corridor_HARDSCAPE",
            "M01_C06R01_Corridor_DETAILS",
            "M01_ACA03R01_Corridor_CONTACT",
            "M01_HSSC02_CoastalA_TERRAIN",
            "M01_HSSC02_CoastalA_HARDSCAPE",
        )
        for exact_label in exact_labels:
            if len(by_label.get(exact_label, [])) != 1:
                raise RuntimeError(f"Expected exactly one Cell03 actor {exact_label}; found {len(by_label.get(exact_label, []))}")
        for prefix, expected_count in {
            "M01_ACA03R01_City_": 9,
            "M01_Promenade_Bollard_": 13,
            "M01_Promenade_BicycleRack_": 8,
            "M01_Promenade_UtilityCabinet_": 5,
            "M01_Promenade_StormDrain_": 12,
            "M01_Promenade_LitterBin_": 10,
            "M01_HSSC01R01_Window_": 36,
            "M01_HSSC01R01_Prop_": 11,
            "M01_HSSC02_CoastalA_": 2,
            "M01_HSSC03_City_": 6,
            "M01_HSSC03_RearWindow_": 36,
        }.items():
            actual_count = sum(actor.get_actor_label().startswith(prefix) for actor in actors)
            if actual_count != expected_count:
                raise RuntimeError(f"Cell03 prefix {prefix}: expected {expected_count}, found {actual_count}")
        district_assets = {
            "M01_HSSC02_CoastalA_TERRAIN": "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_TERRAIN.SM_M01_CoastalA_TERRAIN",
            "M01_HSSC02_CoastalA_HARDSCAPE": "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_HARDSCAPE.SM_M01_CoastalA_HARDSCAPE",
        }
        for label, asset_path in district_assets.items():
            component = by_label[label][0].get_component_by_class(unreal.StaticMeshComponent)
            expected_mesh = unreal.load_asset(asset_path)
            if component is None or expected_mesh is None:
                raise RuntimeError(f"Cell03 district mesh contract unresolved: {label}")
            actual_mesh = component.get_editor_property("static_mesh")
            if asset_identity(actual_mesh) != asset_identity(expected_mesh):
                raise RuntimeError(f"Cell03 district mesh identity changed: {label}")
        for forbidden_prefix in ("M01_VEK02_City_", "M01_VEK02_Lighthouse_", "M01_RS01_Tree_"):
            if any(actor.get_actor_label().startswith(forbidden_prefix) for actor in actors):
                raise RuntimeError(f"Rejected proxy actor survived Cell03: {forbidden_prefix}")
        if any(actor.get_actor_label() == "M01_RS01_Radar_Hero" for actor in actors):
            raise RuntimeError("Unaccepted radar survived Cell03")
        corridor_by_label = by_label
'''
    transformed = transformed[:start] + new_runtime + transformed[end:]
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::hero-cell03-recovery01-proof01", "exec"), globals(), globals())
