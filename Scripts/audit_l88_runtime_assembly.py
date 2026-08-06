"""Classify the governed L88 Yak-52 import into production runtime bundles.

This is a read-only source audit. It does not modify the GLB or Unreal assets.
The output gives Blender and Unreal a shared, deterministic ownership contract
for consolidation, animation, materials, collision, and later LOD generation.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
IMPORT_REPORT = ROOT / "Saved/Reports/L88_VALIDATION_IMPORT.json"
OUTPUT_REPORT = ROOT / "Saved/Reports/L88_RUNTIME_ASSEMBLY_CONTRACT.json"


def mesh_name(asset_path: str) -> str:
    return asset_path.rsplit("/", 1)[-1].split(".", 1)[0]


def bundle_for(name: str) -> str:
    if name.startswith("GEO_GunnerRifle"):
        return "Weapon_Rifle"
    if name.startswith("GEO_Igla"):
        return "Weapon_Igla"
    if name.startswith(("GEO_GunnerGlove", "GEO_GunnerForearm", "GEO_GunnerSleeve")):
        return "Crew_RearGunner_FirstPerson"
    if name.startswith("GEO_RearSoldier"):
        return "Crew_RearGunner_ThirdPerson"
    if name.startswith("GEO_Pilot"):
        return "Crew_Pilot"
    if "CanopyGlass" in name:
        return "Aircraft_CanopyGlass"
    if name.startswith(("GEO_PropBlade", "GEO_PropHub", "GEO_PropSpinner")):
        return "Aircraft_Propeller"
    if any(
        token in name
        for token in (
            "Gear",
            "Wheel",
            "Brake",
            "TorqueLink",
        )
    ):
        return "Aircraft_LandingGear"
    if name.startswith(
        (
            "GEO_Rear",
            "GEO_Cockpit",
            "GEO_Gauge",
            "GEO_Pedal",
            "GEO_ControlStick",
            "GEO_Canopy",
        )
    ):
        return "Aircraft_RearCockpit"
    if any(token in name for token in ("Rivet", "Fastener")):
        return "Aircraft_MicroDetail"
    if name.startswith(
        (
            "GEO_Airframe",
            "GEO_Wings",
            "GEO_Engine",
            "GEO_Cowl",
            "GEO_HorizontalTail",
            "GEO_VerticalTail",
            "GEO_Wing",
            "GEO_Tail",
            "GEO_Fuselage",
            "GEO_Aileron",
            "GEO_Elevator",
            "GEO_Flap",
            "GEO_LeftWing",
            "GEO_RightWing",
            "GEO_Livery",
            "GEO_NavLamp",
            "GEO_RadialCylinder",
        )
    ):
        return "Aircraft_Exterior"
    return "Unclassified"


def runtime_policy(bundle: str) -> dict[str, object]:
    policies = {
        "Aircraft_Exterior": {
            "runtime_target": "SM_Yak52_Exterior",
            "mobility": "Movable",
            "collision": "UCX simple airframe hulls",
            "render": "Nanite optional for nondeforming opaque detail",
            "texture_sets": ["Yak52_Exterior_4K_A", "Yak52_Exterior_4K_B"],
        },
        "Aircraft_MicroDetail": {
            "runtime_target": "bake to normals/decals; do not ship as individual components",
            "mobility": "baked",
            "collision": "none",
            "render": "high-poly bake source",
            "texture_sets": ["Yak52_Exterior_4K_A", "Yak52_Exterior_4K_B"],
        },
        "Aircraft_RearCockpit": {
            "runtime_target": "SM_Yak52_RearCockpit",
            "mobility": "Movable",
            "collision": "cockpit blocking volumes plus interaction proxies",
            "render": "conventional hero mesh",
            "texture_sets": ["Yak52_RearCockpit_4K_A", "Yak52_RearCockpit_4K_B"],
        },
        "Aircraft_CanopyGlass": {
            "runtime_target": "SM_Yak52_CanopyGlass",
            "mobility": "Movable",
            "collision": "query-only canopy shot blocker",
            "render": "conventional translucent mesh",
            "texture_sets": ["Yak52_Glass_2K"],
        },
        "Aircraft_Propeller": {
            "runtime_target": "SM_Yak52_Propeller",
            "mobility": "Movable on SO_PropAxis",
            "collision": "none",
            "render": "authored blade plus high-RPM blur state",
            "texture_sets": ["Yak52_Exterior_4K_A"],
        },
        "Aircraft_LandingGear": {
            "runtime_target": "SK_Yak52_GearAssembly",
            "mobility": "Movable",
            "collision": "simple wheel/strut query shapes",
            "render": "conventional animated meshes",
            "texture_sets": ["Yak52_Exterior_4K_B"],
        },
        "Crew_Pilot": {
            "runtime_target": "SK_Yak52_Pilot",
            "mobility": "Skeletal",
            "collision": "pilot protection volume",
            "render": "skeletal character",
            "texture_sets": ["Yak52_Crew_2K"],
        },
        "Crew_RearGunner_ThirdPerson": {
            "runtime_target": "SK_Yak52_RearGunner",
            "mobility": "Skeletal",
            "collision": "none; airframe owns protection",
            "render": "skeletal character",
            "texture_sets": ["Yak52_Crew_2K"],
        },
        "Crew_RearGunner_FirstPerson": {
            "runtime_target": "SK_Yak52_FP_Arms",
            "mobility": "Skeletal",
            "collision": "none",
            "render": "first-person skeletal overlay",
            "texture_sets": ["Yak52_FP_Arms_2K"],
        },
        "Weapon_Rifle": {
            "runtime_target": "SK_Yak52_Rifle",
            "mobility": "socket driven",
            "collision": "weapon trace only",
            "render": "conventional detachable weapon",
            "texture_sets": ["Yak52_Rifle_2K"],
        },
        "Weapon_Igla": {
            "runtime_target": "SK_Yak52_Igla",
            "mobility": "socket driven",
            "collision": "weapon trace only",
            "render": "conventional detachable weapon",
            "texture_sets": ["Yak52_Igla_2K"],
        },
    }
    return policies.get(
        bundle,
        {
            "runtime_target": "manual classification required",
            "mobility": "unknown",
            "collision": "unknown",
            "render": "hold",
            "texture_sets": [],
        },
    )


def main() -> None:
    source = json.loads(IMPORT_REPORT.read_text(encoding="utf-8"))
    assets = source.get("static_mesh_assets", [])
    entries = []
    for asset in sorted(assets):
        name = mesh_name(asset)
        bundle = bundle_for(name)
        entries.append({"name": name, "asset": asset, "bundle": bundle})

    counts = Counter(entry["bundle"] for entry in entries)
    unclassified = [entry["name"] for entry in entries if entry["bundle"] == "Unclassified"]
    policies = {
        bundle: runtime_policy(bundle)
        for bundle in sorted(counts)
        if bundle != "Unclassified"
    }
    core_required = {
        "GEO_Airframe",
        "GEO_Wings",
        "GEO_EngineCowling",
        "GEO_HorizontalTail",
        "GEO_VerticalTail",
        "GEO_CockpitTub",
        "GEO_RearPanel",
        "GEO_FrontCanopyGlass",
        "GEO_RearCanopyGlass_Stowed",
        "GEO_PropHub",
        "GEO_PropBlade_A",
    }
    names = {entry["name"] for entry in entries}
    missing_core = sorted(core_required - names)

    fingerprint_input = "\n".join(
        f"{entry['name']}|{entry['asset']}|{entry['bundle']}" for entry in entries
    ).encode("utf-8")
    report = {
        "schema": "skyguard.l88.runtime-assembly-contract.v1",
        "source_report": str(IMPORT_REPORT),
        "source_glb_sha256": source.get("source_glb_sha256"),
        "source_mesh_count": len(entries),
        "bundle_counts": dict(sorted(counts.items())),
        "runtime_policies": policies,
        "entries": entries,
        "unclassified": unclassified,
        "missing_core_meshes": missing_core,
        "assembly_fingerprint_sha256": hashlib.sha256(fingerprint_input).hexdigest(),
        "checks": {
            "source_import_gate_pass": source.get("gate") == "PASS",
            "expected_240_meshes": len(entries) == 240,
            "all_meshes_classified": not unclassified,
            "core_runtime_meshes_present": not missing_core,
            "micro_detail_not_individual_runtime_components": (
                policies.get("Aircraft_MicroDetail", {}).get("runtime_target", "").startswith("bake")
            ),
            "weapons_have_separate_runtime_ownership": (
                counts["Weapon_Rifle"] > 0 and counts["Weapon_Igla"] > 0
            ),
            "crew_has_separate_first_and_third_person_ownership": (
                counts["Crew_RearGunner_FirstPerson"] > 0
                and counts["Crew_RearGunner_ThirdPerson"] > 0
                and counts["Crew_Pilot"] > 0
            ),
        },
    }
    report["gate"] = "PASS" if all(report["checks"].values()) else "HOLD"
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "gate": report["gate"],
        "source_mesh_count": report["source_mesh_count"],
        "bundle_counts": report["bundle_counts"],
        "unclassified": report["unclassified"],
        "missing_core_meshes": report["missing_core_meshes"],
        "output": str(OUTPUT_REPORT),
    }, indent=2))
    if report["gate"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
