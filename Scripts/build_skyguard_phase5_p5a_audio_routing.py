"""Build the source-independent Phase 5 P5-A audio routing scaffold.

Run only inside Unreal Editor Python. This script creates no SoundWave, imports
no file, downloads nothing, and never upgrades a missing source to production.
It is safe to rerun: existing correctly typed assets are reused, and an existing
production bank's entries are preserved.
"""

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
    Path(ATTEMPT_DIRECTORY) / "build_receipt.json"
    if ATTEMPT_DIRECTORY
    else ROOT / "Saved/Reports/PHASE5_P5A_ROUTING_BUILD.json"
)
EXPECTED_IDENTITY_CATEGORIES = {
    "EngineIdle": unreal.SkyguardProductionAudioCategory.ENGINE_IDLE,
    "EngineCruise": unreal.SkyguardProductionAudioCategory.ENGINE_CRUISE,
    "EnginePower": unreal.SkyguardProductionAudioCategory.ENGINE_POWER,
    "Propeller": unreal.SkyguardProductionAudioCategory.PROPELLER,
    "OpenCockpitWind": unreal.SkyguardProductionAudioCategory.OPEN_COCKPIT_WIND,
}


def split_asset_path(asset_path):
    package_path, asset_name = asset_path.rsplit("/", 1)
    return package_path, asset_name


def class_name(asset):
    return asset.get_class().get_name() if asset is not None else ""


def ensure_asset(asset_path, expected_class, factory_class):
    existing = unreal.EditorAssetLibrary.load_asset(asset_path)
    if existing is not None:
        if class_name(existing) != expected_class.__name__:
            raise RuntimeError(
                "Existing asset has wrong class: %s expected=%s actual=%s"
                % (asset_path, expected_class.__name__, class_name(existing))
            )
        return existing, False

    package_path, asset_name = split_asset_path(asset_path)
    unreal.EditorAssetLibrary.make_directory(package_path)
    factory = factory_class()
    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, package_path, expected_class, factory
    )
    if asset is None:
        raise RuntimeError("Could not create routing asset: " + asset_path)
    return asset, True


def ensure_production_bank(asset_path):
    existing = unreal.EditorAssetLibrary.load_asset(asset_path)
    expected_class = unreal.SkyguardAudioProductionBank
    if existing is not None:
        if class_name(existing) != expected_class.__name__:
            raise RuntimeError(
                "Existing production bank has wrong class: %s" % asset_path
            )
        # Never reset an existing bank: later sourced entries are authoritative.
        return existing, False

    package_path, asset_name = split_asset_path(asset_path)
    unreal.EditorAssetLibrary.make_directory(package_path)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", expected_class)
    bank = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, package_path, expected_class, factory
    )
    if bank is None:
        raise RuntimeError("Could not create production bank: " + asset_path)
    bank.initialize_required_entries()
    return bank, True


def assert_identity_placeholders_are_honest(bank):
    entries = list(bank.get_editor_property("entries") or [])
    matches = {}
    for category, enum_value in EXPECTED_IDENTITY_CATEGORIES.items():
        candidates = [
            entry
            for entry in entries
            if entry.get_editor_property("category") == enum_value
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                "Production bank requires exactly one P5-A entry: " + category
            )
        matches[category] = candidates[0]
    for category, entry in matches.items():
        if (
            entry.get_editor_property("source_status")
            == unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
        ):
            if entry.get_editor_property("sound"):
                raise RuntimeError(
                    "Missing-source identity entry has a Sound binding: " + category
                )
            if str(entry.get_editor_property("provenance_id")) not in ("", "None"):
                raise RuntimeError(
                    "Missing-source identity entry has provenance: " + category
                )
            if str(entry.get_editor_property("source_sha256")):
                raise RuntimeError(
                    "Missing-source identity entry has a source hash: " + category
                )


def assert_master_children(master, children):
    actual = list(master.get_editor_property("child_submixes") or [])
    if not {asset.get_path_name() for asset in children}.issubset(
        {asset.get_path_name() for asset in actual}
    ):
        raise RuntimeError("Master submix child topology did not persist")


def set_bank_routing(bank, assets, contract):
    routing = unreal.SkyguardProductionAudioRouting()
    routing.set_editor_property("master_submix", assets["MasterSubmix"])
    routing.set_editor_property("cockpit_submix", assets["CockpitSubmix"])
    routing.set_editor_property("exterior_submix", assets["ExteriorSubmix"])
    routing.set_editor_property("weapons_submix", assets["WeaponsSubmix"])
    routing.set_editor_property("explosions_submix", assets["ExplosionsSubmix"])
    routing.set_editor_property("radio_submix", assets["RadioSubmix"])
    routing.set_editor_property("cockpit_sound_mix", assets["CockpitSoundMix"])
    defaults = contract["routing_defaults"]
    routing.set_editor_property(
        "cockpit_exterior_attenuation",
        float(defaults["cockpit_exterior_attenuation"]),
    )
    routing.set_editor_property(
        "cockpit_low_pass_hz", float(defaults["cockpit_low_pass_hz"])
    )
    bank.set_editor_property("routing", routing)


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assets = {}
    created = []
    for spec in contract["routing_assets"]:
        if spec["asset_class"] == "SoundSubmix":
            asset, was_created = ensure_asset(
                spec["asset_path"], unreal.SoundSubmix, unreal.SoundSubmixFactory
            )
        elif spec["asset_class"] == "SoundMix":
            asset, was_created = ensure_asset(
                spec["asset_path"], unreal.SoundMix, unreal.SoundMixFactory
            )
        else:
            raise RuntimeError("Unsupported routing class: " + spec["asset_class"])
        assets[spec["contract_name"]] = asset
        if was_created:
            created.append(spec["asset_path"])

    children = [
        assets[name]
        for name in (
            "CockpitSubmix",
            "ExteriorSubmix",
            "WeaponsSubmix",
            "ExplosionsSubmix",
            "RadioSubmix",
        )
    ]
    bank, bank_created = ensure_production_bank(
        contract["production_bank"]["asset_path"]
    )
    assert_identity_placeholders_are_honest(bank)
    set_bank_routing(bank, assets, contract)
    if not bank.configure_routing_topology():
        raise RuntimeError("Native submix parent configuration failed")
    assert_master_children(assets["MasterSubmix"], children)

    for spec in contract["routing_assets"]:
        unreal.EditorAssetLibrary.save_asset(spec["asset_path"], False)
    unreal.EditorAssetLibrary.save_asset(
        contract["production_bank"]["asset_path"], False
    )

    audit = bank.evaluate_readiness()
    result = {
        "schema": "skyguard.phase5.p5a-routing-build-receipt.v1",
        "wave_id": contract["wave_id"],
        "routing_asset_count": len(assets),
        "routing_assets_created_this_run": created,
        "production_bank_created_this_run": bank_created,
        "identity_placeholder_count": len(EXPECTED_IDENTITY_CATEGORIES),
        "required_category_count": int(audit.required_category_count),
        "bound_production_source_count": int(audit.bound_production_source_count),
        "explicit_missing_source_count": int(audit.explicit_missing_source_count),
        "missing_routing_assets": [str(value) for value in audit.missing_routing_assets],
        "category_contract_complete": bool(audit.category_contract_complete),
        "production_ready": bool(audit.production_ready),
        "status": (
            "P5A_ROUTING_SCAFFOLD_BUILT_SOURCES_STILL_MISSING"
            if not audit.production_ready
            else "FULL_PRODUCTION_BANK_ALREADY_READY"
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
