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
# values, the CameraShakeScale config default (1.f), or the
# setter body.
SET_CAMERA_SHAKE_SCALE = "void SetCameraShakeScale(float Value);"
# Leftover #56–#64 plus GameUserSettings production files.
# This lane only adds an isolated Python SetCameraShakeScale
# declaration contract. Stay off invert-look / ApplySettings
# broadcast (#134), leftover Apache CPG feel constants (#118),
# leftover Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover drafts #56–#64, leftover
# #147 ApacheSystem / #149 weapon stations / #152 pilot
# commands / #154 loadout/lock-phase, leftover gun-fire
# camera shake tests (#8860), CPG mesh/art, Yak/Igla/rifle
# live copy, and dirty D:\Skyguard52.
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
# Isolated-test drafts stay off this lane. GetCameraShakeScale
# is the next unused sibling. GetMasterVolume / SetMouseSensitivity
# / GetMouseSensitivity are in-flight or newly drafted.
# GetSkyguardGameUserSettings (#292), ApplyAndSaveSettings
# (#294), SetMasterVolume (#293), invert-look / ApplySettings
# broadcast (#134), leftover Apache CPG feel constants (#118),
# leftover theater-kit #59, and leftover gun-fire camera
# shake tests (#8860) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_set_master_volume_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_gun_fire_camera_shake_contract.py",
    "Scripts/tests/test_gun_fire_camera_shake_constructor_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();",
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);",
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const { return MasterVolume; }",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
    "float GetCameraShakeScale() const { return CameraShakeScale; }",
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
)
GET_CAMERA_SHAKE_SCALE_NOT_LOCKED = (
    "float GetCameraShakeScale() const { return CameraShakeScale; }"
)
GET_MASTER_VOLUME_NOT_LOCKED = (
    "float GetMasterVolume() const { return MasterVolume; }"
)
MOUSE_NOT_LOCKED = (
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const { return MouseSensitivity; }",
)
GETTER_NOT_LOCKED = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();"
)
APPLY_AND_SAVE_NOT_LOCKED = (
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);"
)
SET_MASTER_VOLUME_NOT_LOCKED = ("void SetMasterVolume(float Value);",)
INVERT_LOOK_NOT_LOCKED = (
    "void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }",
    "bool GetInvertVerticalLook() const { return bInvertVerticalLook; }",
)
APPLY_BROADCAST_NOT_LOCKED = (
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
)
VALIDATE_DEFAULTS_NOT_LOCKED = (
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
)
# Private CameraShakeScale config default stays unlocked.
CAMERA_SHAKE_DEFAULT_NOT_LOCKED = (
    "float CameraShakeScale = 1.f;",
    "CameraShakeScale = 1.f",
    "1.f",
)
# Leftover #118 Apache CPG feel constants stay unlocked.
FEEL_NOT_LOCKED = (
    "CannonFireRate",
    "CannonDamage",
    "CannonMagazineSize",
    "RocketSalvoSeconds",
    "GuidedLockSeconds",
    "SkyguardApacheCpgFeel",
    "namespace SkyguardApacheCpgFeel",
)
# Leftover #147 ApacheSystem, #149 weapon stations, #152 pilot
# commands, #154 loadout/lock-phase, leftover Hydra helper
# that takes ASkyguardGunner*, and leftover #8860 gun-fire
# camera shake tests stay unlocked.
LEFTOVER_SIBLINGS = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeapon",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "ASkyguardGunner",
)
GUN_FIRE_SHAKE_NOT_LOCKED = (
    "USkyguardGunFireCameraShake",
    "SkyguardGunFireCameraShake",
    "SkyguardGunFireCameraShakeTests",
    "test_gun_fire_camera_shake",
    "OscillationDuration",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "FSkyguardSearchlightTrackRuntime",
    "namespace SkyguardApacheCpgFeel",
)
# .cpp setter body / invented return values stay unlocked.
# Do not invent INDEX_NONE or clamp tables.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return nullptr",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "return GEngine",
    "FMath::Clamp",
    "const float Value",
    "0.f",
    "1.f",
    "CameraShakeScale = FMath::Clamp",
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


class SetCameraShakeScaleDeclContractTests(unittest.TestCase):
    def test_game_user_settings_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SET_CAMERA_SHAKE_SCALE), section)

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
            f"\t{SET_CAMERA_SHAKE_SCALE}\n"
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
            f"\t{SET_CAMERA_SHAKE_SCALE}\n"
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
            f"\t{SET_CAMERA_SHAKE_SCALE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SET_CAMERA_SHAKE_SCALE)
        self.assertIn("SetCameraShakeScale", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(SET_CAMERA_SHAKE_SCALE, section)

    def test_missing_set_camera_shake_scale_declaration_fails_closed(
        self,
    ) -> None:
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
            "\tfloat GetCameraShakeScale() const "
            "{ return CameraShakeScale; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SET_CAMERA_SHAKE_SCALE)
        self.assertIn("SetCameraShakeScale", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, '
            'Category = "Settings|Accessibility")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SET_CAMERA_SHAKE_SCALE)
        self.assertIn("SetCameraShakeScale", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_setters_do_not_satisfy(self) -> None:
        other_setters = (
            "\tvoid SetMasterVolume(float Value);\n"
            "\tvoid SetMouseSensitivity(float Value);\n"
            "\tvoid SetInvertVerticalLook(bool bValue) "
            "{ bInvertVerticalLook = bValue; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_setters, SET_CAMERA_SHAKE_SCALE)
        self.assertIn("SetCameraShakeScale", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_set_camera_shake_scale_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertTrue(has_declaration(section, SET_CAMERA_SHAKE_SCALE))
        self.assertEqual(declaration_count(section, SET_CAMERA_SHAKE_SCALE), 1)
        self.assertTrue(
            SET_CAMERA_SHAKE_SCALE.endswith(";"),
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertNotIn("INDEX_NONE", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("return ", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("1.f", SET_CAMERA_SHAKE_SCALE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tSetCameraShakeScale(float Value);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tvoid SetCameraShakeScale(\n"
            "\t\tfloat Value);\n"
            "private:\n"
            "};\n"
        )
        wrap_void = (
            "public:\n"
            "\tvoid\n"
            "\tSetCameraShakeScale(\n"
            "\tfloat Value);\n"
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
        header_wrap_void = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_void}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_void,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, SET_CAMERA_SHAKE_SCALE),
                section,
            )
            self.assertEqual(
                require_declaration(section, SET_CAMERA_SHAKE_SCALE),
                SET_CAMERA_SHAKE_SCALE,
            )
            self.assertEqual(
                declaration_count(section, SET_CAMERA_SHAKE_SCALE),
                1,
            )
        one_line = f"{{\npublic:\n\t{SET_CAMERA_SHAKE_SCALE}\n}}\n"
        self.assertTrue(has_declaration(one_line, SET_CAMERA_SHAKE_SCALE))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, SET_CAMERA_SHAKE_SCALE),
            section,
        )
        self.assertEqual(
            require_declaration(section, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(
            SET_CAMERA_SHAKE_SCALE.endswith(";"),
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertNotIn("return ", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("INDEX_NONE", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("NAME_None", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("{", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("}", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("return GEngine", section)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)

    def test_declaration_does_not_invent_camera_shake_scale_default(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for token in CAMERA_SHAKE_DEFAULT_NOT_LOCKED:
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, section)
        self.assertNotIn("= 1.f", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("CameraShakeScale =", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("float CameraShakeScale = 1.f;", section)

    def test_declaration_does_not_lock_setter_body(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for token in (
            "FMath::Clamp",
            "const float Value",
            "0.f",
            "1.f",
            "CameraShakeScale = FMath::Clamp",
            "USkyguardGameUserSettings::SetCameraShakeScale",
        ):
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_get_camera_shake_scale(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        self.assertEqual(
            require_declaration(locked_only, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertNotIn(GET_CAMERA_SHAKE_SCALE_NOT_LOCKED, locked_only)
        self.assertNotIn(
            GET_CAMERA_SHAKE_SCALE_NOT_LOCKED,
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertNotIn("GetCameraShakeScale", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        self.assertNotIn("return CameraShakeScale", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("return CameraShakeScale", locked_only)

    def test_contract_does_not_relock_get_master_volume(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        self.assertNotIn(GET_MASTER_VOLUME_NOT_LOCKED, locked_only)
        self.assertNotIn(GET_MASTER_VOLUME_NOT_LOCKED, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetMasterVolume", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("return MasterVolume", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("return MasterVolume", locked_only)

    def test_contract_does_not_relock_mouse_sensitivity(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for neighbor in MOUSE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetMouseSensitivity", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetMouseSensitivity", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)

    def test_contract_does_not_relock_get_skyguard_game_user_settings(
        self,
    ) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        self.assertNotIn(GETTER_NOT_LOCKED, locked_only)
        self.assertNotIn(GETTER_NOT_LOCKED, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetSkyguardGameUserSettings", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn(
            "static USkyguardGameUserSettings*",
            SET_CAMERA_SHAKE_SCALE,
        )

    def test_contract_does_not_relock_apply_and_save_settings(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        self.assertNotIn(APPLY_AND_SAVE_NOT_LOCKED, locked_only)
        self.assertNotIn(APPLY_AND_SAVE_NOT_LOCKED, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ApplyAndSaveSettings", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("bCheckForCommandLineOverrides", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("bCheckForCommandLineOverrides", locked_only)

    def test_contract_does_not_relock_set_master_volume(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for neighbor in SET_MASTER_VOLUME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetMasterVolume", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetMasterVolume", locked_only)

    def test_contract_does_not_relock_invert_look_or_apply_broadcast(
        self,
    ) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for neighbor in INVERT_LOOK_NOT_LOCKED + APPLY_BROADCAST_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetInvertVerticalLook", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetInvertVerticalLook", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ApplySettings", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("OnSettingsApplied", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("bInvertVerticalLook", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)

    def test_contract_does_not_relock_validate_or_defaults(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for neighbor in VALIDATE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ValidateSettings", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("SetToDefaults", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)

    def test_contract_does_not_relock_cpg_feel_constants(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        section = public_section(origin_main_header())
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_apache_siblings(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SIBLINGS:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        self.assertNotIn("ApplyHydraForClusters", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ASkyguardGunner*", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("ASkyguardGunner*", section)

    def test_contract_does_not_relock_gun_fire_camera_shake(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        section = public_section(origin_main_header())
        for token in GUN_FIRE_SHAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        self.assertNotIn("GunFireCameraShake", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GunFireCameraShake", locked_only)
        self.assertNotIn("OscillationDuration", section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        self.assertEqual(
            require_declaration(locked_only, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)

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
            require_declaration(section, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn("FMath::Clamp", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn(
            "USkyguardGameUserSettings::SetCameraShakeScale",
            section,
        )
        self.assertNotIn("return GEngine", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("{", SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("}", SET_CAMERA_SHAKE_SCALE)

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
        self.assertNotEqual(SET_CAMERA_SHAKE_SCALE, "Rifle")
        self.assertNotEqual(SET_CAMERA_SHAKE_SCALE, "Igla")
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
                f"SetCameraShakeScale public section contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, SET_CAMERA_SHAKE_SCALE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", SET_CAMERA_SHAKE_SCALE)

    def test_contract_is_set_camera_shake_scale_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SET_CAMERA_SHAKE_SCALE),
            SET_CAMERA_SHAKE_SCALE,
        )
        locked_only = f"{SET_CAMERA_SHAKE_SCALE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CAMERA_SHAKE_SCALE)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("GetInvertVerticalLook", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        self.assertNotIn("GunFireCameraShake", locked_only)
        for token in CAMERA_SHAKE_DEFAULT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
        for token in LEFTOVER_SIBLINGS:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        for token in GUN_FIRE_SHAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
            self.assertNotIn(token, section)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_CAMERA_SHAKE_SCALE)
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
        self.assertNotIn("1.f", section)
        self.assertNotIn("FMath::Clamp", section)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("GunFireCameraShake", section)
        self.assertNotIn("{", SET_CAMERA_SHAKE_SCALE)
        self.assertNotEqual(SET_CAMERA_SHAKE_SCALE, "Rifle")
        self.assertNotEqual(SET_CAMERA_SHAKE_SCALE, "Igla")

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
