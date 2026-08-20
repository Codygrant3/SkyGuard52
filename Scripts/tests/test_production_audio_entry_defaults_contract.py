from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardAudioProductionBank.h"
LOCKED = {
    "SkyguardAudioProductionBank.h",
    "SkyguardAudioProductionBank.cpp",
    "SkyguardAudioProductionBankTests.cpp",
    "SkyguardAudioProductionBankEmptyFailClosedTests.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
}
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_production_audio_routing_defaults_contract.py",
    "Scripts/tests/test_production_audio_audit_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audible_acceptance_receipt_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "ESkyguardProductionAudioCategory Category = "
    "ESkyguardProductionAudioCategory::EngineIdle;",
    "FText DisplayName;",
    "ESkyguardAudioSourceStatus SourceStatus = "
    "ESkyguardAudioSourceStatus::MISSING_SOURCE;",
    "TSoftObjectPtr<USoundBase> Sound;",
    "TSoftObjectPtr<USoundAttenuation> Attenuation;",
    "TSoftObjectPtr<USoundConcurrency> Concurrency;",
    "TSoftObjectPtr<USoundSubmixBase> OutputSubmix;",
    "FName ProvenanceId;",
    "FString SourceSha256;",
)
IN_CLASS_DEFAULTS = {
    "Category": "ESkyguardProductionAudioCategory::EngineIdle",
    "SourceStatus": "ESkyguardAudioSourceStatus::MISSING_SOURCE",
}
FIELDS_WITHOUT_DEFAULTS = (
    "DisplayName",
    "Sound",
    "Attenuation",
    "Concurrency",
    "OutputSubmix",
    "ProvenanceId",
    "SourceSha256",
)
# Historical Rifle / Igla names stay on ESkyguardProductionAudioCategory.
# This contract locks only the FSkyguardProductionAudioEntry EngineIdle default.
RIFLE_IGLA_NOT_LIVE_WEAPONS = (
    "RifleMuzzle",
    "RifleMechanical",
    "RifleCasing",
    "RifleReflection",
    "IglaSearch",
    "IglaLock",
    "IglaLaunch",
    "IglaFlyby",
    "IglaImpact",
)
CATEGORY_ENUMERATORS_NOT_LOCKED = (
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
    *RIFLE_IGLA_NOT_LIVE_WEAPONS,
    "DroneLightMotor",
    "DroneHeavyMotor",
    "DroneFlyby",
    "ExplosionSmallCrack",
    "ExplosionSmallBody",
    "ExplosionSmallDebris",
    "ExplosionSmallTail",
    "ExplosionHeavyCrack",
    "ExplosionHeavyBody",
    "ExplosionHeavyDebris",
    "ExplosionHeavyTail",
)
# USkyguardAudioProductionBank empty EvaluateReadiness belongs to #142.
BANK_OWNED_BY_142 = (
    "EvaluateReadiness",
    "InitializeRequiredEntries",
    "EnsureDefaultEntries",
    "ConfigureRoutingTopology",
    "GetUnboundRequiredCategories",
    "GetRequiredCategories",
    "GetCategoryDisplayName",
)
SIBLING_STRUCTS = (
    "FSkyguardProductionAudioRouting",
    "FSkyguardProductionAudioAudit",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def entry_body(header: str) -> str:
    start = header.index("struct FSkyguardProductionAudioEntry")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(
            r"(?:ESkyguardProductionAudioCategory|ESkyguardAudioSourceStatus)"
            r"\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class ProductionAudioEntryDefaultsContractTests(unittest.TestCase):
    def test_entry_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardProductionAudioEntry", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", entry_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 9)
        self.assertEqual(body.count("EditAnywhere, BlueprintReadWrite"), 9)
        self.assertIn("FText DisplayName;", body)
        self.assertIn("TSoftObjectPtr<USoundBase> Sound;", body)
        self.assertIn("TSoftObjectPtr<USoundAttenuation> Attenuation;", body)
        self.assertIn("TSoftObjectPtr<USoundConcurrency> Concurrency;", body)
        self.assertIn("TSoftObjectPtr<USoundSubmixBase> OutputSubmix;", body)
        self.assertIn("FName ProvenanceId;", body)
        self.assertIn("FString SourceSha256;", body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Category"),
            "ESkyguardProductionAudioCategory::EngineIdle",
        )
        self.assertEqual(
            defaults.get("SourceStatus"),
            "ESkyguardAudioSourceStatus::MISSING_SOURCE",
        )
        self.assertIn(
            "ESkyguardProductionAudioCategory Category = "
            "ESkyguardProductionAudioCategory::EngineIdle;",
            body,
        )
        self.assertIn(
            "ESkyguardAudioSourceStatus SourceStatus = "
            "ESkyguardAudioSourceStatus::MISSING_SOURCE;",
            body,
        )
        self.assertEqual(
            re.findall(r"ESkyguardProductionAudioCategory::(\w+)", body),
            ["EngineIdle"],
        )
        self.assertEqual(
            re.findall(r"ESkyguardAudioSourceStatus::(\w+)", body),
            ["MISSING_SOURCE"],
        )

    def test_struct_does_not_invent_string_soft_path_or_index_none(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FSoftObjectPath", body)
        self.assertNotIn("nullptr", body)
        self.assertNotIn('TEXT("")', body)
        self.assertNotIn('= ""', body)
        for name in FIELDS_WITHOUT_DEFAULTS:
            self.assertNotIn(f"{name} =", body)
            self.assertNotIn(name, defaults)
        self.assertIn("FText DisplayName;", body)
        self.assertIn("TSoftObjectPtr<USoundBase> Sound;", body)
        self.assertIn("TSoftObjectPtr<USoundAttenuation> Attenuation;", body)
        self.assertIn("TSoftObjectPtr<USoundConcurrency> Concurrency;", body)
        self.assertIn("TSoftObjectPtr<USoundSubmixBase> OutputSubmix;", body)
        self.assertIn("FName ProvenanceId;", body)
        self.assertIn("FString SourceSha256;", body)
        self.assertNotIn("FText DisplayName =", body)
        self.assertNotIn("TSoftObjectPtr<USoundBase> Sound =", body)
        self.assertNotIn("TSoftObjectPtr<USoundAttenuation> Attenuation =", body)
        self.assertNotIn("TSoftObjectPtr<USoundConcurrency> Concurrency =", body)
        self.assertNotIn(
            "TSoftObjectPtr<USoundSubmixBase> OutputSubmix =",
            body,
        )
        self.assertNotIn("FName ProvenanceId =", body)
        self.assertNotIn("FString SourceSha256 =", body)

    def test_contract_does_not_lock_rifle_igla_as_live_weapons(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardProductionAudioCategory", body)
        self.assertIn("ESkyguardProductionAudioCategory::EngineIdle", body)
        for name in RIFLE_IGLA_NOT_LIVE_WEAPONS:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardProductionAudioCategory::{name}", body)
        for name in CATEGORY_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardProductionAudioCategory::{name}", body)

    def test_contract_does_not_re_lock_bank_evaluate_readiness(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        for name in BANK_OWNED_BY_142:
            self.assertNotIn(name, body)
        self.assertNotIn("USkyguardAudioProductionBank", body)
        self.assertNotIn("UCLASS", body)
        self.assertNotIn("NewObject", body)
        self.assertNotIn("GetUnboundRequiredCategories", body)

    def test_contract_does_not_lock_sibling_routing_or_audit(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        for name in SIBLING_STRUCTS:
            self.assertNotIn(f"struct {name}", body)
            self.assertNotIn(name, body)
        self.assertNotIn("CockpitExteriorAttenuation", body)
        self.assertNotIn("CockpitLowPassHz", body)
        self.assertNotIn("RequiredCategoryCount", body)
        self.assertNotIn("BoundProductionSourceCount", body)
        self.assertNotIn("bCategoryContractComplete", body)
        self.assertNotIn("bProductionReady", body)
        self.assertNotIn("MissingCategoryEntries", body)
        self.assertNotIn("MissingRoutingAssets", body)

    def test_struct_does_not_re_lock_harbor(self) -> None:
        body = entry_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = entry_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardProductionAudioEntry contains {banned}",
            )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
            if (ROOT / sibling).exists():
                existing.append(sibling)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", *existing],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
