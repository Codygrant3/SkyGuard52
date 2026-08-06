"""Fresh-process serialized audit for Phase 5 routing primitives."""

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
    Path(ATTEMPT_DIRECTORY) / "fresh_audit.json"
    if ATTEMPT_DIRECTORY
    else ROOT / "Saved" / "Reports" / "PHASE5_ROUTING_PRIMITIVES_FRESH_AUDIT.json"
)
BANK_PATH = "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"


def class_name(asset):
    return asset.get_class().get_name() if asset is not None else ""


def enum_value(enum_type, contract_name):
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", contract_name).upper()
    return getattr(enum_type, snake)


def nearly_equal(left, right):
    return abs(float(left) - float(right)) <= 0.01


def main():
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    briefs = json.loads(BRIEFS_PATH.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    errors = []
    attenuation_assets = {}
    for spec in specs["attenuation"]:
        path = runtime["attenuation_asset_root"] + "/ATT_" + spec["name"]
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None or class_name(asset) != "SoundAttenuation":
            errors.append("missing/wrong attenuation asset: " + spec["name"])
            continue
        settings = asset.get_editor_property("attenuation")
        checks = {
            "attenuate": bool(spec["attenuate"]),
            "spatialize": bool(spec["spatialize"]),
            "attenuate_with_lpf": bool(spec["air_absorption"]),
            "enable_occlusion": bool(spec["occlusion"]),
        }
        for field, expected in checks.items():
            if bool(settings.get_editor_property(field)) != expected:
                errors.append(spec["name"] + ": " + field + " mismatch")
        extents = settings.get_editor_property("attenuation_shape_extents")
        if not nearly_equal(extents.x, spec["inner_radius_cm"]):
            errors.append(spec["name"] + ": inner radius mismatch")
        if not nearly_equal(
            settings.get_editor_property("falloff_distance"),
            spec["falloff_cm"],
        ):
            errors.append(spec["name"] + ": falloff mismatch")
        attenuation_assets[spec["name"]] = asset

    concurrency_assets = {}
    for spec in specs["concurrency"]:
        path = runtime["concurrency_asset_root"] + "/CON_" + spec["name"]
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None or class_name(asset) != "SoundConcurrency":
            errors.append("missing/wrong concurrency asset: " + spec["name"])
            continue
        settings = asset.get_editor_property("concurrency")
        expected_rule = enum_value(
            unreal.MaxConcurrentResolutionRule, spec["resolution_rule"]
        )
        if int(settings.get_editor_property("max_count")) != int(
            spec["max_count"]
        ):
            errors.append(spec["name"] + ": max_count mismatch")
        if settings.get_editor_property("resolution_rule") != expected_rule:
            errors.append(spec["name"] + ": resolution_rule mismatch")
        if not nearly_equal(
            settings.get_editor_property("retrigger_time"),
            spec["retrigger_seconds"],
        ):
            errors.append(spec["name"] + ": retrigger mismatch")
        if not nearly_equal(
            settings.get_editor_property("voice_steal_release_time"),
            spec["voice_steal_release_seconds"],
        ):
            errors.append(spec["name"] + ": voice steal release mismatch")
        concurrency_assets[spec["name"]] = asset

    bank = unreal.EditorAssetLibrary.load_asset(BANK_PATH)
    bank_binding_count = 0
    explicit_missing_count = 0
    if bank is None or class_name(bank) != "SkyguardAudioProductionBank":
        errors.append("production bank missing/wrong class")
        audit = None
    else:
        entries = list(bank.get_editor_property("entries") or [])
        by_category = {
            entry.get_editor_property("category"): entry for entry in entries
        }
        routing_paths = {
            path.rsplit("/", 1)[-1].removeprefix("SMX_") + "Submix": path
            for path in runtime["routing_assets"]
            if "/Submixes/" in path
        }
        for brief in briefs["categories"]:
            category = enum_value(
                unreal.SkyguardProductionAudioCategory, brief["category"]
            )
            entry = by_category.get(category)
            if entry is None:
                errors.append("bank entry missing: " + brief["category"])
                continue
            if (
                entry.get_editor_property("source_status")
                != unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
            ):
                errors.append(
                    "source status crossed truth boundary: " + brief["category"]
                )
            else:
                explicit_missing_count += 1
            if entry.get_editor_property("sound"):
                errors.append(
                    "missing source has Sound binding: " + brief["category"]
                )
            if str(entry.get_editor_property("provenance_id")) not in (
                "",
                "None",
            ):
                errors.append(
                    "missing source has provenance: " + brief["category"]
                )
            if str(entry.get_editor_property("source_sha256")):
                errors.append(
                    "missing source has source hash: " + brief["category"]
                )
            expected_att = attenuation_assets.get(
                brief["attenuation_contract"]
            )
            expected_con = concurrency_assets.get(
                brief["concurrency_contract"]
            )
            expected_submix = unreal.EditorAssetLibrary.load_asset(
                routing_paths[brief["output_submix"]]
            )
            if entry.get_editor_property("attenuation") != expected_att:
                errors.append(
                    "attenuation binding mismatch: " + brief["category"]
                )
            if entry.get_editor_property("concurrency") != expected_con:
                errors.append(
                    "concurrency binding mismatch: " + brief["category"]
                )
            if entry.get_editor_property("output_submix") != expected_submix:
                errors.append(
                    "submix binding mismatch: " + brief["category"]
                )
            if (
                entry.get_editor_property("attenuation") == expected_att
                and entry.get_editor_property("concurrency") == expected_con
                and entry.get_editor_property("output_submix") == expected_submix
            ):
                bank_binding_count += 1
        audit = bank.evaluate_readiness()
        if bool(audit.production_ready):
            errors.append("unsourced routing bank falsely reports production ready")
        if int(audit.bound_production_source_count) != 0:
            errors.append("bank falsely reports a bound production source")
        if int(audit.explicit_missing_source_count) != 25:
            errors.append("bank does not preserve 25 explicit missing sources")

    metasound_present = [
        path
        for path in runtime["metasound_assets"]
        if unreal.EditorAssetLibrary.does_asset_exist(path)
    ]
    if metasound_present:
        errors.append(
            "unverified empty MetaSound shells were created: "
            + ", ".join(metasound_present)
        )

    result = {
        "schema": "skyguard.phase5.routing-primitives-fresh-audit.v1",
        "attenuation_asset_count": len(attenuation_assets),
        "concurrency_asset_count": len(concurrency_assets),
        "bank_routing_binding_count": bank_binding_count,
        "explicit_missing_source_count": explicit_missing_count,
        "metasound_shell_count": len(metasound_present),
        "metasound_state": (
            "DEFERRED_UNTIL_GOVERNED_INTERFACES_CAN_BE_AUTHORED_WITHOUT_FAKE_AUDIO"
        ),
        "production_ready": bool(audit.production_ready) if audit else False,
        "errors": errors,
        "status": (
            "PASS_ROUTING_PRIMITIVES_SOURCES_AND_METASOUNDS_MISSING"
            if not errors
            else "FAIL_ROUTING_PRIMITIVES"
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))
    if errors:
        raise RuntimeError("; ".join(errors))


if __name__ == "__main__":
    main()
