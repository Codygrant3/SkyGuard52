from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission10IntegrationDirector.h"
# Leftover #56–#64 plus Mission 10 / Last Flight production sources.
# This lane only adds an isolated Python contract.
LOCKED = {
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
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
# Isolated-test drafts #107–#219 and newer stay off this lane.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
)
# Apache CPG escort categories. Not Yak-52 intercept groups.
LIVE_GROUPS = [
    "Convoy",
    "FerryTerminal",
    "EvacuationShip",
]
SIBLING_TYPES = (
    "FSkyguardMission10ProtectedRuntime",
    "FSkyguardMission10IntegrationReadiness",
    "ESkyguardMission10RoutePhase",
    "ESkyguardLastFlightStage",
)
# Tokens that must not appear inside the protected-group enum body.
# FerryTerminal / EvacuationShip stay locked here as group types, not as
# RoutePhase or LastFlightStage members.
SIBLING_DEFAULT_TOKENS = (
    "Integrity",
    "bDestroyed",
    "Group =",
    "bYakRuntimeReady",
    "bProtectedGroupsReady",
    "bLastFlightReady",
    "NAME_None",
    "INDEX_NONE",
    "Briefing",
    "Highway",
    "BossEngaged",
    "Completed",
    "Failed",
    "DisabledDescent",
    "Defeated",
    "OpenFirstIglaWindow",
    "OpenFinalIglaWindow",
    "ArmCommandCoreRiflePath",
    "FireIgla",
    "FireRifle",
)
ROUTE_PHASE_ORDER = [
    "Briefing",
    "Highway",
    "FerryTerminal",
    "EvacuationShip",
    "BossEngaged",
    "Completed",
    "Failed",
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


class Mission10ProtectedGroupEnumContractTests(unittest.TestCase):
    def test_protected_group_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardMission10ProtectedGroup : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardMission10ProtectedGroup",
            )
        self.assertIn("ESkyguardMission10ProtectedGroup", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10ProtectedGroup",
        )
        self.assertEqual(enumerators, LIVE_GROUPS)
        self.assertEqual(
            enumerators,
            [
                "Convoy",
                "FerryTerminal",
                "EvacuationShip",
            ],
        )
        self.assertEqual(len(enumerators), 3, enumerators)
        body = enum_body(header, "ESkyguardMission10ProtectedGroup")
        for name in LIVE_GROUPS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
        self.assertNotEqual(enumerators, ROUTE_PHASE_ORDER)
        self.assertNotEqual(enumerators, LAST_FLIGHT_ORDER)

    def test_protected_group_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10ProtectedGroup",
        )
        body = enum_body(header, "ESkyguardMission10ProtectedGroup")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_protected_group_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMission10ProtectedGroup",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_protected_group_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMission10ProtectedGroup")
        self.assertIn("Convoy", body)
        self.assertIn("EvacuationShip", body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in SIBLING_DEFAULT_TOKENS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission10ProtectedGroup",
        )
        self.assertEqual(enumerators, LIVE_GROUPS)
        self.assertNotIn("Terminal", enumerators)
        self.assertNotIn("Highway", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(enumerators, ROUTE_PHASE_ORDER)
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
