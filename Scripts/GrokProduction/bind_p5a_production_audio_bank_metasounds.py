"""Bind governed PROCEDURAL_QA_TEST_ONLY MetaSound scaffolds to the P5-A bank.

These bindings are explicit QA scaffolds. They are never classified as authentic
recordings, licensed production sources, or production-ready audio.
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from pathlib import Path

try:
    import unreal
except ModuleNotFoundError:
    unreal = None


ROOT = Path(r"D:\Skyguard52")
BANK_PATH = "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"
METASOUND_ROOT = "/Game/Skyguard/Audio/Production/MetaSounds"
READINESS = ROOT / r"Docs\Toolchain\SKYGUARD_AUDIO_SLOT_READYNESS.json"
ATTEMPT = ROOT / r"Saved\BuildAttempts\P5A_PRODUCTION_AUDIO_BANK_METASOUND_BINDINGS01\attempt_01"
RECEIPT = ATTEMPT / "binding_receipt.json"
QA_STATUS = "PROCEDURAL_QA_TEST_ONLY"

BINDINGS = {
    "EngineIdle": "MS_Yak52IdentityBed",
    "EngineCruise": "MS_Yak52IdentityBed",
    "EnginePower": "MS_Yak52IdentityBed",
    "Propeller": "MS_Yak52IdentityBed",
    "OpenCockpitWind": "MS_Yak52IdentityBed",
    "RifleMuzzle": "MS_RifleShot",
    "RifleMechanical": "MS_RifleShot",
    "RifleCasing": "MS_RifleShot",
    "RifleReflection": "MS_RifleShot",
    "IglaSearch": "MS_IglaWeapon",
    "IglaLock": "MS_IglaWeapon",
    "IglaLaunch": "MS_IglaWeapon",
    "IglaFlyby": "MS_IglaWeapon",
    "IglaImpact": "MS_IglaWeapon",
    "DroneLightMotor": "MS_DronePropulsion",
    "DroneHeavyMotor": "MS_DronePropulsion",
    "DroneFlyby": "MS_DronePropulsion",
    "ExplosionSmallCrack": "MS_ExplosionSmall",
    "ExplosionSmallBody": "MS_ExplosionSmall",
    "ExplosionSmallDebris": "MS_ExplosionSmall",
    "ExplosionSmallTail": "MS_ExplosionSmall",
    "ExplosionHeavyCrack": "MS_ExplosionHeavy",
    "ExplosionHeavyBody": "MS_ExplosionHeavy",
    "ExplosionHeavyDebris": "MS_ExplosionHeavy",
    "ExplosionHeavyTail": "MS_ExplosionHeavy",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def enum_member(enum_type: object, contract_name: str) -> object:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", contract_name).upper()
    return getattr(enum_type, snake)


def asset_disk_path(asset_path: str) -> Path:
    return ROOT / "Content" / (asset_path.removeprefix("/Game/") + ".uasset")


def run_offline_contract_test() -> int:
    require(READINESS.is_file(), f"Audio readiness JSON missing: {READINESS}")
    data = json.loads(READINESS.read_text(encoding="utf-8"))
    require(data.get("schema") == "skyguard.audio-slot-readiness.v1", "Readiness schema mismatch")
    categories = {row.get("category") for row in data.get("categories", [])}
    require(categories == set(BINDINGS), "Readiness categories do not match the 25 binding categories")
    graph_names = {row.get("asset") for row in data.get("metasound_scaffolds", {}).get("graphs", [])}
    require(graph_names == set(BINDINGS.values()), "Readiness MetaSound graph set mismatch")
    for asset_name in sorted(set(BINDINGS.values())):
        disk = asset_disk_path(f"{METASOUND_ROOT}/{asset_name}")
        require(disk.is_file(), f"MetaSound scaffold missing on disk: {disk}")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_P5A_PRODUCTION_AUDIO_BANK_METASOUND_BINDINGS01_OFFLINE_CONTRACT")
    return 0


def class_name(asset: object) -> str:
    return asset.get_class().get_name() if asset is not None else ""


def update_readiness_status() -> None:
    data = json.loads(READINESS.read_text(encoding="utf-8"))
    require(data.get("schema") == "skyguard.audio-slot-readiness.v1", "Readiness schema changed")
    data["metasound_scaffolds"]["status"] = "procedural_qa_test_only_bound_not_authentic"
    data["binding_plan"]["status"] = "BOUND_PROCEDURAL_QA_TEST_ONLY_NOT_AUTHENTIC"
    data["binding_plan"]["last_receipt"] = str(RECEIPT)
    graph_by_name = {
        row["asset"]: row for row in data["metasound_scaffolds"].get("graphs", [])
    }
    category_by_name = {row["category"]: row for row in data.get("categories", [])}
    for category, asset_name in BINDINGS.items():
        require(category in category_by_name, f"Readiness category missing: {category}")
        require(asset_name in graph_by_name, f"Readiness graph missing: {asset_name}")
        row = category_by_name[category]
        row["source_status_current"] = QA_STATUS
        row["binding_status"] = "BOUND_PROCEDURAL_QA_TEST_ONLY_NOT_AUTHENTIC"
        row["sound_binding"] = f"{METASOUND_ROOT}/{asset_name}"
        row["authentic_source"] = False
    for graph in graph_by_name.values():
        graph["binding_status"] = "BOUND_PROCEDURAL_QA_TEST_ONLY_NOT_AUTHENTIC"
    write_json_atomic(READINESS, data)


def run_unreal() -> None:
    require(unreal is not None, "This mode must run inside Unreal Editor Python")
    result: dict[str, object] = {
        "schema": "skyguard.p5a-production-audio-bank.metasound-bindings01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "bank": BANK_PATH,
        "source_status": QA_STATUS,
        "authentic_source_count": 0,
        "procedural_qa_test_only_count": 0,
        "ensure_default_entries_called": False,
        "bindings": [],
        "readiness_json": str(READINESS),
        "error": None,
        "traceback": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=True)
        bank = unreal.EditorAssetLibrary.load_asset(BANK_PATH)
        require(bank is not None, f"Production bank missing: {BANK_PATH}")
        require(class_name(bank) == "SkyguardAudioProductionBank", f"Wrong bank class: {class_name(bank)}")

        ensure_defaults = getattr(bank, "ensure_default_entries", None)
        if callable(ensure_defaults):
            ensure_defaults()
            result["ensure_default_entries_called"] = True

        assets: dict[str, object] = {}
        for asset_name in sorted(set(BINDINGS.values())):
            asset_path = f"{METASOUND_ROOT}/{asset_name}"
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"MetaSound scaffold missing: {asset_path}")
            require(
                isinstance(asset, unreal.SoundBase) or class_name(asset) == "MetaSoundSource",
                f"MetaSound is not a SoundBase-compatible asset: {asset_path} class={class_name(asset)}",
            )
            assets[asset_name] = asset

        entries = list(bank.get_editor_property("entries") or [])
        require(len(entries) == 25, f"Production bank must contain exactly 25 entries, observed {len(entries)}")
        entry_by_category = {entry.get_editor_property("category"): entry for entry in entries}
        rewritten: list[object] = []
        binding_rows: list[dict[str, object]] = []
        for category_name, asset_name in BINDINGS.items():
            category = enum_member(unreal.SkyguardProductionAudioCategory, category_name)
            entry = entry_by_category.get(category)
            require(entry is not None, f"Production bank category missing: {category_name}")
            entry.set_editor_property("sound", assets[asset_name])
            entry.set_editor_property(
                "source_status", unreal.SkyguardAudioSourceStatus.PROCEDURAL_QA_TEST_ONLY
            )
            entry.set_editor_property("provenance_id", f"PROCEDURAL_QA_TEST_ONLY_{asset_name}")
            entry.set_editor_property("source_sha256", "")
            rewritten.append(entry)
            binding_rows.append(
                {
                    "category": category_name,
                    "sound": f"{METASOUND_ROOT}/{asset_name}",
                    "source_status": QA_STATUS,
                    "authentic": False,
                }
            )
        require(len(rewritten) == 25, "Not all production audio entries were rewritten")
        bank.set_editor_property("entries", rewritten)
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bank, only_if_is_dirty=False)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(bank)

        verify_entries = list(bank.get_editor_property("entries") or [])
        qa_count = 0
        for entry in verify_entries:
            require(entry.get_editor_property("sound"), "Saved bank contains an unbound sound entry")
            require(
                entry.get_editor_property("source_status")
                == unreal.SkyguardAudioSourceStatus.PROCEDURAL_QA_TEST_ONLY,
                "Saved bank contains a non-QA source status",
            )
            qa_count += 1
        audit = bank.evaluate_readiness()
        require(int(audit.qa_test_only_count) == 25, "Bank audit does not report 25 QA-only entries")
        require(not bool(audit.production_ready), "QA-only bank must never report production ready")

        result["bindings"] = binding_rows
        result["procedural_qa_test_only_count"] = qa_count
        result["audit"] = {
            "required_category_count": int(audit.required_category_count),
            "qa_test_only_count": int(audit.qa_test_only_count),
            "production_ready": bool(audit.production_ready),
        }
        update_readiness_status()
        result["classification"] = "PASSED_P5A_METASOUNDS_BOUND_PROCEDURAL_QA_TEST_ONLY_NOT_AUTHENTIC"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
        return
    raise RuntimeError(result["error"] or result["classification"])


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
