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
# values, or the .cpp const-bool / SaveSettings body.
APPLY_AND_SAVE_SETTINGS = (
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);"
)
APPLY_AND_SAVE_SETTINGS_NAME = "void ApplyAndSaveSettings("
PARAMETER_LIST = (
    "bool bCheckForCommandLineOverrides = true",
)
# Leftover #56–#64 plus GameUserSettings production sources/tests.
# This lane only adds an isolated Python ApplyAndSaveSettings
# declaration contract. Stay off leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover CPG feel constants (#118), leftover CPG mesh/art,
# Yak/Igla/rifle live copy, and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardGameUserSettings.h",
    "SkyguardGameUserSettings.cpp",
    "SkyguardGameUserSettingsTests.cpp",
    "SkyguardGameUserSettingsApplyTests.cpp",
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
# Isolated-test drafts stay off this lane. In-flight getter
# declaration, invert-look / ApplySettings broadcast (#134),
# leftover CPG feel constants (#118), leftover theater-kit #59,
# leftover Harbor #6/#8/#9, and leftover flare/HUD #57/#61/#62
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();",
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const { return MasterVolume; }",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
    "USkyguardGameUserSettings();",
)
GETTER_NOT_LOCKED = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();"
)
INVERT_LOOK_NOT_LOCKED = (
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
)
APPLY_SETTINGS_NOT_LOCKED = (
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;"
)
VOLUME_SENSITIVITY_SHAKE_NOT_LOCKED = (
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const { return MasterVolume; }",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
)
VALIDATE_DEFAULTS_NOT_LOCKED = (
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
)
# Leftover #118 CPG feel constants stay unlocked.
CPG_FEEL_NOT_LOCKED = (
    "namespace SkyguardApacheCpgFeel",
    "CannonFireRate",
    "CannonMagazineSize",
    "RocketSalvoSeconds",
    "RocketMagazineSize",
    "GuidedLockSeconds",
    "GuidedMagazineSize",
    "12.0f",
    "22.0f",
)
# .cpp bodies / invented return values stay unlocked. Do not
# invent INDEX_NONE or the cpp const bool / SaveSettings form.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "return nullptr",
    "const bool bCheckForCommandLineOverrides",
    "SaveSettings()",
    "OnSettingsApplied.Broadcast",
    "FApp::SetVolumeMultiplier",
    "Cast<USkyguardGameUserSettings>",
    "GEngine",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
    "namespace SkyguardApacheCpgFeel",
)
PRIVATE_FIELDS_NOT_LOCKED = (
    "MasterVolume = 1.f",
    "MouseSensitivity = 0.07f",
    "bInvertVerticalLook = true",
    "CameraShakeScale = 1.f",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
CLASS_RE = re.compile(rf"class\s+\w+\s+{re.escape(CLASS_NAME)}\b")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
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
    start = match.start()
    try:
        brace = header.index("{", start)
    except ValueError as exc:
        raise AssertionError(
            f"{CLASS_NAME} body is unclosed in origin/main:{HEADER_PATH}"
        ) from exc
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[brace : index + 1]
    raise AssertionError(
        f"{CLASS_NAME} body is unclosed in origin/main:{HEADER_PATH}"
    )


def public_section(header: str) -> str:
    body = class_body(header)
    marker = re.search(r"\bpublic\s*:", body)
    if marker is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = marker.end()
    nxt = re.search(r"\b(?:private|protected)\s*:", body[start:])
    if nxt is not None:
        return body[start : start + nxt.start()]
    return body[start:].rstrip().removesuffix("}")


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


class ApplyAndSaveSettingsDeclContractTests(unittest.TestCase):
    def test_game_user_settings_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertRegex(header, CLASS_RE)
        region = public_section(header)
        self.assertTrue(has_declaration(region, APPLY_AND_SAVE_SETTINGS), region)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSettings "
                ": public UGameUserSettings\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uclass_macro_alone_does_not_satisfy_class(self) -> None:
        macro_only = (
            "UCLASS(Config = GameUserSettings, "
            "ConfigDoNotCheckDefaults, BlueprintType)\n"
            "class SKYGUARD52_API USkyguardUnrelatedSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(macro_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "private:\n"
            f"\t{APPLY_AND_SAVE_SETTINGS}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_apply_and_save_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "public:\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "\tvirtual void ValidateSettings() override;\n"
            "\tvirtual void SetToDefaults() override;\n"
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings();\n"
            "\tvoid SetMasterVolume(float Value);\n"
            "\tvoid SetInvertVerticalLook(bool bValue);\n"
            "}\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            f"{neighbors_only}"
        )
        region = public_section(header)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, APPLY_AND_SAVE_SETTINGS)
        self.assertIn("ApplyAndSaveSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_apply_settings_override_does_not_satisfy_declaration(self) -> None:
        apply_only = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "};\n"
        )
        region = public_section(apply_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, APPLY_AND_SAVE_SETTINGS)
        self.assertIn("ApplyAndSaveSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(region, APPLY_AND_SAVE_SETTINGS))

    def test_missing_default_argument_fails_closed(self) -> None:
        no_default = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides);\n"
            "};\n"
        )
        region = public_section(no_default)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, APPLY_AND_SAVE_SETTINGS)
        self.assertIn("ApplyAndSaveSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_private_declaration_does_not_satisfy_public_section(self) -> None:
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "private:\n"
            f"\t{APPLY_AND_SAVE_SETTINGS}\n"
            "};\n"
        )
        region = public_section(header)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, APPLY_AND_SAVE_SETTINGS)
        self.assertIn("ApplyAndSaveSettings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(region, APPLY_AND_SAVE_SETTINGS))
        self.assertNotIn("ApplyAndSaveSettings", region)

    def test_apply_and_save_declaration_matches_origin_main(self) -> None:
        region = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(region, APPLY_AND_SAVE_SETTINGS),
            APPLY_AND_SAVE_SETTINGS,
        )
        self.assertTrue(has_declaration(region, APPLY_AND_SAVE_SETTINGS))
        self.assertEqual(declaration_count(region, APPLY_AND_SAVE_SETTINGS), 1)
        self.assertTrue(
            APPLY_AND_SAVE_SETTINGS.endswith(";"),
            APPLY_AND_SAVE_SETTINGS,
        )
        self.assertIn(APPLY_AND_SAVE_SETTINGS_NAME, APPLY_AND_SAVE_SETTINGS)
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, APPLY_AND_SAVE_SETTINGS)
            self.assertTrue(has_declaration(region, parameter), region)
        self.assertNotIn("INDEX_NONE", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("return ", APPLY_AND_SAVE_SETTINGS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid\n"
            "\tApplyAndSaveSettings(\n"
            "\t\tbool bCheckForCommandLineOverrides = true);\n"
            "};\n"
        )
        wrap_args = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid ApplyAndSaveSettings(\n"
            "\t\tbool bCheckForCommandLineOverrides = true);\n"
            "};\n"
        )
        wrap_default = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid ApplyAndSaveSettings(\n"
            "\t\tbool bCheckForCommandLineOverrides=\n"
            "\t\ttrue);\n"
            "};\n"
        )
        for header in (wrap_type, wrap_args, wrap_default):
            region = public_section(header)
            self.assertTrue(
                has_declaration(region, APPLY_AND_SAVE_SETTINGS),
                region,
            )
            self.assertEqual(
                require_declaration(region, APPLY_AND_SAVE_SETTINGS),
                APPLY_AND_SAVE_SETTINGS,
            )
            self.assertEqual(
                declaration_count(region, APPLY_AND_SAVE_SETTINGS),
                1,
            )
        one_line = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            f"\t{APPLY_AND_SAVE_SETTINGS}\n"
            "};\n"
        )
        self.assertTrue(
            has_declaration(public_section(one_line), APPLY_AND_SAVE_SETTINGS)
        )
        region = public_section(origin_main_header())
        self.assertTrue(has_declaration(region, APPLY_AND_SAVE_SETTINGS), region)
        self.assertEqual(
            require_declaration(region, APPLY_AND_SAVE_SETTINGS),
            APPLY_AND_SAVE_SETTINGS,
        )
        for parameter in PARAMETER_LIST:
            self.assertTrue(
                has_declaration(public_section(wrap_args), parameter),
                wrap_args,
            )
            self.assertTrue(has_declaration(region, parameter), region)

    def test_declaration_accepts_default_argument_form(self) -> None:
        self.assertIn("= true", APPLY_AND_SAVE_SETTINGS)
        self.assertIn(
            "bool bCheckForCommandLineOverrides = true",
            APPLY_AND_SAVE_SETTINGS,
        )
        region = public_section(origin_main_header())
        self.assertTrue(has_declaration(region, "= true"), region)
        self.assertTrue(
            has_declaration(
                region,
                "bool bCheckForCommandLineOverrides = true",
            ),
            region,
        )
        compact_default = (
            f"class SKYGUARD52_API {CLASS_NAME} : public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides=true);\n"
            "};\n"
        )
        self.assertTrue(
            has_declaration(
                public_section(compact_default),
                APPLY_AND_SAVE_SETTINGS,
            )
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        region = public_section(origin_main_header())
        self.assertTrue(
            APPLY_AND_SAVE_SETTINGS.endswith(";"),
            APPLY_AND_SAVE_SETTINGS,
        )
        self.assertTrue(
            APPLY_AND_SAVE_SETTINGS.startswith("void "),
            APPLY_AND_SAVE_SETTINGS,
        )
        self.assertNotIn("return ", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("INDEX_NONE", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("NAME_None", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("{", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("}", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("const bool bCheckForCommandLineOverrides", APPLY_AND_SAVE_SETTINGS)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("INDEX_NONE", region)
        self.assertNotIn("NAME_None", region)

    def test_contract_does_not_relock_getter(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        self.assertNotIn(GETTER_NOT_LOCKED, locked_only)
        self.assertNotIn(GETTER_NOT_LOCKED, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetSkyguardGameUserSettings", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)

    def test_contract_does_not_relock_invert_look_or_apply_settings(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        for neighbor in INVERT_LOOK_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn(APPLY_SETTINGS_NOT_LOCKED, locked_only)
        self.assertNotIn(APPLY_SETTINGS_NOT_LOCKED, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetInvertVerticalLook", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetInvertVerticalLook", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("override", APPLY_AND_SAVE_SETTINGS)

    def test_contract_does_not_relock_volume_sensitivity_or_shake(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        for neighbor in VOLUME_SENSITIVITY_SHAKE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetMasterVolume", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetMasterVolume", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetMouseSensitivity", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetMouseSensitivity", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetCameraShakeScale", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetCameraShakeScale", APPLY_AND_SAVE_SETTINGS)

    def test_contract_does_not_relock_validate_or_defaults(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        for neighbor in VALIDATE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("ValidateSettings", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SetToDefaults", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        self.assertEqual(
            require_declaration(locked_only, APPLY_AND_SAVE_SETTINGS),
            APPLY_AND_SAVE_SETTINGS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        self.assertNotIn("OnSettingsApplied", APPLY_AND_SAVE_SETTINGS)

    def test_contract_does_not_relock_cpg_feel_constants(self) -> None:
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        region = public_section(origin_main_header())
        for token in CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
            self.assertNotIn(token, region)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        region = public_section(header)
        self.assertIn(CLASS_NAME, header)
        self.assertEqual(
            require_declaration(region, APPLY_AND_SAVE_SETTINGS),
            APPLY_AND_SAVE_SETTINGS,
        )
        for token in PRIVATE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, region)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SkyguardGameUserSettings.cpp", region)
        self.assertNotIn("SaveSettings()", region)
        self.assertNotIn("UPROPERTY(Config)", region)

    def test_contract_does_not_read_cpp_or_return_tables(self) -> None:
        region = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("SkyguardGameUserSettings.cpp", region)
        self.assertNotIn(
            "USkyguardGameUserSettings::ApplyAndSaveSettings",
            region,
        )
        self.assertNotIn("SaveSettings()", region)
        self.assertNotIn("OnSettingsApplied.Broadcast", region)
        self.assertNotIn("const bool bCheckForCommandLineOverrides", region)

    def test_contract_does_not_retune_harbor(self) -> None:
        region = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, region)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", region)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", region)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        region = public_section(origin_main_header())
        self.assertNotIn("Rifle", region)
        self.assertNotIn("Igla", region)
        self.assertNotIn("Yak", region)
        self.assertNotEqual(APPLY_AND_SAVE_SETTINGS, "Rifle")
        self.assertNotEqual(APPLY_AND_SAVE_SETTINGS, "Igla")
        self.assertNotIn("FireIgla", region)
        self.assertNotIn("FireRifle", region)
        self.assertNotIn("YakSpawnLocation", region)
        self.assertNotIn("bYakRuntimeReady", region)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", region)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        region = public_section(origin_main_header())
        lowered = region.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"GameUserSettings ApplyAndSaveSettings contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, APPLY_AND_SAVE_SETTINGS.lower())

    def test_contract_is_apply_and_save_settings_declaration_only(self) -> None:
        header = origin_main_header()
        region = public_section(header)
        self.assertIn(CLASS_NAME, header)
        self.assertEqual(
            require_declaration(region, APPLY_AND_SAVE_SETTINGS),
            APPLY_AND_SAVE_SETTINGS,
        )
        locked_only = f"{APPLY_AND_SAVE_SETTINGS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        for token in CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, region)
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, APPLY_AND_SAVE_SETTINGS)
        for token in PRIVATE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, region)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertNotIn("Rifle", region)
        self.assertNotIn("Igla", region)
        self.assertNotIn("Yak", region)
        self.assertNotIn("INDEX_NONE", region)
        self.assertNotIn("return ", APPLY_AND_SAVE_SETTINGS)
        self.assertNotIn("const bool bCheckForCommandLineOverrides", APPLY_AND_SAVE_SETTINGS)
        self.assertNotEqual(APPLY_AND_SAVE_SETTINGS, "Rifle")
        self.assertNotEqual(APPLY_AND_SAVE_SETTINGS, "Igla")
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, APPLY_AND_SAVE_SETTINGS)

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
