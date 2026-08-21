from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCpgDebrief.h"
HEADER_NAME = "SkyguardCpgDebrief.h"
FUNCTION_NAME = "SkyguardCpgCopyHasBannedTerm"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or lock the inline Contains body. origin/main may use
# `inline bool` and may split the signature across lines.
LOCKED_DECL = "bool SkyguardCpgCopyHasBannedTerm(const FString& Text);"
# Leftover #56–#64 plus CpgDebrief production sources/tests.
# This lane only adds an isolated Python HasBannedTerm
# declaration contract. Stay off leftover Harbor #6/#8/#9,
# leftover #8 CPG sortie debrief / playstyle loadouts,
# leftover theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover drafts #56–#64, and leftover Harbor 40/80.
LOCKED = {
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgDebriefFailClosedTests.cpp",
    "SkyguardCpgDebriefLoadoutTests.cpp",
    "SkyguardCpgDebriefCargoCaptureTests.cpp",
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
# Isolated-test drafts stay off this lane. BuildCpgDebriefCopy
# (in-flight copy decl), CaptureCpgDebrief leftover Gunner*
# (#130), and snapshot default fields (#195) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors on the same header. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "FString SkyguardBuildCpgDebriefCopy(const FSkyguardCpgDebriefSnapshot& Snap);",
    "FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief(",
    "struct FSkyguardCpgDebriefSnapshot",
    "const ASkyguardGunner* Gunner",
)
BUILD_COPY_NOT_LOCKED = (
    "FString SkyguardBuildCpgDebriefCopy(const FSkyguardCpgDebriefSnapshot& Snap);"
)
CAPTURE_NOT_LOCKED = (
    "SkyguardCaptureCpgDebrief",
    "const ASkyguardGunner* Gunner",
    "ASkyguardGunner*",
    "const ASkyguardGunshipSortieDirector* Director",
    "const ASkyguardPatrolShipBoss* Ship",
)
# #195 snapshot in-class defaults stay unlocked.
SNAPSHOT_DEFAULTS_NOT_LOCKED = (
    "bool bValid = false;",
    "bool bWon = false;",
    "int32 Score = 0;",
    "int32 Medal = 0;",
    "int32 ShotsFired = 0;",
    "int32 Hits = 0;",
    "int32 CargoPercent = 100;",
    "bool bRadarDead = false;",
    "ESkyguardLoadout SelectedLoadout = ESkyguardLoadout::Balanced;",
    "int32 CannonReady = 0;",
    "int32 RocketReady = 0;",
    "int32 GuidedReady = 0;",
)
# Inline Contains body is not a production-edit lane.
BODY_NOT_LOCKED = (
    "Contains(",
    ".Contains",
    "ToLower",
    "ToLower()",
    "const FString Lower",
    "TEXT(",
    "return ",
)
SIBLING_TYPES = (
    "struct FSkyguardCpgDebriefSnapshot",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
# .cpp bodies / invented return values stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return true",
    "return false",
    "return 0",
    "return -1",
    "return INDEX_NONE",
)
INVENTED = (
    "INDEX_NONE",
    "NAME_None",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
DECL_HEAD_RE = re.compile(
    rf"(?:inline\s+)?bool\s+{re.escape(FUNCTION_NAME)}\s*\(",
)


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    return compact


def strip_inline_kw(text: str) -> str:
    return re.sub(r"\binline\b\s*", "", text)


def normalize_decl(text: str) -> str:
    return collapsed(strip_inline_kw(text)).rstrip(";").strip()


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


def extract_declaration(header: str) -> str:
    """Declaration only. Drop inline and the function body."""
    match = DECL_HEAD_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{LOCKED_DECL} is missing from origin/main:{HEADER_PATH}"
        )
    paren = header.index("(", match.start())
    depth = 0
    end = None
    for index, char in enumerate(header[paren:], start=paren):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise AssertionError(
            f"{LOCKED_DECL} is missing from origin/main:{HEADER_PATH}"
        )
    raw = header[match.start() : end]
    return f"{normalize_decl(raw)};"


def has_declaration(region: str, declaration: str) -> bool:
    try:
        found = extract_declaration(region)
    except AssertionError:
        return False
    return normalize_decl(found) == normalize_decl(declaration)


def declaration_count(region: str, declaration: str) -> int:
    matches = DECL_HEAD_RE.findall(region)
    if not matches:
        return 0
    if has_declaration(region, declaration):
        return len(matches)
    return 0


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH}"
        )
    return declaration


def standalone_harbor_clocks(region: str) -> list[str]:
    found: list[str] = []
    if re.search(r"(?<![\d.])40\.f", region):
        found.append("40.f")
    if re.search(r"(?<![\d.])80\.f", region):
        found.append("80.f")
    return found


class CpgCopyHasBannedTermDeclContractTests(unittest.TestCase):
    def test_declaration_exists(self) -> None:
        header = origin_main_header()
        decl = extract_declaration(header)
        self.assertEqual(decl, LOCKED_DECL)
        self.assertTrue(has_declaration(header, LOCKED_DECL), header)
        self.assertEqual(require_declaration(header, LOCKED_DECL), LOCKED_DECL)

    def test_missing_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "struct FSkyguardCpgDebriefSnapshot\n"
            "{\n"
            "\tbool bValid = false;\n"
            "};\n"
            "FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief(\n"
            "\tconst ASkyguardGunshipSortieDirector* Director,\n"
            "\tconst ASkyguardGunner* Gunner,\n"
            "\tconst ASkyguardPatrolShipBoss* Ship);\n"
            "FString SkyguardBuildCpgDebriefCopy("
            "const FSkyguardCpgDebriefSnapshot& Snap);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LOCKED_DECL)
        self.assertIn(FUNCTION_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_header_fails_closed(self) -> None:
        result = subprocess.run(
            ["git", "show", "origin/main:Source/Skyguard52/SkyguardMissingCpgDebrief.h"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        with self.assertRaises(AssertionError) as raised:
            extract_declaration(
                "FString SkyguardBuildCpgDebriefCopy("
                "const FSkyguardCpgDebriefSnapshot& Snap);\n"
            )
        self.assertIn(FUNCTION_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_snapshot_or_siblings_alone_do_not_satisfy_declaration(self) -> None:
        snapshot_only = (
            "struct FSkyguardCpgDebriefSnapshot\n"
            "{\n"
            "\tbool bValid = false;\n"
            "\tbool bWon = false;\n"
            "\tint32 Score = 0;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            extract_declaration(snapshot_only)
        self.assertIn(FUNCTION_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(snapshot_only, LOCKED_DECL))

    def test_wrong_signature_fails_closed(self) -> None:
        wrong_type = (
            "void SkyguardCpgCopyHasBannedTerm(const FString& Text);\n"
        )
        wrong_args = (
            "bool SkyguardCpgCopyHasBannedTerm(const FText& Text);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong_type, LOCKED_DECL)
        self.assertIn(FUNCTION_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong_args, LOCKED_DECL)
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong_type, LOCKED_DECL))
        self.assertFalse(has_declaration(wrong_args, LOCKED_DECL))

    def test_declaration_matches_origin_main(self) -> None:
        header = origin_main_header()
        decl = extract_declaration(header)
        self.assertEqual(require_declaration(header, LOCKED_DECL), LOCKED_DECL)
        self.assertEqual(decl, LOCKED_DECL)
        self.assertTrue(has_declaration(header, LOCKED_DECL))
        self.assertEqual(declaration_count(header, LOCKED_DECL), 1)
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("INDEX_NONE", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("}", LOCKED_DECL)

    def test_declaration_accepts_inline_and_split_line_forms(self) -> None:
        wrap_type = (
            "bool\n"
            "SkyguardCpgCopyHasBannedTerm(const FString& Text);\n"
        )
        wrap_args = (
            "bool SkyguardCpgCopyHasBannedTerm(\n"
            "\tconst FString& Text);\n"
        )
        inline_one = (
            "inline bool SkyguardCpgCopyHasBannedTerm(const FString& Text);\n"
        )
        inline_def = (
            "inline bool SkyguardCpgCopyHasBannedTerm(const FString& Text)\n"
            "{\n"
            "}\n"
        )
        inline_wrap = (
            "inline bool\n"
            "SkyguardCpgCopyHasBannedTerm(\n"
            "\tconst FString& Text)\n"
            "{\n"
            "}\n"
        )
        for region in (
            wrap_type,
            wrap_args,
            inline_one,
            inline_def,
            inline_wrap,
        ):
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
            self.assertEqual(
                require_declaration(region, LOCKED_DECL),
                LOCKED_DECL,
            )
            self.assertEqual(extract_declaration(region), LOCKED_DECL)
            self.assertEqual(declaration_count(region, LOCKED_DECL), 1)
        one_line = f"{LOCKED_DECL}\n"
        self.assertTrue(has_declaration(one_line, LOCKED_DECL))
        header = origin_main_header()
        self.assertTrue(has_declaration(header, LOCKED_DECL), header)
        self.assertEqual(extract_declaration(header), LOCKED_DECL)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        decl = extract_declaration(origin_main_header())
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("INDEX_NONE", LOCKED_DECL)
        self.assertNotIn("NAME_None", LOCKED_DECL)
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("}", LOCKED_DECL)
        self.assertNotIn("return ", decl)
        self.assertNotIn("INDEX_NONE", decl)
        self.assertNotIn("NAME_None", decl)
        self.assertNotIn("return INDEX_NONE", decl)
        self.assertNotIn("return true", decl)
        self.assertNotIn("return false", decl)
        self.assertNotIn("= INDEX_NONE", decl)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
        for token in INVENTED:
            self.assertNotIn(token, decl)
        self.assertNotEqual(
            LOCKED_DECL,
            "bool SkyguardCpgCopyHasBannedTerm(INDEX_NONE);",
        )

    def test_contract_does_not_lock_contains_body(self) -> None:
        decl = extract_declaration(origin_main_header())
        locked_only = f"{LOCKED_DECL}\n"
        for token in BODY_NOT_LOCKED:
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
            self.assertNotIn(token, locked_only)
        self.assertTrue(has_declaration(locked_only, LOCKED_DECL))
        empty_body = (
            "inline bool SkyguardCpgCopyHasBannedTerm(const FString& Text)\n"
            "{\n"
            "}\n"
        )
        other_body = (
            "bool SkyguardCpgCopyHasBannedTerm(const FString& Text)\n"
            "{\n"
            "\treturn false;\n"
            "}\n"
        )
        self.assertTrue(has_declaration(empty_body, LOCKED_DECL), empty_body)
        self.assertTrue(has_declaration(other_body, LOCKED_DECL), other_body)
        self.assertEqual(extract_declaration(empty_body), LOCKED_DECL)
        self.assertEqual(extract_declaration(other_body), LOCKED_DECL)
        self.assertNotIn("Contains(", decl)
        self.assertNotIn("TEXT(", decl)

    def test_contract_does_not_relock_build_copy(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertNotIn(BUILD_COPY_NOT_LOCKED, locked_only)
        self.assertNotIn(BUILD_COPY_NOT_LOCKED, LOCKED_DECL)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", LOCKED_DECL)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)

    def test_contract_does_not_relock_capture(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        decl = extract_declaration(origin_main_header())
        for token in CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
        self.assertNotIn("SkyguardCaptureCpgDebrief", LOCKED_DECL)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_snapshot_defaults(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        decl = extract_declaration(origin_main_header())
        for token in SNAPSHOT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
        self.assertNotIn("struct FSkyguardCpgDebriefSnapshot", LOCKED_DECL)
        self.assertNotIn("struct FSkyguardCpgDebriefSnapshot", decl)
        self.assertNotIn("bValid", decl)
        self.assertNotIn("CargoPercent", decl)

    def test_contract_does_not_retune_harbor(self) -> None:
        header = origin_main_header()
        decl = extract_declaration(header)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, header)
            self.assertNotIn(token, decl)
            self.assertNotIn(token, LOCKED_DECL)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, header)
            self.assertNotIn(token, decl)
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn("40.f, 80.f", header)
        self.assertNotIn(HARBOR_INCOMING, header)
        self.assertNotIn(HARBOR_INCOMING, decl)
        self.assertEqual(standalone_harbor_clocks(header), [])
        self.assertEqual(standalone_harbor_clocks(decl), [])
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", header)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", header)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        decl = extract_declaration(origin_main_header())
        self.assertNotIn("Rifle", decl)
        self.assertNotIn("Igla", decl)
        self.assertNotIn("Yak", decl)
        self.assertNotEqual(LOCKED_DECL, "Rifle")
        self.assertNotEqual(LOCKED_DECL, "Igla")
        self.assertNotIn("FireIgla", decl)
        self.assertNotIn("FireRifle", decl)
        self.assertNotIn("YakSpawnLocation", decl)
        self.assertNotIn("bYakRuntimeReady", decl)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", decl)
        self.assertNotIn("TEXT(", decl)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        decl = extract_declaration(origin_main_header())
        lowered = decl.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{FUNCTION_NAME} declaration contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover copy",
            )
            self.assertNotIn(banned, LOCKED_DECL.lower())
        self.assertNotIn("FireIgla", decl)
        self.assertNotIn("FireRifle", decl)
        self.assertNotIn("YakSpawnLocation", decl)

    def test_contract_is_banned_term_declaration_only(self) -> None:
        header = origin_main_header()
        decl = extract_declaration(header)
        self.assertEqual(require_declaration(header, LOCKED_DECL), LOCKED_DECL)
        self.assertEqual(decl, LOCKED_DECL)
        locked_only = f"{LOCKED_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOCKED_DECL)
            self.assertNotIn(neighbor, decl)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("struct FSkyguardCpgDebriefSnapshot", locked_only)
        for token in SNAPSHOT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, decl)
        for token in BODY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, decl)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, decl)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, header)
            self.assertNotIn(token, decl)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, header)
            self.assertNotIn(token, decl)
        self.assertNotIn("40.f, 80.f", header)
        self.assertNotIn(HARBOR_INCOMING, header)
        self.assertEqual(standalone_harbor_clocks(header), [])
        self.assertNotIn("Rifle", decl)
        self.assertNotIn("Igla", decl)
        self.assertNotIn("Yak", decl)
        self.assertNotIn("INDEX_NONE", decl)
        self.assertNotIn("return ", decl)
        self.assertNotIn("TEXT(", decl)
        self.assertNotIn("Contains(", decl)
        self.assertNotEqual(LOCKED_DECL, "Rifle")
        self.assertNotEqual(LOCKED_DECL, "Igla")
        self.assertTrue(has_declaration(locked_only, LOCKED_DECL))

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
