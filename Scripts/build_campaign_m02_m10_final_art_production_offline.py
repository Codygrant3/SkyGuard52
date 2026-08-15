#!/usr/bin/env python3
"""Build the offline-only Mission 2-10 final-art production contract.

This script performs no Unreal or Blender work.  It reconciles the accepted
campaign engineering baseline with the still-missing production-art gates and
writes deterministic, reviewable planning artifacts for the remaining nine
missions.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "AAA_Review"
REPORTS = ROOT / "Saved" / "Reports"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": stat.st_size,
        "sha256": sha256_file(path),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


MISSION_ART = {
    2: {
        "id": "M02_HarborShield",
        "name": "Harbor Shield",
        "boss": "Breakwater",
        "boss_class": "SkyguardBreakwaterBoss",
        "protected_objective": "Fuel terminal",
        "exclusive_interaction": "Strip armor panels",
        "environment_identity": "working industrial harbor with grounded cranes, fuel terminal, container ship, surfaced naval silhouette, breakwaters and wet quays",
        "hero_assets": ["harbor crane family", "fuel terminal", "container ship", "surfaced submarine", "Breakwater boss"],
        "boss_art": ["armored maritime strike-drone body", "animated armor panels and latches", "decoy pods", "damaged engine and elevator", "harbor-safe crash pieces"],
        "boss_mechanic": "occluded crossing runs, latch precision fire, armor removal, decoy suppression, Igla engine hit and rifle crash diversion",
        "wave": "WAVE_A_M02_M03",
    },
    3: {
        "id": "M03_ConvoyEscort",
        "name": "Convoy Escort",
        "boss": "RoadHunter",
        "boss_class": "SkyguardRoadHunterBoss",
        "protected_objective": "Convoy core",
        "exclusive_interaction": "Blind targeting camera",
        "environment_identity": "coastal highway with safe opening route, bridge, tunnel, relief convoy, ridge cover and roadside settlements",
        "hero_assets": ["bridge and tunnel hero kit", "relief convoy vehicle set", "Road Hunter boss"],
        "boss_art": ["swept fast-drone body", "nose camera gimbal", "two animated wing actuators", "three progressive damage configurations"],
        "boss_mechanic": "fast crossing attacks, bilateral camera/actuator exposure, short Igla recovery-climb window and convoy-safe rifle finish",
        "wave": "WAVE_A_M02_M03",
    },
    4: {
        "id": "M04_NightBlackout",
        "name": "Night Blackout",
        "boss": "BlackKite",
        "boss_class": "SkyguardBlackKiteBoss",
        "protected_objective": "Emergency substation",
        "exclusive_interaction": "Hold searchlight track",
        "environment_identity": "night waterfront with substation, damaged grid, grounded searchlight batteries, blackout navigation references and controlled practical lighting",
        "hero_assets": ["substation and damaged-grid kit", "searchlight battery family", "Black Kite boss"],
        "boss_art": ["low-observable night-drone silhouette", "reflective navigation vanes", "jammer blister", "exposed power bus", "emissive failure states"],
        "boss_mechanic": "audio localization, searchlight reveal, bilateral vane destruction, jammer removal, Igla lock and burning-glide rifle finish",
        "wave": "WAVE_B_M04_M07",
    },
    5: {
        "id": "M05_StormFront",
        "name": "Storm Front",
        "boss": "Tempest",
        "boss_class": "SkyguardTempestBoss",
        "protected_objective": "Distressed trawler",
        "exclusive_interaction": "Disable discharge booms",
        "environment_identity": "storm ocean route with offshore platform, sea stacks, storm buoys, distressed trawler, rain cells and lightning silhouettes",
        "hero_assets": ["offshore platform", "sea-stack and storm-buoy kit", "distressed trawler", "Tempest boss"],
        "boss_art": ["reinforced storm-drone shell", "discharge booms", "intake shutters", "control servo", "water-shedding panels and bounded debris"],
        "boss_mechanic": "short weather-reveal windows, discharge-boom removal, gust-exposed servo, turbulent Igla lock and debris avoidance",
        "wave": "WAVE_B_M04_M07",
    },
    6: {
        "id": "M06_AirfieldDefense",
        "name": "Airfield Defense",
        "boss": "RunwayBreaker",
        "boss_class": "SkyguardRunwayBreakerBoss",
        "protected_objective": "Airfield targets",
        "exclusive_interaction": "Jam payload racks",
        "environment_identity": "operational airfield with runway, hangars, control tower, hardened shelters, taxiways, ground-defense activity and safe approach corridors",
        "hero_assets": ["runway and taxiway kit", "hangar family", "control tower", "hardened shelter family", "Runway Breaker boss"],
        "boss_art": ["twin-engine bomber body", "three payload bays and modules", "release racks", "internal heat manifold", "progressive engine-damage states"],
        "boss_mechanic": "payload-priority defense, exposed heat manifold, turning Igla window, asymmetric-power phase and off-runway crash",
        "wave": "WAVE_B_M04_M07",
    },
    7: {
        "id": "M07_SearchIntercept",
        "name": "Search and Intercept",
        "boss": "RadarGhost",
        "boss_class": "SkyguardRadarGhostBoss",
        "protected_objective": "Island radar chain",
        "exclusive_interaction": "Classify false tracks",
        "environment_identity": "island patrol box with radar installation, navigation stations, fishing fleet, coastal relief and distinct visual-identification sectors",
        "hero_assets": ["radar installation", "island and navigation-station kit", "fishing fleet", "Radar Ghost boss"],
        "boss_art": ["electronic-warfare drone body", "bilateral jammer pods", "retracting antenna", "heat vent", "command-antenna damage state"],
        "boss_mechanic": "false-contact identification, bilateral jammer attacks, rear-aspect Igla window and command-antenna rifle finish",
        "wave": "WAVE_B_M04_M07",
    },
    8: {
        "id": "M08_RescueCover",
        "name": "Rescue Cover",
        "boss": "LifelineHunter",
        "boss_class": "SkyguardLifelineHunterBoss",
        "protected_objective": "Rescue flight and survivors",
        "exclusive_interaction": "Complete hoist windows",
        "environment_identity": "active maritime rescue box with animated rescue helicopter, hoist, survivors, rafts, rescue vessel and protected extraction lane",
        "hero_assets": ["rescue helicopter and hoist", "survivor and raft set", "rescue vessel", "Lifeline Hunter boss"],
        "boss_art": ["precision-strike drone body", "rotating primary optic", "secondary sensor", "armored sensor covers", "rescue-safe redirected crash state"],
        "boss_mechanic": "friendly-fire discipline, orbit-dependent sensor exposure, safe-separation Igla launch and extraction-lane crash diversion",
        "wave": "WAVE_C_M08_M10",
    },
    9: {
        "id": "M09_SaturationAttack",
        "name": "Saturation Attack",
        "boss": "IronRain",
        "boss_class": "SkyguardIronRainBoss",
        "protected_objective": "City infrastructure",
        "exclusive_interaction": "Break swarm relays",
        "environment_identity": "metropolitan route with nonrepeating skyline, grounded power station, major bridge, rooftop infrastructure and large coordinated attack waves",
        "hero_assets": ["metropolitan skyline kit", "power station", "major bridge", "rooftop infrastructure kit", "Iron Rain boss"],
        "boss_art": ["large carrier-drone body", "three animated dispenser bays and racks", "command antennae", "decoy controller", "three engine pods and multi-phase damage states"],
        "boss_mechanic": "dispenser suppression, relay removal, climb-and-cross engine exposure, decoy defeat and multi-pass resource management",
        "wave": "WAVE_C_M08_M10",
    },
    10: {
        "id": "M10_EvacuationFinale",
        "name": "Evacuation Finale",
        "boss": "LastFlight",
        "boss_class": "SkyguardLastFlightBoss",
        "protected_objective": "Evacuation hub",
        "exclusive_interaction": "Clear evacuation lanes",
        "environment_identity": "three-stage evacuation route linking highway convoy, ferry terminal and evacuation ship with buses, ambulances and civilian staging areas",
        "hero_assets": ["ferry terminal", "evacuation ship", "evacuation vehicle set", "civilian convoy hub", "Last Flight boss"],
        "boss_art": ["heavy command-drone body", "detachable armor shell", "guidance arrays", "two strike bays and cooling systems", "jammer, dual engines, command core and ocean-impact breakup set"],
        "boss_mechanic": "three-phase highway/terminal/ship encounter combining pilot commands, bilateral positioning, decoy suppression, rifle, Igla and civilian protection",
        "wave": "WAVE_C_M08_M10",
    },
}


def director_paths(order: int) -> list[Path]:
    stem = f"SkyguardMission{order:02d}Integration"
    return [
        ROOT / "Source" / "Skyguard52" / f"{stem}Director.cpp",
        ROOT / "Source" / "Skyguard52" / f"{stem}Director.h",
        ROOT / "Source" / "Skyguard52" / f"{stem}Tests.cpp",
    ]


def boss_paths(class_stem: str) -> list[Path]:
    candidates = [
        ROOT / "Source" / "Skyguard52" / f"{class_stem}.cpp",
        ROOT / "Source" / "Skyguard52" / f"{class_stem}.h",
        ROOT / "Source" / "Skyguard52" / f"{class_stem}Tests.cpp",
    ]
    return [path for path in candidates if path.exists()]


def main() -> int:
    created_utc = datetime.now(timezone.utc).isoformat()
    manifest_path = ROOT / "Production" / "production_manifest.json"
    campaign_audit_path = REPORTS / "PHASE7_CAMPAIGN_V1_PERSISTENCE_AUDIT.json"
    campaign_build_path = REPORTS / "PHASE7_CAMPAIGN_V1_BUILD.json"
    recovery07_authoring = DOCS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_ATTEMPT01_TERMINAL_FREEZE.json"
    recovery04_mapped_readiness = DOCS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04_TERMINAL_READINESS_FREEZE.json"

    required_authorities = [
        manifest_path,
        campaign_audit_path,
        campaign_build_path,
        recovery07_authoring,
        recovery04_mapped_readiness,
        DOCS / "PHASE7_GOVERNED_CAMPAIGN_CONTENT.md",
        DOCS / "BOSS_FIGHT_DESIGN_10_MISSIONS.md",
        DOCS / "SKYGUARD52_CAMPAIGN_ACCEPTANCE_MATRIX_GATE0.md",
        DOCS / "SKYGUARD52_CAMPAIGN_ROADMAP_ADDENDUM_GATE7_CYCLE03_2026-08-04.md",
    ]
    missing = [str(path) for path in required_authorities if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing authorities:\n" + "\n".join(missing))

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    campaign_audit = json.loads(campaign_audit_path.read_text(encoding="utf-8"))
    authoring = json.loads(recovery07_authoring.read_text(encoding="utf-8"))
    mapped_readiness = json.loads(recovery04_mapped_readiness.read_text(encoding="utf-8"))
    if authoring.get("classification") != "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_AUTOMATIC_AWAITING_VISUAL_PROOF":
        raise RuntimeError("Recovery07 environment authoring authority is not accepted")
    if mapped_readiness.get("classification") != "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04_AUTHORIZATION":
        raise RuntimeError("Recovery04 mapped-proof readiness authority is not ready")
    if campaign_audit.get("gate") != "PASS":
        raise RuntimeError("Campaign persistence baseline is not accepted")

    assets_by_id = {asset["id"]: asset for asset in manifest["assets"]}
    campaign_missions = {item["mission_id"]: item for item in campaign_audit["missions"]}
    mission_asset_prefixes = {order: f"m{order:02d}-" for order in MISSION_ART}
    matrix: list[dict[str, Any]] = []
    source_paths: list[Path] = list(required_authorities)

    for order, design in MISSION_ART.items():
        mission = campaign_missions[design["id"]]
        prefix = mission_asset_prefixes[order]
        governed_assets = [
            asset for asset_id, asset in assets_by_id.items() if asset_id.startswith(prefix)
        ]
        map_stem = design["id"].replace(f"M{order:02d}_", "")
        map_files = [
            ROOT / "Content" / "Skyguard" / "Maps" / "Campaign_v1" / f"Lvl_M{order:02d}_{map_stem}_Assembly_v1.umap",
            ROOT / "Content" / "Skyguard" / "Maps" / "Campaign_v1" / f"Lvl_M{order:02d}_{map_stem}_Playable_v1.umap",
        ]
        data_asset = ROOT / "Content" / "Skyguard" / "Data" / "Campaign_v1" / f"DA_Mission_M{order:02d}_{map_stem}.uasset"
        implementation = director_paths(order) + boss_paths(design["boss_class"])
        for path in map_files + [data_asset] + implementation:
            if not path.is_file():
                raise FileNotFoundError(path)
        source_paths.extend(map_files + [data_asset] + implementation)
        matrix.append(
            {
                "order": order,
                "mission_id": design["id"],
                "name": design["name"],
                "current_engineering_state": "PLAYABLE_OR_PROXY_ENGINEERING_BASELINE_SOAKED_NOT_PRODUCTION_ACCEPTED",
                "production_acceptance": "UNVERIFIED",
                "route_signature_cm": mission["route_signature"],
                "route_id_unique": True,
                "boss": design["boss"],
                "boss_source_class": design["boss_class"],
                "canonical_weakpoints": mission["weakpoint_ids"],
                "protected_objective": design["protected_objective"],
                "exclusive_interaction": design["exclusive_interaction"],
                "environment_identity": design["environment_identity"],
                "exclusive_hero_assets": design["hero_assets"],
                "boss_art_requirements": design["boss_art"],
                "boss_interaction_contract": design["boss_mechanic"],
                "production_wave": design["wave"],
                "governed_manifest_assets": [
                    {
                        "id": asset["id"],
                        "owner": asset["owner"],
                        "quality": asset["quality"],
                        "status": asset["status"],
                        "blocker": asset.get("blocker"),
                        "required": asset.get("required", []),
                    }
                    for asset in sorted(governed_assets, key=lambda item: item["priority"])
                ],
                "existing_map_files": [record(path) for path in map_files],
                "existing_data_asset": record(data_asset),
                "existing_implementation": [record(path) for path in implementation],
                "required_review_views": [
                    "rear_gunner_port",
                    "rear_gunner_starboard",
                    "route_exterior",
                    "protected_objective",
                    "boss_reveal",
                    "route_entry_temporal",
                    "route_mid_temporal",
                    "route_exit_temporal",
                ],
            }
        )

    shared_assets = [
        asset for asset in manifest["assets"] if asset.get("lane") == "P1-shared-world-library"
    ]
    contract = {
        "schema": "skyguard.campaign-m02-m10-final-art-production-contract.v1",
        "created_utc": created_utc,
        "classification": "OFFLINE_DESIGN_CONDITIONAL_ON_M01_VISUAL_LANGUAGE_ACCEPTANCE",
        "scope": "nine distinct production-quality mission environments and bosses; no runtime mutation or heavy-process authorization",
        "baseline_truth": {
            "campaign_data_definitions": "ACCEPTED_10_OF_10",
            "distinct_routes": "ACCEPTED_10_OF_10",
            "mission_maps": "EXIST_AND_ENGINEERING_SOAK_PASSED",
            "mission_directors": "EXIST",
            "boss_gameplay_classes": "EXIST",
            "production_mission_acceptance": "0_OF_10",
            "final_environment_art": "MISSING_M02_M10",
            "final_boss_art": "MISSING_M02_M10",
            "packaged_campaign_acceptance": "MISSING",
        },
        "hard_dependencies": [
            "Mission 1 mapped visual proof accepted at full resolution",
            "Mission 1 visual/material/performance language frozen as propagation authority",
            "accepted shared destruction and pooled VFX behavior",
            "accepted rifle, Igla, rear-gunner and Yak-52 combat vertical slice",
            "licensed or project-owned provenance for every external environment source",
        ],
        "ownership": {
            "blender": ["hero geometry", "boss geometry", "UVs", "bake sources", "rigs", "pivots", "sockets", "collision", "damage states"],
            "unreal": ["terrain", "water", "shoreline", "PCG", "foliage", "materials", "lighting", "weather", "Niagara", "mission assembly", "profiling", "packaging"],
        },
        "reuse_contract": {
            "shared_geometry_target_percent_min": 65,
            "shared_geometry_target_percent_max": 70,
            "layout_duplication_allowed": False,
            "exclusive_hero_assets_per_mission_min": 3,
            "exclusive_hero_assets_per_mission_max": 10,
            "shared_assets": [
                {
                    "id": asset["id"],
                    "status": asset["status"],
                    "owner": asset["owner"],
                    "required": asset.get("required", []),
                }
                for asset in sorted(shared_assets, key=lambda item: item["priority"])
            ],
        },
        "production_waves": [
            {
                "id": "WAVE_A_M02_M03",
                "missions": [2, 3],
                "purpose": "prove harbor armor/occlusion and high-speed crossing-target variants against the Mission 1 standard",
                "entry": "Mission 1 environment plus combat vertical slice accepted",
                "exit": "both missions pass mapped visuals, boss interactions, input combat, performance and packaged-mission smoke",
            },
            {
                "id": "WAVE_B_M04_M07",
                "missions": [4, 5, 6, 7],
                "purpose": "prove night, storm, airfield and search/decoy variants without forking the shared framework",
                "entry": "Wave A shared kits and boss framework accepted",
                "exit": "four missions pass their unique environmental and boss mechanic gates",
            },
            {
                "id": "WAVE_C_M08_M10",
                "missions": [8, 9, 10],
                "purpose": "prove rescue, saturation and finale scale with bounded destruction and civilian-protection logic",
                "entry": "shared framework performance stable under Wave B",
                "exit": "three missions plus full campaign traversal pass packaged acceptance",
            },
        ],
        "per_mission_gate_order": [
            "reference_and_license_freeze",
            "hero_asset_blockout_and_proportion_review",
            "high_poly_retopology_uv_bake_pbr",
            "rig_socket_collision_damage_state_review",
            "Unreal_import_candidate_with_reversible_manifest",
            "environment_assembly_and_route_grounding",
            "boss_mechanic_and_protected_objective_integration",
            "eight_view_mapped_visual_proof",
            "input_driven_rifle_and_igla_combat_proof",
            "performance_stability_and_hitch_proof",
            "packaged_mission_restart_and_soak",
        ],
        "failure_policy": {
            "one_heavy_process": True,
            "one_attempt_per_namespace": True,
            "automatic_retries": 0,
            "failed_namespace_reuse": False,
            "failed_attempts_immutable": True,
            "runtime_replacement_requires_reversible_manifest": True,
        },
        "heavy_execution_authorized": False,
        "next_heavy_gate": "Recovery07 Mapped Visual Proof01 Recovery04",
    }

    matrix_payload = {
        "schema": "skyguard.campaign-m02-m10-mission-boss-production-matrix.v1",
        "created_utc": created_utc,
        "classification": "ENGINEERING_BASELINE_RECONCILED_FINAL_ART_UNVERIFIED",
        "mission_count": len(matrix),
        "missions": matrix,
    }
    rubric = {
        "schema": "skyguard.campaign-m02-m10-visual-performance-acceptance-rubric.v1",
        "created_utc": created_utc,
        "inherits_m01_thresholds_after_m01_acceptance": True,
        "visual_proof": {
            "resolution": [2560, 1440],
            "static_captures": 5,
            "temporal_captures": 3,
            "human_full_resolution_review_required": True,
            "required_systems": [
                "unique rear-gunner route composition",
                "grounded terrain-road-building transitions",
                "correct waterline and shoreline contact where applicable",
                "unique skyline and landmark readability",
                "mission-specific weather and lighting",
                "protected-objective readability",
                "boss silhouette, weak points, telegraphs, damage states and aftermath",
                "stable clouds, water, foliage, traffic and world geometry",
            ],
            "automatic_rejects": [
                "diagnostic blocks or proxy hero art",
                "floating or disconnected geometry",
                "ungrounded buildings, roads, vehicles or cranes",
                "visible repeating placeholder structures",
                "missing shore contact or waterline",
                "bad exposure or crushed shadows",
                "camera clipping or camera-coupled world motion",
                "unreadable boss telegraphs or weak points",
                "live high-complexity fracture",
                "multi-second ADS, firing, impact or breakup stall",
            ],
        },
        "measurement": {
            "warmup_seconds": 30,
            "measured_seconds": 30,
            "minimum_frame_samples": 900,
            "captures_during_measurement": 0,
            "shader_compilation_allowed_during_measurement": False,
        },
        "thresholds": {
            "mean_frame_ms_max": 16.7,
            "p95_frame_ms_max": 22.2,
            "p99_frame_ms_max": 33.3,
            "max_frame_ms": 50.0,
            "frames_over_50ms_max": 0,
            "mean_gpu_ms_max": 14.0,
            "p95_gpu_ms_max": 20.0,
            "working_set_mib_max": 12288.0,
            "gpu_memory_mib_max": 10240.0,
        },
        "boss_runtime": {
            "preauthored_major_break_pieces_required": True,
            "pooled_debris_required": True,
            "particles_and_smoke_capped": True,
            "destruction_staged_across_frames": True,
            "briefing_preload_required": True,
            "boss_state_deadlocks_allowed": 0,
        },
        "packaged_acceptance": [
            "briefing and asset preload",
            "input and ADS",
            "rifle fire and reload",
            "Igla search, lock, launch and impact",
            "pilot and airframe protection",
            "mission success and failure",
            "save, unlock and relaunch",
            "five-minute mission soak",
            "full-campaign clean-machine traversal",
        ],
    }

    contract_path = DOCS / "CAMPAIGN_M02_M10_FINAL_ART_PRODUCTION_CONTRACT.json"
    matrix_path = DOCS / "CAMPAIGN_M02_M10_MISSION_BOSS_PRODUCTION_MATRIX.json"
    rubric_path = DOCS / "CAMPAIGN_M02_M10_VISUAL_PERFORMANCE_ACCEPTANCE_RUBRIC.json"
    write_json(contract_path, contract)
    write_json(matrix_path, matrix_payload)
    write_json(rubric_path, rubric)

    unique_sources = sorted({path.resolve() for path in source_paths}, key=lambda p: str(p).lower())
    inventory = {
        "schema": "skyguard.campaign-m02-m10-final-art-source-inventory.v1",
        "created_utc": created_utc,
        "classification": "PASS_SOURCE_BASELINE_INVENTORIED",
        "record_count": len(unique_sources),
        "records": [record(path) for path in unique_sources],
    }
    inventory_path = REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_SOURCE_INVENTORY.json"
    write_json(inventory_path, inventory)

    readiness = {
        "schema": "skyguard.campaign-m02-m10-final-art-readiness.v1",
        "created_utc": created_utc,
        "classification": "PASSED_OFFLINE_DESIGN_AWAITING_M01_VISUAL_LANGUAGE_ACCEPTANCE",
        "campaign_engineering_baseline": "PASS",
        "mission_contracts": "9_OF_9",
        "unique_routes": "9_OF_9",
        "unique_bosses": "9_OF_9",
        "exclusive_hero_asset_bounds": "PASS_3_TO_10_PER_MISSION",
        "production_acceptance": "0_OF_10",
        "heavy_execution_authorized": False,
        "first_heavy_gate_unchanged": "Recovery07 Mapped Visual Proof01 Recovery04",
        "campaign_wave01_blocked_by": "Mission 1 mapped visual plus combat vertical-slice acceptance",
    }
    readiness_path = REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_READINESS.json"
    write_json(readiness_path, readiness)

    prompt_path = DOCS / "NEXT_PROMPT_CAMPAIGN_M02_M03_FINAL_ART_PRODUCTION_WAVE01_OFFLINE_ORCHESTRATION.md"
    write_text(
        prompt_path,
        """# Next prompt — Mission 2-3 final-art production Wave 01 offline orchestration

Resume only the canonical Unreal Engine 5.8 / Blender 5.2 project at `D:\\Skyguard52`.

Treat the Mission 2-10 final-art production freeze as immutable authority. Perform an offline-only Wave 01 orchestration for Mission 2 Harbor Shield and Mission 3 Convoy Escort. Do not launch Unreal, Blender, a build, renderer, importer, exporter, or external model.

First require an accepted Mission 1 mapped visual proof and accepted Mission 1 combat vertical slice. If either is absent, classify `AWAITING_M01_VISUAL_AND_COMBAT_LANGUAGE` and create no heavy execution prompt.

When both prerequisites exist, freeze exact reference, provenance, scale, topology, UV, bake, PBR, rig, socket, collision, damage-state, camera, performance, integration and rollback contracts for:

- harbor crane family, fuel terminal, container ship, surfaced submarine and Breakwater;
- bridge/tunnel hero kit, relief convoy and Road Hunter;
- shared road, vehicle, vegetation, industrial, damage/debris and pooled-destruction libraries.

Preserve the existing campaign data assets, route definitions, maps, directors and boss classes. Do not treat them as production-art acceptance. Require 65-70% shared modular geometry without duplicated layouts, three to ten exclusive hero assets per mission, fixed full-resolution review cameras, bounded pooled boss breakup and immutable license/source receipts.

Classify only `PASSED_READY_FOR_SEPARATE_M02_ASSET_PRODUCTION_AUTHORIZATIONS`, `AWAITING_M01_VISUAL_AND_COMBAT_LANGUAGE`, or `FAILED_WITH_EVIDENCE`. Never execute a heavy process during this gate.
""",
    )

    audit_addendum = DOCS / "PHASE1_8_COMPLETION_AUDIT_ADDENDUM_CAMPAIGN_M02_M10_FINAL_ART_OFFLINE_DESIGN_2026-08-09.md"
    write_text(
        audit_addendum,
        f"""# Phase 1-8 audit addendum — Missions 2-10 final-art offline production design

Classification: `PASSED_OFFLINE_DESIGN_AWAITING_M01_VISUAL_LANGUAGE_ACCEPTANCE`

The current filesystem proves that all ten governed mission definitions, distinct routes, mission maps, integration directors and boss gameplay classes exist. The accepted engineering baseline remains separate from production acceptance.

Current production truth:

- production mission acceptance: **0 of 10**;
- Mission 1 Recovery07 environment authoring: accepted automatically, awaiting mapped visual proof;
- first heavy gate: Recovery07 Mapped Visual Proof01 Recovery04;
- Missions 2-10 final environments, hero art, boss art, destruction states and packaged acceptance: unverified;
- Mission 2-10 offline final-art contracts: **9 of 9 created**;
- no Unreal or Blender execution was authorized by this design package.

The campaign is now divided into three propagation waves: M02-M03, M04-M07 and M08-M10. Wave execution remains conditional on accepted Mission 1 visual, combat and performance language.

Generated: {created_utc}
""",
    )

    matrix_addendum = DOCS / "SKYGUARD52_CAMPAIGN_ACCEPTANCE_MATRIX_ADDENDUM_M02_M10_FINAL_ART_OFFLINE_DESIGN_2026-08-09.md"
    write_text(
        matrix_addendum,
        """# Campaign acceptance matrix addendum — Mission 2-10 final-art offline design

The nine mission production contracts are now explicit, but no production acceptance changed. M02-M10 remain `UNVERIFIED` for final environment art, hero assets, boss art, mapped visuals, input-driven combat, audio, performance, stability and packaged gameplay.

The existing map files, mission directors, boss classes, governed DataAssets and earlier fixed-route soaks remain engineering evidence only. They must not be promoted to visual or packaged acceptance.

The propagation order is M02-M03, M04-M07, then M08-M10 after Mission 1 establishes the accepted visual/combat/performance standard.
""",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
