from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardGameUserSettings.h"
CLASS_NAME = "USkyguardGameUserSettings"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or the GameUserSettings getter body.
GETTER_DECL = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();"
)
# Leftover #56–#64 plus GameUserSettings production files.
# This lane only adds an isolated Python GetSkyguardGameUserSettings
# declaration contract. Stay off invert-look / ApplySettings
# broadcast (#134), leftover Apache CPG feel constants (#118),
# leftover Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover drafts #56–#64, CPG mesh/art,
# Yak/Igla/rifle live copy, and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardGameUserSettings.h",
    "SkyguardGameUserSettings.cpp",
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
# Isolated-test drafts stay off this lane. Invert-look /
# ApplySettings broadcast (#134) is a C++ sibling, leftover
# Apache CPG feel constants (#118) and leftover theater-kit
# #59 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);",
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const { return MasterVolume; }",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
)
APPLY_AND_VOLUME_NOT_LOCKED = (
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);",
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const { return MasterVolume; }",
)
MOUSE_NOT_LOCKED = (
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
)
VALIDATE_DEFAULTS_NOT_LOCKED = (
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
)
INVERT_LOOK_NOT_LOCKED = (
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
)
APPLY_BROADCAST_NOT_LOCKED = (
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
)
# Leftover #118 Apache CPG feel constants stay unlocked.
FEEL_NOT_LOCKED = (
    "CannonFireRate",
    "CannonDamage",
    "CannonMagazineSize",
    "RocketSalvoSeconds",
    "GuidedLockSeconds",
    "SkyguardApacheCpgFeel",
)
# .cpp getter body / invented return values stay unlocked.
CPP_AND_INVENTED = (
    "return GEngine",
    "INDEX_NONE",
    "NAME_None",
    "return nullptr",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "Cast<USkyguardGameUserSettings>",
    "GEngine->GetGameUserSettings()",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "FSkyguardSearchlightTrackRuntime",
    "namespace SkyguardApacheCpgFeel",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
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


def class_body(header: str) -> str:
    match = CLASS_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{CLASS_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index("{", match.start())
    depth = 0
    for index, char in enumerate(header[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[start : index + 1]
    raise AssertionError(
        f"{CLASS_NAME} class body is missing from origin/main:{HEADER_PATH}"
    )


def public_section(header: str) -> str:
    body = class_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        return rest[: next_access.start()]
    close = rest.rfind("}")
    if close == -1:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    return rest[:close]


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
            f"class {CLASS_NAME} public section"
        )
    return declaration


class GameUserSettingsGetterDeclContractTests(unittest.TestCase):
    def test_game_user_settings_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, GETTER_DECL), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSettings "
                ": public UGameUserSettings\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            f"\t{GETTER_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameUserSettings\n"
            "{\n"
            "private:\n"
            f"\t{GETTER_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_private_declaration_does_not_satisfy_public_lock(self) -> None:
        mixed = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid SetMasterVolume(float Value);\n"
            "private:\n"
            f"\t{GETTER_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GETTER_DECL)
        self.assertIn("GetSkyguardGameUserSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(GETTER_DECL, section)

    def test_missing_getter_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "\tvirtual void ValidateSettings() override;\n"
            "\tvirtual void SetToDefaults() override;\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides = true);\n"
            "\tvoid SetMasterVolume(float Value);\n"
            "\tfloat GetMasterVolume() const { return MasterVolume; }\n"
            "\tvoid SetMouseSensitivity(float Value);\n"
            "\tfloat GetMouseSensitivity() const "
            "{ return MouseSensitivity; }\n"
            "\tvoid SetInvertVerticalLook(bool bValue) "
            "{ bInvertVerticalLook = bValue; }\n"
            "\tbool GetInvertVerticalLook() const "
            "{ return bInvertVerticalLook; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GETTER_DECL)
        self.assertIn("GetSkyguardGameUserSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintPure, Category = "Settings")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GETTER_DECL)
        self.assertIn("GetSkyguardGameUserSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_getter_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GETTER_DECL),
            GETTER_DECL,
        )
        self.assertTrue(has_declaration(section, GETTER_DECL))
        self.assertEqual(declaration_count(section, GETTER_DECL), 1)
        self.assertTrue(GETTER_DECL.endswith(";"), GETTER_DECL)
        self.assertNotIn("INDEX_NONE", GETTER_DECL)
        self.assertNotIn("return ", GETTER_DECL)
        self.assertIn("static ", GETTER_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tstatic USkyguardGameUserSettings*\n"
            "\tGetSkyguardGameUserSettings();\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings(\n"
            "\t);\n"
            "private:\n"
            "};\n"
        )
        wrap_static = (
            "public:\n"
            "\tstatic\n"
            "\tUSkyguardGameUserSettings*\n"
            "\tGetSkyguardGameUserSettings();\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_type}"
        )
        header_wrap_args = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_args}"
        )
        header_wrap_static = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_static}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_static,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, GETTER_DECL), section)
            self.assertEqual(
                require_declaration(section, GETTER_DECL),
                GETTER_DECL,
            )
            self.assertEqual(declaration_count(section, GETTER_DECL), 1)
        one_line = f"{{\npublic:\n\t{GETTER_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, GETTER_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GETTER_DECL), section)
        self.assertEqual(
            require_declaration(section, GETTER_DECL),
            GETTER_DECL,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(GETTER_DECL.endswith(";"), GETTER_DECL)
        self.assertNotIn("return ", GETTER_DECL)
        self.assertNotIn("INDEX_NONE", GETTER_DECL)
        self.assertNotIn("NAME_None", GETTER_DECL)
        self.assertNotIn("{", GETTER_DECL)
        self.assertNotIn("}", GETTER_DECL)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("return GEngine", section)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GETTER_DECL)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_apply_and_volume(self) -> None:
        locked_only = f"{GETTER_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, GETTER_DECL),
            GETTER_DECL,
        )
        for neighbor in APPLY_AND_VOLUME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("ApplyAndSaveSettings", GETTER_DECL)
        self.assertNotIn("SetMasterVolume", GETTER_DECL)
        self.assertNotIn("GetMasterVolume", GETTER_DECL)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)

    def test_contract_does_not_relock_mouse_sensitivity(self) -> None:
        locked_only = f"{GETTER_DECL}\n"
        for neighbor in MOUSE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("SetMouseSensitivity", GETTER_DECL)
        self.assertNotIn("GetMouseSensitivity", GETTER_DECL)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)

    def test_contract_does_not_relock_validate_or_defaults(self) -> None:
        locked_only = f"{GETTER_DECL}\n"
        for neighbor in VALIDATE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("ValidateSettings", GETTER_DECL)
        self.assertNotIn("SetToDefaults", GETTER_DECL)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)

    def test_contract_does_not_relock_invert_look_or_apply_broadcast(
        self,
    ) -> None:
        locked_only = f"{GETTER_DECL}\n"
        for neighbor in INVERT_LOOK_NOT_LOCKED + APPLY_BROADCAST_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("SetInvertVerticalLook", GETTER_DECL)
        self.assertNotIn("GetInvertVerticalLook", GETTER_DECL)
        self.assertNotIn("ApplySettings", GETTER_DECL)
        self.assertNotIn("OnSettingsApplied", GETTER_DECL)
        self.assertNotIn("bInvertVerticalLook", GETTER_DECL)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)

    def test_contract_does_not_relock_cpg_feel_constants(self) -> None:
        locked_only = f"{GETTER_DECL}\n"
        section = public_section(origin_main_header())
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GETTER_DECL)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GETTER_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, GETTER_DECL),
            GETTER_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("SetCameraShakeScale", GETTER_DECL)
        self.assertNotIn("GetCameraShakeScale", GETTER_DECL)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UPROPERTY(Config)", section)
        self.assertNotIn("float MasterVolume", section)
        self.assertNotIn("float MouseSensitivity", section)
        self.assertNotIn("bool bInvertVerticalLook", section)
        self.assertNotIn("float CameraShakeScale", section)
        self.assertEqual(
            require_declaration(section, GETTER_DECL),
            GETTER_DECL,
        )
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn("return GEngine", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GETTER_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn(
            "USkyguardGameUserSettings::GetSkyguardGameUserSettings",
            section,
        )
        self.assertNotIn("return GEngine", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("{", GETTER_DECL)
        self.assertNotIn("}", GETTER_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(GETTER_DECL, "Rifle")
        self.assertNotEqual(GETTER_DECL, "Igla")
        self.assertNotIn("FireIgla", section)
        self.assertNotIn("FireRifle", section)
        self.assertNotIn("YakSpawnLocation", section)
        self.assertNotIn("bYakRuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"GameUserSettings getter contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, GETTER_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", GETTER_DECL)

    def test_contract_is_getter_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GETTER_DECL),
            GETTER_DECL,
        )
        locked_only = f"{GETTER_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GETTER_DECL)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GETTER_DECL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GETTER_DECL)
            self.assertNotIn(token, section)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return GEngine", section)
        self.assertNotIn("{", GETTER_DECL)
        self.assertNotEqual(GETTER_DECL, "Rifle")
        self.assertNotEqual(GETTER_DECL, "Igla")

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
