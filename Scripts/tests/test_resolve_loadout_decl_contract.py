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
# ResolveLoadout declaration-presence contract.
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
# #253 in-struct Balanced defaults, #262 slot helpers, #263 display
# name, leftover #114/#154 loadout enum contract, leftover theater-kit
# #59 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_loadout_slot_helpers_contract.py",
    "Scripts/tests/test_loadout_display_name_contract.py",
    "Scripts/tests/test_gunship_types_loadout_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Header free-function declaration after FSkyguardLoadoutSpec.
# Not the .cpp ResolveLoadout table / magazine counts.
RESOLVE_DECLARATION = (
    "FSkyguardLoadoutSpec SkyguardResolveLoadout(ESkyguardLoadout Loadout);"
)
# In-flight / sibling helpers stay unlocked. Presence is documentary
# only — this contract must still pass if they are absent.
SIBLING_DECLARATIONS = (
    "ESkyguardLoadout SkyguardLoadoutFromSlot(int32 Slot);",
    "int32 SkyguardLoadoutSlot(ESkyguardLoadout Loadout);",
    "const TCHAR* SkyguardLoadoutDisplayName(ESkyguardLoadout Loadout);",
)
# #253 Balanced in-struct defaults stay in the struct body.
SPEC_DEFAULT_TOKENS = (
    "ESkyguardLoadout Loadout = ESkyguardLoadout::Balanced;",
    "ESkyguardGunshipWeapon StartingStation = ESkyguardGunshipWeapon::Cannon;",
    "int32 CannonMagazineSize = SkyguardApacheCpgFeel::CannonMagazineSize;",
    "int32 CannonReserve = SkyguardApacheCpgFeel::CannonReserve;",
    "int32 RocketMagazineSize = SkyguardApacheCpgFeel::RocketMagazineSize;",
    "int32 RocketReserve = SkyguardApacheCpgFeel::RocketReserve;",
    "int32 GuidedMagazineSize = SkyguardApacheCpgFeel::GuidedMagazineSize;",
    "int32 GuidedReserve = SkyguardApacheCpgFeel::GuidedReserve;",
    "int32 FlareCount = 6;",
    "float HullIntegrity = 140.f;",
    "PlaystyleLine",
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
# .cpp ResolveLoadout tables stay unlocked. Do not invent magazine counts.
CPP_TABLE_TOKENS = (
    "switch (Loadout)",
    "case ESkyguardLoadout::",
    "Hellfire station",
    "Hydra station",
    "extra guided missiles",
    "extra rockets",
    "extra cannon and flares",
    "CannonMagazineSize = 24",
    "CannonMagazineSize = 40",
    "FlareCount = 8",
    "FlareCount = 5",
    "FlareCount = 10",
    "HullIntegrity = 120.f",
    "HullIntegrity = 170.f",
    "return ",
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
HARBOR_TUNING = ("40.f", "80.f")


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
    """Free-function declarations after FSkyguardLoadoutSpec, not the body."""
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
                clip = re.search(
                    r"\n(?:UENUM|USTRUCT|UCLASS|enum class|struct |class |"
                    r"namespace )",
                    after,
                )
                if clip is not None:
                    after = after[: clip.start()]
                return after
    raise AssertionError(
        f"{STRUCT_NAME} body is unclosed in origin/main:{HEADER_PATH}"
    )


def free_function_declarations(region: str) -> list[str]:
    decls: list[str] = []
    for raw in region.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("/*"):
            continue
        if "(" in line and line.endswith(";"):
            decls.append(line)
    return decls


def require_resolve_declaration(region: str) -> str:
    for decl in free_function_declarations(region):
        if decl == RESOLVE_DECLARATION:
            return decl
    raise AssertionError(
        f"{RESOLVE_DECLARATION} is missing from "
        f"origin/main:{HEADER_PATH} after {STRUCT_NAME}"
    )


def standalone_harbor_clocks(region: str) -> list[str]:
    found: list[str] = []
    if re.search(r"(?<![\d.])40\.f", region):
        found.append("40.f")
    if re.search(r"(?<![\d.])80\.f", region):
        found.append("80.f")
    return found


class ResolveLoadoutDeclContractTests(unittest.TestCase):
    def test_resolve_loadout_declaration_exists(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_resolve_declaration(region)
        self.assertEqual(decl, RESOLVE_DECLARATION)
        self.assertIn(RESOLVE_DECLARATION, region)
        self.assertIn(RESOLVE_DECLARATION, free_function_declarations(region))

    def test_missing_declaration_fails_closed(self) -> None:
        region = "\n".join(SIBLING_DECLARATIONS) + "\n"
        with self.assertRaises(AssertionError) as raised:
            require_resolve_declaration(region)
        self.assertIn("SkyguardResolveLoadout", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_loadout_spec_anchor_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            free_function_region(
                "struct FSkyguardUnrelated\n{\n};\n"
                f"{RESOLVE_DECLARATION}\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_inside_struct_body_fails_closed(self) -> None:
        header = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{RESOLVE_DECLARATION}\n"
            "};\n"
            "UENUM(BlueprintType)\n"
            "enum class ESkyguardClimaxKind : uint8\n"
            "{\n"
            "};\n"
        )
        region = free_function_region(header)
        with self.assertRaises(AssertionError) as raised:
            require_resolve_declaration(region)
        self.assertIn("SkyguardResolveLoadout", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(RESOLVE_DECLARATION, region)

    def test_contract_does_not_require_sibling_helper_declarations(self) -> None:
        region = f"{RESOLVE_DECLARATION}\n"
        self.assertEqual(
            require_resolve_declaration(region),
            RESOLVE_DECLARATION,
        )
        decls = free_function_declarations(region)
        self.assertEqual(decls, [RESOLVE_DECLARATION])
        for sibling in SIBLING_DECLARATIONS:
            self.assertNotIn(sibling, decls)
            self.assertNotIn(sibling, region)
        self.assertNotIn("SkyguardLoadoutFromSlot", decls)
        self.assertNotIn("SkyguardLoadoutSlot", decls)
        self.assertNotIn("SkyguardLoadoutDisplayName", decls)

    def test_contract_does_not_relock_loadout_spec_defaults(self) -> None:
        region = free_function_region(origin_main_header())
        for token in SPEC_DEFAULT_TOKENS:
            self.assertNotIn(token, region)
        self.assertNotIn("struct FSkyguardLoadoutSpec", region)
        self.assertNotIn("StartingStation", region)
        self.assertNotIn("CannonMagazineSize", region)
        self.assertNotIn("USTRUCT(", region)
        self.assertNotIn("GENERATED_BODY()", region)
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
        self.assertNotIn("ESkyguardLoadout::Balanced", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Search", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Detect", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Track", region)
        self.assertNotIn("ESkyguardGuidedLockPhase::Lock", region)
        self.assertNotIn("ESkyguardCpgSightMode::Helmet", region)
        self.assertNotIn("TargetingSensor", region)

    def test_contract_does_not_lock_resolve_tables_or_return_values(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_resolve_declaration(region)
        decls = free_function_declarations(region)
        for token in CPP_TABLE_TOKENS:
            self.assertNotIn(token, region)
            self.assertNotIn(token, decls)
            self.assertNotIn(token, decl)
        self.assertTrue(decl.endswith(";"), decl)
        self.assertNotIn("return ", decl)
        self.assertNotIn("{", decl)
        self.assertNotIn("}", decl)
        self.assertNotIn("SkyguardGunshipTypes.cpp", region)
        self.assertNotIn("const ESkyguardLoadout Loadout", region)

    def test_declaration_does_not_invent_index_none(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_resolve_declaration(region)
        for token in INVENTED:
            self.assertNotIn(token, region)
            self.assertNotIn(token, decl)
        self.assertNotIn("INDEX_NONE", decl)
        self.assertNotIn("NAME_None", decl)
        self.assertNotIn("return INDEX_NONE", region)
        self.assertNotEqual(
            decl,
            "FSkyguardLoadoutSpec SkyguardResolveLoadout(INDEX_NONE);",
        )

    def test_contract_does_not_retune_harbor(self) -> None:
        region = free_function_region(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, region)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, region)
        self.assertNotIn("40.f, 80.f", region)
        self.assertNotIn(HARBOR_INCOMING, region)
        self.assertEqual(standalone_harbor_clocks(region), [])
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", region)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", region)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        region = free_function_region(origin_main_header())
        decl = require_resolve_declaration(region)
        lowered = region.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{RESOLVE_DECLARATION} region contains {banned}; "
                "Apache CPG ResolveLoadout declaration only, not Yak",
            )
            self.assertNotIn(banned, decl.lower())
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", region)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", region)
        self.assertNotIn("FireIgla", region)
        self.assertNotIn("FireRifle", region)
        self.assertNotIn("YakSpawnLocation", region)
        self.assertNotIn("bYakRuntimeReady", region)

    def test_contract_is_resolve_loadout_declaration_only(self) -> None:
        region = free_function_region(origin_main_header())
        decls = free_function_declarations(region)
        required = [d for d in decls if "SkyguardResolveLoadout" in d]
        self.assertEqual(required, [RESOLVE_DECLARATION])
        self.assertEqual(
            require_resolve_declaration(region),
            RESOLVE_DECLARATION,
        )
        for sibling in SIBLING_DECLARATIONS:
            self.assertNotIn(sibling, required)
        for token in SPEC_DEFAULT_TOKENS:
            self.assertNotIn(token, region)
        for token in ENUM_TOKENS:
            self.assertNotIn(token, region)
        for token in CPP_TABLE_TOKENS:
            self.assertNotIn(token, region)
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
        self.assertNotEqual(required, ["Rifle", "Igla"])
        only_resolve = f"{RESOLVE_DECLARATION}\n"
        self.assertEqual(
            require_resolve_declaration(only_resolve),
            RESOLVE_DECLARATION,
        )
        self.assertEqual(
            free_function_declarations(only_resolve),
            [RESOLVE_DECLARATION],
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
