from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardGunshipTypes.h"
STRUCT_NAME = "FSkyguardLoadoutSpec"
# Leftover #56–#64 plus GunshipTypes production sources and leftover
# #8/#114 loadout test files. This lane only adds an isolated Python
# defaults contract. Stay off leftover Harbor #8 debrief loadouts.
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
# Isolated-test drafts #107–#247 and newer stay off this lane.
# #149 weapon/sight enums, #154 loadout/lock-phase enums, leftover
# theater-kit #59, and in-flight day-sortie / storm-rain beat defaults
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
)
# Balanced in-struct initializers on FSkyguardLoadoutSpec itself.
# Not SkyguardResolveLoadout tables. GuidedMissile is the live CPG
# station name; do not restore player Igla. PlaystyleLine is split
# across two lines on origin/main; markers stay in order.
PUBLIC_FIELDS = (
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
    "const TCHAR* PlaystyleLine =",
    'TEXT("30 mm station, mixed cannon, rockets, missiles");',
)
IN_CLASS_DEFAULTS = {
    "Loadout": "ESkyguardLoadout::Balanced",
    "StartingStation": "ESkyguardGunshipWeapon::Cannon",
    "CannonMagazineSize": "SkyguardApacheCpgFeel::CannonMagazineSize",
    "CannonReserve": "SkyguardApacheCpgFeel::CannonReserve",
    "RocketMagazineSize": "SkyguardApacheCpgFeel::RocketMagazineSize",
    "RocketReserve": "SkyguardApacheCpgFeel::RocketReserve",
    "GuidedMagazineSize": "SkyguardApacheCpgFeel::GuidedMagazineSize",
    "GuidedReserve": "SkyguardApacheCpgFeel::GuidedReserve",
    "FlareCount": "6",
    "HullIntegrity": "140.f",
    "PlaystyleLine": (
        'TEXT("30 mm station, mixed cannon, rockets, missiles")'
    ),
}
# #154 loadout / guided-lock-phase enums and #149 weapon / sight-mode
# enums stay unlocked. ResolveLoadout tables stay in .cpp.
TYPES_NOT_LOCKED = (
    "enum class ESkyguardLoadout",
    "enum class ESkyguardGuidedLockPhase",
    "enum class ESkyguardGunshipWeapon",
    "enum class ESkyguardCpgSightMode",
    "SkyguardResolveLoadout",
    "SkyguardLoadoutFromSlot",
    "SkyguardLoadoutSlot",
    "SkyguardLoadoutDisplayName",
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
LOADOUTS_NOT_LOCKED = (
    "AntiArmor",
    "RocketHeavy",
    "Intercept",
)
WEAPON_ENUMERATORS_NOT_LOCKED = (
    "Rockets",
    "GuidedMissile",
)
LOCK_PHASES_NOT_LOCKED = (
    "Search",
    "Detect",
    "Track",
    "Lock",
)
SIGHT_MODES_NOT_LOCKED = (
    "Helmet",
    "TargetingSensor",
)
RESOLVE_TABLE_COPY = (
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
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "FString()",
)
BANNED = ("igla", "yak", "rifle")
# HullIntegrity = 140.f is Balanced integrity, not Harbor 40/80 clocks.
# Check IncomingRadar symbols and standalone 40.f / 80.f only.
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def loadout_spec_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardLoadout|ESkyguardGunshipWeapon|int32|float|"
            r"const TCHAR\*)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


def standalone_harbor_clocks(body: str) -> list[str]:
    found: list[str] = []
    if re.search(r"(?<![\d.])40\.f", body):
        found.append("40.f")
    if re.search(r"(?<![\d.])80\.f", body):
        found.append("80.f")
    return found


class LoadoutSpecDefaultsContractTests(unittest.TestCase):
    def test_loadout_spec_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = loadout_spec_body(header)
        self.assertIn("ESkyguardLoadout Loadout =", body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            loadout_spec_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = loadout_spec_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("Loadout"), "ESkyguardLoadout::Balanced")
        self.assertEqual(
            defaults.get("StartingStation"),
            "ESkyguardGunshipWeapon::Cannon",
        )
        self.assertEqual(
            defaults.get("CannonMagazineSize"),
            "SkyguardApacheCpgFeel::CannonMagazineSize",
        )
        self.assertEqual(
            defaults.get("CannonReserve"),
            "SkyguardApacheCpgFeel::CannonReserve",
        )
        self.assertEqual(
            defaults.get("RocketMagazineSize"),
            "SkyguardApacheCpgFeel::RocketMagazineSize",
        )
        self.assertEqual(
            defaults.get("RocketReserve"),
            "SkyguardApacheCpgFeel::RocketReserve",
        )
        self.assertEqual(
            defaults.get("GuidedMagazineSize"),
            "SkyguardApacheCpgFeel::GuidedMagazineSize",
        )
        self.assertEqual(
            defaults.get("GuidedReserve"),
            "SkyguardApacheCpgFeel::GuidedReserve",
        )
        self.assertEqual(defaults.get("FlareCount"), "6")
        self.assertEqual(defaults.get("HullIntegrity"), "140.f")
        self.assertEqual(
            defaults.get("PlaystyleLine"),
            'TEXT("30 mm station, mixed cannon, rockets, missiles")',
        )
        self.assertIn(
            "ESkyguardLoadout Loadout = ESkyguardLoadout::Balanced;",
            body,
        )
        self.assertIn(
            "ESkyguardGunshipWeapon StartingStation = "
            "ESkyguardGunshipWeapon::Cannon;",
            body,
        )
        self.assertIn(
            "int32 CannonMagazineSize = "
            "SkyguardApacheCpgFeel::CannonMagazineSize;",
            body,
        )
        self.assertIn(
            "int32 CannonReserve = SkyguardApacheCpgFeel::CannonReserve;",
            body,
        )
        self.assertIn(
            "int32 RocketMagazineSize = "
            "SkyguardApacheCpgFeel::RocketMagazineSize;",
            body,
        )
        self.assertIn(
            "int32 RocketReserve = SkyguardApacheCpgFeel::RocketReserve;",
            body,
        )
        self.assertIn(
            "int32 GuidedMagazineSize = "
            "SkyguardApacheCpgFeel::GuidedMagazineSize;",
            body,
        )
        self.assertIn(
            "int32 GuidedReserve = SkyguardApacheCpgFeel::GuidedReserve;",
            body,
        )
        self.assertIn("int32 FlareCount = 6;", body)
        self.assertIn("float HullIntegrity = 140.f;", body)
        compact = re.sub(r"\s+", " ", body)
        self.assertIn(
            "const TCHAR* PlaystyleLine = "
            'TEXT("30 mm station, mixed cannon, rockets, missiles");',
            compact,
        )
        self.assertNotIn("Loadout = INDEX_NONE", body)
        self.assertNotIn("StartingStation = INDEX_NONE", body)
        self.assertNotIn("CannonMagazineSize = INDEX_NONE", body)
        self.assertNotIn("FlareCount = INDEX_NONE", body)
        self.assertNotIn("HullIntegrity = INDEX_NONE", body)
        self.assertNotIn("PlaystyleLine = INDEX_NONE", body)
        self.assertEqual(len(defaults), 11, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_relock_loadout_weapon_or_sight_enums(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertNotIn("enum class ESkyguardLoadout", body)
        self.assertNotIn("enum class ESkyguardGuidedLockPhase", body)
        self.assertNotIn("enum class ESkyguardGunshipWeapon", body)
        self.assertNotIn("enum class ESkyguardCpgSightMode", body)
        self.assertIn("ESkyguardLoadout::Balanced", body)
        self.assertIn("ESkyguardGunshipWeapon::Cannon", body)
        for name in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
            self.assertNotIn(f"ESkyguardLoadout::{name}", body)
        for name in WEAPON_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardGunshipWeapon::{name}", body)
            self.assertNotIn(name, defaults)
        for name in LOCK_PHASES_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardGuidedLockPhase::{name}", body)
            self.assertNotIn(name, defaults)
        for name in SIGHT_MODES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
            self.assertNotIn(f"ESkyguardCpgSightMode::{name}", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("ESkyguardGuidedLockPhase", body)
        self.assertNotIn("ESkyguardCpgSightMode", body)

    def test_contract_does_not_lock_resolve_loadout_tables(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("SkyguardResolveLoadout", body)
        self.assertNotIn("SkyguardLoadoutFromSlot", body)
        self.assertNotIn("SkyguardLoadoutSlot", body)
        self.assertNotIn("SkyguardLoadoutDisplayName", body)
        for token in RESOLVE_TABLE_COPY:
            self.assertNotIn(token, body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", body)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = loadout_spec_body(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertEqual(standalone_harbor_clocks(body), [])
        # 140.f is Balanced hull integrity, not IncomingRadar 40.
        self.assertIn("float HullIntegrity = 140.f;", body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "loadout-spec defaults are Apache CPG Balanced 30 mm / "
                "Hydra / Hellfire stations, not Yak",
            )
            self.assertNotIn(banned, defaults)
            self.assertNotIn(banned, defaults.values())

    def test_contract_is_loadout_spec_defaults_only(self) -> None:
        body = loadout_spec_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardLoadout Loadout = ESkyguardLoadout::Balanced;",
            body,
        )
        self.assertIn(
            "ESkyguardGunshipWeapon StartingStation = "
            "ESkyguardGunshipWeapon::Cannon;",
            body,
        )
        self.assertIn("int32 FlareCount = 6;", body)
        self.assertIn("float HullIntegrity = 140.f;", body)
        compact = re.sub(r"\s+", " ", body)
        self.assertIn(
            "const TCHAR* PlaystyleLine = "
            'TEXT("30 mm station, mixed cannon, rockets, missiles");',
            compact,
        )
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in RESOLVE_TABLE_COPY:
            self.assertNotIn(token, body)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertEqual(standalone_harbor_clocks(body), [])
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotIn("SkyguardResolveLoadout", defaults)
        self.assertNotIn("AntiArmor", defaults)
        self.assertEqual(len(defaults), 11, defaults)
        self.assertEqual(
            defaults.get("StartingStation"),
            "ESkyguardGunshipWeapon::Cannon",
        )
        self.assertNotEqual(
            defaults.get("StartingStation"),
            "ESkyguardGunshipWeapon::Igla",
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
