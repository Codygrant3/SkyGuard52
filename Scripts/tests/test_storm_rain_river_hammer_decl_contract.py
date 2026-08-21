from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
DAY_HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
NIGHT_HEADER_PATH = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
NAMESPACE_NAME = "SkyguardStormRainBeatKits"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, sequence contents, or which beats RiverHammer returns.
RIVER_HAMMER = "const FSkyguardStormRainBeatKit& RiverHammer();"
LOCKED_DECLARATION = RIVER_HAMMER
LOCKED_DECLARATIONS = (RIVER_HAMMER,)
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python RiverHammer() factory declaration
# contract. Stay off leftover Harbor #6/#8/#9, leftover theater-kit
# #59, flare/HUD #57/#61/#62, CPG mesh/art, Harbor IncomingRadar
# 40/80, and FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady).
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
# Isolated-test drafts stay off this lane. IronRain() is the sibling
# in-flight factory. ForMission (#274), KeepsHydraForClusters (#264),
# BeatIndexForElapsed (#267), kind enum, kit defaults, Kinds, leftover
# theater-kit #59, and day/night kits stay sibling-only.
# ApplyHydraForClusters stays unlocked (takes leftover ASkyguardGunner*).
# On-main storm-rain beat-kit sequence contents stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_for_mission_contract.py",
    "Scripts/tests/test_storm_rain_keeps_hydra_contract.py",
    "Scripts/tests/test_storm_rain_beat_index_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
    "Scripts/tests/test_day_sortie_for_mission_contract.py",
    "Scripts/tests/test_night_sortie_for_mission_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardStormRainBeatKit& IronRain();",
    "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);",
    "bool KeepsHydraForClusters(ESkyguardMissionWeather Weather);",
    "bool ApplyHydraForClusters(",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
)
SIBLING_FACTORY_NOT_LOCKED = (
    "const FSkyguardStormRainBeatKit& IronRain();"
)
FOR_MISSION_NOT_LOCKED = (
    "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);"
)
UNLOCKED_KEEPS_HYDRA = (
    "bool KeepsHydraForClusters(ESkyguardMissionWeather Weather);"
)
UNLOCKED_APPLY = (
    "bool ApplyHydraForClusters(",
    "ASkyguardGunner* Gunner",
    "const FSkyguardStormRainBeatKit& Kit",
)
UNLOCKED_BEAT_INDEX = (
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
)
DAY_FOR_MISSION = (
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);"
)
NIGHT_FOR_MISSION = (
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);"
)
# On-main RiverHammer() sequence contents stay unlocked.
SEQUENCE_CONTENTS_NOT_LOCKED = (
    "MakeRiverHammer",
    "MakeIronRain",
    "M05_StormFront",
    "M08_RescueCover",
    "SevereSquall",
    "RescueSunset",
    "River Hammer",
    "Storm valley",
    "Kinds[0]",
    "Kinds[1]",
    "Kinds[2]",
    "Kinds[3]",
    "Kinds[4]",
    "Kinds[5]",
    "Kinds[6]",
)
# Which beats RiverHammer returns stays unlocked.
KIT_RETURNS_NOT_LOCKED = (
    "return Kit",
    "MakeRiverHammer",
    "M05_StormFront",
    "WaterwayBoats",
    "BargeClusters",
    "LightningWindow",
    "ProtectWaterway",
    "Tempest",
    "return RiverHammer()",
    "return IronRain()",
)
ELAPSED_TABLES_NOT_LOCKED = (
    "ElapsedSeconds",
    "BeatIndexForElapsed",
    "return 0",
    "return -1",
    "return INDEX_NONE",
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
# .cpp bodies / invented return values / which-kit tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "return RiverHammer()",
    "return IronRain()",
    "MakeRiverHammer",
    "MakeIronRain",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NAMESPACE_RE = re.compile(rf"namespace\s+{re.escape(NAMESPACE_NAME)}\b")


def collapsed(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    return collapsed(declaration) in collapsed(region)


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    return collapsed(region).count(collapsed(declaration))


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class StormRainRiverHammerDeclContractTests(unittest.TestCase):
    def test_storm_rain_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        block = kits_namespace(header)
        self.assertTrue(has_declaration(block, RIVER_HAMMER), block)
        self.assertIn(f"namespace {NAMESPACE_NAME}", block)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", block)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", block)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kits_namespace(
                "namespace SkyguardUnrelatedBeatKits\n{\n};\n"
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
            "\tFName MissionId;\n"
            "\tbool bHydraForClusters = true;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kits_namespace(enum_and_struct)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_river_hammer_declaration_fails_closed(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain();\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission(FName MissionId);\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        block = kits_namespace(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, RIVER_HAMMER)
        self.assertIn("RiverHammer", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_missing_type_or_declaration_fails_closed(self) -> None:
        no_type = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst auto& RiverHammer();\n"
            "\tvoid RiverHammer();\n"
            "}\n"
        )
        block = kits_namespace(no_type)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, RIVER_HAMMER)
        self.assertIn("RiverHammer", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("FSkyguardStormRainBeatKit", RIVER_HAMMER)
        self.assertNotIn(RIVER_HAMMER, block)

    def test_neighbors_do_not_satisfy_river_hammer(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain();\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission(FName MissionId);\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        block = kits_namespace(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, RIVER_HAMMER)
        self.assertIn("RiverHammer", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(block, RIVER_HAMMER), block)
        self.assertIn("IronRain()", block)
        self.assertIn("ForMission", block)
        self.assertIn("KeepsHydraForClusters", block)
        self.assertIn("ApplyHydraForClusters", block)
        self.assertIn("BeatIndexForElapsed", block)

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tvoid RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer(FName MissionId);\n"
            "\tconst FSkyguardDaySortieBeatKit& RiverHammer();\n"
            "\tconst FSkyguardNightSortieBeatKit& RiverHammer();\n"
            "}\n"
        )
        block = kits_namespace(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, RIVER_HAMMER)
        self.assertIn("RiverHammer", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("RiverHammer", block)
        self.assertFalse(has_declaration(block, RIVER_HAMMER), block)

    def test_origin_main_split_line_form_is_accepted(self) -> None:
        split = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit&\n"
            "\tRiverHammer();\n"
            "}\n"
        )
        block = kits_namespace(split)
        self.assertTrue(has_declaration(block, RIVER_HAMMER), block)
        self.assertEqual(require_declaration(block, RIVER_HAMMER), RIVER_HAMMER)
        self.assertEqual(declaration_count(block, RIVER_HAMMER), 1)

    def test_river_hammer_declaration_matches_origin_main(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertEqual(
            require_declaration(block, RIVER_HAMMER),
            RIVER_HAMMER,
        )
        self.assertEqual(LOCKED_DECLARATIONS, (RIVER_HAMMER,))
        self.assertEqual(LOCKED_DECLARATION, RIVER_HAMMER)
        self.assertTrue(has_declaration(block, RIVER_HAMMER), block)
        self.assertEqual(declaration_count(block, RIVER_HAMMER), 1)
        self.assertTrue(RIVER_HAMMER.endswith(";"), RIVER_HAMMER)
        self.assertNotIn("INDEX_NONE", RIVER_HAMMER)
        self.assertNotIn("return ", RIVER_HAMMER)
        self.assertNotIn("ASkyguardGunner", RIVER_HAMMER)
        self.assertNotIn("KeepsHydraForClusters", RIVER_HAMMER)
        self.assertNotIn("ApplyHydraForClusters", RIVER_HAMMER)
        self.assertNotIn("BeatIndexForElapsed", RIVER_HAMMER)
        self.assertNotIn("ForMission", RIVER_HAMMER)
        self.assertNotIn("IronRain", RIVER_HAMMER)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        block = kits_namespace(origin_main_header())
        for declaration in LOCKED_DECLARATIONS:
            self.assertTrue(declaration.endswith(";"), declaration)
            self.assertNotIn("return ", declaration)
            self.assertNotIn("INDEX_NONE", declaration)
            self.assertNotIn("NAME_None", declaration)
            self.assertNotIn("{", declaration)
            self.assertNotIn("}", declaration)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, RIVER_HAMMER)
            if token != "return ":
                self.assertNotIn(token, block)
        self.assertNotIn("return ", RIVER_HAMMER)
        self.assertNotIn("return ", block)
        self.assertNotIn("INDEX_NONE", block)
        self.assertNotIn("NAME_None", block)
        self.assertNotIn("return INDEX_NONE", block)
        self.assertNotIn("return 0", block)
        self.assertNotIn("return -1", block)
        self.assertNotIn("= INDEX_NONE", block)
        self.assertNotIn("bHydraForClusters = true", block)

    def test_contract_does_not_invent_which_beats_are_returned(self) -> None:
        locked_only = f"{RIVER_HAMMER}\n"
        self.assertEqual(
            require_declaration(locked_only, RIVER_HAMMER),
            RIVER_HAMMER,
        )
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIVER_HAMMER)
        self.assertNotIn("MakeRiverHammer", RIVER_HAMMER)
        self.assertNotIn("M05", RIVER_HAMMER)
        self.assertNotIn("M08", RIVER_HAMMER)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, RIVER_HAMMER)

    def test_contract_does_not_relock_sibling_factory(self) -> None:
        locked_only = f"{RIVER_HAMMER}\n"
        self.assertEqual(
            require_declaration(locked_only, RIVER_HAMMER),
            RIVER_HAMMER,
        )
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, locked_only)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, RIVER_HAMMER)
        self.assertNotIn("IronRain()", locked_only)
        self.assertNotIn("IronRain", RIVER_HAMMER)
        self.assertNotEqual(RIVER_HAMMER, "IronRain()")
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, LOCKED_DECLARATIONS)

    def test_contract_does_not_relock_for_mission(self) -> None:
        locked_only = f"{RIVER_HAMMER}\n"
        self.assertEqual(LOCKED_DECLARATIONS, (RIVER_HAMMER,))
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, locked_only)
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("ForMission", RIVER_HAMMER)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn(
            "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);",
            LOCKED_DECLARATIONS,
        )
        self.assertIn(
            "Scripts/tests/test_storm_rain_for_mission_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_kit_sequence_contents(self) -> None:
        locked_only = f"{RIVER_HAMMER}\n"
        block = kits_namespace(origin_main_header())
        self.assertEqual(
            require_declaration(locked_only, RIVER_HAMMER),
            RIVER_HAMMER,
        )
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIVER_HAMMER)
            self.assertNotIn(token, block)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, RIVER_HAMMER)

    def test_contract_does_not_lock_keeps_hydra_or_apply_hydra(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (RIVER_HAMMER,))
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        self.assertNotIn("KeepsHydraForClusters", RIVER_HAMMER)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, RIVER_HAMMER)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", RIVER_HAMMER)
        self.assertNotIn("ASkyguardGunner", RIVER_HAMMER)
        self.assertNotIn("ASkyguardGunner*", RIVER_HAMMER)
        self.assertIn(
            "Scripts/tests/test_storm_rain_keeps_hydra_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_lock_beat_index(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (RIVER_HAMMER,))
        locked_only = f"{RIVER_HAMMER}\n"
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, locked_only)
        self.assertNotIn("BeatIndexForElapsed", RIVER_HAMMER)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            LOCKED_DECLARATIONS,
        )
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_index_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_elapsed_tables(self) -> None:
        locked_only = f"{RIVER_HAMMER}\n"
        block = kits_namespace(origin_main_header())
        for token in ELAPSED_TABLES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIVER_HAMMER)
        self.assertNotIn("ElapsedSeconds", RIVER_HAMMER)
        self.assertNotIn("return INDEX_NONE", block)
        self.assertNotIn("return 0", block)
        self.assertNotIn("return -1", block)

    def test_contract_does_not_lock_day_or_night_kits(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardStormRainBeatKit.h",
        )
        self.assertNotEqual(HEADER_PATH, DAY_HEADER_PATH)
        self.assertNotEqual(HEADER_PATH, NIGHT_HEADER_PATH)
        self.assertNotIn("SkyguardDaySortieBeatKit", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit", HEADER_PATH)
        self.assertNotIn("SkyguardDaySortieBeatKit", NAMESPACE_NAME)
        self.assertNotIn("SkyguardNightSortieBeatKit", NAMESPACE_NAME)
        self.assertEqual(NAMESPACE_NAME, "SkyguardStormRainBeatKits")
        self.assertNotEqual(RIVER_HAMMER, DAY_FOR_MISSION)
        self.assertNotEqual(RIVER_HAMMER, NIGHT_FOR_MISSION)
        self.assertNotIn(DAY_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn(NIGHT_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn("NightEyes", RIVER_HAMMER)
        self.assertNotIn("HunterKiller", RIVER_HAMMER)
        self.assertIn(
            "Scripts/tests/test_day_sortie_for_mission_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_night_sortie_for_mission_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_lock_struct_fields_or_defaults(self) -> None:
        block = kits_namespace(origin_main_header())
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, RIVER_HAMMER)
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
        self.assertNotIn("MissionId", RIVER_HAMMER)
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", block)
        self.assertNotIn("enum class", block)
        self.assertNotIn("UENUM(", block)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", block)
            self.assertNotIn(name, RIVER_HAMMER)
        self.assertNotIn("Approach", block)
        self.assertNotIn("WaterwayBoats", block)
        self.assertNotIn("BargeClusters", block)
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_parses_namespace_not_struct_or_enum(self) -> None:
        header = origin_main_header()
        block = kits_namespace(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertIn("struct FSkyguardStormRainBeatKit", header)
        self.assertIn("enum class ESkyguardStormRainBeatKind", header)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", block)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", block)
        self.assertEqual(require_declaration(block, RIVER_HAMMER), RIVER_HAMMER)
        self.assertNotIn("Kinds[BeatCount]", block)
        self.assertNotIn("bHydraForClusters = true", block)
        self.assertNotIn("FName WeatherIdentity;", block)

    def test_contract_does_not_read_cpp_or_which_kit_tables(self) -> None:
        block = kits_namespace(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, RIVER_HAMMER)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", block)
        self.assertNotIn("SkyguardStormRainBeatKits::RiverHammer", block)
        self.assertNotIn("MakeRiverHammer", block)
        self.assertNotIn("MakeIronRain", block)
        self.assertNotIn("return RiverHammer()", block)
        self.assertNotIn("return IronRain()", block)
        self.assertNotIn("M05_StormFront", block)
        self.assertNotIn("M08_RescueCover", block)

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
        self.assertNotEqual(RIVER_HAMMER, "Rifle")
        self.assertNotEqual(RIVER_HAMMER, "Igla")
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
                "RiverHammer is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, RIVER_HAMMER.lower())

    def test_contract_is_river_hammer_declaration_only(self) -> None:
        header = origin_main_header()
        block = kits_namespace(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (RIVER_HAMMER,))
        self.assertEqual(
            require_declaration(block, RIVER_HAMMER),
            RIVER_HAMMER,
        )
        locked_only = f"{RIVER_HAMMER}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, RIVER_HAMMER)
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn(DAY_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn(NIGHT_FOR_MISSION, LOCKED_DECLARATIONS)
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, block)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, block)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, RIVER_HAMMER)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
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
        self.assertNotIn("KeepsHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("BeatIndexForElapsed", LOCKED_DECLARATIONS)
        self.assertNotIn("ForMission", LOCKED_DECLARATIONS)
        self.assertNotIn("IronRain", LOCKED_DECLARATIONS)
        self.assertNotIn("ASkyguardGunner", RIVER_HAMMER)
        self.assertNotEqual(HEADER_PATH, DAY_HEADER_PATH)
        self.assertNotEqual(HEADER_PATH, NIGHT_HEADER_PATH)
        self.assertNotEqual(list(LOCKED_DECLARATIONS), ["Rifle", "Igla"])
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            LOCKED_SCRIPTS,
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
