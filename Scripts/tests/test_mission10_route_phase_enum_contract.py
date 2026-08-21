from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission10IntegrationDirector.h"
# Leftover #56–#64 plus Mission 10 / Last Flight production sources.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
    "SkyguardMission10IntegrationDirectorTests.cpp",
    "SkyguardMission10IntegrationTests.cpp",
    "SkyguardLastFlightBoss.h",
    "SkyguardLastFlightBoss.cpp",
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
# Isolated-test drafts #107–#229 and newer stay off this lane.
# Protected-group (#220) and protected-runtime (#216) are sibling Mission 10 contracts.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
)
# Apache CPG finale route phases. Not Yak-52 intercept stages.
LIVE_PHASES = [
    "Briefing",
    "Highway",
    "FerryTerminal",
    "EvacuationShip",
    "BossEngaged",
    "Completed",
    "Failed",
]
# Field defaults (#216), protected-group (#220), readiness (bYakRuntimeReady),
# and Last Flight Igla/rifle methods stay unlocked.
SIBLING_TYPES = (
    "FSkyguardMission10ProtectedRuntime",
    "ESkyguardMission10ProtectedGroup",
    "FSkyguardMission10IntegrationReadiness",
    "ESkyguardLastFlightStage",
)
# Tokens that must not appear inside the route-phase enum body.
# FerryTerminal / EvacuationShip / Highway stay locked here as route phases,
# not as ProtectedGroup or LastFlightStage members.
SIBLING_DEFAULT_TOKENS = (
    "Convoy",
    "Integrity",
    "bDestroyed",
    "Group =",
    "bYakRuntimeReady",
    "bProtectedGroupsReady",
    "bLastFlightReady",
    "NAME_None",
    "INDEX_NONE",
    "DisabledDescent",
    "Defeated",
    "OpenFirstIglaWindow",
    "OpenFinalIglaWindow",
    "ArmCommandCoreRiflePath",
    "FireIgla",
    "FireRifle",
)
PROTECTED_GROUP_ORDER = [
    "Convoy",
    "FerryTerminal",
    "EvacuationShip",
]
LAST_FLIGHT_ORDER = [
    "Highway",
    "Terminal",
    "EvacuationShip",
    "DisabledDescent",
    "Defeated",
]
HARBOR_TUNING = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
    "40.f",
    "80.f",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{name} is missing from origin/main:Source/Skyguard52/{name}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def enum_body(header: str, enum_name: str) -> str:
    marker = f"enum class {enum_name}"
    if marker not in header:
        raise AssertionError(
            f"{enum_name} is missing from origin/main:Source/Skyguard52/{HEADER_NAME}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b",
        enum_body(header, enum_name),
        re.M,
    )


class Mission10RoutePhaseEnumContractTests(unittest.TestCase):
    def test_route_phase_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardMission10RoutePhase : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardMission10RoutePhase",
            )
        self.assertIn("ESkyguardMission10RoutePhase", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10RoutePhase",
        )
        self.assertEqual(enumerators, LIVE_PHASES)
        self.assertEqual(
            enumerators,
            [
                "Briefing",
                "Highway",
                "FerryTerminal",
                "EvacuationShip",
                "BossEngaged",
                "Completed",
                "Failed",
            ],
        )
        self.assertEqual(len(enumerators), 7, enumerators)
        body = enum_body(header, "ESkyguardMission10RoutePhase")
        for name in LIVE_PHASES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
        self.assertNotEqual(enumerators, PROTECTED_GROUP_ORDER)
        self.assertNotEqual(enumerators, LAST_FLIGHT_ORDER)

    def test_route_phase_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10RoutePhase",
        )
        body = enum_body(header, "ESkyguardMission10RoutePhase")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_route_phase_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMission10RoutePhase",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_route_phase_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMission10RoutePhase")
        self.assertIn("Briefing", body)
        self.assertIn("Failed", body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in SIBLING_DEFAULT_TOKENS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10RoutePhase",
        )
        self.assertEqual(enumerators, LIVE_PHASES)
        self.assertNotIn("Convoy", enumerators)
        self.assertNotIn("Terminal", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(enumerators, PROTECTED_GROUP_ORDER)
        self.assertNotEqual(enumerators, LAST_FLIGHT_ORDER)

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
