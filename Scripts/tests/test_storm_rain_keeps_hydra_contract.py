from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
NAMESPACE_NAME = "SkyguardStormRainBeatKits"
# Declaration presence only. Do not invent INDEX_NONE or return values.
# Do not lock ApplyHydraForClusters (it takes ASkyguardGunner*).
LOCKED_DECLARATION = (
    "bool KeepsHydraForClusters(ESkyguardMissionWeather Weather);"
)
LOCKED_DECLARATIONS = (LOCKED_DECLARATION,)
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python KeepsHydraForClusters declaration contract.
# Stay off leftover Harbor #6/#8/#9, leftover theater-kit #59, flare/HUD
# #57/#61/#62, CPG mesh/art, Harbor IncomingRadar 40/80, and
# FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady).
LOCKED = {
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardStormRainBeatKitTests.cpp",
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
# Isolated-test drafts stay off this lane. RiverHammer()/IronRain()/
# ForMission() sequences stay on-main. Kind enum (#245), kit defaults
# (#248), Kinds (#255), Threats (#257), Stations (#258), Calls (#259),
# MissionId/WeatherIdentity (#260), Title/WeatherLabel, leftover
# theater-kit #59, and ApplyHydraForClusters stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_threats_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_stations_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_labels_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_SEQUENCES = (
    "const FSkyguardStormRainBeatKit& RiverHammer();",
    "const FSkyguardStormRainBeatKit& IronRain();",
    "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);",
)
UNLOCKED_APPLY = (
    "bool ApplyHydraForClusters(",
    "ASkyguardGunner* Gunner",
    "const FSkyguardStormRainBeatKit& Kit",
)
UNLOCKED_BEAT_INDEX = (
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
)
# Struct / enum / defaults stay unlocked. Parse the namespace only.
STRUCT_FIELDS_NOT_LOCKED = (
    "FName MissionId;",
    'const TCHAR* Title = TEXT("");',
    "FName WeatherIdentity;",
    'const TCHAR* WeatherLabel = TEXT("");',
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
    "bool bHydraForClusters = true;",
    "ESkyguardStormRainBeatKind Kinds[BeatCount] = {};",
    "ESkyguardThreatKind Threats[BeatCount] = {};",
    "ESkyguardGunshipWeapon Stations[BeatCount] = {};",
    "const TCHAR* Calls[BeatCount] = {};",
    "static constexpr int32 BeatCount = 7;",
)
BEAT_KIND_ENUMERATORS_NOT_LOCKED = (
    "Approach",
    "WaterwayBoats",
    "BargeClusters",
    "LightningWindow",
    "ProtectWaterway",
    "Tempest",
    "GunLine",
    "KillBattery",
    "BarrageCover",
    "RescueCorridor",
    "IronRain",
    "Extract",
)
SIBLING_TYPES = (
    "enum class ESkyguardStormRainBeatKind",
    "struct FSkyguardStormRainBeatKit",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardNightSortieBeatKit",
    "FSkyguardLoadoutSpec",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return ",
    "return true",
    "return false",
    "return 0",
    "return -1",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NAMESPACE_RE = re.compile(rf"namespace\s+{NAMESPACE_NAME}\b")


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{HEADER_PATH} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def kits_namespace(header: str) -> str:
    """Parse namespace SkyguardStormRainBeatKits only, not the struct or enum."""
    match = NAMESPACE_RE.search(header)
    if match is None:
        raise AssertionError(
            f"namespace {NAMESPACE_NAME} is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[start : index + 1]
    raise AssertionError(
        f"namespace {NAMESPACE_NAME} body is unclosed in "
        f"origin/main:{HEADER_PATH}"
    )


def require_declaration(region: str, declaration: str) -> str:
    if declaration not in region:
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class StormRainKeepsHydraContractTests(unittest.TestCase):
    def test_keeps_hydra_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        block = kits_namespace(header)
        self.assertIn(LOCKED_DECLARATION, block)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", block)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", block)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kits_namespace(
                "enum class ESkyguardStormRainBeatKind : uint8\n{\n};\n"
                "struct FSkyguardStormRainBeatKit\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_or_struct_alone_does_not_satisfy_namespace(self) -> None:
        enum_and_struct = (
            "enum class ESkyguardStormRainBeatKind : uint8\n"
            "{\n"
            "\tApproach,\n"
            "\tExtract\n"
            "};\n"
            "struct FSkyguardStormRainBeatKit\n"
            "{\n"
            "\tbool bHydraForClusters = true;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kits_namespace(enum_and_struct)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_keeps_hydra_declaration_fails_closed(self) -> None:
        empty_namespace = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain();\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission(FName MissionId);\n"
            "}\n"
        )
        block = kits_namespace(empty_namespace)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, LOCKED_DECLARATION)
        self.assertIn("KeepsHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_apply_hydra_does_not_satisfy_keeps_hydra(self) -> None:
        apply_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "}\n"
        )
        block = kits_namespace(apply_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, LOCKED_DECLARATION)
        self.assertIn("KeepsHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(LOCKED_DECLARATION, block)

    def test_name_or_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tbool KeepsHydraForClusters();\n"
            "\tvoid KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        block = kits_namespace(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, LOCKED_DECLARATION)
        self.assertIn("KeepsHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("KeepsHydraForClusters", block)

    def test_keeps_hydra_declaration_matches_origin_main(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertEqual(
            require_declaration(block, LOCKED_DECLARATION),
            LOCKED_DECLARATION,
        )
        self.assertEqual(LOCKED_DECLARATIONS, (LOCKED_DECLARATION,))
        self.assertEqual(block.count(LOCKED_DECLARATION), 1)
        self.assertTrue(LOCKED_DECLARATION.endswith(";"), LOCKED_DECLARATION)
        self.assertNotIn("INDEX_NONE", LOCKED_DECLARATION)
        self.assertNotIn("ASkyguardGunner", LOCKED_DECLARATION)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATION)

    def test_declaration_does_not_invent_index_none_or_return_values(self) -> None:
        block = kits_namespace(origin_main_header())
        for declaration in LOCKED_DECLARATIONS:
            self.assertTrue(declaration.endswith(";"), declaration)
            self.assertNotIn("return ", declaration)
            self.assertNotIn("INDEX_NONE", declaration)
            self.assertNotIn("NAME_None", declaration)
            self.assertNotIn("{", declaration)
            self.assertNotIn("}", declaration)
        for token in INVENTED:
            self.assertNotIn(token, LOCKED_DECLARATION)
            self.assertNotIn(token, block)
        self.assertNotIn("return INDEX_NONE", block)
        self.assertNotIn("= INDEX_NONE", block)
        self.assertNotIn("bHydraForClusters = true", block)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (LOCKED_DECLARATION,))
        for neighbor in UNLOCKED_SEQUENCES:
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        self.assertNotIn("RiverHammer()", LOCKED_DECLARATION)
        self.assertNotIn("IronRain()", LOCKED_DECLARATION)
        self.assertNotIn("ForMission(", LOCKED_DECLARATION)
        self.assertNotIn("RiverHammer", LOCKED_DECLARATIONS)
        self.assertNotIn("IronRain", LOCKED_DECLARATIONS)
        self.assertNotIn("ForMission", LOCKED_DECLARATIONS)

    def test_contract_does_not_lock_apply_hydra_or_beat_index(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (LOCKED_DECLARATION,))
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, LOCKED_DECLARATION)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATION)
        self.assertNotIn("BeatIndexForElapsed", LOCKED_DECLARATION)
        self.assertNotIn("ASkyguardGunner", LOCKED_DECLARATION)
        self.assertNotIn("ASkyguardGunner*", LOCKED_DECLARATION)

    def test_contract_does_not_lock_struct_fields_or_defaults(self) -> None:
        block = kits_namespace(origin_main_header())
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, LOCKED_DECLARATION)
            self.assertNotIn(field, block)
        self.assertNotIn("bHydraForClusters = true", block)
        self.assertNotIn("Kinds[BeatCount]", block)
        self.assertNotIn("Threats[BeatCount]", block)
        self.assertNotIn("Stations[BeatCount]", block)
        self.assertNotIn("Calls[BeatCount]", block)
        self.assertNotIn("BeatCount = 7", block)
        self.assertNotIn("Weather =", block)
        self.assertNotIn("Title", block)
        self.assertNotIn("WeatherLabel", block)
        self.assertNotIn("WeatherIdentity", block)

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", block)
        self.assertNotIn("enum class", block)
        self.assertNotIn("UENUM(", block)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", block)
            self.assertNotIn(name, LOCKED_DECLARATION)
        self.assertNotIn("Approach", block)
        self.assertNotIn("WaterwayBoats", block)
        self.assertNotIn("BargeClusters", block)

    def test_contract_does_not_retune_harbor(self) -> None:
        block = kits_namespace(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, block)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, block)
        self.assertNotIn("40.f, 80.f", block)
        self.assertNotIn(HARBOR_INCOMING, block)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", block)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", block)
        self.assertNotIn("bYakRuntimeReady", block)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", block)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertNotIn("Rifle", block)
        self.assertNotIn("Igla", block)
        self.assertNotIn("Yak", block)
        self.assertNotEqual(LOCKED_DECLARATIONS, ("Rifle", "Igla"))
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", block)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", block)
        self.assertNotIn("FireIgla", block)
        self.assertNotIn("FireRifle", block)
        self.assertNotIn("YakSpawnLocation", block)

    def test_namespace_bans_igla_yak_rifle(self) -> None:
        block = kits_namespace(origin_main_header())
        lowered = block.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"namespace {NAMESPACE_NAME} contains {banned}; "
                "KeepsHydraForClusters is Apache CPG 30 mm / Hydra / "
                "Hellfire, not Yak",
            )
            self.assertNotIn(banned, LOCKED_DECLARATION.lower())

    def test_contract_is_keeps_hydra_declaration_only(self) -> None:
        header = origin_main_header()
        block = kits_namespace(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (LOCKED_DECLARATION,))
        self.assertEqual(
            require_declaration(block, LOCKED_DECLARATION),
            LOCKED_DECLARATION,
        )
        for neighbor in UNLOCKED_SEQUENCES:
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, block)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, block)
        for token in INVENTED:
            self.assertNotIn(token, block)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, block)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, block)
        self.assertNotIn("40.f, 80.f", block)
        self.assertNotIn(HARBOR_INCOMING, block)
        self.assertNotIn("Rifle", block)
        self.assertNotIn("Igla", block)
        self.assertNotIn("Yak", block)
        self.assertNotIn("INDEX_NONE", block)
        self.assertNotIn("return ", block)
        self.assertNotIn("enum class", block)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", block)
        self.assertNotIn("bHydraForClusters = true", block)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("BeatIndexForElapsed", LOCKED_DECLARATIONS)
        self.assertNotIn("RiverHammer", LOCKED_DECLARATIONS)
        self.assertNotIn("ASkyguardGunner", LOCKED_DECLARATION)
        self.assertNotEqual(list(LOCKED_DECLARATIONS), ["Rifle", "Igla"])

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
