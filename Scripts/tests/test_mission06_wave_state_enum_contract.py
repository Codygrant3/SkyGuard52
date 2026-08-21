from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission06IntegrationDirector.h"
# Leftover #56–#64 plus Mission 06 production sources and merged #105.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardMission06IntegrationDirector.h",
    "SkyguardMission06IntegrationDirector.cpp",
    "SkyguardMission06IntegrationDirectorTests.cpp",
    "SkyguardMission06IntegrationTests.cpp",
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
# Isolated-test drafts #107–#232 and newer stay off this lane.
# Payload-window (#215), airfield-target runtime (#217), and
# airfield-target enum (#222) are the sibling Mission 06 contracts.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_airfield_target_runtime_defaults_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
)
# Apache CPG airfield-defense wave progression. Not Yak-52 intercept states.
LIVE_WAVE_STATES = [
    "Briefing",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
    "Completed",
    "Failed",
]
# Payload-window (#215), airfield-target runtime (#217), airfield-target
# enum (#222), and readiness (bYakRuntimeReady) stay unlocked.
SIBLING_TYPES = (
    "FSkyguardPayloadWindowRuntime",
    "FSkyguardAirfieldTargetRuntime",
    "ESkyguardAirfieldTarget",
    "FSkyguardMission06IntegrationReadiness",
    "FSkyguardDaySortieBeatKit",
    "ESkyguardDaySortieBeatKind",
)
SIBLING_DEFAULT_TOKENS = (
    "bActive",
    "RemainingSeconds",
    "bJammed",
    "Integrity",
    "bDestroyed",
    "bYakRuntimeReady",
    "bMissionDefinitionValid",
    "bCampaignDefinitionValid",
    "bMapAssemblyReady",
    "bGunnerReady",
    "bRunwayBreakerReady",
    "bObjectivesReady",
    "bWavesReady",
    "bProtectedTargetsReady",
    "bBriefingReady",
    "Hangars",
    "ParkedAircraft",
    "RidgeIngress",
    "TechnicalScreen",
    "NAME_None",
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


class Mission06WaveStateEnumContractTests(unittest.TestCase):
    def test_wave_state_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardMission06WaveState : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardMission06WaveState",
            )
        self.assertIn("ESkyguardMission06WaveState", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission06WaveState",
        )
        self.assertEqual(enumerators, LIVE_WAVE_STATES)
        self.assertEqual(
            enumerators,
            [
                "Briefing",
                "AwaitingWave",
                "WaveActive",
                "BossEngaged",
                "Completed",
                "Failed",
            ],
        )
        self.assertEqual(len(enumerators), 6, enumerators)
        body = enum_body(header, "ESkyguardMission06WaveState")
        for name in LIVE_WAVE_STATES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_wave_state_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardMission06WaveState",
        )
        body = enum_body(header, "ESkyguardMission06WaveState")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_wave_state_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMission06WaveState",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_wave_state_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMission06WaveState")
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
            "ESkyguardMission06WaveState",
        )
        self.assertEqual(enumerators, LIVE_WAVE_STATES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(
            enumerators,
            ["Runway", "Hangars", "ParkedAircraft"],
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
