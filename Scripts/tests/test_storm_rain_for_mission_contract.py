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
# values, or which kit ForMission returns.
FOR_MISSION = "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);"
LOCKED_DECLARATION = FOR_MISSION
LOCKED_DECLARATIONS = (FOR_MISSION,)
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python ForMission declaration contract.
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
# Isolated-test drafts stay off this lane. RiverHammer()/IronRain()
# sequences stay on-main. KeepsHydraForClusters (#264),
# BeatIndexForElapsed (#267), kind enum (#245), kit defaults (#248),
# Kinds (#255), leftover theater-kit #59, and day/night ForMission
# stay sibling-only. ApplyHydraForClusters stays unlocked.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
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
UNLOCKED_SEQUENCES = (
    "const FSkyguardStormRainBeatKit& RiverHammer();",
    "const FSkyguardStormRainBeatKit& IronRain();",
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
# Day/night ForMission live in different headers. This lane does not
# read those headers or lock those declarations.
DAY_FOR_MISSION = (
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);"
)
NIGHT_FOR_MISSION = (
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);"
)
KIT_SEQUENCES_NOT_LOCKED = (
    "RiverHammer",
    "IronRain",
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
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NAMESPACE_RE = re.compile(rf"namespace\s+{re.escape(NAMESPACE_NAME)}\b")


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


class StormRainForMissionContractTests(unittest.TestCase):
    def test_storm_rain_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        block = kits_namespace(header)
        self.assertIn(FOR_MISSION, block)
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

    def test_missing_for_mission_declaration_fails_closed(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain();\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        block = kits_namespace(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, FOR_MISSION)
        self.assertIn("ForMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbors_do_not_satisfy_for_mission(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain();\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        block = kits_namespace(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, FOR_MISSION)
        self.assertIn("ForMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(FOR_MISSION, block)
        self.assertIn("RiverHammer()", block)
        self.assertIn("KeepsHydraForClusters", block)
        self.assertIn("ApplyHydraForClusters", block)
        self.assertIn("BeatIndexForElapsed", block)

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tvoid ForMission(FName MissionId);\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission();\n"
            "\tconst FSkyguardDaySortieBeatKit& ForMission(FName MissionId);\n"
            "\tconst FSkyguardNightSortieBeatKit& ForMission(FName MissionId);\n"
            "}\n"
        )
        block = kits_namespace(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(block, FOR_MISSION)
        self.assertIn("ForMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("ForMission", block)
        self.assertNotIn(FOR_MISSION, block)

    def test_day_or_night_for_mission_does_not_satisfy(self) -> None:
        day_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            f"\t{DAY_FOR_MISSION}\n"
            "}\n"
        )
        night_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            f"\t{NIGHT_FOR_MISSION}\n"
            "}\n"
        )
        day_block = kits_namespace(day_only)
        night_block = kits_namespace(night_only)
        with self.assertRaises(AssertionError) as raised_day:
            require_declaration(day_block, FOR_MISSION)
        with self.assertRaises(AssertionError) as raised_night:
            require_declaration(night_block, FOR_MISSION)
        self.assertIn("ForMission", str(raised_day.exception))
        self.assertIn("missing", str(raised_day.exception).lower())
        self.assertIn("ForMission", str(raised_night.exception))
        self.assertIn("missing", str(raised_night.exception).lower())
        self.assertNotIn(FOR_MISSION, day_block)
        self.assertNotIn(FOR_MISSION, night_block)
        self.assertIn(DAY_FOR_MISSION, day_block)
        self.assertIn(NIGHT_FOR_MISSION, night_block)

    def test_for_mission_declaration_matches_origin_main(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertEqual(
            require_declaration(block, FOR_MISSION),
            FOR_MISSION,
        )
        self.assertEqual(LOCKED_DECLARATIONS, (FOR_MISSION,))
        self.assertEqual(LOCKED_DECLARATION, FOR_MISSION)
        self.assertEqual(block.count(FOR_MISSION), 1)
        self.assertTrue(FOR_MISSION.endswith(";"), FOR_MISSION)
        self.assertNotIn("INDEX_NONE", FOR_MISSION)
        self.assertNotIn("return ", FOR_MISSION)
        self.assertNotIn("ASkyguardGunner", FOR_MISSION)
        self.assertNotIn("KeepsHydraForClusters", FOR_MISSION)
        self.assertNotIn("ApplyHydraForClusters", FOR_MISSION)
        self.assertNotIn("BeatIndexForElapsed", FOR_MISSION)

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
            self.assertNotIn(token, FOR_MISSION)
            self.assertNotIn(token, block)
        self.assertNotIn("return INDEX_NONE", block)
        self.assertNotIn("= INDEX_NONE", block)
        self.assertNotIn("bHydraForClusters = true", block)

    def test_declaration_does_not_invent_which_kit_is_returned(self) -> None:
        block = kits_namespace(origin_main_header())
        self.assertNotIn("return RiverHammer()", FOR_MISSION)
        self.assertNotIn("return IronRain()", FOR_MISSION)
        self.assertNotIn("return RiverHammer()", block)
        self.assertNotIn("return IronRain()", block)
        self.assertNotIn("RiverHammer()", FOR_MISSION)
        self.assertNotIn("IronRain()", FOR_MISSION)
        self.assertNotEqual(FOR_MISSION, "RiverHammer()")
        self.assertNotEqual(FOR_MISSION, "IronRain()")
        self.assertNotEqual(FOR_MISSION, UNLOCKED_SEQUENCES[0])
        self.assertNotEqual(FOR_MISSION, UNLOCKED_SEQUENCES[1])

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (FOR_MISSION,))
        locked_only = f"{FOR_MISSION}\n"
        for neighbor in UNLOCKED_SEQUENCES:
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
            self.assertNotIn(neighbor, FOR_MISSION)
            self.assertNotIn(neighbor, locked_only)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, FOR_MISSION)
        self.assertNotIn("RiverHammer()", FOR_MISSION)
        self.assertNotIn("IronRain()", FOR_MISSION)
        self.assertNotIn("RiverHammer", LOCKED_DECLARATIONS)
        self.assertNotIn("IronRain", LOCKED_DECLARATIONS)

    def test_contract_does_not_lock_keeps_hydra_or_apply_hydra(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (FOR_MISSION,))
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        self.assertNotIn("KeepsHydraForClusters", FOR_MISSION)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, FOR_MISSION)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", FOR_MISSION)
        self.assertNotIn("ASkyguardGunner", FOR_MISSION)
        self.assertNotIn("ASkyguardGunner*", FOR_MISSION)

    def test_contract_does_not_lock_beat_index(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (FOR_MISSION,))
        locked_only = f"{FOR_MISSION}\n"
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, locked_only)
        self.assertNotIn("BeatIndexForElapsed", FOR_MISSION)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            LOCKED_DECLARATIONS,
        )

    def test_contract_does_not_lock_day_or_night_for_mission(self) -> None:
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
        self.assertNotEqual(FOR_MISSION, DAY_FOR_MISSION)
        self.assertNotEqual(FOR_MISSION, NIGHT_FOR_MISSION)
        self.assertNotIn(DAY_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn(NIGHT_FOR_MISSION, LOCKED_DECLARATIONS)
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
            self.assertNotIn(field, FOR_MISSION)
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
            self.assertNotIn(name, FOR_MISSION)
        self.assertNotIn("Approach", block)
        self.assertNotIn("WaterwayBoats", block)
        self.assertNotIn("BargeClusters", block)

    def test_contract_does_not_read_cpp_or_which_kit_tables(self) -> None:
        block = kits_namespace(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FOR_MISSION)
            self.assertNotIn(token, block)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", block)
        self.assertNotIn("SkyguardStormRainBeatKits::ForMission", block)
        self.assertNotIn("return RiverHammer()", block)
        self.assertNotIn("return IronRain()", block)

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
        self.assertNotEqual(FOR_MISSION, "Rifle")
        self.assertNotEqual(FOR_MISSION, "Igla")
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
                "ForMission is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, FOR_MISSION.lower())

    def test_contract_is_for_mission_declaration_only(self) -> None:
        header = origin_main_header()
        block = kits_namespace(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (FOR_MISSION,))
        self.assertEqual(
            require_declaration(block, FOR_MISSION),
            FOR_MISSION,
        )
        locked_only = f"{FOR_MISSION}\n"
        for neighbor in UNLOCKED_SEQUENCES:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FOR_MISSION)
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(DAY_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn(NIGHT_FOR_MISSION, LOCKED_DECLARATIONS)
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, block)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, block)
        for token in CPP_AND_INVENTED:
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
        self.assertNotIn("KeepsHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("BeatIndexForElapsed", LOCKED_DECLARATIONS)
        self.assertNotIn("RiverHammer", LOCKED_DECLARATIONS)
        self.assertNotIn("ASkyguardGunner", FOR_MISSION)
        self.assertNotEqual(HEADER_PATH, DAY_HEADER_PATH)
        self.assertNotEqual(HEADER_PATH, NIGHT_HEADER_PATH)
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
