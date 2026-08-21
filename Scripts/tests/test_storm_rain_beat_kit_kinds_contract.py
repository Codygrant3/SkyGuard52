from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
STRUCT_NAME = "FSkyguardStormRainBeatKit"
LOCKED_KINDS = "ESkyguardStormRainBeatKind Kinds[BeatCount] = {};"
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python Kinds[BeatCount] contract.
LOCKED = {
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
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
# Isolated-test drafts #107–#253 and newer stay off this lane.
# Storm-rain-beat-kind enum (#245), kit defaults (#248), day/night
# Beats[7] (#251/#252), and loadout defaults (#253) stay sibling-only.
# RiverHammer()/IronRain()/ForMission() stay on-main.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG storm-rain kit Kinds[BeatCount] only. BeatCount is the
# array bound identifier. Do not re-lock BeatCount=7 / Weather=Storm /
# bHydraForClusters=true (#248).
DEFAULTS_NOT_LOCKED = (
    "static constexpr int32 BeatCount = 7;",
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
    "bool bHydraForClusters = true;",
)
UNLOCKED_MEMBER_NAMES = (
    "MissionId",
    "Title",
    "WeatherIdentity",
    "WeatherLabel",
    "Threats",
    "Stations",
    "Calls",
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
KIT_SEQUENCES_NOT_LOCKED = (
    "RiverHammer",
    "IronRain",
    "ForMission",
    "KeepsHydraForClusters",
    "ApplyHydraForClusters",
    "BeatIndexForElapsed",
)
SIBLING_TYPES = (
    "enum class ESkyguardStormRainBeatKind",
    "namespace SkyguardStormRainBeatKits",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardDaySortieBeat",
    "ESkyguardDaySortieBeatKind",
    "FSkyguardNightSortieBeatKit",
    "FSkyguardNightSortieBeat",
    "ESkyguardNightSortieBeatKind",
    "FSkyguardLoadoutSpec",
    "ESkyguardLoadout",
    "ESkyguardSortieBeat",
)
LOADOUT_DEFAULTS_NOT_LOCKED = (
    "CannonMagazineSize",
    "CannonReserve",
    "RocketMagazineSize",
    "RocketReserve",
    "GuidedMagazineSize",
    "GuidedReserve",
    "FlareCount",
    "HullIntegrity",
    "PlaystyleLine",
    "StartingStation",
)
INVENTED_TOKENS = (
    "INDEX_NONE",
    "NAME_None",
    "Beats[7]",
    "Kinds[7]",
    "Kinds[INDEX_NONE]",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"


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


def kit_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                finish = index + 1
                if finish < len(header) and header[finish] == ";":
                    finish += 1
                return header[brace:finish]
    raise AssertionError(
        f"{STRUCT_NAME} body is unclosed in origin/main:{HEADER_PATH}"
    )


def kinds_declaration(body: str) -> str:
    match = re.search(
        r"ESkyguardStormRainBeatKind\s+Kinds\[BeatCount\]\s*=\s*\{\};",
        body,
    )
    if match is None:
        raise AssertionError(
            f"ESkyguardStormRainBeatKind Kinds[BeatCount] is missing from "
            f"origin/main:{HEADER_PATH} struct {STRUCT_NAME}"
        )
    return match.group(0)


def kinds_array_bound(body: str) -> str:
    match = re.search(
        r"ESkyguardStormRainBeatKind\s+Kinds\[([A-Za-z_][A-Za-z0-9_]*)\]\s*=\s*\{\};",
        body,
    )
    if match is None:
        raise AssertionError(
            f"ESkyguardStormRainBeatKind Kinds[BeatCount] is missing from "
            f"origin/main:{HEADER_PATH} struct {STRUCT_NAME}"
        )
    return match.group(1)


class StormRainBeatKitKindsContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = kit_body(header)
        self.assertIn(LOCKED_KINDS, body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kit_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_kinds_declaration_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kinds_declaration(
                "{\n\tstatic constexpr int32 BeatCount = 7;\n"
                "\tESkyguardThreatKind Threats[BeatCount] = {};\n};\n"
            )
        self.assertIn("Kinds[BeatCount]", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_kinds_is_declared_as_beatcount_array(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(kinds_declaration(body), LOCKED_KINDS)
        self.assertIn(LOCKED_KINDS, body)
        self.assertEqual(kinds_array_bound(body), "BeatCount")
        self.assertNotEqual(kinds_array_bound(body), "7")
        self.assertNotEqual(kinds_array_bound(body), "INDEX_NONE")
        self.assertNotIn("Kinds[7]", body)
        self.assertNotIn("Kinds[6]", body)
        self.assertNotIn("Kinds[8]", body)
        self.assertNotIn("Kinds[INDEX_NONE]", body)
        self.assertNotIn("Beats[BeatCount]", body)
        self.assertNotIn("FSkyguardDaySortieBeat Beats[7]", body)
        self.assertNotIn("FSkyguardNightSortieBeat Beats[7]", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(kinds_declaration(body), LOCKED_KINDS)
        for token in INVENTED_TOKENS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("Kinds[INDEX_NONE]", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("namespace SkyguardStormRainBeatKits", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", body)
            self.assertNotIn(name, body)

    def test_contract_does_not_relock_kit_defaults(self) -> None:
        declaration = kinds_declaration(kit_body(origin_main_header()))
        self.assertEqual(declaration, LOCKED_KINDS)
        for token in DEFAULTS_NOT_LOCKED:
            self.assertNotEqual(declaration, token)
        self.assertNotIn("Weather", declaration)
        self.assertNotIn("bHydraForClusters", declaration)
        self.assertNotIn("= 7", declaration)
        self.assertNotIn("Storm", declaration)
        self.assertNotIn("true", declaration)
        self.assertNotIn("static constexpr", declaration)

    def test_contract_does_not_lock_unlocked_members(self) -> None:
        declaration = kinds_declaration(kit_body(origin_main_header()))
        self.assertEqual(declaration, LOCKED_KINDS)
        for name in UNLOCKED_MEMBER_NAMES:
            self.assertNotIn(name, declaration)
        self.assertNotIn("Threats[BeatCount]", declaration)
        self.assertNotIn("Stations[BeatCount]", declaration)
        self.assertNotIn("Calls[BeatCount]", declaration)
        self.assertNotIn("FName MissionId", declaration)
        self.assertNotIn("WeatherIdentity", declaration)
        self.assertNotIn("WeatherLabel", declaration)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("RiverHammer()", body)
        self.assertNotIn("IronRain()", body)
        self.assertNotIn("ForMission(", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_lock_day_night_beats_or_loadout(self) -> None:
        body = kit_body(origin_main_header())
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in LOADOUT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Beats[7]", body)
        self.assertNotIn("FSkyguardDaySortieBeat Beats[7];", body)
        self.assertNotIn("FSkyguardNightSortieBeat Beats[7];", body)
        self.assertNotIn("FSkyguardLoadoutSpec", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = kit_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = kit_body(origin_main_header())
        declaration = kinds_declaration(body)
        self.assertEqual(declaration, LOCKED_KINDS)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(declaration, "Rifle")
        self.assertNotEqual(declaration, "Igla")
        self.assertNotEqual(
            declaration,
            "ESkyguardStormRainBeatKind Rifle[BeatCount] = {};",
        )

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "storm-rain beat-kit Kinds[BeatCount] is Apache CPG "
                "Hydra/Storm identity, not Yak",
            )

    def test_contract_is_storm_rain_beat_kit_kinds_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        declaration = kinds_declaration(body)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(declaration, LOCKED_KINDS)
        self.assertIn(LOCKED_KINDS, body)
        self.assertEqual(kinds_array_bound(body), "BeatCount")
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in LOADOUT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in INVENTED_TOKENS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        for token in DEFAULTS_NOT_LOCKED:
            self.assertNotEqual(declaration, token)
        for name in UNLOCKED_MEMBER_NAMES:
            self.assertNotIn(name, declaration)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("Beats[7]", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("namespace SkyguardStormRainBeatKits", body)
        self.assertNotEqual(declaration, "Rifle Kinds[BeatCount] = {};")

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
