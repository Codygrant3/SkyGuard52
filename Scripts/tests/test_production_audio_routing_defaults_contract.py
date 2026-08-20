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
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
SOFT_FIELDS = (
    "TSoftObjectPtr<USoundSubmixBase> MasterSubmix;",
    "TSoftObjectPtr<USoundSubmixBase> CockpitSubmix;",
    "TSoftObjectPtr<USoundSubmixBase> ExteriorSubmix;",
    "TSoftObjectPtr<USoundSubmixBase> WeaponsSubmix;",
    "TSoftObjectPtr<USoundSubmixBase> ExplosionsSubmix;",
    "TSoftObjectPtr<USoundSubmixBase> RadioSubmix;",
    "TSoftObjectPtr<USoundMix> CockpitSoundMix;",
)
SOFT_FIELD_NAMES = (
    "MasterSubmix",
    "CockpitSubmix",
    "ExteriorSubmix",
    "WeaponsSubmix",
    "ExplosionsSubmix",
    "RadioSubmix",
    "CockpitSoundMix",
)
PUBLIC_FIELDS = SOFT_FIELDS + (
    "float CockpitExteriorAttenuation = 0.72f;",
    "float CockpitLowPassHz = 7200.f;",
)
IN_CLASS_DEFAULTS = {
    "CockpitExteriorAttenuation": "0.72f",
    "CockpitLowPassHz": "7200.f",
}
# USkyguardAudioProductionBank empty EvaluateReadiness (#142) stays on
# its own isolated draft. This contract locks routing defaults only.
EVALUATE_READINESS_SYMBOLS = (
    "EvaluateReadiness",
    "InitializeRequiredEntries",
    "EnsureDefaultEntries",
    "ConfigureRoutingTopology",
    "GetUnboundRequiredCategories",
    "GetRequiredCategories",
    "GetCategoryDisplayName",
    "FindEntry",
    "HasBoundObject",
    "HasValidSha256",
    "EmptyEntriesFailClosed",
    "class USkyguardAudioProductionBank",
    "USkyguardAudioProductionBank",
)
# FSkyguardProductionAudioAudit stays on a sibling isolated draft.
AUDIT_TOKENS = (
    "struct FSkyguardProductionAudioAudit",
    "FSkyguardProductionAudioAudit",
    "RequiredCategoryCount",
    "BoundProductionSourceCount",
    "ExplicitMissingSourceCount",
    "QATestOnlyCount",
    "MissingCategoryEntries",
    "InvalidSourceEntries",
    "MissingSoundBindings",
    "MissingAttenuationBindings",
    "MissingConcurrencyBindings",
    "MissingOutputSubmixBindings",
    "MissingRoutingAssets",
    "bCategoryContractComplete",
    "bProductionReady",
)
# Historical category names are not live CPG player weapons.
RIFLE_IGLA_CATEGORY_NAMES = (
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
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "FSoftObjectPath",
    "/Game/",
    "TEXT(",
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


def routing_body(header: str) -> str:
    start = header.index("struct FSkyguardProductionAudioRouting")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


def assigned_soft_fields(body: str) -> list[str]:
    return re.findall(
        r"TSoftObjectPtr<[^>]+>\s+(\w+)\s*=",
        body,
    )


class ProductionAudioRoutingDefaultsContractTests(unittest.TestCase):
    def test_routing_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardProductionAudioRouting", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", routing_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        for name in SOFT_FIELD_NAMES:
            self.assertIn(name, body)
        self.assertIn("CockpitExteriorAttenuation", body)
        self.assertIn("CockpitLowPassHz", body)
        self.assertEqual(body.count("UPROPERTY("), 9)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadWrite)"), 9)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("float CockpitExteriorAttenuation = 0.72f;", body)
        self.assertIn("float CockpitLowPassHz = 7200.f;", body)
        self.assertIn('meta=(ClampMin="0.0", ClampMax="1.0")', body)
        self.assertIn('meta=(ClampMin="100.0", ClampMax="20000.0")', body)

    def test_soft_fields_have_presence_without_invented_defaults(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        self.assertEqual(assigned_soft_fields(body), [])
        for field in SOFT_FIELDS:
            self.assertIn(field, body)
        for name in SOFT_FIELD_NAMES:
            self.assertIn(f"{name};", body)
            self.assertNotIn(f"{name} =", body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn(" = NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)

    def test_contract_does_not_relock_empty_evaluate_readiness(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        for name in EVALUATE_READINESS_SYMBOLS:
            self.assertNotIn(name, body)
        self.assertNotIn("Entries", body)
        self.assertNotIn("nullptr", body)
        self.assertNotIn("fail-closed", body.lower())
        self.assertNotIn("FailClosed", body)

    def test_contract_does_not_lock_production_audio_audit(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        for token in AUDIT_TOKENS:
            self.assertNotIn(token, body)

    def test_contract_does_not_lock_rifle_igla_category_names(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        self.assertNotIn("ESkyguardProductionAudioCategory", body)
        self.assertNotIn("enum class ESkyguardProductionAudioCategory", body)
        for name in RIFLE_IGLA_CATEGORY_NAMES:
            self.assertNotIn(name, body)

    def test_struct_does_not_retune_harbor_or_invent_live_copy(self) -> None:
        body = routing_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("rifle", body.lower())

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = routing_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardProductionAudioRouting contains {banned}",
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
