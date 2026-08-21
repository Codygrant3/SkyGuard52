from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
NAMESPACE_NAME = "SkyguardDaySortieBeatKit"
# Declaration presence only. Do not invent INDEX_NONE, sequence
# contents, beat kinds, or elapsed tables.
BROKEN_HIGHWAY = "const FSkyguardDaySortieBeatKit& BrokenHighway();"
# Leftover #56–#64 plus DaySortieBeatKit production sources.
# This lane only adds an isolated Python BrokenHighway() factory
# declaration contract. Stay off leftover Harbor #6/#8/#9.
LOCKED = {
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
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
# Isolated-test drafts stay off this lane. ForMission (opening now),
# on-main BrokenHighway() sequences, SequencesDiffer (#269),
# BeatIndexForElapsed (#265), KindAt (#266), Beats[7] (#251),
# beat-kind enum (#244), beat defaults (#249), and kit FName
# fields (#256) stay sibling-only. DustOffensive / HunterKiller
# factories are later lanes.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_for_mission_contract.py",
    "Scripts/tests/test_day_sortie_sequences_differ_contract.py",
    "Scripts/tests/test_day_sortie_beat_index_contract.py",
    "Scripts/tests/test_day_sortie_kind_at_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardDaySortieBeatKit& DustOffensive();",
    "const FSkyguardDaySortieBeatKit& HunterKiller();",
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);",
    "bool SequencesDiffer(",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
    "ESkyguardDaySortieBeatKind KindAt(",
)
# Sibling factories stay unlocked (later lanes).
SIBLING_FACTORIES_NOT_LOCKED = (
    "const FSkyguardDaySortieBeatKit& DustOffensive();",
    "const FSkyguardDaySortieBeatKit& HunterKiller();",
)
FOR_MISSION_NOT_LOCKED = (
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);"
)
SEQUENCES_DIFFER_NOT_LOCKED = "bool SequencesDiffer("
BEAT_INDEX_NOT_LOCKED = (
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
)
KIND_AT_NOT_LOCKED = "ESkyguardDaySortieBeatKind KindAt("
# On-main BrokenHighway() sequence contents stay unlocked.
SEQUENCE_CONTENTS_NOT_LOCKED = (
    "BrokenHighwayKit",
    "M03_ConvoyEscort",
    "DryMorning",
    "Beats[0]",
    "Beats[1]",
    "Beats[2]",
    "Beats[3]",
    "Beats[4]",
    "Beats[5]",
    "Beats[6]",
    "MakeBeat",
)
ELAPSED_TABLES_NOT_LOCKED = (
    "ElapsedSeconds",
    "BeatIndexForElapsed",
    "return 0",
    "return -1",
    "return INDEX_NONE",
)
# #251 Beats[7], #244 kind enum, #249 beat defaults, #256 FName
# fields stay unlocked. Parse the namespace, not those types.
BEATS_NOT_LOCKED = "FSkyguardDaySortieBeat Beats[7];"
FIELDS_NOT_LOCKED = (
    "FName MissionId;",
    "FName WeatherIdentity;",
)
BEAT_KINDS_NOT_LOCKED = (
    "RidgeIngress",
    "TechnicalScreen",
    "ClusterRidge",
    "TankAmbush",
    "ConvoyPressure",
    "ArmorColumn",
    "HazeIngress",
    "FenceSweep",
    "DugInLine",
    "AdaAcquire",
    "AdaSuppress",
    "ArmorPush",
    "DuskIngress",
    "SensorTrack",
    "DecoyScreen",
    "TelAcquire",
    "TelStrike",
    "ConvoyBreak",
    "Extraction",
)
DAY_BEAT_DEFAULTS_NOT_LOCKED = (
    "ESkyguardDaySortieBeatKind Kind =",
    "const TCHAR* Call =",
    "ESkyguardThreatKind Threat =",
    "ESkyguardDaySortieBeatKind::RidgeIngress",
    'TEXT("")',
    "ESkyguardThreatKind::GroundArmor",
)
SIBLING_TYPES = (
    "enum class ESkyguardDaySortieBeatKind",
    "struct FSkyguardDaySortieBeat",
    "struct FSkyguardDaySortieBeatKit",
    "FSkyguardNightSortieBeatKit",
    "ESkyguardNightSortieBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardStormRainBeatKind",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
# .cpp bodies / invented return values / sequence tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "BrokenHighwayKit",
    "DustOffensiveKit",
    "HunterKillerKit",
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


class DaySortieBrokenHighwayDeclContractTests(unittest.TestCase):
    def test_day_sortie_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertIn(BROKEN_HIGHWAY, body)
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
            "enum class ESkyguardDaySortieBeatKind : uint8\n"
            "{\n"
            "\tRidgeIngress,\n"
            "\tExtraction\n"
            "};\n"
            "struct FSkyguardDaySortieBeat\n"
            "{\n"
            "\tESkyguardDaySortieBeatKind Kind = "
            "ESkyguardDaySortieBeatKind::RidgeIngress;\n"
            "};\n"
            "struct FSkyguardDaySortieBeatKit\n"
            "{\n"
            "\tFName MissionId;\n"
            "\tFName WeatherIdentity;\n"
            "\tFSkyguardDaySortieBeat Beats[7];\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(kit_and_enum)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_broken_highway_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardDaySortieBeatKit& DustOffensive();\n"
            "\tconst FSkyguardDaySortieBeatKit& HunterKiller();\n"
            "\tconst FSkyguardDaySortieBeatKit& ForMission(FName MissionId);\n"
            "\tbool SequencesDiffer(\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Left,\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Right);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "\tESkyguardDaySortieBeatKind KindAt(\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Kit,\n"
            "\t\tint32 Index);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, BROKEN_HIGHWAY)
        self.assertIn("BrokenHighway", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_broken_highway_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, BROKEN_HIGHWAY),
            BROKEN_HIGHWAY,
        )
        self.assertIn(BROKEN_HIGHWAY, body)
        self.assertEqual(body.count(BROKEN_HIGHWAY), 1)
        self.assertTrue(BROKEN_HIGHWAY.endswith(";"), BROKEN_HIGHWAY)
        self.assertNotIn("INDEX_NONE", BROKEN_HIGHWAY)
        self.assertNotIn("return ", BROKEN_HIGHWAY)

    def test_sibling_factories_are_not_required(self) -> None:
        broken_highway_only = (
            "{\n"
            f"\t{BROKEN_HIGHWAY}\n"
            "}\n"
        )
        self.assertEqual(
            require_declaration(broken_highway_only, BROKEN_HIGHWAY),
            BROKEN_HIGHWAY,
        )
        for neighbor in SIBLING_FACTORIES_NOT_LOCKED:
            self.assertNotIn(neighbor, broken_highway_only)
            self.assertNotIn(neighbor, BROKEN_HIGHWAY)
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, broken_highway_only)
        self.assertNotIn("DustOffensive()", BROKEN_HIGHWAY)
        self.assertNotIn("HunterKiller()", BROKEN_HIGHWAY)
        self.assertNotIn("ForMission", BROKEN_HIGHWAY)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(BROKEN_HIGHWAY.endswith(";"), BROKEN_HIGHWAY)
        self.assertNotIn("return ", BROKEN_HIGHWAY)
        self.assertNotIn("INDEX_NONE", BROKEN_HIGHWAY)
        self.assertNotIn("NAME_None", BROKEN_HIGHWAY)
        self.assertNotIn("{", BROKEN_HIGHWAY)
        self.assertNotIn("}", BROKEN_HIGHWAY)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BROKEN_HIGHWAY)
            if token != "return ":
                self.assertNotIn(token, body)

    def test_contract_does_not_relock_sibling_factories(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        self.assertEqual(
            require_declaration(locked_only, BROKEN_HIGHWAY),
            BROKEN_HIGHWAY,
        )
        for neighbor in SIBLING_FACTORIES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BROKEN_HIGHWAY)
        self.assertNotIn("DustOffensive()", locked_only)
        self.assertNotIn("HunterKiller()", locked_only)
        self.assertNotEqual(BROKEN_HIGHWAY, "DustOffensive()")
        self.assertNotEqual(BROKEN_HIGHWAY, "HunterKiller()")

    def test_contract_does_not_relock_for_mission(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, locked_only)
        self.assertNotIn("ForMission", BROKEN_HIGHWAY)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn(
            "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);",
            (BROKEN_HIGHWAY,),
        )

    def test_contract_does_not_relock_kit_sequence_contents(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(locked_only, BROKEN_HIGHWAY),
            BROKEN_HIGHWAY,
        )
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BROKEN_HIGHWAY)
            self.assertNotIn(token, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, BROKEN_HIGHWAY)
            self.assertNotIn(name, body)

    def test_contract_does_not_relock_sequences_differ(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        self.assertNotIn(SEQUENCES_DIFFER_NOT_LOCKED, locked_only)
        self.assertNotIn("SequencesDiffer", BROKEN_HIGHWAY)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn(
            "bool SequencesDiffer(",
            (BROKEN_HIGHWAY,),
        )

    def test_contract_does_not_relock_beat_index(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        self.assertNotIn(BEAT_INDEX_NOT_LOCKED, locked_only)
        self.assertNotIn("BeatIndexForElapsed", BROKEN_HIGHWAY)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            (BROKEN_HIGHWAY,),
        )

    def test_contract_does_not_relock_kind_at(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        self.assertNotIn(KIND_AT_NOT_LOCKED, locked_only)
        self.assertNotIn("KindAt", BROKEN_HIGHWAY)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn("ESkyguardDaySortieBeatKind KindAt(", (BROKEN_HIGHWAY,))

    def test_contract_does_not_relock_elapsed_tables(self) -> None:
        locked_only = f"{BROKEN_HIGHWAY}\n"
        body = namespace_body(origin_main_header())
        for token in ELAPSED_TABLES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BROKEN_HIGHWAY)
        self.assertNotIn("ElapsedSeconds", BROKEN_HIGHWAY)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)

    def test_contract_does_not_relock_beats_enum_defaults_or_fields(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(BEATS_NOT_LOCKED, BROKEN_HIGHWAY)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, BROKEN_HIGHWAY)
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, BROKEN_HIGHWAY)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, BROKEN_HIGHWAY)
        self.assertNotIn("enum class ESkyguardDaySortieBeatKind", body)
        self.assertNotIn("struct FSkyguardDaySortieBeat", body)
        self.assertNotIn("struct FSkyguardDaySortieBeatKit", body)

    def test_contract_parses_namespace_not_struct_or_enum(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertIn("struct FSkyguardDaySortieBeatKit", header)
        self.assertIn("enum class ESkyguardDaySortieBeatKind", header)
        self.assertNotIn("enum class ESkyguardDaySortieBeatKind", body)
        self.assertNotIn("struct FSkyguardDaySortieBeat", body)
        self.assertNotIn("struct FSkyguardDaySortieBeatKit", body)
        self.assertIn(BROKEN_HIGHWAY, body)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn("FName WeatherIdentity;", body)

    def test_contract_does_not_read_cpp_or_sequence_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BROKEN_HIGHWAY)
        self.assertNotIn("SkyguardDaySortieBeatKit.cpp", body)
        self.assertNotIn("SkyguardDaySortieBeatKit::BrokenHighway", body)
        self.assertNotIn("BrokenHighwayKit", body)
        self.assertNotIn("M03_ConvoyEscort", body)
        self.assertNotIn("DryMorning", body)

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
        self.assertNotEqual(BROKEN_HIGHWAY, "Rifle")
        self.assertNotEqual(BROKEN_HIGHWAY, "Igla")
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
                f"day-sortie BrokenHighway contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, BROKEN_HIGHWAY.lower())

    def test_contract_is_broken_highway_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, BROKEN_HIGHWAY),
            BROKEN_HIGHWAY,
        )
        locked_only = f"{BROKEN_HIGHWAY}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BROKEN_HIGHWAY)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        self.assertNotIn("DustOffensive", locked_only)
        self.assertNotIn("HunterKiller", locked_only)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn("KindAt", locked_only)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BROKEN_HIGHWAY)
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
        self.assertNotEqual(BROKEN_HIGHWAY, "Rifle")
        self.assertNotEqual(BROKEN_HIGHWAY, "Igla")

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
