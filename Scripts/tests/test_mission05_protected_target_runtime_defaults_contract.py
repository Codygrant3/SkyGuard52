from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission05IntegrationDirector.h"
STRUCT_NAME = "FSkyguardMission05ProtectedTargetRuntime"
# Leftover #56–#64 plus Mission 05 production sources and merged #101.
# This lane only adds an isolated Python contract.
LOCKED = {
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirectorTests.cpp",
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
# Isolated-test drafts #107–#222 and newer stay off this lane.
# Storm runtime (#212) and storm-rain beat kit are sibling Mission 05 contracts.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_airfield_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
)
# Target default is split across two lines on origin/main; markers stay in order.
# Apache CPG storm-sortie escort integrity. Lock the Target default only —
# not the full ESkyguardMission05ProtectedTarget enumerator set.
PUBLIC_FIELDS = (
    "ESkyguardMission05ProtectedTarget Target =",
    "int32 Integrity = 100;",
    "bool bDestroyed = false;",
)
IN_CLASS_DEFAULTS = {
    "Target": "ESkyguardMission05ProtectedTarget::OffshorePlatform",
    "Integrity": "100",
    "bDestroyed": "false",
}
# Storm runtime (#212), storm-rain beat kit, readiness (bYakRuntimeReady),
# wave state, and the full protected-target enumerator set stay unlocked.
TYPES_NOT_LOCKED = (
    "struct FSkyguardStormRuntime",
    "struct FSkyguardStormRainBeatKit",
    "enum class ESkyguardStormRainBeatKind",
    "struct FSkyguardMission05IntegrationReadiness",
    "enum class ESkyguardMission05WaveState",
    "enum class ESkyguardMission05ProtectedTarget",
    "bYakRuntimeReady",
    "DistressedTrawler",
    "Turbulence",
    "bLightningActive",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
    "WaterwayBoats",
    "Tempest",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "TEXT(",
    "FString()",
    'TEXT("")',
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def protected_target_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardMission05ProtectedTarget|int32|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class Mission05ProtectedTargetRuntimeDefaultsContractTests(unittest.TestCase):
    def test_protected_target_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", protected_target_body(header))

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            protected_target_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = protected_target_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 3)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            3,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = protected_target_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Target"),
            "ESkyguardMission05ProtectedTarget::OffshorePlatform",
        )
        self.assertEqual(defaults.get("Integrity"), "100")
        self.assertEqual(defaults.get("bDestroyed"), "false")
        compact = re.sub(r"\s+", " ", body)
        self.assertIn(
            "ESkyguardMission05ProtectedTarget Target = "
            "ESkyguardMission05ProtectedTarget::OffshorePlatform;",
            compact,
        )
        self.assertIn("int32 Integrity = 100;", body)
        self.assertIn("bool bDestroyed = false;", body)
        self.assertNotIn("bDestroyed = true", body)
        self.assertNotIn("Integrity = 0;", body)
        self.assertNotIn("Integrity = INDEX_NONE", body)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = protected_target_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_storm_readiness_or_wave(self) -> None:
        body = protected_target_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("FSkyguardStormRuntime", body)
        self.assertNotIn("FSkyguardStormRainBeatKit", body)
        self.assertNotIn("ESkyguardStormRainBeatKind", body)
        self.assertNotIn("FSkyguardMission05IntegrationReadiness", body)
        self.assertNotIn("ESkyguardMission05WaveState", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("DistressedTrawler", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = protected_target_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = protected_target_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "protected-target runtime is Apache CPG storm-sortie "
                "escort integrity, not Yak",
            )
            self.assertNotIn(banned, defaults)

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
