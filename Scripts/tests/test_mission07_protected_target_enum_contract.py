from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission07IntegrationDirector.h"
# Leftover #56–#64 plus Mission 07 production sources.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardMission07IntegrationDirector.h",
    "SkyguardMission07IntegrationDirector.cpp",
    "SkyguardMission07IntegrationDirectorTests.cpp",
    "SkyguardMission07IntegrationTests.cpp",
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
# Isolated-test drafts #107–#221 and newer stay off this lane.
# Runtime defaults (#221), search-track (#219), and search-sector (#218)
# are sibling Mission 07 contracts.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission07_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
)
# Apache CPG escort categories. Not Yak-52 intercept targets.
LIVE_TARGETS = [
    "NavigationStation",
    "FishingFleet",
]
# Field defaults (#221), search-track (#219), search-sector (#218),
# readiness (bYakRuntimeReady), and wave state stay unlocked.
SIBLING_TYPES = (
    "FSkyguardMission07ProtectedTargetRuntime",
    "FSkyguardSearchTrackRuntime",
    "FSkyguardMission07IntegrationReadiness",
    "ESkyguardSearchSector",
    "ESkyguardMission07WaveState",
)
SIBLING_DEFAULT_TOKENS = (
    "TrackId",
    "bClassifiedFalse",
    "NAME_None",
    "bYakRuntimeReady",
    "Integrity",
    "bDestroyed",
    "SectorA",
    "SectorB",
    "Intercept",
    "Briefing",
    "Searching",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
    "Completed",
    "Failed",
)
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


class Mission07ProtectedTargetEnumContractTests(unittest.TestCase):
    def test_protected_target_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardMission07ProtectedTarget : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardMission07ProtectedTarget",
            )
        self.assertIn("ESkyguardMission07ProtectedTarget", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission07ProtectedTarget",
        )
        self.assertEqual(enumerators, LIVE_TARGETS)
        self.assertEqual(
            enumerators,
            [
                "NavigationStation",
                "FishingFleet",
            ],
        )
        self.assertEqual(len(enumerators), 2, enumerators)
        body = enum_body(header, "ESkyguardMission07ProtectedTarget")
        for name in LIVE_TARGETS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_protected_target_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission07ProtectedTarget",
        )
        body = enum_body(header, "ESkyguardMission07ProtectedTarget")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_protected_target_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMission07ProtectedTarget",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_protected_target_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMission07ProtectedTarget")
        self.assertIn("NavigationStation", body)
        self.assertIn("FishingFleet", body)
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
            "ESkyguardMission07ProtectedTarget",
        )
        self.assertEqual(enumerators, LIVE_TARGETS)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

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
