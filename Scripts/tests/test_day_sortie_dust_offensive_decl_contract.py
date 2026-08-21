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
# values, sequence contents, or which beats DustOffensive returns.
# origin/main may split the factory as
# const FSkyguardDaySortieBeatKit& /
# DustOffensive();
DUST_OFFENSIVE = "const FSkyguardDaySortieBeatKit& DustOffensive();"
DUST_OFFENSIVE_HEAD = "DustOffensive("
# Leftover #56–#64 plus DaySortieBeatKit production sources/tests.
# This lane only adds an isolated Python DustOffensive
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
# Isolated-test drafts stay off this lane. In-flight BrokenHighway()
# factory (#decl sibling), ForMission (#273), SequencesDiffer (#269),
# BeatIndexForElapsed (#265), KindAt (#266), on-main BrokenHighway()
# sequences, Beats[7] (#251), beat-kind enum (#244), beat defaults
# (#249), kit FName fields (#256), and next unused HunterKiller()
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_for_mission_contract.py",
    "Scripts/tests/test_day_sortie_broken_highway_decl_contract.py",
    "Scripts/tests/test_day_sortie_sequences_differ_contract.py",
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
    "const FSkyguardDaySortieBeatKit& HunterKiller();",
    "const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);",
    "bool SequencesDiffer(",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
    "ESkyguardDaySortieBeatKind KindAt(",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "BrokenHighway",
    "HunterKiller",
    "ForMission",
)
SEQUENCES_DIFFER_NOT_LOCKED = "bool SequencesDiffer("
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
    "ApplyHydraForClusters",
)
# .cpp bodies / invented return values / which-beats tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "return BrokenHighway()",
    "return DustOffensive()",
    "return HunterKiller()",
    "return DustOffensiveKit()",
    "DustOffensiveKit()",
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


class DaySortieDustOffensiveDeclContractTests(unittest.TestCase):
    def test_day_sortie_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertEqual(
            require_declaration(body, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
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

    def test_missing_dust_offensive_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardDaySortieBeatKit& BrokenHighway();\n"
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
            require_declaration(neighbors_only, DUST_OFFENSIVE)
        self.assertIn("DustOffensive", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_dust_offensive_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertIn(DUST_OFFENSIVE_HEAD, body)
        self.assertEqual(body.count(DUST_OFFENSIVE_HEAD), 1)
        self.assertTrue(DUST_OFFENSIVE.endswith(";"), DUST_OFFENSIVE)
        self.assertNotIn("INDEX_NONE", DUST_OFFENSIVE)
        self.assertNotIn("return ", DUST_OFFENSIVE)

    def test_dust_offensive_declaration_may_be_split_across_lines(
        self,
    ) -> None:
        split_return = (
            "{\n"
            "\tconst FSkyguardDaySortieBeatKit&\n"
            "\tDustOffensive();\n"
            "}\n"
        )
        split_parens = (
            "{\n"
            "\tconst FSkyguardDaySortieBeatKit& DustOffensive(\n"
            "\t);\n"
            "}\n"
        )
        one_line = "{\n\t" + DUST_OFFENSIVE + "\n}\n"
        self.assertEqual(
            require_declaration(split_return, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertEqual(
            require_declaration(split_parens, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertEqual(
            require_declaration(one_line, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertIn(DUST_OFFENSIVE_HEAD, split_return)
        self.assertIn(DUST_OFFENSIVE_HEAD, split_parens)
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertIn(DUST_OFFENSIVE_HEAD, body)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(DUST_OFFENSIVE.endswith(";"), DUST_OFFENSIVE)
        self.assertNotIn("return ", DUST_OFFENSIVE)
        self.assertNotIn("INDEX_NONE", DUST_OFFENSIVE)
        self.assertNotIn("NAME_None", DUST_OFFENSIVE)
        self.assertNotIn("{", DUST_OFFENSIVE)
        self.assertNotIn("}", DUST_OFFENSIVE)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DUST_OFFENSIVE)
            if token not in ("return ", "DustOffensiveKit()"):
                self.assertNotIn(token, body)

    def test_declaration_does_not_invent_which_beats_the_factory_returns(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("return DustOffensive()", DUST_OFFENSIVE)
        self.assertNotIn("return DustOffensiveKit()", DUST_OFFENSIVE)
        self.assertNotIn("return BrokenHighway()", DUST_OFFENSIVE)
        self.assertNotIn("return HunterKiller()", DUST_OFFENSIVE)
        self.assertNotIn("return DustOffensive()", body)
        self.assertNotIn("return DustOffensiveKit()", body)
        self.assertNotIn("DustOffensiveKit()", DUST_OFFENSIVE)
        self.assertNotIn("DustOffensiveKit()", body)
        self.assertNotIn("Beats[0]", DUST_OFFENSIVE)
        self.assertNotIn("Beats[0]", body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, DUST_OFFENSIVE)
            self.assertNotIn(name, body)
        self.assertNotEqual(DUST_OFFENSIVE, "BrokenHighway()")
        self.assertNotEqual(DUST_OFFENSIVE, "HunterKiller()")

    def test_contract_does_not_relock_kit_sequences(self) -> None:
        locked_only = f"{DUST_OFFENSIVE}\n"
        self.assertEqual(
            require_declaration(locked_only, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, DUST_OFFENSIVE)
        self.assertNotIn("BrokenHighway()", locked_only)
        self.assertNotIn("HunterKiller()", locked_only)
        self.assertNotIn("ForMission(", locked_only)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, locked_only)

    def test_contract_does_not_relock_sequences_differ(self) -> None:
        locked_only = f"{DUST_OFFENSIVE}\n"
        self.assertNotIn(SEQUENCES_DIFFER_NOT_LOCKED, locked_only)
        self.assertNotIn("SequencesDiffer", DUST_OFFENSIVE)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn(
            "bool SequencesDiffer(",
            (DUST_OFFENSIVE,),
        )

    def test_contract_does_not_relock_beat_index(self) -> None:
        locked_only = f"{DUST_OFFENSIVE}\n"
        self.assertNotIn(BEAT_INDEX_NOT_LOCKED, locked_only)
        self.assertNotIn("BeatIndexForElapsed", DUST_OFFENSIVE)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            (DUST_OFFENSIVE,),
        )

    def test_contract_does_not_relock_kind_at(self) -> None:
        locked_only = f"{DUST_OFFENSIVE}\n"
        self.assertNotIn(KIND_AT_NOT_LOCKED, locked_only)
        self.assertNotIn("KindAt", DUST_OFFENSIVE)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn("ESkyguardDaySortieBeatKind KindAt(", (DUST_OFFENSIVE,))

    def test_contract_does_not_relock_beats_enum_defaults_or_fields(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(BEATS_NOT_LOCKED, DUST_OFFENSIVE)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, DUST_OFFENSIVE)
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, DUST_OFFENSIVE)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, DUST_OFFENSIVE)
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
            require_declaration(body, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn("FName WeatherIdentity;", body)

    def test_contract_does_not_read_cpp_or_which_beats_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DUST_OFFENSIVE)
        self.assertNotIn("SkyguardDaySortieBeatKit.cpp", body)
        self.assertNotIn("SkyguardDaySortieBeatKit::DustOffensive", body)
        self.assertNotIn("return BrokenHighway()", body)
        self.assertNotIn("return DustOffensive()", body)
        self.assertNotIn("return HunterKiller()", body)
        self.assertNotIn("DustOffensiveKit()", body)
        self.assertNotIn("HazeIngress", body)
        self.assertNotIn("AdaSuppress", body)
        self.assertNotIn("FenceSweep", body)

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
        self.assertNotEqual(DUST_OFFENSIVE, "Rifle")
        self.assertNotEqual(DUST_OFFENSIVE, "Igla")
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
                f"day-sortie DustOffensive contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, DUST_OFFENSIVE.lower())

    def test_contract_is_dust_offensive_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, DUST_OFFENSIVE),
            DUST_OFFENSIVE,
        )
        locked_only = f"{DUST_OFFENSIVE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DUST_OFFENSIVE)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
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
            self.assertNotIn(token, DUST_OFFENSIVE)
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
        self.assertNotIn("ApplyHydraForClusters", body)
        self.assertNotEqual(DUST_OFFENSIVE, "Rifle")
        self.assertNotEqual(DUST_OFFENSIVE, "Igla")

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
