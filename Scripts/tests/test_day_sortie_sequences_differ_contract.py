from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
NAMESPACE_NAME = "SkyguardDaySortieBeatKit"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or sequence contents. origin/main may split
# SequencesDiffer across lines as SequencesDiffer( /
# const FSkyguardDaySortieBeatKit& Left, /
# const FSkyguardDaySortieBeatKit& Right);
SEQUENCES_DIFFER = (
    "bool SequencesDiffer("
    "const FSkyguardDaySortieBeatKit& Left, "
    "const FSkyguardDaySortieBeatKit& Right);"
)
SEQUENCES_DIFFER_HEAD = "SequencesDiffer("
SEQUENCES_DIFFER_LEFT = "const FSkyguardDaySortieBeatKit& Left,"
SEQUENCES_DIFFER_RIGHT = "const FSkyguardDaySortieBeatKit& Right);"
# Leftover #56–#64 plus DaySortieBeatKit production sources/tests.
# This lane only adds an isolated Python SequencesDiffer
# declaration contract. Stay off leftover Harbor #6/#8/#9.
LOCKED = {
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardDaySortieBeatKitTests.cpp",
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
# Isolated-test drafts stay off this lane. In-flight BeatIndexForElapsed
# (#265), KindAt (#266), on-main BrokenHighway() sequences, Beats[7]
# (#251), beat-kind enum (#244), beat defaults (#249), and kit FName
# fields (#256) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_index_contract.py",
    "Scripts/tests/test_day_sortie_kind_at_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardDaySortieBeatKit& BrokenHighway();",
    "const FSkyguardDaySortieBeatKit& DustOffensive();",
    "const FSkyguardDaySortieBeatKit& HunterKiller();",
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
    "ESkyguardDaySortieBeatKind KindAt(",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "BrokenHighway",
    "DustOffensive",
    "HunterKiller",
    "ForMission",
)
BEAT_INDEX_NOT_LOCKED = (
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
)
KIND_AT_NOT_LOCKED = "ESkyguardDaySortieBeatKind KindAt("
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
# .cpp bodies / invented return values / sequence contents stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return true",
    "return false",
    "return INDEX_NONE",
    "Left.Beats",
    "Right.Beats",
    "Left.MissionId",
    "Right.MissionId",
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


def normalize_decl(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text)
    collapsed = re.sub(r"\s*\(\s*", "(", collapsed)
    collapsed = re.sub(r"\s*\)\s*", ")", collapsed)
    collapsed = re.sub(r"\s*,\s*", ", ", collapsed)
    return collapsed.strip()


def require_declaration(region: str, declaration: str) -> str:
    if normalize_decl(declaration) not in normalize_decl(region):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class DaySortieSequencesDifferContractTests(unittest.TestCase):
    def test_day_sortie_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertEqual(
            require_declaration(body, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
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

    def test_missing_sequences_differ_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardDaySortieBeatKit& BrokenHighway();\n"
            "\tconst FSkyguardDaySortieBeatKit& DustOffensive();\n"
            "\tconst FSkyguardDaySortieBeatKit& HunterKiller();\n"
            "\tconst FSkyguardDaySortieBeatKit& ForMission(FName MissionId);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "\tESkyguardDaySortieBeatKind KindAt(\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Kit,\n"
            "\t\tint32 Index);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SEQUENCES_DIFFER)
        self.assertIn("SequencesDiffer", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_sequences_differ_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        self.assertIn(SEQUENCES_DIFFER_HEAD, body)
        self.assertIn(SEQUENCES_DIFFER_LEFT, body)
        self.assertIn(SEQUENCES_DIFFER_RIGHT, body)
        self.assertEqual(body.count(SEQUENCES_DIFFER_HEAD), 1)
        self.assertTrue(SEQUENCES_DIFFER.endswith(";"), SEQUENCES_DIFFER)
        self.assertNotIn("INDEX_NONE", SEQUENCES_DIFFER)
        self.assertNotIn("return ", SEQUENCES_DIFFER)

    def test_sequences_differ_declaration_may_be_split_across_lines(
        self,
    ) -> None:
        split = (
            "{\n"
            "\tbool SequencesDiffer(\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Left,\n"
            "\t\tconst FSkyguardDaySortieBeatKit& Right);\n"
            "}\n"
        )
        one_line = "{\n\t" + SEQUENCES_DIFFER + "\n}\n"
        self.assertEqual(require_declaration(split, SEQUENCES_DIFFER), SEQUENCES_DIFFER)
        self.assertEqual(
            require_declaration(one_line, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        self.assertIn(SEQUENCES_DIFFER_HEAD, split)
        self.assertIn(SEQUENCES_DIFFER_LEFT, split)
        self.assertIn(SEQUENCES_DIFFER_RIGHT, split)
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        self.assertIn(SEQUENCES_DIFFER_HEAD, body)
        self.assertIn(SEQUENCES_DIFFER_LEFT, body)
        self.assertIn(SEQUENCES_DIFFER_RIGHT, body)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(SEQUENCES_DIFFER.endswith(";"), SEQUENCES_DIFFER)
        self.assertNotIn("return ", SEQUENCES_DIFFER)
        self.assertNotIn("INDEX_NONE", SEQUENCES_DIFFER)
        self.assertNotIn("NAME_None", SEQUENCES_DIFFER)
        self.assertNotIn("{", SEQUENCES_DIFFER)
        self.assertNotIn("}", SEQUENCES_DIFFER)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("return true", body)
        self.assertNotIn("return false", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SEQUENCES_DIFFER)
            if token != "return ":
                self.assertNotIn(token, body)

    def test_contract_does_not_relock_kit_sequences(self) -> None:
        locked_only = f"{SEQUENCES_DIFFER}\n"
        self.assertEqual(
            require_declaration(locked_only, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, SEQUENCES_DIFFER)
        self.assertNotIn("BrokenHighway()", locked_only)
        self.assertNotIn("DustOffensive()", locked_only)
        self.assertNotIn("HunterKiller()", locked_only)
        self.assertNotIn("ForMission(", locked_only)

    def test_contract_does_not_relock_beat_index(self) -> None:
        locked_only = f"{SEQUENCES_DIFFER}\n"
        self.assertNotIn(BEAT_INDEX_NOT_LOCKED, locked_only)
        self.assertNotIn("BeatIndexForElapsed", SEQUENCES_DIFFER)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            (SEQUENCES_DIFFER,),
        )

    def test_contract_does_not_relock_kind_at(self) -> None:
        locked_only = f"{SEQUENCES_DIFFER}\n"
        self.assertNotIn(KIND_AT_NOT_LOCKED, locked_only)
        self.assertNotIn("KindAt", SEQUENCES_DIFFER)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn("ESkyguardDaySortieBeatKind KindAt(", (SEQUENCES_DIFFER,))

    def test_contract_does_not_relock_beats_enum_defaults_or_fields(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(BEATS_NOT_LOCKED, SEQUENCES_DIFFER)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, SEQUENCES_DIFFER)
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, SEQUENCES_DIFFER)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, SEQUENCES_DIFFER)
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
        self.assertEqual(
            require_declaration(body, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn("FName WeatherIdentity;", body)

    def test_contract_does_not_read_cpp_or_sequence_contents(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SEQUENCES_DIFFER)
        self.assertNotIn("SkyguardDaySortieBeatKit.cpp", body)
        self.assertNotIn("SkyguardDaySortieBeatKit::SequencesDiffer", body)
        self.assertNotIn("Left.Beats", body)
        self.assertNotIn("Right.Beats", body)
        self.assertNotIn("Left.MissionId", body)
        self.assertNotIn("Right.MissionId", body)
        self.assertNotIn("Beats[7]", body)

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
        self.assertNotEqual(SEQUENCES_DIFFER, "Rifle")
        self.assertNotEqual(SEQUENCES_DIFFER, "Igla")
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
                f"day-sortie SequencesDiffer contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, SEQUENCES_DIFFER.lower())

    def test_contract_is_sequences_differ_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, SEQUENCES_DIFFER),
            SEQUENCES_DIFFER,
        )
        locked_only = f"{SEQUENCES_DIFFER}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SEQUENCES_DIFFER)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
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
            self.assertNotIn(token, SEQUENCES_DIFFER)
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
        self.assertNotEqual(SEQUENCES_DIFFER, "Rifle")
        self.assertNotEqual(SEQUENCES_DIFFER, "Igla")

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
