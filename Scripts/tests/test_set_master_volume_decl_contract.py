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
# values, or the MasterVolume default.
SET_MASTER_VOLUME = "void SetMasterVolume(float Value);"
# Leftover #56–#64 plus GameUserSettings production sources/tests.
# This lane only adds an isolated Python SetMasterVolume
# declaration contract. Stay off leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover CPG feel constants (#118), leftover CPG mesh/art,
# and leftover Yak/Igla/rifle live copy.
LOCKED = {
    "SkyguardGameUserSettings.h",
    "SkyguardGameUserSettings.cpp",
    "SkyguardGameUserSettingsTests.cpp",
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
# Isolated-test drafts stay off this lane. GetSkyguardGameUserSettings
# (in-flight getter), ApplyAndSaveSettings (sibling in-flight),
# invert-look / ApplySettings broadcast (#134), leftover CPG feel
# (#118), and leftover theater-kit #59 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_get_skyguard_game_user_settings_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_invert_look_apply_settings_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();",
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);",
    "float GetMasterVolume() const { return MasterVolume; }",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
)
GETTER_NOT_LOCKED = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();"
)
APPLY_AND_SAVE_NOT_LOCKED = (
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);"
)
GET_MASTER_VOLUME_NOT_LOCKED = (
    "float GetMasterVolume() const { return MasterVolume; }"
)
INVERT_LOOK_NOT_LOCKED = (
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
)
MOUSE_AND_SHAKE_NOT_LOCKED = (
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
)
# Private MasterVolume default stays unlocked. Do not invent 1.f.
MASTER_VOLUME_DEFAULT_NOT_LOCKED = (
    "float MasterVolume = 1.f;",
    "MasterVolume = 1.f",
)
# Leftover #118 CPG feel constants stay unlocked.
CPG_FEEL_NOT_LOCKED = (
    "namespace SkyguardApacheCpgFeel",
    "CannonFireRate",
    "CannonDamage",
    "RocketSalvoSeconds",
    "GuidedLockSeconds",
    "12.0f",
    "22.0f",
    "1.65f",
    "1.80f",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "namespace SkyguardApacheCpgFeel",
    "ESkyguardGunshipWeapon",
    "ASkyguardIglaMissile",
)
# .cpp bodies / invented return values / MasterVolume default
# stay unlocked. Do not invent INDEX_NONE or clamp tables.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "MasterVolume = 1.f",
    "FMath::Clamp",
    "SetVolumeMultiplier",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
CLASS_RE = re.compile(
    rf"class\s+SKYGUARD52_API\s+{re.escape(CLASS_NAME)}\b"
)


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


def class_body(header: str) -> str:
    match = CLASS_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{CLASS_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    brace = header.index("{", match.start())
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[brace : index + 1]
    raise AssertionError(
        f"{CLASS_NAME} class body is missing from "
        f"origin/main:{HEADER_PATH}"
    )


def public_section(header: str) -> str:
    body = class_body(header)
    public_match = re.search(r"\bpublic\s*:", body)
    if public_match is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public_match.end()
    next_access = re.search(r"\b(private|protected)\s*:", body[start:])
    if next_access is None:
        return body[start:-1]
    return body[start : start + next_access.start()]


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
            f"class {CLASS_NAME}"
        )
    return declaration


class SetMasterVolumeDeclContractTests(unittest.TestCase):
    def test_game_user_settings_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertRegex(header, CLASS_RE)
        body = class_body(header)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SET_MASTER_VOLUME), section)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        self.assertIn("public:", body)
        self.assertNotIn("public:", section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            public_section(
                "class SKYGUARD52_API USkyguardUnrelatedSettings "
                ": public UGameUserSettings\n"
                "{\n"
                "public:\n"
                "\tvoid SetMasterVolume(float Value);\n"
                "};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_delegate_mention_does_not_satisfy_class(self) -> None:
        delegate_only = (
            "DECLARE_MULTICAST_DELEGATE_OneParam(\n"
            "\tFSkyguardUserSettingsApplied,\n"
            "\tconst class USkyguardGameUserSettings&);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(delegate_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            "class SKYGUARD52_API USkyguardGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "private:\n"
            "\tfloat MasterVolume = 1.f;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_set_master_volume_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "public:\n"
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings();\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides = true);\n"
            "\tfloat GetMasterVolume() const { return MasterVolume; }\n"
            "\tvoid SetMouseSensitivity(float Value);\n"
            "\tvoid SetInvertVerticalLook(bool bValue) "
            "{ bInvertVerticalLook = bValue; }\n"
            "\tvoid SetCameraShakeScale(float Value);\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "private:\n"
            "\tfloat MasterVolume = 1.f;\n"
            "}\n"
        )
        section = public_section(
            "class SKYGUARD52_API USkyguardGameUserSettings "
            ": public UGameUserSettings\n"
            + neighbors_only
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SET_MASTER_VOLUME)
        self.assertIn("SetMasterVolume", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_set_master_volume_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        self.assertTrue(has_declaration(section, SET_MASTER_VOLUME))
        self.assertEqual(declaration_count(section, SET_MASTER_VOLUME), 1)
        self.assertTrue(SET_MASTER_VOLUME.endswith(";"), SET_MASTER_VOLUME)
        self.assertNotIn("INDEX_NONE", SET_MASTER_VOLUME)
        self.assertNotIn("return ", SET_MASTER_VOLUME)
        self.assertNotIn("MasterVolume = 1.f", SET_MASTER_VOLUME)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "class SKYGUARD52_API USkyguardGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid\n"
            "\tSetMasterVolume(float Value);\n"
            "};\n"
        )
        wrap_args = (
            "class SKYGUARD52_API USkyguardGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid SetMasterVolume(\n"
            "\t\tfloat Value);\n"
            "};\n"
        )
        wrap_type_section = public_section(wrap_type)
        wrap_args_section = public_section(wrap_args)
        self.assertTrue(
            has_declaration(wrap_type_section, SET_MASTER_VOLUME),
            wrap_type_section,
        )
        self.assertTrue(
            has_declaration(wrap_args_section, SET_MASTER_VOLUME),
            wrap_args_section,
        )
        self.assertEqual(
            require_declaration(wrap_type_section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        self.assertEqual(
            require_declaration(wrap_args_section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        self.assertEqual(
            declaration_count(wrap_type_section, SET_MASTER_VOLUME),
            1,
        )
        self.assertEqual(
            declaration_count(wrap_args_section, SET_MASTER_VOLUME),
            1,
        )
        one_line = (
            "class SKYGUARD52_API USkyguardGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            f"public:\n\t{SET_MASTER_VOLUME}\n"
            "};\n"
        )
        self.assertTrue(
            has_declaration(public_section(one_line), SET_MASTER_VOLUME)
        )
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SET_MASTER_VOLUME), section)
        self.assertEqual(
            require_declaration(section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(SET_MASTER_VOLUME.endswith(";"), SET_MASTER_VOLUME)
        self.assertNotIn("return ", SET_MASTER_VOLUME)
        self.assertNotIn("INDEX_NONE", SET_MASTER_VOLUME)
        self.assertNotIn("NAME_None", SET_MASTER_VOLUME)
        self.assertNotIn("{", SET_MASTER_VOLUME)
        self.assertNotIn("}", SET_MASTER_VOLUME)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_MASTER_VOLUME)

    def test_declaration_does_not_invent_master_volume_default(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SET_MASTER_VOLUME}\n"
        for token in MASTER_VOLUME_DEFAULT_NOT_LOCKED:
            self.assertNotIn(token, SET_MASTER_VOLUME)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, section)
        self.assertNotIn("= 1.f", SET_MASTER_VOLUME)
        self.assertNotIn("MasterVolume =", SET_MASTER_VOLUME)
        self.assertNotIn("float MasterVolume = 1.f;", section)

    def test_contract_does_not_relock_get_master_volume(self) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        self.assertEqual(
            require_declaration(locked_only, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        self.assertNotIn(GET_MASTER_VOLUME_NOT_LOCKED, locked_only)
        self.assertNotIn(GET_MASTER_VOLUME_NOT_LOCKED, SET_MASTER_VOLUME)
        self.assertNotIn("GetMasterVolume", SET_MASTER_VOLUME)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("return MasterVolume", SET_MASTER_VOLUME)
        self.assertNotIn("return MasterVolume", locked_only)

    def test_contract_does_not_relock_get_skyguard_game_user_settings(
        self,
    ) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        self.assertNotIn(GETTER_NOT_LOCKED, locked_only)
        self.assertNotIn(GETTER_NOT_LOCKED, SET_MASTER_VOLUME)
        self.assertNotIn("GetSkyguardGameUserSettings", SET_MASTER_VOLUME)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn(
            "static USkyguardGameUserSettings*",
            SET_MASTER_VOLUME,
        )

    def test_contract_does_not_relock_apply_and_save_settings(self) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        self.assertNotIn(APPLY_AND_SAVE_NOT_LOCKED, locked_only)
        self.assertNotIn(APPLY_AND_SAVE_NOT_LOCKED, SET_MASTER_VOLUME)
        self.assertNotIn("ApplyAndSaveSettings", SET_MASTER_VOLUME)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("bCheckForCommandLineOverrides", SET_MASTER_VOLUME)
        self.assertNotIn("bCheckForCommandLineOverrides", locked_only)

    def test_contract_does_not_relock_invert_look_or_apply_settings(
        self,
    ) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        for neighbor in INVERT_LOOK_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_MASTER_VOLUME)
        self.assertNotIn("SetInvertVerticalLook", SET_MASTER_VOLUME)
        self.assertNotIn("GetInvertVerticalLook", SET_MASTER_VOLUME)
        self.assertNotIn("ApplySettings", SET_MASTER_VOLUME)
        self.assertNotIn("OnSettingsApplied", SET_MASTER_VOLUME)
        self.assertNotIn("bInvertVerticalLook", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)

    def test_contract_does_not_relock_mouse_sensitivity_or_camera_shake(
        self,
    ) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        for neighbor in MOUSE_AND_SHAKE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_MASTER_VOLUME)
        self.assertNotIn("SetMouseSensitivity", SET_MASTER_VOLUME)
        self.assertNotIn("GetMouseSensitivity", SET_MASTER_VOLUME)
        self.assertNotIn("SetCameraShakeScale", SET_MASTER_VOLUME)
        self.assertNotIn("GetCameraShakeScale", SET_MASTER_VOLUME)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)

    def test_contract_does_not_relock_cpg_feel_constants(self) -> None:
        locked_only = f"{SET_MASTER_VOLUME}\n"
        section = public_section(origin_main_header())
        for token in CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, SET_MASTER_VOLUME)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, section)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertRegex(header, CLASS_RE)
        self.assertIn("public:", body)
        self.assertIn("private:", body)
        self.assertNotIn("private:", section)
        self.assertNotIn("float MasterVolume = 1.f;", section)
        self.assertNotIn("float MouseSensitivity = 0.07f;", section)
        self.assertNotIn("bool bInvertVerticalLook = true;", section)
        self.assertNotIn("float CameraShakeScale = 1.f;", section)
        self.assertEqual(
            require_declaration(section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn("FMath::Clamp", section)
        self.assertNotIn("SetVolumeMultiplier", section)

    def test_contract_does_not_read_cpp_or_clamp_tables(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_MASTER_VOLUME)
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn(
            "USkyguardGameUserSettings::SetMasterVolume",
            section,
        )
        self.assertNotIn("FMath::Clamp", section)
        self.assertNotIn("const float Value", section)
        self.assertNotIn("SetVolumeMultiplier", section)

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
        self.assertNotEqual(SET_MASTER_VOLUME, "Rifle")
        self.assertNotEqual(SET_MASTER_VOLUME, "Igla")
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
                f"SetMasterVolume public section contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, SET_MASTER_VOLUME.lower())

    def test_contract_is_set_master_volume_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertRegex(header, CLASS_RE)
        self.assertEqual(
            require_declaration(section, SET_MASTER_VOLUME),
            SET_MASTER_VOLUME,
        )
        locked_only = f"{SET_MASTER_VOLUME}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_MASTER_VOLUME)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        for token in MASTER_VOLUME_DEFAULT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_MASTER_VOLUME)
            self.assertNotIn(token, section)
        for token in CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_MASTER_VOLUME)
            self.assertNotIn(token, section)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_MASTER_VOLUME)
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
        self.assertNotIn("float MasterVolume = 1.f;", section)
        self.assertNotEqual(SET_MASTER_VOLUME, "Rifle")
        self.assertNotEqual(SET_MASTER_VOLUME, "Igla")

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
