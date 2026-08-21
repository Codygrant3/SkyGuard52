from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
STRUCT_NAME = "FSkyguardNightSortieBeatKit"
LOCKED_BEATS = "FSkyguardNightSortieBeat Beats[7];"
# Leftover #56–#64 plus NightSortieBeatKit production sources/tests and
# the on-main beat-kit contract. This lane only adds an isolated
# Python Beats[7] contract.
LOCKED = {
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardNightSortieBeatKitTests.cpp",
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
# Isolated-test drafts #107–#249 and newer stay off this lane.
# Night-sortie-beat-kit defaults (bKeepThermal) is now being opened.
# Night-sortie-beat-kind enum (#246), night-sortie-beat defaults (#247),
# and in-flight loadout-spec / day-kit Beats[7] stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_threat_kind_roster_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG night-sortie kit Beats[7] only. MissionId / WeatherIdentity /
# bKeepThermal may appear in the kit body but are not the lock surface.
# ESkyguardNightSortieBeatKind enumerators (#246), FSkyguardNightSortieBeat
# in-struct defaults (#247), bKeepThermal=true (now opening), and
# NightEyes() / DownedBird() sequences stay unlocked.
BEAT_KINDS_NOT_LOCKED = (
    "DarkIngress",
    "ThermalHunt",
    "RadarVanHunt",
    "RooftopHeat",
    "RadarNetCollapse",
    "IslandIngress",
    "SearchIsland",
    "HoldTheWreck",
    "RescuePressure",
    "RescueLift",
    "MixedSwarm",
    "Extraction",
)
NIGHT_BEAT_DEFAULTS_NOT_LOCKED = (
    "ESkyguardNightSortieBeatKind Kind =",
    "const TCHAR* Call =",
    "ESkyguardThreatKind Threat =",
    "ESkyguardNightSortieBeatKind::DarkIngress",
    'TEXT("")',
    "ESkyguardThreatKind::FastAttacker",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "NightEyes",
    "DownedBird",
    "ForMission",
    "SequencesDiffer",
    "BeatIndexForElapsed",
    "KindAt",
)
SIBLING_TYPES = (
    "enum class ESkyguardNightSortieBeatKind",
    "struct FSkyguardNightSortieBeat",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardDaySortieBeat",
    "ESkyguardDaySortieBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardStormRainBeatKind",
    "ESkyguardSortieBeat",
    "FSkyguardLoadoutSpec",
    "ESkyguardMissionWeather",
)
# bKeepThermal is present on origin/main and locked by the sibling
# kit-defaults draft. Do not treat it as invented or as this lock.
INVENTED_FIELDS = (
    "BeatCount",
    "Kinds",
    "Threats",
    "Stations",
    "Calls",
    "Title",
    "WeatherLabel",
    "bHydraForClusters",
    "INDEX_NONE",
    "NAME_None",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "FString()",
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
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def beats_declaration(body: str) -> str:
    match = re.search(r"FSkyguardNightSortieBeat\s+Beats\[7\];", body)
    if match is None:
        raise AssertionError(
            f"FSkyguardNightSortieBeat Beats[7] is missing from "
            f"origin/main:{HEADER_PATH} struct {STRUCT_NAME}"
        )
    return match.group(0)


def array_declarations(body: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\];",
        body,
    )


class NightSortieBeatKitBeatsContractTests(unittest.TestCase):
    def test_night_sortie_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = kit_body(header)
        self.assertIn(LOCKED_BEATS, body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kit_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_beat_struct_alone_does_not_satisfy_kit_struct(self) -> None:
        beat_only = (
            "struct FSkyguardNightSortieBeat\n"
            "{\n"
            "\tESkyguardNightSortieBeatKind Kind = "
            "ESkyguardNightSortieBeatKind::DarkIngress;\n"
            '\tconst TCHAR* Call = TEXT("");\n'
            "\tESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::FastAttacker;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kit_body(beat_only)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_beats_declaration_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            beats_declaration(
                "{\n"
                "\tFName MissionId;\n"
                "\tFName WeatherIdentity;\n"
                "\tbool bKeepThermal = true;\n"
                "};\n"
            )
        self.assertIn("Beats[7]", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_beats_is_declared_as_seven_night_sortie_beats(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(beats_declaration(body), LOCKED_BEATS)
        self.assertIn(LOCKED_BEATS, body)
        self.assertEqual(
            array_declarations(body),
            [("FSkyguardNightSortieBeat", "Beats", "7")],
        )
        self.assertNotIn("Beats[7] =", body)
        self.assertNotIn("Beats[INDEX_NONE]", body)
        self.assertNotIn("Beats[BeatCount]", body)
        self.assertNotIn("Beats[6]", body)
        self.assertNotIn("Beats[8]", body)
        self.assertNotIn("FSkyguardDaySortieBeat Beats[7]", body)

    def test_struct_does_not_invent_index_none_or_extra_fields(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(beats_declaration(body), LOCKED_BEATS)
        for token in INVENTED_FIELDS:
            self.assertNotIn(token, body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString", body)
        self.assertNotIn("int32", body)
        self.assertNotIn("float", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardNightSortieBeatKind", body)
        self.assertNotIn("enum class", body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardNightSortieBeatKind::{name}", body)

    def test_contract_does_not_relock_night_sortie_beat_defaults(self) -> None:
        body = kit_body(origin_main_header())
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Kind =", body)
        self.assertNotIn("Call =", body)
        self.assertNotIn("Threat =", body)
        self.assertNotIn("struct FSkyguardNightSortieBeat", body)
        self.assertIn("FSkyguardNightSortieBeat Beats[7];", body)

    def test_contract_does_not_relock_bkeepthermal(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(beats_declaration(body), LOCKED_BEATS)
        self.assertNotIn("bKeepThermal", LOCKED_BEATS)
        self.assertNotIn("true", LOCKED_BEATS)
        self.assertNotEqual(LOCKED_BEATS, "bool bKeepThermal = true;")
        self.assertNotIn("bKeepThermal = true", LOCKED_BEATS)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("NightEyes()", body)
        self.assertNotIn("DownedBird()", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

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
        declaration = beats_declaration(body)
        self.assertEqual(declaration, LOCKED_BEATS)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(declaration, "Rifle")
        self.assertNotEqual(declaration, "Igla")
        self.assertNotEqual(
            array_declarations(body),
            [("Rifle", "Beats", "7")],
        )

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "night-sortie-beat-kit Beats[7] is Apache CPG radar-net / "
                "search-island identity, not Yak",
            )

    def test_contract_is_night_sortie_beat_kit_beats_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(beats_declaration(body), LOCKED_BEATS)
        self.assertIn(LOCKED_BEATS, body)
        self.assertEqual(
            array_declarations(body),
            [("FSkyguardNightSortieBeat", "Beats", "7")],
        )
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in INVENTED_FIELDS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotEqual(beats_declaration(body), "Rifle Beats[7];")
        self.assertNotIn("NightEyes", body)
        self.assertNotIn("DownedBird", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotIn("bKeepThermal", LOCKED_BEATS)

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
