from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission04IntegrationDirector.h"
STRUCT_NAME = "FSkyguardSearchlightTrackRuntime"
LOCKED = {
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirectorTests.cpp",
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
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_configuration_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
)
# Apache CPG night-sortie sensor track. Do not lock readiness or wave state.
PUBLIC_FIELDS = (
    "bool bActive = false;",
    "bool bBossTracked = false;",
    "float RemainingSeconds = 0.f;",
    "float HeldSeconds = 0.f;",
    "int32 CompletedPasses = 0;",
)
IN_CLASS_DEFAULTS = {
    "bActive": "false",
    "bBossTracked": "false",
    "RemainingSeconds": "0.f",
    "HeldSeconds": "0.f",
    "CompletedPasses": "0",
}
READINESS_AND_WAVE_NOT_LOCKED = (
    "struct FSkyguardMission04IntegrationReadiness",
    "enum class ESkyguardMission04WaveState",
    "bYakRuntimeReady",
    "bMissionDefinitionValid",
    "bSearchlightsReady",
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


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def searchlight_body(header: str) -> str:
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
            r"(?:bool|int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class SearchlightTrackRuntimeDefaultsContractTests(unittest.TestCase):
    def test_searchlight_track_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", searchlight_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = searchlight_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 5)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            5,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = searchlight_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("bool bActive = false;", body)
        self.assertIn("bool bBossTracked = false;", body)
        self.assertIn("float RemainingSeconds = 0.f;", body)
        self.assertIn("float HeldSeconds = 0.f;", body)
        self.assertIn("int32 CompletedPasses = 0;", body)
        self.assertNotIn("bActive = true", body)
        self.assertNotIn("bBossTracked = true", body)
        self.assertEqual(len(defaults), 5, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_name_none_or_error(self) -> None:
        body = searchlight_body(origin_main_header())
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("Error =", body)
        self.assertNotIn("FString Error", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_readiness_or_wave_state(self) -> None:
        body = searchlight_body(origin_main_header())
        for token in READINESS_AND_WAVE_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("bYakRuntimeReady", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = searchlight_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = searchlight_body(origin_main_header()).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}",
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
