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
# values, sequence contents, or which beats DownedBird returns.
DOWNED_BIRD = "const FSkyguardNightSortieBeatKit& DownedBird();"
# Leftover #56–#64 plus NightSortieBeatKit production sources.
# This lane only adds an isolated Python DownedBird() factory
# declaration contract. Stay off leftover Harbor #6/#8/#9.
LOCKED = {
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
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
# Isolated-test drafts stay off this lane. NightEyes() factory
# declaration is the in-flight sibling. ForMission (#272),
# SequencesDiffer (#271), BeatIndexForElapsed (#268), KindAt
# (#270), Beats[7] (#252), bKeepThermal (#250), beat-kind enum /
# beat defaults drafts, kit FName fields (#254), and on-main
# NightEyes() / DownedBird() sequence contents stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_for_mission_contract.py",
    "Scripts/tests/test_night_sortie_night_eyes_decl_contract.py",
    "Scripts/tests/test_night_sortie_sequences_differ_contract.py",
    "Scripts/tests/test_night_sortie_beat_index_contract.py",
    "Scripts/tests/test_night_sortie_kind_at_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_day_sortie_for_mission_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardNightSortieBeatKit& NightEyes();",
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);",
    "bool SequencesDiffer(",
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
    "ESkyguardNightSortieBeatKind KindAt(",
)
# In-flight sibling factory stays unlocked.
SIBLING_FACTORY_NOT_LOCKED = (
    "const FSkyguardNightSortieBeatKit& NightEyes();"
)
FOR_MISSION_NOT_LOCKED = (
    "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);"
)
SEQUENCES_DIFFER_NOT_LOCKED = "bool SequencesDiffer("
BEAT_INDEX_NOT_LOCKED = (
    "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);"
)
KIND_AT_NOT_LOCKED = "ESkyguardNightSortieBeatKind KindAt("
# On-main NightEyes() / DownedBird() sequence contents stay unlocked.
SEQUENCE_CONTENTS_NOT_LOCKED = (
    "NightEyesKit",
    "DownedBirdKit",
    "M04_NightBlackout",
    "M07_SearchIntercept",
    "BlackoutNight",
    "IslandMist",
    "Beats[0]",
    "Beats[1]",
    "Beats[2]",
    "Beats[3]",
    "Beats[4]",
    "Beats[5]",
    "Beats[6]",
    "MakeBeat",
)
# Which beats DownedBird returns stays unlocked.
KIT_RETURNS_NOT_LOCKED = (
    "return DownedBird",
    "return NightEyes",
    "NightEyesKit",
    "DownedBirdKit",
    "M04_NightBlackout",
    "M07_SearchIntercept",
    "RadarVanHunt",
    "RadarNetCollapse",
    "HoldTheWreck",
    "SearchIsland",
)
ELAPSED_TABLES_NOT_LOCKED = (
    "ElapsedSeconds",
    "BeatIndexForElapsed",
    "return 0",
    "return -1",
    "return INDEX_NONE",
)
# #252 Beats[7], #250 bKeepThermal, kind enum, beat defaults,
# #254 FName fields stay unlocked. Parse the namespace, not
# those types.
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
    "ApplyHydraForClusters",
)
# .cpp bodies / invented return values / sequence tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "NightEyesKit",
    "DownedBirdKit",
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


class NightSortieDownedBirdDeclContractTests(unittest.TestCase):
    def test_night_sortie_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, DOWNED_BIRD), body)
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

    def test_missing_downed_bird_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardNightSortieBeatKit& NightEyes();\n"
            "\tconst FSkyguardNightSortieBeatKit& ForMission(FName MissionId);\n"
            "\tbool SequencesDiffer(\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Left,\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Right);\n"
            "\tint32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);\n"
            "\tESkyguardNightSortieBeatKind KindAt(\n"
            "\t\tconst FSkyguardNightSortieBeatKit& Kit,\n"
            "\t\tint32 Index);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, DOWNED_BIRD)
        self.assertIn("DownedBird", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_origin_main_split_line_form_is_accepted(self) -> None:
        split = (
            "{\n"
            "\tconst FSkyguardNightSortieBeatKit&\n"
            "\tDownedBird();\n"
            "}\n"
        )
        self.assertTrue(has_declaration(split, DOWNED_BIRD), split)
        self.assertEqual(require_declaration(split, DOWNED_BIRD), DOWNED_BIRD)
        self.assertEqual(declaration_count(split, DOWNED_BIRD), 1)

    def test_downed_bird_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(body, DOWNED_BIRD), DOWNED_BIRD)
        self.assertTrue(has_declaration(body, DOWNED_BIRD), body)
        self.assertEqual(declaration_count(body, DOWNED_BIRD), 1)
        self.assertTrue(DOWNED_BIRD.endswith(";"), DOWNED_BIRD)
        self.assertNotIn("INDEX_NONE", DOWNED_BIRD)
        self.assertNotIn("return ", DOWNED_BIRD)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(DOWNED_BIRD.endswith(";"), DOWNED_BIRD)
        self.assertNotIn("return ", DOWNED_BIRD)
        self.assertNotIn("INDEX_NONE", DOWNED_BIRD)
        self.assertNotIn("NAME_None", DOWNED_BIRD)
        self.assertNotIn("{", DOWNED_BIRD)
        self.assertNotIn("}", DOWNED_BIRD)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DOWNED_BIRD)
            if token != "return ":
                self.assertNotIn(token, body)

    def test_contract_does_not_invent_which_beats_are_returned(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertEqual(require_declaration(locked_only, DOWNED_BIRD), DOWNED_BIRD)
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DOWNED_BIRD)
        self.assertNotIn("DownedBirdKit", DOWNED_BIRD)
        self.assertNotIn("NightEyes", DOWNED_BIRD)
        self.assertNotIn("M04", DOWNED_BIRD)
        self.assertNotIn("M07", DOWNED_BIRD)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, DOWNED_BIRD)

    def test_contract_does_not_relock_sibling_factory(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertEqual(require_declaration(locked_only, DOWNED_BIRD), DOWNED_BIRD)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, locked_only)
        self.assertNotIn(SIBLING_FACTORY_NOT_LOCKED, DOWNED_BIRD)
        self.assertNotIn("NightEyes()", locked_only)
        self.assertNotIn("NightEyes", DOWNED_BIRD)
        self.assertNotEqual(DOWNED_BIRD, "NightEyes()")

    def test_contract_does_not_relock_for_mission(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertNotIn(FOR_MISSION_NOT_LOCKED, locked_only)
        self.assertNotIn("ForMission", DOWNED_BIRD)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn(
            "const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);",
            (DOWNED_BIRD,),
        )

    def test_contract_does_not_relock_kit_sequence_contents(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(locked_only, DOWNED_BIRD), DOWNED_BIRD)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DOWNED_BIRD)
            self.assertNotIn(token, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, DOWNED_BIRD)
            self.assertNotIn(name, body)

    def test_contract_does_not_relock_sequences_differ(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertNotIn(SEQUENCES_DIFFER_NOT_LOCKED, locked_only)
        self.assertNotIn("SequencesDiffer", DOWNED_BIRD)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn(
            "bool SequencesDiffer(",
            (DOWNED_BIRD,),
        )

    def test_contract_does_not_relock_beat_index(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertNotIn(BEAT_INDEX_NOT_LOCKED, locked_only)
        self.assertNotIn("BeatIndexForElapsed", DOWNED_BIRD)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            (DOWNED_BIRD,),
        )

    def test_contract_does_not_relock_kind_at(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        self.assertNotIn(KIND_AT_NOT_LOCKED, locked_only)
        self.assertNotIn("KindAt", DOWNED_BIRD)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn("ESkyguardNightSortieBeatKind KindAt(", (DOWNED_BIRD,))

    def test_contract_does_not_relock_elapsed_tables(self) -> None:
        locked_only = f"{DOWNED_BIRD}\n"
        body = namespace_body(origin_main_header())
        for token in ELAPSED_TABLES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DOWNED_BIRD)
        self.assertNotIn("ElapsedSeconds", DOWNED_BIRD)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)

    def test_contract_does_not_relock_beats_enum_defaults_or_fields(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(BEATS_NOT_LOCKED, DOWNED_BIRD)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, DOWNED_BIRD)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, DOWNED_BIRD)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, DOWNED_BIRD)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, DOWNED_BIRD)
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
        self.assertEqual(require_declaration(body, DOWNED_BIRD), DOWNED_BIRD)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)
        self.assertNotIn("FName WeatherIdentity;", body)

    def test_contract_does_not_read_cpp_or_sequence_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DOWNED_BIRD)
        self.assertNotIn("SkyguardNightSortieBeatKit.cpp", body)
        self.assertNotIn("SkyguardNightSortieBeatKit::DownedBird", body)
        self.assertNotIn("NightEyesKit", body)
        self.assertNotIn("DownedBirdKit", body)
        self.assertNotIn("M04_NightBlackout", body)
        self.assertNotIn("M07_SearchIntercept", body)

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
        self.assertNotEqual(DOWNED_BIRD, "Rifle")
        self.assertNotEqual(DOWNED_BIRD, "Igla")
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
                f"night-sortie DownedBird contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, DOWNED_BIRD.lower())

    def test_contract_is_downed_bird_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(require_declaration(body, DOWNED_BIRD), DOWNED_BIRD)
        locked_only = f"{DOWNED_BIRD}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DOWNED_BIRD)
        for token in SEQUENCE_CONTENTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        for token in KIT_RETURNS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        self.assertNotIn("NightEyes", locked_only)
        self.assertNotIn("ForMission", locked_only)
        self.assertNotIn("SequencesDiffer", locked_only)
        self.assertNotIn("BeatIndexForElapsed", locked_only)
        self.assertNotIn("KindAt", locked_only)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, locked_only)
        self.assertNotIn(KEEP_THERMAL_NOT_LOCKED, body)
        for token in FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn(BEATS_NOT_LOCKED, body)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DOWNED_BIRD)
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
        self.assertNotEqual(DOWNED_BIRD, "Rifle")
        self.assertNotEqual(DOWNED_BIRD, "Igla")

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
