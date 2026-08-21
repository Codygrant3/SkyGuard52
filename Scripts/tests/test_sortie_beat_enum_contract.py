from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardGunshipSortieDirector.h"
# Leftover #56–#64 plus GunshipSortieDirector production sources/tests.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardGunshipSortieTests.cpp",
    "SkyguardFlareEmptyInboundTests.cpp",
    "SkyguardShippingCheckTests.cpp",
    "SkyguardCpgDebrief.cpp",
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
# Isolated-test drafts #107–#236 and newer stay off this lane.
# Climax-kind is already drafted. Mission 08 wave-state is now being opened.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_climax_kind_enum_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_sortie_presentation_state_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
)
# Apache CPG sortie beat progression. Not Harbor IncomingRadar 40/80
# and not a live weapon roster.
LIVE_BEATS = [
    "Approach",
    "InitialContact",
    "ShoreAssault",
    "RadarNet",
    "Choice",
    "Climax",
    "Extraction",
    "Succeeded",
    "Failed",
]
# Climax-kind (already drafted) stays unlocked. Do not re-lock
# ESkyguardClimaxKind. Sibling types in the same header stay unlocked.
SIBLING_TYPES = (
    "ESkyguardLoadout",
    "ESkyguardThreatKind",
    "ESkyguardSortiePresentationState",
    "ESkyguardPatrolShipSystem",
    "ESkyguardPilotLine",
    "ESkyguardGunshipWeapon",
    "ESkyguardGuidedLockPhase",
    "ESkyguardCpgSightMode",
    "FSkyguardCpgDebriefSnapshot",
    "ASkyguardProtectAsset",
    "ASkyguardRadarNode",
    "ASkyguardPatrolShipBoss",
)
SIBLING_DEFAULT_TOKENS = (
    "IncomingFirstDelaySeconds",
    "ContactWaveCount",
    "ShoreWaveCount",
    "RadarNetWaveCount",
    "ChoiceWaveCount",
    "ExtractWaveCount",
    "CoastalConvoyCount",
    "PendingLoadout",
    "bAwaitingContinue",
    "bYakRuntimeReady",
    "NAME_None",
    "PatrolShip",
    "RivalHelo",
    "ArmorColumn",
    "MixedSwarm",
    "Briefing",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
    "Completed",
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


class SortieBeatEnumContractTests(unittest.TestCase):
    def test_sortie_beat_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardSortieBeat : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardSortieBeat",
            )
        self.assertIn("ESkyguardSortieBeat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardSortieBeat")
        self.assertEqual(enumerators, LIVE_BEATS)
        self.assertEqual(
            enumerators,
            [
                "Approach",
                "InitialContact",
                "ShoreAssault",
                "RadarNet",
                "Choice",
                "Climax",
                "Extraction",
                "Succeeded",
                "Failed",
            ],
        )
        self.assertEqual(len(enumerators), 9, enumerators)
        body = enum_body(header, "ESkyguardSortieBeat")
        for name in LIVE_BEATS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
        self.assertNotEqual(
            enumerators,
            [
                "PatrolShip",
                "RivalHelo",
                "ArmorColumn",
                "MixedSwarm",
            ],
        )

    def test_sortie_beat_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardSortieBeat")
        body = enum_body(header, "ESkyguardSortieBeat")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_sortie_beat_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardSortieBeat",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_sortie_beat_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardSortieBeat")
        self.assertIn("Approach", body)
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
        enumerators = enum_enumerators(header, "ESkyguardSortieBeat")
        self.assertEqual(enumerators, LIVE_BEATS)
        self.assertEqual(len(enumerators), 9, enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(
            enumerators,
            [
                "PatrolShip",
                "RivalHelo",
                "ArmorColumn",
                "MixedSwarm",
            ],
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
