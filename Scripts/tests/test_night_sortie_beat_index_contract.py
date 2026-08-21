from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
NAMESPACE_NAME = "SkyguardNightSortieBeatKit"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or elapsed-second tables.
BEAT_INDEX = "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
# Leftover #56–#64 plus NightSortieBeatKit production sources/tests.
# This lane only adds an isolated Python BeatIndexForElapsed
# declaration contract. Stay off leftover Harbor #6/#8/#9.
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
# Isolated-test drafts stay off this lane. On-main NightEyes() /
# DownedBird() / ForMission() sequences, Beats[7] (#252),
# bKeepThermal (#250), beat-kind enum (#246), beat defaults
# (#247), and kit FName fields (#254) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_index_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardNightSortieBeatKit& NightEyes();",
    "const FSkyguardNightSortieBeatKit& DownedBird();",
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);",
    "bool SequencesDiffer(",
    "ESkyguardNightSortieBeatKind KindAt(",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "NightEyes",
    "DownedBird",
    "ForMission",
)
SEQUENCES_DIFFER_NOT_LOCKED = "bool SequencesDiffer("
KIND_AT_NOT_LOCKED = "ESkyguardNightSortieBeatKind KindAt("
# #252 Beats[7], #250 bKeepThermal, #246 kind enum, #247 beat
# defaults, #254 FName fields stay unlocked. Parse the
# namespace, not those types.
BEATS_NOT_LOCKED = "FSkyguardNightSortieBeat Beats[7];"
KEEP_THERMAL_NOT_LOCKED = "bool bKeepThermal = true;"
FIELDS_NOT_LOCKED = (
    "FName MissionId;",
    "FName WeatherIdentity;",
)
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
SIBLING_TYPES = (
    "enum class ESkyguardNightSortieBeatKind",
    "struct FSkyguardNightSortieBeat",
    "struct FSkyguardNightSortieBeatKit",
    "FSkyguardDaySortieBeatKit",
    "ESkyguardDaySortieBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardStormRainBeatKind",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
# .cpp bodies / invented elapsed tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f",
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


def namespace_body(header: str) -> str:
    match = NAMESPACE_RE.search(header)
    if match is None:
        raise AssertionError(
            f"namespace {NAMESPACE_NAME} is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def require_declaration(region: str, declaration: str) -> str:
    if declaration not in region:
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class NightSortieBeatIndexContractTests(unittest.TestCase):
    def test_night_sortie_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertIn(BEAT_INDEX, body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedBeatKit\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_struct_or_enum_alone_does_not_satisfy_namespace(self) -> None:
        kit_and_enum = (
            "enum class ESkyguardNightSortieBeatKind : uint8\n"
            "{\n"
            "\tDarkIngress,\n"
            "\tExtraction\n"
            "};\n"
            "struct FSkyguardNightSortieBeat\n"
            "{\n"
            "\tESkyguardNightSortieBeatKind Kind = "
            "ESkyguardNightSortieBeatKind::DarkIngress;\n"
            "};\n"
            "struct FSkyguardNightSortieBeatKit\n"
            "{\n"
            "\tFName MissionId;\n"
            "\tFName WeatherIdentity;\n"
            "\tbool bKeepThermal = true;\n"
            "\tFSkyguardNightSortieBeat Beats[7];\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(kit_and_enum)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_beat_index_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardNightSortieBeatKit& NightEyes();\n"
            "\tconst FSkyguardNightSortieBeatKit& DownedBird();\n"
            "\tconst FSkyguardNightSortieBeatKit& ForMission(FName MissionId);\n"
            "\tbool SequencesDiffer(\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Left,\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Right);\n"
            "\tESkyguardNightSortieBeatKind KindAt(\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Kit,\n"
            "\t\tint32 Index);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, BEAT_INDEX)
        self.assertIn("BeatIndexForElapsed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_beat_index_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(body, BEAT_INDEX), BEAT_INDEX)
        self.assertIn(BEAT_INDEX, body)
        self.assertEqual(body.count(BEAT_INDEX), 1)
        self.assertTrue(BEAT_INDEX.endswith(";"), BEAT_INDEX)
        self.assertNotIn("INDEX_NONE", BEAT_INDEX)
        self.assertNotIn("return ", BEAT_INDEX)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(BEAT_INDEX.endswith(";"), BEAT_INDEX)
        self.assertNotIn("return ", BEAT_INDEX)
        self.assertNotIn("INDEX_NONE", BEAT_INDEX)
        self.assertNotIn("NAME_None", BEAT_INDEX)
        self.assertNotIn("{", BEAT_INDEX)
        self.assertNotIn("}", BEAT_INDEX)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BEAT_INDEX)
            if token != "return ":
                self.assertNotIn(token, body)

    def test_contract_does_not_relock_kit_sequences(self) -> None:
        locked_only = f"{BEAT_INDEX}\n"
        self.assertEqual(require_declaration(locked_only, BEAT_INDEX), BEAT_INDEX)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, BEAT_INDEX)
        self.assertNotIn("NightEyes()", locked_only)
        self.assertNotIn("DownedBird()", locked_only)
        self.assertNotIn("ForMission(", locked_only)

    def test_contract_does_not_relock_sequences_differ(self) -> None:
        locked_only = f"{BEAT_INDEX}\n"
        self.assertNotIn(SEQUENCES_DIFFER_NOT_LOCKED, locked_only)
        self.assertNotIn("SequencesDiffer", BEAT_INDEX)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn(
            "bool SequencesDiffer(",
            (BEAT_INDEX,),
        )

    def test_contract_does_not_relock_kind_at(self) -> None:
        locked_only = f"{BEAT_INDEX}\n"
        self.assertNotIn(KIND_AT_NOT_LOCKED, locked_only)
        self.assertNotIn("KindAt", BEAT_INDEX)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn("ESkyguardNightSortieBeatKind KindAt(", (BEAT_INDEX,))

    def test_contract_does_not_relock_beats_enum_defaults_or_fields(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(BEATS_NOT_LOCKED, BEAT_INDEX)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, BEAT_INDEX)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, BEAT_INDEX)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, BEAT_INDEX)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, BEAT_INDEX)
        self.assertNotIn("enum class ESkyguardNightSortieBeatKind", body)
        self.assertNotIn("struct FSkyguardNightSortieBeat", body)
        self.assertNotIn("struct FSkyguardNightSortieBeatKit", body)

    def test_contract_parses_namespace_not_struct_or_enum(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertIn("struct FSkyguardNightSortieBeatKit", header)
        self.assertIn("enum class ESkyguardNightSortieBeatKind", header)
        self.assertNotIn("enum class ESkyguardNightSortieBeatKind", body)
        self.assertNotIn("struct FSkyguardNightSortieBeat", body)
        self.assertNotIn("struct FSkyguardNightSortieBeatKit", body)
        self.assertIn(BEAT_INDEX, body)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn("FName WeatherIdentity;", body)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)

    def test_contract_does_not_read_cpp_or_elapsed_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BEAT_INDEX)
        self.assertNotIn("SkyguardNightSortieBeatKit.cpp", body)
        self.assertNotIn("SkyguardNightSortieBeatKit::BeatIndexForElapsed", body)
        self.assertNotIn("ElapsedSeconds <", body)
        self.assertNotIn("ElapsedSeconds >", body)
        self.assertNotIn("120.f", body)
        self.assertNotIn("240.f", body)

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

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(BEAT_INDEX, "Rifle")
        self.assertNotEqual(BEAT_INDEX, "Igla")
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"night-sortie BeatIndexForElapsed contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, BEAT_INDEX.lower())

    def test_contract_is_beat_index_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(require_declaration(body, BEAT_INDEX), BEAT_INDEX)
        locked_only = f"{BEAT_INDEX}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BEAT_INDEX)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, locked_only)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BEAT_INDEX)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return ", body)
        self.assertNotIn("enum class", body)
        self.assertNotEqual(BEAT_INDEX, "Rifle")
        self.assertNotEqual(BEAT_INDEX, "Igla")

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
