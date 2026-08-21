from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardAudioProductionBank.h"
# Leftover #56–#64 plus audio production-bank sources.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardAudioProductionBank.h",
    "SkyguardAudioProductionBank.cpp",
    "SkyguardAudioProductionBankTests.cpp",
    "SkyguardAudioProductionBankEmptyFailClosedTests.cpp",
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
# Isolated-test drafts #107–#237 and newer stay off this lane.
# Production-audio entry (#198), routing (#197), and audit (#196) are
# sibling contracts. Mission 09 wave-state and Iron Rain maneuver
# contracts are being opened in parallel.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_production_audio_entry_defaults_contract.py",
    "Scripts/tests/test_production_audio_routing_defaults_contract.py",
    "Scripts/tests/test_production_audio_audit_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audible_acceptance_receipt_defaults_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Production-audio provenance/status. Not a live weapon roster and not
# ESkyguardProductionAudioCategory Rifle / Igla names.
LIVE_SOURCE_STATUSES = [
    "MISSING_SOURCE",
    "PROJECT_OWNED_RECORDING",
    "LICENSED_THIRD_PARTY",
    "PROCEDURAL_QA_TEST_ONLY",
]
# Production-audio structs (#198/#197/#196) and the Rifle/Igla category
# enum stay unlocked. This contract locks only ESkyguardAudioSourceStatus.
SIBLING_TYPES = (
    "ESkyguardProductionAudioCategory",
    "FSkyguardProductionAudioEntry",
    "FSkyguardProductionAudioRouting",
    "FSkyguardProductionAudioAudit",
)
SIBLING_DEFAULT_TOKENS = (
    "RifleMuzzle",
    "IglaSearch",
    "IglaLock",
    "IglaLaunch",
    "EngineIdle",
    "DisplayName",
    "CockpitExteriorAttenuation",
    "CockpitLowPassHz",
    "RequiredCategoryCount",
    "BoundProductionSourceCount",
    "bCategoryContractComplete",
    "bProductionReady",
    "bYakRuntimeReady",
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


class AudioSourceStatusEnumContractTests(unittest.TestCase):
    def test_audio_source_status_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardAudioSourceStatus : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardAudioSourceStatus",
            )
        self.assertIn("ESkyguardAudioSourceStatus", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardAudioSourceStatus",
        )
        self.assertEqual(enumerators, LIVE_SOURCE_STATUSES)
        self.assertEqual(
            enumerators,
            [
                "MISSING_SOURCE",
                "PROJECT_OWNED_RECORDING",
                "LICENSED_THIRD_PARTY",
                "PROCEDURAL_QA_TEST_ONLY",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardAudioSourceStatus")
        for name in LIVE_SOURCE_STATUSES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
        self.assertIn("MISSING_SOURCE", enumerators)

    def test_audio_source_status_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardAudioSourceStatus",
        )
        body = enum_body(header, "ESkyguardAudioSourceStatus")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_audio_source_status_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardAudioSourceStatus",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotIn("RifleMuzzle", enumerators)
        self.assertNotIn("IglaSearch", enumerators)
        self.assertNotIn("IglaLock", enumerators)
        self.assertNotIn("IglaLaunch", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_audio_source_status_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardAudioSourceStatus")
        self.assertIn("MISSING_SOURCE", body)
        self.assertIn("PROCEDURAL_QA_TEST_ONLY", body)
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
        self.assertNotIn("RifleMuzzle", body)
        self.assertNotIn("IglaSearch", body)
        self.assertNotIn("IglaLock", body)
        self.assertNotIn("IglaLaunch", body)
        enumerators = enum_enumerators(
            header,
            "ESkyguardAudioSourceStatus",
        )
        self.assertEqual(enumerators, LIVE_SOURCE_STATUSES)
        self.assertEqual(len(enumerators), 4, enumerators)
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
