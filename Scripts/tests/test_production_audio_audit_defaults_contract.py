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
    "Scripts/tests/test_audible_acceptance_receipt_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_production_audio_routing_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
)
PUBLIC_FIELDS = (
    "int32 RequiredCategoryCount = 0;",
    "int32 BoundProductionSourceCount = 0;",
    "int32 ExplicitMissingSourceCount = 0;",
    "int32 QATestOnlyCount = 0;",
    "TArray<FName> MissingCategoryEntries;",
    "TArray<FName> InvalidSourceEntries;",
    "TArray<FName> MissingSoundBindings;",
    "TArray<FName> MissingAttenuationBindings;",
    "TArray<FName> MissingConcurrencyBindings;",
    "TArray<FName> MissingOutputSubmixBindings;",
    "TArray<FName> MissingRoutingAssets;",
    "bool bCategoryContractComplete = false;",
    "bool bProductionReady = false;",
)
IN_CLASS_DEFAULTS = {
    "RequiredCategoryCount": "0",
    "BoundProductionSourceCount": "0",
    "ExplicitMissingSourceCount": "0",
    "QATestOnlyCount": "0",
    "bCategoryContractComplete": "false",
    "bProductionReady": "false",
}
MISSING_TARRAY_FIELDS = (
    "MissingCategoryEntries",
    "MissingSoundBindings",
    "MissingAttenuationBindings",
    "MissingConcurrencyBindings",
    "MissingOutputSubmixBindings",
    "MissingRoutingAssets",
)
ARRAY_FIELDS_WITHOUT_DEFAULTS = MISSING_TARRAY_FIELDS + ("InvalidSourceEntries",)
EMPTY_EVALUATE_READINESS_OWNED_BY_142 = (
    "EvaluateReadiness",
    "InitializeRequiredEntries",
    "EnsureDefaultEntries",
    "ConfigureRoutingTopology",
    "GetUnboundRequiredCategories",
    "GetRequiredCategories",
    "NewObject",
    "HasBoundObject",
    "HasValidSha256",
)
ROUTING_OWNED_BY_SIBLING = (
    "struct FSkyguardProductionAudioRouting",
    "CockpitExteriorAttenuation",
    "CockpitLowPassHz",
    "MasterSubmix",
    "CockpitSubmix",
    "ExteriorSubmix",
    "WeaponsSubmix",
    "ExplosionsSubmix",
    "RadioSubmix",
    "CockpitSoundMix",
)
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


def audit_body(header: str) -> str:
    start = header.index("struct FSkyguardProductionAudioAudit")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:bool|int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class ProductionAudioAuditDefaultsContractTests(unittest.TestCase):
    def test_audit_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardProductionAudioAudit", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", audit_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 13)
        self.assertEqual(body.count("BlueprintReadOnly"), 13)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("int32 RequiredCategoryCount = 0;", body)
        self.assertIn("int32 BoundProductionSourceCount = 0;", body)
        self.assertIn("int32 ExplicitMissingSourceCount = 0;", body)
        self.assertIn("int32 QATestOnlyCount = 0;", body)
        self.assertIn("bool bCategoryContractComplete = false;", body)
        self.assertIn("bool bProductionReady = false;", body)

    def test_missing_tarray_fields_have_presence_without_invented_defaults(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        for name in ARRAY_FIELDS_WITHOUT_DEFAULTS:
            self.assertIn(f"TArray<FName> {name};", body)
            self.assertNotIn(f"{name} =", body)
            self.assertNotIn(name, in_class_defaults(body))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("= {}", body)
        self.assertNotIn("TArray<FName>()", body)
        self.assertNotIn("Empty()", body)

    def test_contract_does_not_re_lock_empty_evaluate_readiness(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        for name in EMPTY_EVALUATE_READINESS_OWNED_BY_142:
            self.assertNotIn(name, body)
        self.assertNotIn("USkyguardAudioProductionBank", body)
        self.assertNotIn("UCLASS", body)
        self.assertNotIn("NewObject", body)
        self.assertNotIn("GetRequiredCategories", body)
        self.assertNotIn("MissingRoutingAssets.Num()", body)
        self.assertNotIn("0.72f", body)
        self.assertNotIn("7200.f", body)

    def test_contract_does_not_lock_production_audio_routing(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        for name in ROUTING_OWNED_BY_SIBLING:
            self.assertNotIn(name, body)
        self.assertNotIn("FSkyguardProductionAudioRouting", body)
        self.assertNotIn("FSkyguardProductionAudioEntry", body)

    def test_contract_does_not_lock_rifle_igla_as_live_weapons(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardProductionAudioCategory", body)
        self.assertNotIn("ESkyguardProductionAudioCategory", body)
        for name in RIFLE_IGLA_CATEGORY_NAMES:
            self.assertNotIn(name, body)

    def test_struct_does_not_retune_harbor(self) -> None:
        body = audit_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = audit_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardProductionAudioAudit contains {banned}",
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
