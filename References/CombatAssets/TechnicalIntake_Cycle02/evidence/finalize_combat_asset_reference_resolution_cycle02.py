from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent
ROOT = WORKSPACE / "combat_asset_reference_resolution_cycle02_20260805"
REPORTS = ROOT / "reports"
EVIDENCE = ROOT / "evidence"
PREFIX = "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path, root: Path = ROOT) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_json(name: str, payload: object) -> Path:
    path = REPORTS / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_text(name: str, payload: str) -> Path:
    path = REPORTS / name
    path.write_text(payload.rstrip() + "\n", encoding="utf-8")
    return path


def main() -> None:
    if not ROOT.is_dir():
        raise FileNotFoundError(ROOT)
    if REPORTS.exists() or EVIDENCE.exists():
        raise RuntimeError("Refusing to overwrite existing Cycle02 reports/evidence")
    REPORTS.mkdir()
    EVIDENCE.mkdir()
    created_at = datetime.now(timezone.utc).isoformat()

    for source_name in [
        "extract_cycle02_reference_frames.py",
        "add_cycle02_rifle_crops.py",
        "finalize_combat_asset_reference_resolution_cycle02.py",
    ]:
        shutil.copy2(WORKSPACE / source_name, EVIDENCE / source_name)

    cycle01_authorities = [
        {
            "path": r"D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_ASSET_TECHNICAL_REFERENCE_INTAKE_CYCLE01_FREEZE.json",
            "bytes": 7263,
            "sha256": "17b377efd0a94847e576a0b340e5ca0446511ecbd2ca7cdb9bff0858fba99744",
        },
        {
            "path": r"D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_TECHNICAL_REFERENCE_INTAKE_CYCLE01_READINESS.json",
            "bytes": 1701,
            "sha256": "95a68b513c4306d6cbc04c329ac1d7d2f0bca69a3514a97b9a59ce2b3b00851a",
        },
        {
            "path": r"D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_TECHNICAL_REFERENCE_INTAKE_CYCLE01_DIMENSION_AUTHORITY_MATRIX.json",
            "bytes": 3320,
            "sha256": "47fb2e97ff4a2a1d74bbba1a80449bff3db57cbe897410b73b88e0622fdbcf4f",
        },
        {
            "path": r"D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_TECHNICAL_REFERENCE_INTAKE_CYCLE01_PUBLICATION_RECOVERY01_RECEIPT.json",
            "bytes": 2311,
            "sha256": "c296b33a3da9ea00b5dfafce7b41cf5f1c7c2916293afc10771d0f0071a2de87",
        },
    ]

    extraction = json.loads((ROOT / "frame_extraction_manifest.json").read_text(encoding="utf-8"))
    crops = json.loads((ROOT / "rifle_crop_manifest.json").read_text(encoding="utf-8"))

    source_inventory = {
        "gate": PREFIX,
        "created_at_utc": created_at,
        "scope": "visual-modeling and Unreal integration reference only",
        "cycle01_authorities": cycle01_authorities,
        "cycle01_archive": r"D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle01_Recovery01",
        "onboard_video": extraction["source"],
        "extracted_frames": {
            "count": len(extraction["lossless_original_resolution_frames"]),
            "manifest": record(ROOT / "frame_extraction_manifest.json"),
        },
        "lossless_crops": {
            "count": len(crops["lossless_crops"]),
            "manifest": record(ROOT / "rifle_crop_manifest.json"),
        },
        "project_search": {
            "scope": [r"D:\Skyguard52\Source", r"D:\Skyguard52\Config", r"D:\Skyguard52\Docs\AAA_Review"],
            "finding": "No project authority selects 9K38 versus 9K338; all current records use generic Igla naming.",
        },
        "research_limitations": [
            "Two live web-search calls aborted without results.",
            "Cycle02 therefore relies on the frozen official and manufacturer sources acquired in Cycle01 plus governed footage.",
            "No new source was promoted from an unverified search result.",
        ],
    }
    write_json(f"{PREFIX}_SOURCE_INVENTORY.json", source_inventory)

    extraction_receipt = {
        "gate": PREFIX,
        "source": extraction["source"],
        "decoder": extraction["decoder"],
        "source_stream": {
            "codec": "H.264",
            "width": 1280,
            "height": 720,
            "nominal_frame_rate": "30/1",
            "average_frame_rate": "197888/6613",
            "duration_seconds": 25.832031,
            "frames_reported": 773,
        },
        "sampled_frames": len(extraction["lossless_original_resolution_frames"]),
        "sample_interval_nominal_seconds": 0.5,
        "contact_sheets": len(extraction["contact_sheets"]),
        "rifle_crops": len(crops["lossless_crops"]),
        "source_modified": False,
        "output_format": "lossless PNG at original 1280x720 for full frames",
    }
    write_json(f"{PREFIX}_VIDEO_EXTRACTION_RECEIPT.json", extraction_receipt)

    frame_manifest = {
        "gate": PREFIX,
        "full_frames": extraction["lossless_original_resolution_frames"],
        "contact_sheets": extraction["contact_sheets"],
        "rifle_crops": crops["lossless_crops"],
        "visually_inspected": [
            "contact_sheets/contact_01.png",
            "contact_sheets/contact_02.png",
            "contact_sheets/contact_03.png",
            "frames_full/frame_0000_0000.000s.png",
            "frames_full/frame_0450_0015.000s.png",
            "frames_full/frame_0510_0017.000s.png",
            "frames_full/frame_0675_0022.500s.png",
            "frames_full/frame_0690_0023.000s.png",
            "rifle_crops/frame_0450_0015.000s_rifle_crop.png",
            "rifle_crops/frame_0675_0022.500s_rifle_crop.png",
        ],
    }
    write_json(f"{PREFIX}_FRAME_MANIFEST.json", frame_manifest)

    rifle_matrix = {
        "gate": PREFIX,
        "narrowest_defensible_identity": "AR/M4-pattern rifle with free-float ventilated handguard; exact configuration unresolved",
        "lane_classification": "READY_FOR_FAMILY_ACCURATE_BLOCKOUT_ONLY",
        "normalized_classification": "READY_FOR_BLOCKOUT_ONLY",
        "observations": [
            {
                "feature": "continuous top rail",
                "footage": "clearly visible from 0.0 s and 14.5-17.0 s",
                "M4A1_candidate": "family-compatible but frozen Colt configuration uses a two-piece quad rail",
                "AK74_candidate": "does not match the frozen conventional AK-74 comparison",
            },
            {
                "feature": "handguard",
                "footage": "long free-float appearance with large elongated ventilation windows and rail interfaces",
                "M4A1_candidate": "conflicts with frozen Colt M4A1 two-piece quad-rail configuration",
                "AK74_candidate": "conflicts with frozen AK-74 handguard/gas-system silhouette",
            },
            {
                "feature": "muzzle device",
                "footage": "open-tine/pronged device visible; exact tine count and model uncertain",
                "M4A1_candidate": "not sufficient for exact Colt M4A1 acceptance",
                "AK74_candidate": "does not match the characteristic comparison geometry",
            },
            {
                "feature": "rear sight",
                "footage": "a rear aperture/flip-sight-like form is partially visible near 22.5 s",
                "M4A1_candidate": "family-compatible only",
                "AK74_candidate": "not consistent with tangent U-notch comparison",
            },
            {
                "feature": "receiver and controls",
                "footage": "obscured or out of frame",
                "M4A1_candidate": "cannot verify",
                "AK74_candidate": "cannot verify directly",
            },
            {
                "feature": "magazine",
                "footage": "not visible clearly enough for geometry or chambering",
                "M4A1_candidate": "cannot verify",
                "AK74_candidate": "cannot verify",
            },
            {
                "feature": "stock",
                "footage": "not visible",
                "M4A1_candidate": "cannot verify",
                "AK74_candidate": "cannot verify",
            },
            {
                "feature": "finish",
                "footage": "handguard appears tan in bright coastal segment and dark in later low-light segment; color is not identity authority",
                "M4A1_candidate": "not determinative",
                "AK74_candidate": "not determinative",
            },
        ],
        "decision": {
            "Colt_M4A1_exact": "REJECTED_AS_UNPROVEN_CONFIGURATION",
            "AK74_exact": "REJECTED_BY_VISIBLE_HANDGUARD_AND_SIGHT_FAMILY",
            "accepted_family": "AR/M4-pattern only",
            "blocked_details": [
                "manufacturer and model",
                "receiver and controls",
                "barrel length",
                "stock",
                "magazine and chambering",
                "exact handguard",
                "exact muzzle device",
                "exact front and rear sights",
                "markings and accessories",
            ],
        },
    }
    write_json(f"{PREFIX}_RIFLE_FEATURE_COMPARISON.json", rifle_matrix)
    write_json(
        f"{PREFIX}_RIFLE_IDENTITY_DECISION.json",
        {
            "gate": PREFIX,
            "identity": rifle_matrix["narrowest_defensible_identity"],
            "classification": rifle_matrix["normalized_classification"],
            "reason": "Visible family cues are strong, but the receiver, magazine, stock, controls and markings never become verifiable.",
            "production_boundary": "Use only a replaceable AR/M4-family silhouette blockout. Do not finalize ammunition, ejection, receiver controls, stock, magazine, sights, muzzle or markings.",
        },
    )

    igla_matrix = {
        "gate": PREFIX,
        "project_authority_search": "No existing source or design authority selects 9K38 or 9K338.",
        "historical_evidence": {
            "9K38": "Frozen ODIN/CIA-derived authority supports a 1574 mm by 72 mm missile blockout.",
            "9K338_Igla_S": "Visual references are mixed into public imagery, but no frozen dimension set governs this project.",
            "training_VISMOD": "May differ from operational launcher details and cannot govern final production geometry.",
        },
        "component_comparison": [
            {"component": "missile", "9K38": "dimensioned blockout available", "9K338": "not dimensioned in frozen gate", "status": "READY_FOR_BLOCKOUT_ONLY"},
            {"component": "nose", "9K38": "variant-specific detail unresolved", "9K338": "variant-specific detail unresolved", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
            {"component": "launch tube", "9K38": "global visual reference only", "9K338": "mixed imagery", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
            {"component": "gripstock", "9K38": "close measured reference absent", "9K338": "mixed imagery", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
            {"component": "battery/coolant assembly", "9K38": "close measured reference absent", "9K338": "variant differs", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
            {"component": "sight", "9K38": "close measured reference absent", "9K338": "variant differs", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
            {"component": "caps, bands, fasteners and markings", "9K38": "partial visual evidence", "9K338": "mixed imagery", "status": "BLOCKED_AWAITING_REFERENCE_INPUT"},
        ],
        "anti_mix_rule": "No nose, gripstock, battery, sight, cap, band or marking may be copied between 9K38, 9K338, trainer or VISMOD records.",
    }
    write_json(f"{PREFIX}_IGLA_VARIANT_COMPARISON.json", igla_matrix)
    write_json(
        f"{PREFIX}_IGLA_PROJECT_DECISION.json",
        {
            "gate": PREFIX,
            "decision_status": "RECOMMENDATION_AWAITING_EXPLICIT_ACCEPTANCE",
            "recommended_variant": "9K38 Igla / SA-18",
            "basis": [
                "matches the accepted Cycle01 naming",
                "has the strongest frozen global missile dimensions",
                "avoids mixing Igla-S imagery into a generic launcher",
            ],
            "accepted_without_further_choice": {"missile_blockout_length_mm": 1574, "missile_body_diameter_mm": 72},
            "not_accepted": "final launcher, gripstock, battery, sight, caps, bands, fasteners and markings",
        },
    )

    character_contract = {
        "gate": PREFIX,
        "profile_status": "PROJECT_PROFILE_SELECTED_AT_DESIGN_LEVEL; FINAL_DIMENSION_VECTOR_BLOCKED",
        "profile": "median-size adult rear gunner, male presentation, fully clothed and gloved",
        "critical_caveat": "The frozen NASA tables provide mixed-sex Min/Max accommodation bounds, not a coherent 50th-percentile male vector. No independent midpoint averaging is permitted.",
        "accommodation_envelope_mm": {
            "sitting_height": [777, 1013],
            "sitting_eye_height": [665, 889],
            "shoulder_elbow": [296, 419],
            "hand_length": [158, 221],
            "hand_breadth": [71, 102],
            "hand_circumference": [168, 241],
            "forearm_hand_length": [387, 546],
        },
        "blockout_rule": "Preserve the existing governed R3 proportions as a replaceable mannequin and validate clearance against the full NASA envelope. Do not label the mannequin as a measured percentile.",
        "visual_design_spec": {
            "gloves": "black close-fitting padded leather/tactical appearance with articulated fingers, thumb web, knuckle plane and cuff; exact manufacturer unresolved",
            "sleeves": "muted olive/gray flight-suit fabric with wrist folds and no block geometry",
            "headgear": "rear-gunner headgear is not visible in the camera-worn footage; exact helmet/hood is blocked",
            "headset": "rear-gunner headset identity blocked; pilot headset is not authority for the rear gunner",
            "harness": "retain governed safety concept, but webbing and buckle model remain blocked",
        },
        "pose_contracts": {
            "rifle": "two-hand support, articulated fingers, no palm/barrel interpenetration, replaceable family blockout",
            "Igla": "shoulder contact plus two governed grips only after exact launcher variant is accepted",
            "ADS": "rear sight, front sight and eye must share one alignment axis; no UI reticle substitute",
            "cockpit": "test hands, elbows, weapon sweep, canopy rim, pilot safety and rear-frame clearance",
        },
        "classification": "READY_FOR_BLOCKOUT_ONLY",
    }
    write_json(f"{PREFIX}_CHARACTER_ANTHROPOMETRIC_CONTRACT.json", character_contract)
    write_json(
        f"{PREFIX}_EQUIPMENT_REFERENCE_BOARD.json",
        {
            "gate": PREFIX,
            "reference_frames": [
                {"path": "frames_full/frame_0000_0000.000s.png", "use": "support-hand and glove silhouette"},
                {"path": "frames_full/frame_0450_0015.000s.png", "use": "black glove, tan handguard and olive/gray sleeve relationship"},
                {"path": "frames_full/frame_0510_0017.000s.png", "use": "glove contact and cockpit proximity"},
                {"path": "frames_full/frame_0675_0022.500s.png", "use": "two-hand pose and sleeve volume in low light"},
            ],
            "accepted_visual_language": ["black articulated gloves", "muted olive/gray sleeve", "functional webbing", "matte low-glare surfaces"],
            "blocked_identities": ["glove manufacturer/model", "rear helmet or hood", "rear headset", "harness model and buckle"],
            "classification": "READY_FOR_BLOCKOUT_ONLY",
        },
    )

    shahed = {
        "gate": PREFIX,
        "global_dimensions": [
            {
                "dimension": "overall length",
                "value_mm": 3300,
                "class": "OFFICIAL_REPORTED",
                "authority": "2023 Ukrainian/Estonian military handbook frozen in Cycle01",
            },
            {
                "dimension": "wingspan",
                "value_mm": 3000,
                "class": "OFFICIAL_REPORTED",
                "authority": "2023 Ukrainian/Estonian military handbook frozen in Cycle01",
            },
        ],
        "visual_authorities": [
            {"element": "airframe silhouette and component placement", "class": "OFFICIAL_REPORTED", "authority": "DIA illustration"},
            {"element": "MD550 engine appearance", "class": "OFFICIAL_REPORTED", "authority": "UN S/2023/418 imagery"},
            {"element": "servo and connector appearance", "class": "OFFICIAL_REPORTED", "authority": "UN S/2023/418 imagery"},
        ],
        "unknowns": [
            "wing airfoil and thickness stations",
            "fuselage cross-sections",
            "propeller diameter, pitch and blade stations",
            "engine mount dimensions",
            "servo installation dimensions",
            "antenna, fastener and access-panel exact positions",
        ],
        "conflict_resolution": "Retain 3300 x 3000 mm as the sole official blockout envelope. Do not reconcile conflicts by averaging.",
        "new_measured_primary_found": False,
        "classification": "READY_FOR_BLOCKOUT_ONLY",
    }
    write_json(f"{PREFIX}_SHAHED136_DIMENSION_RECONCILIATION.json", shahed)

    readiness_rows = [
        ("rifle family silhouette", "READY_FOR_BLOCKOUT_ONLY", "AR/M4 family only; exact configuration unresolved"),
        ("rifle final receiver/stock/magazine/sights/muzzle", "BLOCKED_AWAITING_REFERENCE_INPUT", "critical features not visible"),
        ("MIL-STD-1913 rail coupon", "READY_FOR_BLENDER_PRODUCTION", "standard dimensions frozen; coupon is validation geometry, not claimed weapon identity"),
        ("rifle magazines/ammunition/casings", "BLOCKED_AWAITING_REFERENCE_INPUT", "chambering and magazine identity unresolved"),
        ("rifle sling", "BLOCKED_AWAITING_REFERENCE_INPUT", "attachment and hardware not visible"),
        ("9K38 missile envelope", "READY_FOR_BLOCKOUT_ONLY", "1574 x 72 mm"),
        ("Igla launch tube/gripstock/battery/sight/caps", "BLOCKED_AWAITING_REFERENCE_INPUT", "variant choice and measured closeups absent"),
        ("gunner hands/forearms", "READY_FOR_BLOCKOUT_ONLY", "NASA envelope plus footage pose"),
        ("gloves/sleeves", "READY_FOR_BLOCKOUT_ONLY", "project visual design only; exact equipment unresolved"),
        ("helmet/headset/harness", "BLOCKED_AWAITING_REFERENCE_INPUT", "rear-gunner identity absent"),
        ("Shahed-136 exterior envelope", "READY_FOR_BLOCKOUT_ONLY", "3300 x 3000 mm official reported"),
        ("Shahed engine/servo/connector visual detail", "READY_FOR_BLOCKOUT_ONLY", "visual evidence but no measured installation"),
        ("Shahed final cross-sections/propeller", "BLOCKED_AWAITING_REFERENCE_INPUT", "measured authority absent"),
        ("Yak-52 propeller final blade geometry", "BLOCKED_AWAITING_REFERENCE_INPUT", "inherits Cycle04 missing blade stations/twist/airfoil"),
        ("cockpit controls lacking Cycle04 authority", "BLOCKED_AWAITING_REFERENCE_INPUT", "no new measured source"),
        ("fictional heavy drones", "BLOCKED_AWAITING_REFERENCE_INPUT", "separate fictional design authority required"),
        ("mission bosses", "BLOCKED_AWAITING_REFERENCE_INPUT", "separate silhouette/weak-point/destruction contract required"),
        ("destruction fragments and weak points", "BLOCKED_AWAITING_REFERENCE_INPUT", "must follow accepted production geometry and gameplay contract"),
    ]
    readiness = {
        "gate": PREFIX,
        "classification": "PARTIAL_READY_WITH_BLOCKED_ASSET_FAMILIES",
        "families": [{"asset": a, "status": s, "basis": b} for a, s, b in readiness_rows],
        "blender_launched": False,
        "unreal_launched": False,
        "external_ai_models_invoked": False,
        "heavy_processes_launched": 0,
        "next_gate": "Explicitly accept 9K38 as project variant, then run the separate blockout-only Blender prompt; pursue targeted identity references in parallel for blocked final assets.",
    }
    write_json(f"{PREFIX}_READINESS.json", readiness)

    conflicts = {
        "gate": PREFIX,
        "conflicts": [
            {"id": "RIFLE-EXACT-IDENTITY", "status": "OPEN", "decision": "AR/M4 family only"},
            {"id": "RIFLE-COLOR-SEGMENTS", "status": "OPEN", "decision": "Do not infer separate rifles or finish identity from exposure/color shift"},
            {"id": "IGLA-VARIANT", "status": "OPEN", "decision": "9K38 recommended; explicit project acceptance required"},
            {"id": "NASA-PERCENTILE-VECTOR", "status": "OPEN", "decision": "Use accommodation bounds; do not fabricate a 50th-percentile vector"},
            {"id": "SHAHED-CROSS-SECTIONS", "status": "OPEN", "decision": "global envelope only"},
            {"id": "SHAHED-SCALE-CONFLICT", "status": "BOUNDED", "decision": "retain official 3300 x 3000 mm without averaging"},
            {"id": "FICTIONAL-BOSSES", "status": "OPEN", "decision": "separate fictional design authority"},
        ],
    }
    write_json(f"{PREFIX}_CONFLICT_UNCERTAINTY_REGISTER.json", conflicts)

    boundary = {
        "gate": PREFIX,
        "allowed_in_next_blender_gate": [
            "dimensioned MIL-STD-1913 validation coupon",
            "replaceable AR/M4-family silhouette blockout using only visible footage features",
            "9K38 missile envelope blockout at 1574 mm by 72 mm",
            "replaceable gunner hand/forearm mannequin constrained by NASA envelope and footage pose",
            "Shahed-136 exterior envelope blockout at 3300 mm by 3000 mm",
        ],
        "prohibited": [
            "final rifle make/model or chambering",
            "final receiver, stock, magazine, ammunition, casing, sight or muzzle geometry",
            "mixing Igla and Igla-S components",
            "final Igla launcher component geometry",
            "inventing coherent percentile dimensions from independent NASA bounds",
            "inventing Shahed cross-sections or propeller measurements",
            "final helmet, headset, harness or glove product identity",
            "fictional boss production without separate design authority",
            "operational, assembly, firing, targeting or employment guidance",
        ],
    }
    write_json(f"{PREFIX}_BLENDER_BOUNDARY_CONTRACT.json", boundary)

    unreal = {
        "gate": PREFIX,
        "import_authorized": False,
        "future_socket_contract": {
            "rifle_blockout": ["muzzle_axis_provisional", "support_hand", "trigger_hand", "ads_rear", "ads_front"],
            "igla_missile_blockout": ["forward_origin", "rear_axis"],
            "gunner_blockout": ["hand_l", "hand_r", "forearm_l", "forearm_r", "eye_ads", "shoulder_contact"],
            "shahed_blockout": ["engine_visual", "wing_l", "wing_r", "damage_core"],
        },
        "collision": "Keep visual, gameplay, cockpit-safety and clearance volumes separate.",
        "pivots": "Use metric Blender sources, forward-axis documentation and centimetre validation in Unreal.",
        "provisional_rule": "Every Cycle02 blockout name must contain PROVISIONAL and be replaceable without changing gameplay socket consumers.",
    }
    write_json(f"{PREFIX}_UNREAL_SOCKET_PIVOT_COLLISION_CONTRACT.json", unreal)

    retain_refine = {
        "gate": PREFIX,
        "retain": [
            "pilot safety volume",
            "rifle muzzle-clearance volume",
            "Igla rear-clearance volume",
            "existing gameplay socket consumers",
            "Cycle04 accepted Yak-52 geometry not superseded by this gate",
        ],
        "refine_provisionally": [
            "GEO_GunnerRifleTopRail to standard coupon where visually applicable",
            "GEO_GunnerForearm and hand components as replaceable anatomy blockout",
            "9K38 missile envelope as a new separate provisional mesh",
            "Shahed exterior envelope as a provisional silhouette mesh",
        ],
        "replace_after_identity": [
            "GEO_GunnerRifleReceiver",
            "GEO_GunnerRifleBarrel",
            "GEO_GunnerRifleHandguard",
            "GEO_GunnerRifleMagazine",
            "GEO_GunnerRifleStock",
            "GEO_GunnerRifleFrontSight",
            "GEO_GunnerRifleRearSight_L",
            "GEO_GunnerRifleRearSight_R",
            "GEO_GunnerRifleRearSightAperture",
            "GEO_IglaLauncherTube",
            "GEO_IglaBattery",
            "GEO_IglaSight",
            "GEO_IglaGrip",
            "GEO_IglaFrontCap",
            "GEO_IglaRearCap",
        ],
        "do_not_promote": [
            "WebGame rifle, glove, sleeve and Igla proxies",
            "engine-cylinder missile",
            "procedural Shahed proxy as final art",
        ],
    }
    write_json(f"{PREFIX}_RETAIN_REFINE_REPLACE_MATRIX.json", retain_refine)

    rubric = {
        "gate": PREFIX,
        "blockout_acceptance": [
            "matches only accepted family/envelope evidence",
            "contains PROVISIONAL naming",
            "dimension report passes",
            "no unsupported make/model markings",
            "hand silhouette has palm, articulated fingers, thumb, knuckle plane and cuff",
            "no weapon/hand/cockpit interpenetration",
            "ADS axis is geometrically coherent without a UI reticle",
            "Igla missile forward end and export axis are unambiguous",
            "Shahed wingspan and length match the frozen envelope",
        ],
        "automatic_rejection": [
            "claims Colt M4A1, AK-74, 9K338 or another exact identity",
            "mixes Igla variants",
            "adds ammunition or chambering details",
            "labels a fabricated character vector as a NASA percentile",
            "adds invented Shahed cross-sections",
            "removes or overwrites accepted runtime assets",
        ],
    }
    write_json(f"{PREFIX}_VISUAL_ACCEPTANCE_RUBRIC.json", rubric)

    blender_prompt = """Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\\Skyguard52`.

Treat the Cycle02 freeze as immutable. Perform one offline Blender design-and-production gate for provisional blockouts only. Do not launch Unreal, import assets, invoke external AI models, or modify accepted runtime assets.

Authorized objects:

1. A MIL-STD-1913 validation coupon using the frozen standard dimensions.
2. A replaceable `PROVISIONAL_AR_M4_FAMILY_RIFLE_BLOCKOUT` constrained only by the visible footage cues: continuous top rail, ventilated free-float handguard family, provisional open-tine muzzle silhouette and provisional rear aperture. Do not finalize receiver, stock, magazine, controls, barrel length, chambering, sights, markings or manufacturer.
3. A separate `PROVISIONAL_9K38_MISSILE_ENVELOPE` at exactly 1574 mm length and 72 mm body diameter. Do not build the launcher, gripstock, battery, sight, caps or markings.
4. A replaceable rear-gunner hand/forearm mannequin constrained by the NASA accommodation envelope and frozen footage poses. Do not claim a measured percentile or exact equipment product.
5. A `PROVISIONAL_SHAHED136_ENVELOPE` at exactly 3300 mm length and 3000 mm wingspan. Do not invent airfoil, cross-section, propeller or internal dimensions.

Before launching Blender, verify every Cycle02 hash and confirm no heavy process is active. Create a fresh namespace, launch Blender exactly once, run no Unreal process concurrently, never retry automatically, and preserve stdout, stderr, source, blend, exports, dimension receipts and renders.

Produce separate objects and collections with documented axes, pivots and provisional sockets. Do not combine the rifle, Igla missile, hands or Shahed into accepted production assets.

Classify each blockout as `PASSED_PROVISIONAL_BLOCKOUT`, `FAILED_WITH_EVIDENCE`, or `AWAITING_VISUAL_REVIEW`. Stop without Unreal import.
"""
    write_text(f"{PREFIX}_NEXT_BLENDER_BLOCKOUT_PROMPT.md", blender_prompt)

    report = """# Combat Asset Reference Resolution — Cycle 02

## Outcome

`PARTIAL_READY_WITH_BLOCKED_ASSET_FAMILIES`

Fifty-two original-resolution frames and six lossless rifle crops were extracted from the governed onboard video. The footage proves an AR/M4-pattern family with a continuous top rail, long ventilated free-float handguard and open-tine muzzle silhouette. It does not expose the receiver controls, magazine, stock or markings well enough to prove an exact weapon configuration.

The project contains no previous decision between 9K38 Igla and 9K338 Igla-S. Cycle02 recommends 9K38 because it matches current naming and has the strongest frozen dimension authority. Only its 1,574 mm by 72 mm missile envelope may proceed before explicit variant acceptance.

NASA supplies an accommodation envelope rather than a coherent 50th-percentile male vector. Hands and forearms may proceed as replaceable blockouts, but final character dimensions, equipment and poses remain subject to a dedicated identity/reference gate.

The Shahed-136 may proceed only as a 3,300 mm by 3,000 mm official-reported envelope. No measured cross-sections, airfoil stations or propeller geometry were found.

No Blender, Unreal, compiler or external AI model was launched.
"""
    write_text(f"{PREFIX}_REPORT.md", report)

    members = sorted(
        [record(path) for path in ROOT.rglob("*") if path.is_file()],
        key=lambda item: str(item["path"]),
    )
    freeze = {
        "gate": PREFIX,
        "created_at_utc": created_at,
        "classification": "PARTIAL_READY_WITH_BLOCKED_ASSET_FAMILIES",
        "blender_execution_authorized": False,
        "unreal_execution_authorized": False,
        "external_ai_models_invoked": False,
        "heavy_processes_launched": 0,
        "member_count": len(members),
        "members": members,
    }
    freeze_path = ROOT / f"{PREFIX}_FREEZE.json"
    freeze_path.write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")

    publish = {
        "source_root": str(ROOT),
        "archive_destination": r"D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02",
        "conventional_copies": [
            {
                "source": f"{PREFIX}_FREEZE.json",
                "destination": rf"D:\Skyguard52\Docs\AAA_Review\{PREFIX}_FREEZE.json",
            },
            {
                "source": f"reports/{PREFIX}_REPORT.md",
                "destination": rf"D:\Skyguard52\Docs\AAA_Review\{PREFIX}_REPORT.md",
            },
            {
                "source": f"reports/{PREFIX}_NEXT_BLENDER_BLOCKOUT_PROMPT.md",
                "destination": rf"D:\Skyguard52\Docs\AAA_Review\NEXT_PROMPT_{PREFIX}_BLENDER_BLOCKOUT.md",
            },
            {
                "source": f"reports/{PREFIX}_READINESS.json",
                "destination": rf"D:\Skyguard52\Saved\Reports\{PREFIX}_READINESS.json",
            },
            {
                "source": f"reports/{PREFIX}_RIFLE_IDENTITY_DECISION.json",
                "destination": rf"D:\Skyguard52\Saved\Reports\{PREFIX}_RIFLE_IDENTITY_DECISION.json",
            },
            {
                "source": f"reports/{PREFIX}_IGLA_PROJECT_DECISION.json",
                "destination": rf"D:\Skyguard52\Saved\Reports\{PREFIX}_IGLA_PROJECT_DECISION.json",
            },
        ],
    }
    (ROOT / "publish_manifest.json").write_text(json.dumps(publish, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"root": str(ROOT), "classification": freeze["classification"], "members": len(members)}, indent=2))


if __name__ == "__main__":
    main()
