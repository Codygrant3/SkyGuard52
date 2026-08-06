"""Author the governed Phase 5 attenuation and concurrency primitives.

Run only in Unreal Editor Python. This script imports and synthesizes no audio,
does not author misleading MetaSound shells, and preserves every missing source
entry as null/MISSING_SOURCE. It is idempotent and refuses wrong-class assets.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs" / "AAA_Review"
SPECS_PATH = DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
BRIEFS_PATH = DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
RUNTIME_PATH = DOCS / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
ATTEMPT_DIRECTORY = os.environ.get("SKYGUARD_PHASE5_PRIMITIVES_ATTEMPT_DIR")
REPORT_PATH = (
    Path(ATTEMPT_DIRECTORY) / "build_receipt.json"
    if ATTEMPT_DIRECTORY
    else ROOT / "Saved" / "Reports" / "PHASE5_ROUTING_PRIMITIVES_BUILD.json"
)
BANK_PATH = "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"


def class_name(asset):
    return asset.get_class().get_name() if asset is not None else ""


def split_asset_path(asset_path):
    package_path, asset_name = asset_path.rsplit("/", 1)
    return package_path, asset_name


def ensure_asset(asset_path, expected_class, factory_class):
    existing = unreal.EditorAssetLibrary.load_asset(asset_path)
    if existing is not None:
        if class_name(existing) != expected_class.__name__:
            raise RuntimeError(
                "Wrong asset class at %s expected=%s actual=%s"
                % (asset_path, expected_class.__name__, class_name(existing))
            )
        return existing, False
    package_path, asset_name = split_asset_path(asset_path)
    unreal.EditorAssetLibrary.make_directory(package_path)
    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, package_path, expected_class, factory_class()
    )
    if asset is None:
        raise RuntimeError("Could not create " + asset_path)
    return asset, True


def enum_value(enum_type, contract_name):
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", contract_name).upper()
    return getattr(enum_type, snake)


def configure_attenuation(asset, spec):
    settings = asset.get_editor_property("attenuation")
    settings.set_editor_property("attenuate", bool(spec["attenuate"]))
    settings.set_editor_property("spatialize", bool(spec["spatialize"]))
    settings.set_editor_property(
        "attenuation_shape_extents",
        unreal.Vector(float(spec["inner_radius_cm"]), 0.0, 0.0),
    )
    settings.set_editor_property("falloff_distance", float(spec["falloff_cm"]))
    settings.set_editor_property(
        "attenuate_with_lpf", bool(spec["air_absorption"])
    )
    settings.set_editor_property("enable_occlusion", bool(spec["occlusion"]))
    asset.set_editor_property("attenuation", settings)


def configure_concurrency(asset, spec):
    settings = asset.get_editor_property("concurrency")
    settings.set_editor_property("max_count", int(spec["max_count"]))
    settings.set_editor_property(
        "resolution_rule",
        enum_value(
            unreal.MaxConcurrentResolutionRule, spec["resolution_rule"]
        ),
    )
    settings.set_editor_property(
        "retrigger_time", float(spec["retrigger_seconds"])
    )
    settings.set_editor_property(
        "voice_steal_release_time",
        float(spec["voice_steal_release_seconds"]),
    )
    asset.set_editor_property("concurrency", settings)


def assert_and_bind_bank(
    bank, briefs, attenuation_assets, concurrency_assets, routing_paths
):
    entries = list(bank.get_editor_property("entries") or [])
    if len(entries) != 25:
        raise RuntimeError("Production bank must retain exactly 25 entries")
    by_category = {}
    for entry in entries:
        by_category[entry.get_editor_property("category")] = entry

    output_assets = {
        name: unreal.EditorAssetLibrary.load_asset(path)
        for name, path in routing_paths.items()
        if name.endswith("Submix")
    }
    if any(asset is None for asset in output_assets.values()):
        raise RuntimeError("One or more governed output submixes are missing")

    rewritten = []
    for brief in briefs["categories"]:
        category = enum_value(
            unreal.SkyguardProductionAudioCategory, brief["category"]
        )
        entry = by_category.get(category)
        if entry is None:
            raise RuntimeError("Missing production bank category " + brief["category"])
        if (
            entry.get_editor_property("source_status")
            == unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
        ):
            if entry.get_editor_property("sound"):
                raise RuntimeError(
                    "Missing source acquired an unauthorized Sound binding: "
                    + brief["category"]
                )
            if str(entry.get_editor_property("provenance_id")) not in ("", "None"):
                raise RuntimeError(
                    "Missing source acquired provenance: " + brief["category"]
                )
            if str(entry.get_editor_property("source_sha256")):
                raise RuntimeError(
                    "Missing source acquired source hash: " + brief["category"]
                )
        entry.set_editor_property(
            "attenuation",
            attenuation_assets[brief["attenuation_contract"]],
        )
        entry.set_editor_property(
            "concurrency",
            concurrency_assets[brief["concurrency_contract"]],
        )
        entry.set_editor_property(
            "output_submix", output_assets[brief["output_submix"]]
        )
        rewritten.append(entry)
    bank.set_editor_property("entries", rewritten)


def main():
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    briefs = json.loads(BRIEFS_PATH.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    created = []
    attenuation_assets = {}
    for spec in specs["attenuation"]:
        path = (
            runtime["attenuation_asset_root"] + "/ATT_" + spec["name"]
        )
        asset, was_created = ensure_asset(
            path, unreal.SoundAttenuation, unreal.SoundAttenuationFactory
        )
        configure_attenuation(asset, spec)
        attenuation_assets[spec["name"]] = asset
        if was_created:
            created.append(path)
        unreal.EditorAssetLibrary.save_asset(path, False)

    concurrency_assets = {}
    for spec in specs["concurrency"]:
        path = (
            runtime["concurrency_asset_root"] + "/CON_" + spec["name"]
        )
        asset, was_created = ensure_asset(
            path, unreal.SoundConcurrency, unreal.SoundConcurrencyFactory
        )
        configure_concurrency(asset, spec)
        concurrency_assets[spec["name"]] = asset
        if was_created:
            created.append(path)
        unreal.EditorAssetLibrary.save_asset(path, False)

    bank = unreal.EditorAssetLibrary.load_asset(BANK_PATH)
    if bank is None or class_name(bank) != "SkyguardAudioProductionBank":
        raise RuntimeError("Governed production bank is missing or wrong class")
    routing_paths = {
        path.rsplit("/", 1)[-1].removeprefix("SMX_") + "Submix": path
        for path in runtime["routing_assets"]
        if "/Submixes/" in path
    }
    assert_and_bind_bank(
        bank,
        briefs,
        attenuation_assets,
        concurrency_assets,
        routing_paths,
    )
    unreal.EditorAssetLibrary.save_asset(BANK_PATH, False)

    audit = bank.evaluate_readiness()
    result = {
        "schema": "skyguard.phase5.routing-primitives-build.v1",
        "attenuation_asset_count": len(attenuation_assets),
        "concurrency_asset_count": len(concurrency_assets),
        "created_this_run": created,
        "metasound_shell_count": 0,
        "metasound_state": (
            "DEFERRED_NO_EMPTY_OR_PROCEDURAL_PRODUCTION_SHELLS"
        ),
        "required_category_count": int(audit.required_category_count),
        "bound_production_source_count": int(
            audit.bound_production_source_count
        ),
        "explicit_missing_source_count": int(
            audit.explicit_missing_source_count
        ),
        "production_ready": bool(audit.production_ready),
        "status": "ROUTING_PRIMITIVES_BUILT_SOURCES_AND_METASOUNDS_MISSING",
    }
    if result["explicit_missing_source_count"] != 25:
        raise RuntimeError(
            "Expected all 25 source bindings to remain explicitly missing"
        )
    if result["bound_production_source_count"] != 0 or result["production_ready"]:
        raise RuntimeError("Routing-only build crossed the source truth boundary")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
