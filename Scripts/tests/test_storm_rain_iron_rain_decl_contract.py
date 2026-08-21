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
# values, sequence contents, or which beats IronRain returns.
# origin/main may split the factory as
# const FSkyguardStormRainBeatKit& /
# IronRain();
IRON_RAIN = "const FSkyguardStormRainBeatKit& IronRain();"
IRON_RAIN_HEAD = "IronRain("
LOCKED_DECLARATION = IRON_RAIN
LOCKED_DECLARATIONS = (IRON_RAIN,)
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python IronRain() factory declaration contract.
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
# Isolated-test drafts stay off this lane. RiverHammer() is the
# sibling in-flight factory. ForMission (#274), KeepsHydraForClusters
# (#264), BeatIndexForElapsed (#267), kind enum (#245), kit defaults
# (#248), Kinds (#255), leftover theater-kit #59, on-main IronRain()
# sequence contents, and day/night kits stay sibling-only.
# ApplyHydraForClusters stays unlocked (takes leftover ASkyguardGunner*).
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_for_mission_contract.py",
    "Scripts/tests/test_storm_rain_keeps_hydra_contract.py",
    "Scripts/tests/test_storm_rain_beat_index_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
    "Scripts/tests/test_storm_rain_river_hammer_decl_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py",
    "Scripts/tests/test_day_sortie_for_mission_contract.py",
    "Scripts/tests/test_night_sortie_for_mission_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardStormRainBeatKit& RiverHammer();",
    "const FSkyguardStormRainBeatKit& ForMission(FName MissionId);",
    "bool KeepsHydraForClusters(ESkyguardMissionWeather Weather);",
    "bool ApplyHydraForClusters(",
    "ASkyguardGunner* Gunner",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
)
# Sibling in-flight factory stays unlocked.
SIBLING_FACTORY_NOT_LOCKED = (
    "const FSkyguardStormRainBeatKit& RiverHammer();"
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
# Iron Rain methods with leftover Rifle/Igla names stay deferred.
UNLOCKED_IGLA_RIFLE_FINISH = (
    "ApplySecondIglaFinish",
    "ArmFuelControlRifleFinish",
)
# Day/night factories live in different headers. This lane does not
# read those headers or lock those declarations.
DAY_FOR_MISSION = (
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);"
)
NIGHT_FOR_MISSION = (
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);"
)
# On-main IronRain() sequence contents stay unlocked. Do not invent
# which beats the factory returns.
SEQUENCE_CONTENTS_NOT_LOCKED = (
    "MakeIronRain",
    "MakeRiverHammer",
    "M05_StormFront",
    "M08_RescueCover",
    "SevereSquall",
    "RescueSunset",
    "WaterwayBoats",
    "BargeClusters",
    "LightningWindow",
    "ProtectWaterway",
    "Tempest",
    "GunLine",
    "KillBattery",
    "BarrageCover",
    "RescueCorridor",
)
KIT_RETURNS_NOT_LOCKED = (
    "return IronRain()",
    "return RiverHammer()",
    "MakeIronRain",
    "MakeRiverHammer",
    "M08_RescueCover",
    "M05_StormFront",
    "GunLine",
    "KillBattery",
    "BarrageCover",
    "RescueCorridor",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "RiverHammer",
    "ForMission",
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
    "MakeIronRain",
    "MakeRiverHammer",
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
    normalized = re.sub(r"\s+", " ", text)
    normalized = re.sub(r"\s*\(\s*", "(", normalized)
    normalized = re.sub(r"\s*\)\s*", ")", normalized)
    return normalized.strip()


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


def namespace_body(header: str) -> str:
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
                return header[brace : index + 1]
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


class StormRainIronRainDeclContractTests(unittest.TestCase):
    def test_storm_rain_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, IRON_RAIN), body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedBeatKits\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_or_struct_alone_does_not_satisfy_namespace(self) -> None:
        enum_and_struct = (
            "enum class ESkyguardStormRainBeatKind : uint8\n"
            "{\n"
            "\tApproach,\n"
            "\tIronRain,\n"
            "\tExtract\n"
            "};\n"
            "struct FSkyguardStormRainBeatKit\n"
            "{\n"
            "\tFName MissionId;\n"
            "\tbool bHydraForClusters = true;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(enum_and_struct)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_iron_rain_declaration_fails_closed(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission(FName MissionId);\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        body = namespace_body(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, IRON_RAIN)
        self.assertIn("IronRain", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbors_do_not_satisfy_iron_rain(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "\tconst FSkyguardStormRainBeatKit& ForMission(FName MissionId);\n"
            "\tbool KeepsHydraForClusters(ESkyguardMissionWeather Weather);\n"
            "\tbool ApplyHydraForClusters(\n"
            "\t\tASkyguardGunner* Gunner,\n"
            "\t\tconst FSkyguardStormRainBeatKit& Kit);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "}\n"
        )
        body = namespace_body(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, IRON_RAIN)
        self.assertIn("IronRain", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(body, IRON_RAIN))
        self.assertIn("RiverHammer()", body)
        self.assertIn("ForMission", body)
        self.assertIn("KeepsHydraForClusters", body)
        self.assertIn("ApplyHydraForClusters", body)
        self.assertIn("BeatIndexForElapsed", body)

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tvoid IronRain();\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain(FName MissionId);\n"
            "\tconst FSkyguardDaySortieBeatKit& IronRain();\n"
            "\tFSkyguardStormRainBeatKit IronRain();\n"
            "}\n"
        )
        body = namespace_body(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, IRON_RAIN)
        self.assertIn("IronRain", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("IronRain", body)
        self.assertFalse(has_declaration(body, IRON_RAIN))

    def test_origin_main_split_line_form_is_accepted(self) -> None:
        split_return = (
            "{\n"
            "\tconst FSkyguardStormRainBeatKit&\n"
            "\tIronRain();\n"
            "}\n"
        )
        split_parens = (
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& IronRain(\n"
            "\t);\n"
            "}\n"
        )
        one_line = "{\n\t" + IRON_RAIN + "\n}\n"
        self.assertTrue(has_declaration(split_return, IRON_RAIN), split_return)
        self.assertEqual(require_declaration(split_return, IRON_RAIN), IRON_RAIN)
        self.assertEqual(declaration_count(split_return, IRON_RAIN), 1)
        self.assertEqual(require_declaration(split_parens, IRON_RAIN), IRON_RAIN)
        self.assertEqual(require_declaration(one_line, IRON_RAIN), IRON_RAIN)
        self.assertIn(IRON_RAIN_HEAD, split_return)
        self.assertIn(IRON_RAIN_HEAD, split_parens)
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(body, IRON_RAIN), IRON_RAIN)
        self.assertIn(IRON_RAIN_HEAD, body)

    def test_iron_rain_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, IRON_RAIN),
            IRON_RAIN,
        )
        self.assertEqual(LOCKED_DECLARATIONS, (IRON_RAIN,))
        self.assertEqual(LOCKED_DECLARATION, IRON_RAIN)
        self.assertTrue(has_declaration(body, IRON_RAIN), body)
        self.assertEqual(declaration_count(body, IRON_RAIN), 1)
        self.assertTrue(IRON_RAIN.endswith(";"), IRON_RAIN)
        self.assertNotIn("INDEX_NONE", IRON_RAIN)
        self.assertNotIn("return ", IRON_RAIN)
        self.assertNotIn("ASkyguardGunner", IRON_RAIN)
        self.assertNotIn("KeepsHydraForClusters", IRON_RAIN)
        self.assertNotIn("ApplyHydraForClusters", IRON_RAIN)
        self.assertNotIn("BeatIndexForElapsed", IRON_RAIN)
        self.assertNotIn("ForMission", IRON_RAIN)
        self.assertNotIn("RiverHammer", IRON_RAIN)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        for declaration in LOCKED_DECLARATIONS:
            self.assertTrue(declaration.endswith(";"), declaration)
            self.assertNotIn("return ", declaration)
            self.assertNotIn("INDEX_NONE", declaration)
            self.assertNotIn("NAME_None", declaration)
            self.assertNotIn("{", declaration)
            self.assertNotIn("}", declaration)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IRON_RAIN)
            if token not in ("return ",):
                self.assertNotIn(token, body)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("bHydraForClusters = true", body)

    def test_declaration_does_not_invent_which_beats_are_returned(
        self,
    ) -> None:
        locked_only = f"{IRON_RAIN}\n"
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(locked_only, IRON_RAIN), IRON_RAIN)
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IRON_RAIN)
        self.assertNotIn("return IronRain()", body)
        self.assertNotIn("return RiverHammer()", body)
        self.assertNotIn("MakeIronRain", IRON_RAIN)
        self.assertNotIn("MakeIronRain", body)
        self.assertNotIn("M08_RescueCover", IRON_RAIN)
        self.assertNotIn("M08_RescueCover", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, IRON_RAIN)
            self.assertNotIn(name, body)
        self.assertNotIn("ESkyguardStormRainBeatKind::IronRain", IRON_RAIN)
        self.assertNotIn("ESkyguardStormRainBeatKind::IronRain", body)
        self.assertNotEqual(IRON_RAIN, SIBLING_FACTORY_NOT_LOCKED)
        self.assertNotEqual(IRON_RAIN, FOR_MISSION_NOT_LOCKED)

    def test_contract_does_not_relock_sibling_factory(self) -> None:
        locked_only = f"{IRON_RAIN}\n"
        self.assertEqual(require_declaration(locked_only, IRON_RAIN), IRON_RAIN)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, locked_only)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, IRON_RAIN)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("RiverHammer()", locked_only)
        self.assertNotIn("RiverHammer", IRON_RAIN)
        self.assertNotEqual(IRON_RAIN, "RiverHammer()")
        self.assertIn(
            "Scripts/tests/test_storm_rain_river_hammer_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_for_mission(self) -> None:
        locked_only = f"{IRON_RAIN}\n"
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, locked_only)
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("ForMission", IRON_RAIN)
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
        locked_only = f"{IRON_RAIN}\n"
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(locked_only, IRON_RAIN), IRON_RAIN)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IRON_RAIN)
            self.assertNotIn(token, body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, IRON_RAIN)
            self.assertNotIn(name, body)
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_lock_keeps_hydra_or_apply_hydra(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (IRON_RAIN,))
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        self.assertNotIn("KeepsHydraForClusters", IRON_RAIN)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, IRON_RAIN)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", IRON_RAIN)
        self.assertNotIn("ASkyguardGunner", IRON_RAIN)
        self.assertNotIn("ASkyguardGunner*", IRON_RAIN)
        self.assertIn(
            "Scripts/tests/test_storm_rain_keeps_hydra_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_lock_beat_index(self) -> None:
        self.assertEqual(LOCKED_DECLARATIONS, (IRON_RAIN,))
        locked_only = f"{IRON_RAIN}\n"
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, locked_only)
        self.assertNotIn("BeatIndexForElapsed", IRON_RAIN)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            LOCKED_DECLARATIONS,
        )
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_index_contract.py",
            LOCKED_SCRIPTS,
        )

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
        self.assertNotEqual(IRON_RAIN, DAY_FOR_MISSION)
        self.assertNotEqual(IRON_RAIN, NIGHT_FOR_MISSION)
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
        body = namespace_body(origin_main_header())
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, IRON_RAIN)
            self.assertNotIn(field, body)
        self.assertNotIn("bHydraForClusters = true", body)
        self.assertNotIn("Kinds[BeatCount]", body)
        self.assertNotIn("Threats[BeatCount]", body)
        self.assertNotIn("Stations[BeatCount]", body)
        self.assertNotIn("Calls[BeatCount]", body)
        self.assertNotIn("BeatCount = 7", body)
        self.assertNotIn("Weather =", body)
        self.assertNotIn("Title", body)
        self.assertNotIn("WeatherLabel", body)
        self.assertNotIn("WeatherIdentity", body)
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("UENUM(", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", body)
            self.assertNotIn(name, IRON_RAIN)
        self.assertNotIn("ESkyguardStormRainBeatKind::IronRain", body)
        self.assertNotIn("ESkyguardStormRainBeatKind::IronRain", IRON_RAIN)
        self.assertNotIn("Approach", body)
        self.assertNotIn("WaterwayBoats", body)
        self.assertNotIn("BargeClusters", body)
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_read_cpp_or_which_kit_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IRON_RAIN)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", body)
        self.assertNotIn("SkyguardStormRainBeatKits::IronRain", body)
        self.assertNotIn("return RiverHammer()", body)
        self.assertNotIn("return IronRain()", body)
        self.assertNotIn("MakeIronRain", body)
        self.assertNotIn("MakeRiverHammer", body)

    def test_contract_does_not_lock_igla_rifle_finish_methods(self) -> None:
        body = namespace_body(origin_main_header())
        for token in UNLOCKED_IGLA_RIFLE_FINISH:
            self.assertNotIn(token, IRON_RAIN)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
            self.assertNotIn(token, body)
        self.assertNotIn("ApplySecondIglaFinish", body)
        self.assertNotIn("ArmFuelControlRifleFinish", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(LOCKED_DECLARATIONS, ("Rifle", "Igla"))
        self.assertNotEqual(IRON_RAIN, "Rifle")
        self.assertNotEqual(IRON_RAIN, "Igla")
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", body)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)

    def test_namespace_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"namespace {NAMESPACE_NAME} contains {banned}; "
                "IronRain is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, IRON_RAIN.lower())

    def test_contract_is_iron_rain_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (IRON_RAIN,))
        self.assertEqual(
            require_declaration(body, IRON_RAIN),
            IRON_RAIN,
        )
        locked_only = f"{IRON_RAIN}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IRON_RAIN)
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        self.assertNotIn("RiverHammer", locked_only)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn(UNLOCKED_KEEPS_HYDRA, LOCKED_DECLARATIONS)
        for token in UNLOCKED_APPLY:
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn(UNLOCKED_BEAT_INDEX, LOCKED_DECLARATIONS)
        self.assertNotIn(DAY_FOR_MISSION, LOCKED_DECLARATIONS)
        self.assertNotIn(NIGHT_FOR_MISSION, LOCKED_DECLARATIONS)
        for field in STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_DECLARATIONS)
            self.assertNotIn(field, body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IRON_RAIN)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        for token in UNLOCKED_IGLA_RIFLE_FINISH:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return ", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("struct FSkyguardStormRainBeatKit", body)
        self.assertNotIn("bHydraForClusters = true", body)
        self.assertNotIn("KeepsHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("ApplyHydraForClusters", LOCKED_DECLARATIONS)
        self.assertNotIn("BeatIndexForElapsed", LOCKED_DECLARATIONS)
        self.assertNotIn("RiverHammer", LOCKED_DECLARATIONS)
        self.assertNotIn("ForMission", LOCKED_DECLARATIONS)
        self.assertNotIn("ASkyguardGunner", IRON_RAIN)
        self.assertNotEqual(HEADER_PATH, DAY_HEADER_PATH)
        self.assertNotEqual(HEADER_PATH, NIGHT_HEADER_PATH)
        self.assertNotEqual(list(LOCKED_DECLARATIONS), ["Rifle", "Igla"])
        self.assertIn(
            "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
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
