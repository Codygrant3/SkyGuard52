from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionDirectorCampaignHelpers.h"
NAMESPACE_NAME = "SkyguardMissionDirectorCampaignHelpers"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or leftover FillAndFinalize / FillAndFail Gunner paths.
LOAD_CAMPAIGN_PROGRESS = (
    "void LoadCampaignProgressAfterConfigure("
    "USkyguardCampaignSubsystem* Campaign, "
    "const FString& SlotName, "
    "int32 UserIndex);"
)
LOAD_CAMPAIGN_PROGRESS_NAME = "void LoadCampaignProgressAfterConfigure("
PARAMETER_LIST = (
    "USkyguardCampaignSubsystem* Campaign,",
    "const FString& SlotName,",
    "int32 UserIndex",
)
# Leftover #56–#64 plus MissionDirectorCampaignHelpers production
# sources/tests. This lane only adds an isolated Python
# LoadCampaignProgressAfterConfigure declaration contract. Stay off
# leftover Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover Gunner files, leftover campaign
# save empty-fail-closed drafts, and leftover FillAndFinalize /
# FillAndFail ASkyguardGunner* paths.
LOCKED = {
    "SkyguardMissionDirectorCampaignHelpers.h",
    "SkyguardMissionDirectorCampaignHelpers.cpp",
    "SkyguardMissionDirectorCampaignHelpersTests.cpp",
    "SkyguardCampaignSaveGameEmptyFailClosedTests.cpp",
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
# Isolated-test drafts stay off this lane. FillAndFinalize /
# FillAndFail leftover Gunner helpers, leftover campaign save
# empty-fail-closed, leftover theater-kit #59, leftover Harbor
# #6/#8/#9, and leftover flare/HUD #57/#61/#62 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# FillAndFinalize / FillAndFail take leftover ASkyguardGunner*.
UNLOCKED_NEIGHBORS = (
    "bool FillAndFinalize(",
    "bool FillAndFail(",
    "const ASkyguardGunner* Gunner,",
    "const UObject* WorldContextObject,",
    "USkyguardSortiePresentationComponent* SortiePresentation,",
)
FILL_AND_FINALIZE_NOT_LOCKED = (
    "bool FillAndFinalize(",
    "const ASkyguardGunner* Gunner,",
    "USkyguardSortiePresentationComponent* SortiePresentation,",
)
FILL_AND_FAIL_NOT_LOCKED = (
    "bool FillAndFail(",
    "const ASkyguardGunner* Gunner,",
    "const UObject* WorldContextObject,",
)
# .cpp bodies / invented return values stay unlocked. Do not
# invent INDEX_NONE or the cpp const int32 UserIndex form.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "return false",
    "const int32 UserIndex",
    "LoadCampaignFromSlot",
    "if (!Campaign)",
    "UE_LOG",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "USkyguardCampaignSaveGame",
    "ASkyguardIglaMissile",
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
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    return compact


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


class CampaignLoadProgressDeclContractTests(unittest.TestCase):
    def test_campaign_helpers_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, LOAD_CAMPAIGN_PROGRESS), body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedCampaignHelpers\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_type_alone_does_not_satisfy_namespace(self) -> None:
        type_only = (
            "class USkyguardCampaignSubsystem;\n"
            "class ASkyguardGunner;\n"
            "class USkyguardSortiePresentationComponent;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(type_only)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_load_progress_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tbool FillAndFinalize(\n"
            "\t\tUSkyguardCampaignSubsystem* Campaign,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject,\n"
            "\t\tUSkyguardSortiePresentationComponent* SortiePresentation,\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex);\n"
            "\tbool FillAndFail(\n"
            "\t\tUSkyguardCampaignSubsystem* Campaign,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject,\n"
            "\t\tUSkyguardSortiePresentationComponent* SortiePresentation,\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LOAD_CAMPAIGN_PROGRESS)
        self.assertIn("LoadCampaignProgressAfterConfigure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_missing_parameter_list_fails_closed(self) -> None:
        name_only = (
            "{\n"
            "\tvoid LoadCampaignProgressAfterConfigure();\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(name_only, LOAD_CAMPAIGN_PROGRESS)
        self.assertIn("LoadCampaignProgressAfterConfigure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_load_progress_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        self.assertTrue(has_declaration(body, LOAD_CAMPAIGN_PROGRESS))
        self.assertEqual(declaration_count(body, LOAD_CAMPAIGN_PROGRESS), 1)
        self.assertTrue(LOAD_CAMPAIGN_PROGRESS.endswith(";"), LOAD_CAMPAIGN_PROGRESS)
        self.assertIn(LOAD_CAMPAIGN_PROGRESS_NAME, LOAD_CAMPAIGN_PROGRESS)
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, LOAD_CAMPAIGN_PROGRESS)
            self.assertTrue(has_declaration(body, parameter), body)
        self.assertNotIn("INDEX_NONE", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("return ", LOAD_CAMPAIGN_PROGRESS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tvoid\n"
            "\tLoadCampaignProgressAfterConfigure(\n"
            "\t\tUSkyguardCampaignSubsystem* Campaign,\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex);\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tvoid LoadCampaignProgressAfterConfigure(\n"
            "\t\tUSkyguardCampaignSubsystem* Campaign,\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex);\n"
            "}\n"
        )
        self.assertTrue(has_declaration(wrap_type, LOAD_CAMPAIGN_PROGRESS), wrap_type)
        self.assertTrue(has_declaration(wrap_args, LOAD_CAMPAIGN_PROGRESS), wrap_args)
        self.assertEqual(
            require_declaration(wrap_type, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        self.assertEqual(
            require_declaration(wrap_args, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        self.assertEqual(declaration_count(wrap_type, LOAD_CAMPAIGN_PROGRESS), 1)
        self.assertEqual(declaration_count(wrap_args, LOAD_CAMPAIGN_PROGRESS), 1)
        one_line = f"{{\n\t{LOAD_CAMPAIGN_PROGRESS}\n}}\n"
        self.assertTrue(has_declaration(one_line, LOAD_CAMPAIGN_PROGRESS))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, LOAD_CAMPAIGN_PROGRESS), body)
        self.assertEqual(
            require_declaration(body, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        for parameter in PARAMETER_LIST:
            self.assertTrue(has_declaration(wrap_args, parameter), wrap_args)
            self.assertTrue(has_declaration(body, parameter), body)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(LOAD_CAMPAIGN_PROGRESS.endswith(";"), LOAD_CAMPAIGN_PROGRESS)
        self.assertTrue(LOAD_CAMPAIGN_PROGRESS.startswith("void "), LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("return ", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("INDEX_NONE", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("NAME_None", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("{", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("}", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("const int32 UserIndex", LOAD_CAMPAIGN_PROGRESS)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)

    def test_contract_does_not_relock_fill_and_finalize(self) -> None:
        locked_only = f"{LOAD_CAMPAIGN_PROGRESS}\n"
        for neighbor in FILL_AND_FINALIZE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFinalize", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("ASkyguardGunner", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("SortiePresentation", LOAD_CAMPAIGN_PROGRESS)

    def test_contract_does_not_relock_fill_and_fail(self) -> None:
        locked_only = f"{LOAD_CAMPAIGN_PROGRESS}\n"
        for neighbor in FILL_AND_FAIL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFail", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("WorldContextObject", LOAD_CAMPAIGN_PROGRESS)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{LOAD_CAMPAIGN_PROGRESS}\n"
        self.assertEqual(
            require_declaration(locked_only, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("WorldContextObject", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)

    def test_contract_parses_namespace_not_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        self.assertNotIn("SkyguardMissionDirectorCampaignHelpers.cpp", body)
        self.assertNotIn("LoadCampaignFromSlot", body)
        self.assertNotIn("UE_LOG", body)
        self.assertNotIn("if (!Campaign)", body)

    def test_contract_does_not_read_cpp_or_return_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("SkyguardMissionDirectorCampaignHelpers.cpp", body)
        self.assertNotIn(
            "SkyguardMissionDirectorCampaignHelpers::LoadCampaignProgressAfterConfigure",
            body,
        )
        self.assertNotIn("LoadCampaignFromSlot", body)
        self.assertNotIn("return false", LOAD_CAMPAIGN_PROGRESS)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(LOAD_CAMPAIGN_PROGRESS, "Rifle")
        self.assertNotEqual(LOAD_CAMPAIGN_PROGRESS, "Igla")
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
                f"campaign LoadCampaignProgressAfterConfigure contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, LOAD_CAMPAIGN_PROGRESS.lower())

    def test_contract_is_load_campaign_progress_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, LOAD_CAMPAIGN_PROGRESS),
            LOAD_CAMPAIGN_PROGRESS,
        )
        locked_only = f"{LOAD_CAMPAIGN_PROGRESS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("WorldContextObject", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOAD_CAMPAIGN_PROGRESS)
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
        self.assertNotIn("return ", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotIn("const int32 UserIndex", LOAD_CAMPAIGN_PROGRESS)
        self.assertNotEqual(LOAD_CAMPAIGN_PROGRESS, "Rifle")
        self.assertNotEqual(LOAD_CAMPAIGN_PROGRESS, "Igla")
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, LOAD_CAMPAIGN_PROGRESS)

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
