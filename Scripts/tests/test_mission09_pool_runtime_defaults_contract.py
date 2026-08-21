from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission09IntegrationDirector.h"
STRUCT_NAME = "FSkyguardMission09PoolRuntime"
# Leftover #56–#64 plus Mission 09 production sources (merged #106).
# This lane only adds an isolated Python contract.
LOCKED = {
    "SkyguardMission09IntegrationDirector.h",
    "SkyguardMission09IntegrationDirector.cpp",
    "SkyguardMission09IntegrationDirectorTests.cpp",
    "SkyguardMission09IntegrationTests.cpp",
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
# Isolated-test drafts #107–#239 and newer stay off this lane.
# Pool-budget defaults (in flight), wave-state (#238), Iron Rain
# maneuver (#239), and protected-target (#225/#228) are siblings.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
)
# Apache CPG saturation-attack pool occupancy. Not Harbor 40/80 clocks.
# Lock in-struct defaults only — not FSkyguardMission09PoolBudget.
PUBLIC_FIELDS = (
    "int32 Available = 48;",
    "int32 Active = 0;",
    "int32 PeakActive = 0;",
    "int32 Recycled = 0;",
)
IN_CLASS_DEFAULTS = {
    "Available": "48",
    "Active": "0",
    "PeakActive": "0",
    "Recycled": "0",
}
# Pool budget (MaxActiveThreats/PoolCapacity/MaxActiveDecoys/
# MaxSimultaneousExplosions), wave state, protected-target
# enum/runtime, and readiness (bYakRuntimeReady) stay unlocked.
TYPES_NOT_LOCKED = (
    "struct FSkyguardMission09PoolBudget",
    "struct FSkyguardMission09ProtectedTargetRuntime",
    "struct FSkyguardMission09IntegrationReadiness",
    "enum class ESkyguardMission09WaveState",
    "enum class ESkyguardMission09ProtectedTarget",
    "ESkyguardIronRainManeuver",
    "bYakRuntimeReady",
    "int32 MaxActiveThreats",
    "int32 PoolCapacity",
    "int32 MaxActiveDecoys",
    "int32 MaxSimultaneousExplosions",
    "MetropolitanSkyline",
    "CoastalPowerStation",
    "MajorBridge",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "TEXT(",
    "FString()",
    'TEXT("")',
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def pool_runtime_body(header: str) -> str:
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
            r"int32\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class Mission09PoolRuntimeDefaultsContractTests(unittest.TestCase):
    def test_pool_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", pool_runtime_body(header))

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            pool_runtime_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = pool_runtime_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            4,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = pool_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("Available"), "48")
        self.assertEqual(defaults.get("Active"), "0")
        self.assertEqual(defaults.get("PeakActive"), "0")
        self.assertEqual(defaults.get("Recycled"), "0")
        self.assertIn("int32 Available = 48;", body)
        self.assertIn("int32 Active = 0;", body)
        self.assertIn("int32 PeakActive = 0;", body)
        self.assertIn("int32 Recycled = 0;", body)
        self.assertNotIn("Available = 0;", body)
        self.assertNotIn("Available = INDEX_NONE", body)
        self.assertNotIn("Active = INDEX_NONE", body)
        self.assertNotIn("PeakActive = INDEX_NONE", body)
        self.assertNotIn("Recycled = INDEX_NONE", body)
        self.assertEqual(len(defaults), 4, defaults)
        self.assertNotIn("Error", defaults)
        self.assertNotIn("MaxActiveThreats", defaults)
        self.assertNotIn("PoolCapacity", defaults)
        self.assertNotIn("MaxActiveDecoys", defaults)
        self.assertNotIn("MaxSimultaneousExplosions", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = pool_runtime_body(origin_main_header())
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

    def test_contract_does_not_lock_pool_budget_wave_or_protected(self) -> None:
        body = pool_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("FSkyguardMission09PoolBudget", body)
        self.assertNotIn("FSkyguardMission09ProtectedTargetRuntime", body)
        self.assertNotIn("FSkyguardMission09IntegrationReadiness", body)
        self.assertNotIn("ESkyguardMission09WaveState", body)
        self.assertNotIn("enum class ESkyguardMission09ProtectedTarget", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("MetropolitanSkyline", body)
        self.assertNotIn("CoastalPowerStation", body)
        self.assertNotIn("MajorBridge", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = pool_runtime_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = pool_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "pool-runtime defaults are Apache CPG saturation occupancy, "
                "not Yak",
            )
            self.assertNotIn(banned, defaults)

    def test_contract_is_pool_runtime_defaults_only(self) -> None:
        body = pool_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("int32 Available = 48;", body)
        self.assertIn("int32 Active = 0;", body)
        self.assertIn("int32 PeakActive = 0;", body)
        self.assertIn("int32 Recycled = 0;", body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotIn("MaxActiveThreats", defaults)
        self.assertNotIn("PoolCapacity", defaults)
        self.assertNotIn("MaxActiveDecoys", defaults)
        self.assertNotIn("MaxSimultaneousExplosions", defaults)
        self.assertEqual(len(defaults), 4, defaults)

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
