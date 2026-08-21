from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCpgDebrief.h"
HEADER_NAME = "SkyguardCpgDebrief.h"
STRUCT_NAME = "FSkyguardCpgDebriefSnapshot"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or debrief copy strings.
BUILD_COPY = (
    "FString SkyguardBuildCpgDebriefCopy("
    "const FSkyguardCpgDebriefSnapshot& Snap);"
)
# Leftover #56–#64 plus CpgDebrief production sources.
# This lane only adds an isolated Python SkyguardBuildCpgDebriefCopy
# declaration contract. Stay off leftover Harbor #6/#8/#9.
LOCKED = {
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
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
# Isolated-test drafts stay off this lane. Snapshot defaults (#195)
# and leftover empty-capture fail-closed (#130) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
)
# Leftover Gunner / SortieDirector / PatrolShip capture stays unlocked.
CAPTURE_NOT_LOCKED = (
    "SkyguardCaptureCpgDebrief",
    "ASkyguardGunner*",
    "ASkyguardGunshipSortieDirector*",
    "ASkyguardPatrolShipBoss*",
)
CAPTURE_DECLARATION = (
    "FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief("
    "const ASkyguardGunshipSortieDirector* Director, "
    "const ASkyguardGunner* Gunner, "
    "const ASkyguardPatrolShipBoss* Ship);"
)
# #195 snapshot field defaults stay in the struct body.
SNAPSHOT_DEFAULTS_NOT_LOCKED = (
    "bool bValid = false;",
    "bool bWon = false;",
    "FString MissionTitle;",
    "FString OutcomeNarrative;",
    "int32 Score = 0;",
    "int32 Medal = 0;",
    "int32 ShotsFired = 0;",
    "int32 Hits = 0;",
    "int32 CargoPercent = 100;",
    "bool bRadarDead = false;",
    "TArray<ESkyguardPatrolShipSystem> DestroyedSystems;",
    "ESkyguardLoadout SelectedLoadout = ESkyguardLoadout::Balanced;",
    "int32 CannonReady = 0;",
    "int32 RocketReady = 0;",
    "int32 GuidedReady = 0;",
)
# SkyguardCpgCopyHasBannedTerm is a sibling inline helper.
BANNED_TERM_HELPER = "SkyguardCpgCopyHasBannedTerm"
# Leftover #8 CPG sortie debrief / playstyle loadouts stay unlocked.
LOADOUTS_NOT_LOCKED = (
    "AntiArmor",
    "RocketHeavy",
    "Intercept",
    "Anti-Armor",
    "Rocket Heavy",
)
# .cpp copy bodies / invented return values stay unlocked.
COPY_STRINGS_NOT_LOCKED = (
    "WIN",
    "FAIL",
    "Gold",
    "Silver",
    "Bronze",
    "30 mm",
    "Hydra",
    "Hellfire",
    "N / Enter continues",
    "Search Radar",
    "Drone Deck",
    "MedalName",
    "SystemLongName",
    "CollectDestroyedSystems",
    'TEXT("%s',
    "Patrol ship systems stripped",
)
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "struct FSkyguardCpgDebriefSnapshot",
    "inline bool SkyguardCpgCopyHasBannedTerm",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NEXT_SURFACE_RE = re.compile(
    r"\n(?:UENUM|USTRUCT|UCLASS|enum class|struct |class |"
    r"namespace |inline )"
)


def collapsed(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("( ", "(").replace(" )", ")")


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{HEADER_NAME} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def after_snapshot_region(header: str) -> str:
    """Free-function declarations after FSkyguardCpgDebriefSnapshot.

    Do not parse leftover Gunner capture as the lock, and do not
    treat the snapshot struct body as this lane.
    """
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
                after = header[finish:]
                clip = NEXT_SURFACE_RE.search(after)
                if clip is not None:
                    after = after[: clip.start()]
                return after
    raise AssertionError(
        f"{STRUCT_NAME} body is unclosed in origin/main:{HEADER_PATH}"
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
            f"after {STRUCT_NAME}"
        )
    return declaration


def standalone_harbor_clocks(region: str) -> list[str]:
    found: list[str] = []
    if re.search(r"(?<![\d.])40\.f", region):
        found.append("40.f")
    if re.search(r"(?<![\d.])80\.f", region):
        found.append("80.f")
    return found


class CpgDebriefCopyDeclContractTests(unittest.TestCase):
    def test_snapshot_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        region = after_snapshot_region(header)
        self.assertTrue(has_declaration(region, BUILD_COPY), region)
        self.assertNotIn(f"struct {STRUCT_NAME}", region)

    def test_missing_snapshot_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            after_snapshot_region(
                "struct FSkyguardUnrelated\n{\n};\n"
                f"{BUILD_COPY}\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_inside_struct_body_fails_closed(self) -> None:
        header = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{BUILD_COPY}\n"
            "};\n"
            "inline bool SkyguardCpgCopyHasBannedTerm(const FString& Text)\n"
            "{\n"
            "\treturn false;\n"
            "}\n"
        )
        region = after_snapshot_region(header)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, BUILD_COPY)
        self.assertIn("SkyguardBuildCpgDebriefCopy", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(BUILD_COPY, region)

    def test_missing_build_copy_declaration_fails_closed(self) -> None:
        capture_only = (
            "\n"
            "FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief(\n"
            "\tconst ASkyguardGunshipSortieDirector* Director,\n"
            "\tconst ASkyguardGunner* Gunner,\n"
            "\tconst ASkyguardPatrolShipBoss* Ship);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(capture_only, BUILD_COPY)
        self.assertIn("SkyguardBuildCpgDebriefCopy", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_leftover_gunner_capture_does_not_satisfy_lock(self) -> None:
        locked_only = f"{BUILD_COPY}\n"
        self.assertEqual(
            require_declaration(locked_only, BUILD_COPY),
            BUILD_COPY,
        )
        self.assertFalse(has_declaration(locked_only, CAPTURE_DECLARATION))
        for token in CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotEqual(BUILD_COPY, CAPTURE_DECLARATION)
        self.assertNotIn("ASkyguardGunner*", BUILD_COPY)

    def test_origin_main_split_line_form_is_accepted(self) -> None:
        split = (
            "\n"
            "FString SkyguardBuildCpgDebriefCopy(\n"
            "\tconst FSkyguardCpgDebriefSnapshot& Snap);\n"
        )
        self.assertTrue(has_declaration(split, BUILD_COPY), split)
        self.assertEqual(require_declaration(split, BUILD_COPY), BUILD_COPY)
        self.assertEqual(declaration_count(split, BUILD_COPY), 1)

    def test_build_copy_declaration_matches_origin_main(self) -> None:
        region = after_snapshot_region(origin_main_header())
        self.assertEqual(require_declaration(region, BUILD_COPY), BUILD_COPY)
        self.assertTrue(has_declaration(region, BUILD_COPY), region)
        self.assertEqual(declaration_count(region, BUILD_COPY), 1)
        self.assertTrue(BUILD_COPY.endswith(";"), BUILD_COPY)
        self.assertNotIn("INDEX_NONE", BUILD_COPY)
        self.assertNotIn("return ", BUILD_COPY)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        region = after_snapshot_region(origin_main_header())
        self.assertTrue(BUILD_COPY.endswith(";"), BUILD_COPY)
        self.assertNotIn("return ", BUILD_COPY)
        self.assertNotIn("INDEX_NONE", BUILD_COPY)
        self.assertNotIn("NAME_None", BUILD_COPY)
        self.assertNotIn("{", BUILD_COPY)
        self.assertNotIn("}", BUILD_COPY)
        self.assertNotIn("return ", region)
        self.assertNotIn("INDEX_NONE", region)
        self.assertNotIn("NAME_None", region)
        self.assertNotIn("return INDEX_NONE", region)
        self.assertNotIn("return 0", region)
        self.assertNotIn("return -1", region)
        self.assertNotIn("= INDEX_NONE", region)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BUILD_COPY)
            if token != "return ":
                self.assertNotIn(token, region)

    def test_declaration_does_not_invent_debrief_copy_strings(self) -> None:
        locked_only = f"{BUILD_COPY}\n"
        region = after_snapshot_region(origin_main_header())
        self.assertEqual(
            require_declaration(locked_only, BUILD_COPY),
            BUILD_COPY,
        )
        for token in COPY_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
            self.assertNotIn(token, region)
        self.assertNotIn("MedalName", BUILD_COPY)
        self.assertNotIn("SystemLongName", BUILD_COPY)

    def test_contract_does_not_relock_snapshot_defaults(self) -> None:
        region = after_snapshot_region(origin_main_header())
        locked_only = f"{BUILD_COPY}\n"
        for token in SNAPSHOT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, region)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotIn("struct FSkyguardCpgDebriefSnapshot", region)
        self.assertNotIn("bValid = false", region)
        self.assertNotIn("CargoPercent = 100", region)
        self.assertNotIn("{", region)

    def test_contract_does_not_relock_banned_term_helper(self) -> None:
        region = after_snapshot_region(origin_main_header())
        locked_only = f"{BUILD_COPY}\n"
        self.assertNotIn(BANNED_TERM_HELPER, region)
        self.assertNotIn(BANNED_TERM_HELPER, locked_only)
        self.assertNotIn(BANNED_TERM_HELPER, BUILD_COPY)
        self.assertNotIn("inline bool SkyguardCpgCopyHasBannedTerm", region)
        self.assertNotEqual(BUILD_COPY, "SkyguardCpgCopyHasBannedTerm")

    def test_contract_does_not_relock_leftover_capture(self) -> None:
        locked_only = f"{BUILD_COPY}\n"
        self.assertEqual(
            require_declaration(locked_only, BUILD_COPY),
            BUILD_COPY,
        )
        for token in CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotIn("SkyguardCaptureCpgDebrief", BUILD_COPY)
        self.assertNotIn("ASkyguardGunner*", locked_only)

    def test_contract_does_not_relock_playstyle_loadouts(self) -> None:
        region = after_snapshot_region(origin_main_header())
        locked_only = f"{BUILD_COPY}\n"
        for token in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(token, region)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotIn("ESkyguardLoadout::Balanced", region)
        self.assertNotIn("PlaystyleLine", region)

    def test_contract_does_not_read_cpp_or_copy_tables(self) -> None:
        region = after_snapshot_region(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotIn("SkyguardCpgDebrief.cpp", region)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy(", region.split("FString")[0])
        self.assertNotIn("MedalName", region)
        self.assertNotIn("FString::Printf", region)

    def test_contract_does_not_retune_harbor(self) -> None:
        region = after_snapshot_region(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertEqual(standalone_harbor_clocks(region), [])
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", region)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", region)
        self.assertNotIn("40", BUILD_COPY)
        self.assertNotIn("80", BUILD_COPY)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        region = after_snapshot_region(origin_main_header())
        self.assertNotIn("Rifle", region)
        self.assertNotIn("Igla", region)
        self.assertNotIn("Yak", region)
        self.assertNotEqual(BUILD_COPY, "Rifle")
        self.assertNotEqual(BUILD_COPY, "Igla")
        self.assertNotIn("FireIgla", region)
        self.assertNotIn("FireRifle", region)
        self.assertNotIn("YakSpawnLocation", region)
        self.assertNotIn("bYakRuntimeReady", region)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", region)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        region = after_snapshot_region(origin_main_header())
        lowered = region.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"CPG debrief copy declaration contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, BUILD_COPY.lower())

    def test_contract_is_build_copy_declaration_only(self) -> None:
        header = origin_main_header()
        region = after_snapshot_region(header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(require_declaration(region, BUILD_COPY), BUILD_COPY)
        locked_only = f"{BUILD_COPY}\n"
        for token in CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        self.assertNotIn(BANNED_TERM_HELPER, locked_only)
        self.assertNotIn(BANNED_TERM_HELPER, region)
        for token in SNAPSHOT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, region)
        for token in COPY_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BUILD_COPY)
        for token in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, region)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BUILD_COPY)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertEqual(standalone_harbor_clocks(region), [])
        self.assertNotIn("Rifle", region)
        self.assertNotIn("Igla", region)
        self.assertNotIn("Yak", region)
        self.assertNotIn("INDEX_NONE", region)
        self.assertNotIn("return ", region)
        self.assertNotIn("enum class", region)
        self.assertNotEqual(BUILD_COPY, "Rifle")
        self.assertNotEqual(BUILD_COPY, "Igla")
        self.assertEqual(
            require_declaration(locked_only, BUILD_COPY),
            BUILD_COPY,
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
