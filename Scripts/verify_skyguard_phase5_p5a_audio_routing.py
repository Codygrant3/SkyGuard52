"""Fresh-process Unreal persistence audit for the P5-A routing scaffold."""

import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_P5A_IDENTITY_BED_ROUTING_CONTRACT.json"
)
ATTEMPT_DIRECTORY = os.environ.get("SKYGUARD_P5A_ATTEMPT_DIR")
REPORT_PATH = (
    Path(ATTEMPT_DIRECTORY) / "fresh_audit.json"
    if ATTEMPT_DIRECTORY
    else ROOT / "Saved/Reports/PHASE5_P5A_ROUTING_FRESH_AUDIT.json"
)
IDENTITY_ENUMS = {
    "EngineIdle": unreal.SkyguardProductionAudioCategory.ENGINE_IDLE,
    "EngineCruise": unreal.SkyguardProductionAudioCategory.ENGINE_CRUISE,
    "EnginePower": unreal.SkyguardProductionAudioCategory.ENGINE_POWER,
    "Propeller": unreal.SkyguardProductionAudioCategory.PROPELLER,
    "OpenCockpitWind": unreal.SkyguardProductionAudioCategory.OPEN_COCKPIT_WIND,
}


def class_name(asset):
    return asset.get_class().get_name() if asset is not None else ""


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors = []
    assets = {}
    for spec in contract["routing_assets"]:
        asset = unreal.EditorAssetLibrary.load_asset(spec["asset_path"])
        if asset is None:
            errors.append("missing routing asset: " + spec["contract_name"])
            continue
        if class_name(asset) != spec["asset_class"]:
            errors.append("wrong routing class: " + spec["contract_name"])
            continue
        assets[spec["contract_name"]] = asset

    if "MasterSubmix" in assets:
        actual_children = {
            child.get_path_name()
            for child in list(
                assets["MasterSubmix"].get_editor_property("child_submixes") or []
            )
        }
        required_children = {
            assets[name].get_path_name()
            for name in (
                "CockpitSubmix",
                "ExteriorSubmix",
                "WeaponsSubmix",
                "ExplosionsSubmix",
                "RadioSubmix",
            )
            if name in assets
        }
        if not required_children.issubset(actual_children):
            errors.append("master submix child topology incomplete")

    bank_path = contract["production_bank"]["asset_path"]
    bank = unreal.EditorAssetLibrary.load_asset(bank_path)
    if bank is None or class_name(bank) != "SkyguardAudioProductionBank":
        errors.append("production bank missing or wrong class")
        audit = None
    else:
        entries = list(bank.get_editor_property("entries") or [])
        for category, enum_value in IDENTITY_ENUMS.items():
            candidates = [
                entry
                for entry in entries
                if entry.get_editor_property("category") == enum_value
            ]
            if len(candidates) != 1:
                errors.append("identity entry count invalid: " + category)
                continue
            entry = candidates[0]
            if (
                entry.get_editor_property("source_status")
                != unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
            ):
                errors.append("identity source no longer explicitly missing: " + category)
            if entry.get_editor_property("sound"):
                errors.append("missing identity source has Sound binding: " + category)
            if str(entry.get_editor_property("source_sha256")):
                errors.append("missing identity source has hash: " + category)
        audit = bank.evaluate_readiness()
        if int(audit.required_category_count) != 25:
            errors.append("production bank no longer contains 25 required categories")
        if list(audit.missing_routing_assets):
            errors.append("production bank reports missing routing assets")
        if bool(audit.production_ready):
            errors.append("unsourced identity bank falsely reports production ready")

    result = {
        "schema": "skyguard.phase5.p5a-routing-fresh-audit.v1",
        "routing_asset_count": len(assets),
        "identity_missing_source_count": 5 if not errors and audit else 0,
        "bound_production_source_count": (
            int(audit.bound_production_source_count) if audit else 0
        ),
        "explicit_missing_source_count": (
            int(audit.explicit_missing_source_count) if audit else 0
        ),
        "production_ready": bool(audit.production_ready) if audit else False,
        "errors": errors,
        "status": (
            "P5A_ROUTING_FRESH_AUDIT_PASS_SOURCES_MISSING"
            if not errors
            else "P5A_ROUTING_FRESH_AUDIT_FAIL"
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))
    if errors:
        raise RuntimeError("; ".join(errors))


if __name__ == "__main__":
    main()
