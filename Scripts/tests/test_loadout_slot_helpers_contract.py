from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardGunshipTypes.h"
STRUCT_NAME = "FSkyguardLoadoutSpec"
# Declaration presence only. Do not invent INDEX_NONE or return values.
# Do not lock SkyguardResolveLoadout tables or DisplayName.
FROM_SLOT = "ESkyguardLoadout SkyguardLoadoutFromSlot(int32 Slot);"
SLOT_OF = "int32 SkyguardLoadoutSlot(ESkyguardLoadout Loadout);"
LOCKED_DECLARATIONS = (
    FROM_SLOT,
    SLOT_OF,
)
# Leftover #56–#64 plus GunshipTypes production sources and leftover
# #8/#114/#154 loadout files. This lane only adds an isolated Python
# slot-helper declaration contract. Stay off leftover Harbor #6/#8/#9.
LOCKED = {
    "SkyguardGunshipTypes.h",
    "SkyguardGunshipTypes.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardCpgLoadoutSlot34Tests.cpp",
    "SkyguardCpgDebriefLoadoutTests.cpp",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgDebrief.h",
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
# Isolated-test drafts #107–#253 and newer stay off this lane.
# #253 in-struct Balanced defaults, #149/#154 enums, leftover theater-kit
# #59, and storm-rain Calls/Stations stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_gunship_types_loadout_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_stations_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py",
)
# Neighbors in the same free-function block. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "FSkyguardLoadoutSpec SkyguardResolveLoadout(ESkyguardLoadout Loadout);",
    "const TCHAR* SkyguardLoadoutDisplayName(ESkyguardLoadout Loadout);",
)
# #253 Balanced in-struct defaults stay unlocked. Parse after the struct.
DEFAULTS_NOT_LOCKED = (
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
# #154 loadout / guided-lock-phase enums and #149 weapon enums stay
# unlocked. Type names in the two helper signatures are not enumerator locks.
ENUMS_NOT_LOCKED = (
    "enum class ESkyguardLoadout",
    "enum class ESkyguardGuidedLockPhase",
    "enum class ESkyguardGunshipWeapon",
    "enum class ESkyguardCpgSightMode",
)
LOADOUTS_NOT_LOCKED = (
    "Balanced",
    "AntiArmor",
    "RocketHeavy",
    "Intercept",
)
WEAPON_ENUMERATORS_NOT_LOCKED = (
    "Cannon",
    "Rockets",
    "GuidedMissile",
)
LOCK_PHASES_NOT_LOCKED = (
    "Search",
    "Detect",
    "Track",
    "Lock",
)
# .cpp tables / invented bodies stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
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
    "bYakRuntimeReady",
    "FSkyguardMission0NIntegrationReadiness",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
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
            f"{HEADER_PATH} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def loadout_spec_after(header: str) -> str:
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


def require_declaration(region: str, declaration: str) -> str:
    if declaration not in region:
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"after {STRUCT_NAME}"
        )
    return declaration


class LoadoutSlotHelpersContractTests(unittest.TestCase):
    def test_loadout_spec_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        after = loadout_spec_after(header)
        self.assertIn(FROM_SLOT, after)
        self.assertIn(SLOT_OF, after)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            loadout_spec_after("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_from_slot_declaration_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                "int32 SkyguardLoadoutSlot(ESkyguardLoadout Loadout);\n",
                FROM_SLOT,
            )
        self.assertIn("SkyguardLoadoutFromSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_slot_declaration_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                "ESkyguardLoadout SkyguardLoadoutFromSlot(int32 Slot);\n",
                SLOT_OF,
            )
        self.assertIn("SkyguardLoadoutSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_helper_declarations_match_origin_main_in_order(self) -> None:
        after = loadout_spec_after(origin_main_header())
        positions = [after.index(item) for item in LOCKED_DECLARATIONS]
        self.assertEqual(positions, sorted(positions), LOCKED_DECLARATIONS)
        for declaration in LOCKED_DECLARATIONS:
            self.assertEqual(require_declaration(after, declaration), declaration)
            self.assertIn(declaration, after)
        self.assertEqual(after.count(FROM_SLOT), 1)
        self.assertEqual(after.count(SLOT_OF), 1)
        self.assertNotIn("INDEX_NONE", FROM_SLOT)
        self.assertNotIn("INDEX_NONE", SLOT_OF)

    def test_declarations_do_not_invent_index_none_or_return_values(self) -> None:
        after = loadout_spec_after(origin_main_header())
        for declaration in LOCKED_DECLARATIONS:
            self.assertTrue(declaration.endswith(";"), declaration)
            self.assertNotIn("return ", declaration)
            self.assertNotIn("INDEX_NONE", declaration)
            self.assertNotIn("NAME_None", declaration)
            self.assertNotIn("{", declaration)
            self.assertNotIn("}", declaration)
        self.assertNotIn("return ", after)
        self.assertNotIn("INDEX_NONE", after)
        self.assertNotIn("NAME_None", after)
        self.assertNotIn("return INDEX_NONE", after)
        self.assertNotIn("return 0", after)
        self.assertNotIn("return -1", after)
        self.assertNotIn("= INDEX_NONE", after)
        self.assertNotIn("{", after)
        self.assertNotIn("}", after)

    def test_contract_does_not_relock_loadout_spec_defaults(self) -> None:
        after = loadout_spec_after(origin_main_header())
        for token in DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, after)
        self.assertNotIn("FlareCount = 6;", after)
        self.assertNotIn("HullIntegrity = 140.f;", after)
        self.assertNotIn("StartingStation", after)
        self.assertNotIn("PlaystyleLine", after)
        self.assertNotIn("CannonMagazineSize", after)
        self.assertNotIn("USTRUCT(", after)
        self.assertNotIn("GENERATED_BODY()", after)

    def test_contract_does_not_lock_resolve_or_display_name(self) -> None:
        helpers_only = f"{FROM_SLOT}\n{SLOT_OF}\n"
        for declaration in LOCKED_DECLARATIONS:
            self.assertEqual(
                require_declaration(helpers_only, declaration),
                declaration,
            )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
            self.assertNotIn(neighbor, helpers_only)
        self.assertNotIn("SkyguardResolveLoadout", LOCKED_DECLARATIONS)
        self.assertNotIn("SkyguardLoadoutDisplayName", LOCKED_DECLARATIONS)
        self.assertNotIn("SkyguardResolveLoadout", helpers_only)
        self.assertNotIn("SkyguardLoadoutDisplayName", helpers_only)

    def test_contract_does_not_relock_loadout_weapon_or_lock_enums(self) -> None:
        after = loadout_spec_after(origin_main_header())
        for token in ENUMS_NOT_LOCKED:
            self.assertNotIn(token, after)
        self.assertNotIn("enum class", after)
        self.assertNotIn("UENUM(", after)
        for name in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardLoadout::{name}", after)
            self.assertNotIn(name, LOCKED_DECLARATIONS)
        for name in WEAPON_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardGunshipWeapon::{name}", after)
            self.assertNotIn(name, after)
        for name in LOCK_PHASES_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardGuidedLockPhase::{name}", after)
            self.assertNotIn(name, after)
        self.assertNotIn("ESkyguardGuidedLockPhase", after)
        self.assertNotIn("ESkyguardCpgSightMode", after)
        self.assertNotIn("ESkyguardGunshipWeapon", after)

    def test_contract_does_not_read_cpp_tables(self) -> None:
        after = loadout_spec_after(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, after)
        self.assertNotIn("SkyguardGunshipTypes.cpp", after)
        self.assertNotIn("const int32 Slot", after)
        self.assertNotIn("const ESkyguardLoadout Loadout", after)

    def test_contract_does_not_retune_harbor(self) -> None:
        after = loadout_spec_after(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, after)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, after)
        self.assertNotIn("40.f, 80.f", after)
        self.assertNotIn(HARBOR_INCOMING, after)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", after)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", after)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        after = loadout_spec_after(origin_main_header())
        self.assertNotIn("Rifle", after)
        self.assertNotIn("Igla", after)
        self.assertNotIn("Yak", after)
        self.assertNotEqual(LOCKED_DECLARATIONS, ("Rifle", "Igla"))
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", after)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", after)
        self.assertNotIn("FireIgla", after)
        self.assertNotIn("FireRifle", after)
        self.assertNotIn("YakSpawnLocation", after)

    def test_helpers_ban_igla_yak_rifle(self) -> None:
        after = loadout_spec_after(origin_main_header())
        lowered = after.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"loadout slot helpers contain {banned}; "
                "slot helpers are Apache CPG 30 mm / Hydra / Hellfire "
                "keys 1-4, not Yak",
            )
            self.assertNotIn(banned, FROM_SLOT.lower())
            self.assertNotIn(banned, SLOT_OF.lower())

    def test_contract_is_loadout_slot_helpers_only(self) -> None:
        header = origin_main_header()
        after = loadout_spec_after(header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (FROM_SLOT, SLOT_OF))
        for declaration in LOCKED_DECLARATIONS:
            self.assertEqual(require_declaration(after, declaration), declaration)
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        for token in DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, after)
        for token in ENUMS_NOT_LOCKED:
            self.assertNotIn(token, after)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, after)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, after)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, after)
        self.assertNotIn("40.f, 80.f", after)
        self.assertNotIn(HARBOR_INCOMING, after)
        self.assertNotIn("Rifle", after)
        self.assertNotIn("Igla", after)
        self.assertNotIn("Yak", after)
        self.assertNotIn("INDEX_NONE", after)
        self.assertNotIn("return ", after)
        self.assertNotIn("enum class", after)
        self.assertNotIn("PlaystyleLine", after)
        self.assertNotEqual(list(LOCKED_DECLARATIONS), ["Rifle", "Igla"])
        self.assertNotIn("SkyguardResolveLoadout", LOCKED_DECLARATIONS)
        self.assertNotIn("SkyguardLoadoutDisplayName", LOCKED_DECLARATIONS)

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
