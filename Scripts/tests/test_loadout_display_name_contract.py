from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardGunshipTypes.h"
HEADER_NAME = "SkyguardGunshipTypes.h"
STRUCT_NAME = "FSkyguardLoadoutSpec"
# Leftover #56–#64 plus GunshipTypes production sources and leftover
# #8/#114/#154 loadout files. This lane only adds an isolated Python
# declaration-presence contract.
LOCKED = {
    "SkyguardGunshipTypes.h",
    "SkyguardGunshipTypes.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardCpgLoadoutSlot34Tests.cpp",
    "SkyguardCpgDebriefLoadoutTests.cpp",
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
# Isolated-test drafts and in-flight siblings stay off this lane.
# #253 loadout-spec in-struct defaults, in-flight slot helpers, leftover
# #154 loadout enum contract, leftover theater-kit #59, and storm-rain
# beat-kit field/label contracts stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_loadout_slot_helpers_contract.py",
    "Scripts/tests/test_gunship_types_loadout_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_labels_contract.py",
)
# Header free-function declaration after FSkyguardLoadoutSpec.
# Not the .cpp switch / TEXT("...") table.
DISPLAY_NAME_DECLARATION = (
    "const TCHAR* SkyguardLoadoutDisplayName(ESkyguardLoadout Loadout);"
)
# In-flight / sibling helpers stay unlocked. Presence here is documentary
# only — this contract must still pass if they are absent.
SIBLING_DECLARATIONS = (
    "FSkyguardLoadoutSpec SkyguardResolveLoadout(ESkyguardLoadout Loadout);",
    "ESkyguardLoadout SkyguardLoadoutFromSlot(int32 Slot);",
    "int32 SkyguardLoadoutSlot(ESkyguardLoadout Loadout);",
)
# #253 Balanced in-struct defaults stay in the struct body.
SPEC_DEFAULT_TOKENS = (
    "ESkyguardLoadout Loadout = ESkyguardLoadout::Balanced;",
    "ESkyguardGunshipWeapon StartingStation = ESkyguardGunshipWeapon::Cannon;",
    "int32 FlareCount = 6;",
    "float HullIntegrity = 140.f;",
    "PlaystyleLine",
    "CannonMagazineSize",
    "CannonReserve",
    "RocketMagazineSize",
    "RocketReserve",
    "GuidedMagazineSize",
    "GuidedReserve",
)
# #154 / #149 enum enumerators stay unlocked.
ENUM_TOKENS = (
    "enum class ESkyguardLoadout",
    "enum class ESkyguardGuidedLockPhase",
    "enum class ESkyguardGunshipWeapon",
    "enum class ESkyguardCpgSightMode",
    "UENUM(",
    "UMETA(",
)
# .cpp display-name / resolve tables stay unlocked. Do not invent strings.
CPP_TABLE_TOKENS = (
    "switch (Loadout)",
    'return TEXT("',
    "case ESkyguardLoadout::",
    "CannonMagazineSize = 24",
    "CannonMagazineSize = 40",
    "FlareCount = 8",
    "FlareCount = 5",
    "FlareCount = 10",
)
INVENTED = (
    "INDEX_NONE",
    "NAME_None",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_INCOMING = "IncomingRadar"


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


def free_function_region(header: str) -> str:
    """Header text after FSkyguardLoadoutSpec, not the struct body."""
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    after = header[finish + 2 :]
    cut = len(after)
    for token in ("\nUENUM(", "\nenum class "):
        if token in after:
            cut = min(cut, after.index(token))
    return after[:cut]


def free_function_declarations(region: str) -> list[str]:
    decls: list[str] = []
    for raw in region.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("/*"):
            continue
        if "(" in line and line.endswith(";"):
            decls.append(line)
    return decls


def require_display_name_declaration(region: str) -> str:
    for decl in free_function_declarations(region):
        if decl == DISPLAY_NAME_DECLARATION:
            return decl
    raise AssertionError(
        f"{DISPLAY_NAME_DECLARATION} is missing from "
        f"origin/main:{HEADER_PATH} after {STRUCT_NAME}"
    )


def standalone_harbor_clocks(region: str) -> list[str]:
    found: list[str] = []
    if re.search(r"(?<![\d.])40\.f", region):
        found.append("40.f")
    if re.search(r"(?<![\d.])80\.f", region):
        found.append("80.f")
    return found


class LoadoutDisplayNameContractTests(unittest.TestCase):
    def test_display_name_declaration_exists(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_display_name_declaration(region)
        self.assertEqual(decl, DISPLAY_NAME_DECLARATION)
        self.assertIn(DISPLAY_NAME_DECLARATION, region)
        self.assertIn(DISPLAY_NAME_DECLARATION, free_function_declarations(region))

    def test_missing_declaration_fails_closed(self) -> None:
        region = "\n".join(SIBLING_DECLARATIONS) + "\n"
        with self.assertRaises(AssertionError) as raised:
            require_display_name_declaration(region)
        self.assertIn("SkyguardLoadoutDisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_loadout_spec_anchor_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            free_function_region(
                "struct FSkyguardUnrelated\n{\n};\n"
                f"{DISPLAY_NAME_DECLARATION}\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_inside_struct_body_fails_closed(self) -> None:
        header = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{DISPLAY_NAME_DECLARATION}\n"
            "};\n"
            "UENUM(BlueprintType)\n"
            "enum class ESkyguardClimaxKind : uint8\n"
            "{\n"
            "};\n"
        )
        region = free_function_region(header)
        with self.assertRaises(AssertionError) as raised:
            require_display_name_declaration(region)
        self.assertIn("SkyguardLoadoutDisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(DISPLAY_NAME_DECLARATION, region)

    def test_contract_does_not_require_sibling_helper_declarations(self) -> None:
        region = f"{DISPLAY_NAME_DECLARATION}\n"
        self.assertEqual(
            require_display_name_declaration(region),
            DISPLAY_NAME_DECLARATION,
        )
        decls = free_function_declarations(region)
        self.assertEqual(decls, [DISPLAY_NAME_DECLARATION])
        for sibling in SIBLING_DECLARATIONS:
            self.assertNotIn(sibling, decls)
            self.assertNotIn(sibling, region)

    def test_contract_does_not_relock_loadout_spec_defaults(self) -> None:
        region = free_function_region(origin_main_header())
        for token in SPEC_DEFAULT_TOKENS:
            self.assertNotIn(token, region)
        self.assertNotIn("struct FSkyguardLoadoutSpec", region)
        self.assertNotIn("{", region)

    def test_contract_does_not_relock_loadout_weapon_or_sight_enums(self) -> None:
        region = free_function_region(origin_main_header())
        for token in ENUM_TOKENS:
            self.assertNotIn(token, region)
        self.assertNotIn("AntiArmor", region)
        self.assertNotIn("RocketHeavy", region)
        self.assertNotIn("Intercept", region)
        self.assertNotIn("Balanced", region)
        self.assertNotIn("GuidedMissile", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Search", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Detect", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Track", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Lock", region)
        self.assertNotIn("ESkyguardCpgSightMode::Helmet", region)
        self.assertNotIn("TargetingSensor", region)

    def test_contract_does_not_lock_display_name_string_contents(self) -> None:
        region = free_function_region(origin_main_header())
        decls = free_function_declarations(region)
        for token in CPP_TABLE_TOKENS:
            self.assertNotIn(token, region)
            self.assertNotIn(token, decls)
        self.assertNotIn('TEXT("', region)
        self.assertNotIn("DisplayName =", region)
        self.assertNotIn("UMETA(", region)

    def test_declaration_does_not_invent_index_none(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_display_name_declaration(region)
        for token in INVENTED:
            self.assertNotIn(token, region)
            self.assertNotIn(token, decl)
        self.assertNotIn("INDEX_NONE", decl)
        self.assertNotIn("NAME_None", decl)
        self.assertNotEqual(decl, "const TCHAR* SkyguardLoadoutDisplayName(INDEX_NONE);")

    def test_contract_does_not_retune_harbor(self) -> None:
        region = free_function_region(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertEqual(standalone_harbor_clocks(region), [])
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", region)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", region)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_display_name_declaration(region)
        lowered = region.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{DISPLAY_NAME_DECLARATION} region contains {banned}; "
                "Apache CPG loadout display-name declaration only, not Yak",
            )
            self.assertNotIn(banned, decl.lower())
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", region)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", region)

    def test_contract_is_display_name_declaration_only(self) -> None:
        region = free_function_region(origin_main_header())
        decls = free_function_declarations(region)
        required = [d for d in decls if "SkyguardLoadoutDisplayName" in d]
        self.assertEqual(required, [DISPLAY_NAME_DECLARATION])
        self.assertEqual(
            require_display_name_declaration(region),
            DISPLAY_NAME_DECLARATION,
        )
        for token in SPEC_DEFAULT_TOKENS:
            self.assertNotIn(token, region)
        for token in ENUM_TOKENS:
            self.assertNotIn(token, region)
        for token in CPP_TABLE_TOKENS:
            self.assertNotIn(token, region)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertEqual(standalone_harbor_clocks(region), [])
        self.assertNotIn("Rifle", region)
        self.assertNotIn("Igla", region)
        self.assertNotIn("Yak", region)
        self.assertNotIn("INDEX_NONE", region)
        self.assertNotEqual(required, ["Rifle", "Igla"])
        only_display = f"{DISPLAY_NAME_DECLARATION}\n"
        self.assertEqual(
            require_display_name_declaration(only_display),
            DISPLAY_NAME_DECLARATION,
        )
        self.assertEqual(
            free_function_declarations(only_display),
            [DISPLAY_NAME_DECLARATION],
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
