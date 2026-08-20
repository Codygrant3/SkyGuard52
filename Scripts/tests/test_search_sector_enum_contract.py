from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission07IntegrationDirector.h"
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
LOCKED_SCRIPTS = (
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
)
# Apache CPG night-search sensor sectors. Not Yak-52 intercept sectors.
LIVE_SECTORS = [
    "SectorA",
    "SectorB",
    "Intercept",
]
SIBLING_TYPES = (
    "FSkyguardSearchTrackRuntime",
    "FSkyguardMission07IntegrationReadiness",
    "FSkyguardMission07ProtectedTargetRuntime",
    "ESkyguardMission07WaveState",
    "ESkyguardMission07ProtectedTarget",
)
SIBLING_DEFAULT_TOKENS = (
    "TrackId",
    "bClassifiedFalse",
    "NAME_None",
    "bYakRuntimeReady",
    "Integrity",
    "bDestroyed",
    "NavigationStation",
    "FishingFleet",
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


class SearchSectorEnumContractTests(unittest.TestCase):
    def test_search_sector_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardSearchSector : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardSearchSector",
            )
        self.assertIn("ESkyguardSearchSector", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardSearchSector")
        self.assertEqual(enumerators, LIVE_SECTORS)
        self.assertEqual(
            enumerators,
            [
                "SectorA",
                "SectorB",
                "Intercept",
            ],
        )
        self.assertEqual(len(enumerators), 3, enumerators)
        body = enum_body(header, "ESkyguardSearchSector")
        for name in LIVE_SECTORS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_search_sector_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardSearchSector")
        body = enum_body(header, "ESkyguardSearchSector")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_search_sector_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardSearchSector",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_search_sector_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardSearchSector")
        self.assertIn("SectorA", body)
        self.assertIn("Intercept", body)
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
        enumerators = enum_enumerators(header, "ESkyguardSearchSector")
        self.assertEqual(enumerators, LIVE_SECTORS)
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
