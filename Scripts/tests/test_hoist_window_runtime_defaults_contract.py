from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission08IntegrationDirector.h"
LOCKED = {
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirectorTests.cpp",
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
# Isolated-test drafts stay off this lane. Storm/rain and sibling
# defaults contracts are pending siblings, not this PR.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "bool bActive = false;",
    "float RemainingSeconds = 0.f;",
    "float CoveredSeconds = 0.f;",
    "int32 CompletedWindows = 0;",
)
IN_CLASS_DEFAULTS = {
    "bActive": "false",
    "RemainingSeconds": "0.f",
    "CoveredSeconds": "0.f",
    "CompletedWindows": "0",
}
# Readiness, protected-target runtime, and M08 enums stay on other drafts.
TYPES_NOT_LOCKED = (
    "struct FSkyguardMission08IntegrationReadiness",
    "struct FSkyguardMission08ProtectedTargetRuntime",
    "enum class ESkyguardMission08WaveState",
    "enum class ESkyguardMission08ProtectedTarget",
    "bYakRuntimeReady",
    "ESkyguardMission08ProtectedTarget Target",
    "int32 Integrity = 100;",
    "bool bDestroyed = false;",
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


def hoist_window_body(header: str) -> str:
    marker = "struct FSkyguardHoistWindowRuntime"
    if marker not in header:
        raise AssertionError(
            "FSkyguardHoistWindowRuntime is missing from origin/main"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:bool|float|int32)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class HoistWindowRuntimeDefaultsContractTests(unittest.TestCase):
    def test_hoist_window_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn("struct FSkyguardHoistWindowRuntime", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", hoist_window_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = hoist_window_body(origin_main_header())
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
        body = hoist_window_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("bActive"), "false")
        self.assertEqual(defaults.get("RemainingSeconds"), "0.f")
        self.assertEqual(defaults.get("CoveredSeconds"), "0.f")
        self.assertEqual(defaults.get("CompletedWindows"), "0")
        self.assertIn("bool bActive = false;", body)
        self.assertIn("float RemainingSeconds = 0.f;", body)
        self.assertIn("float CoveredSeconds = 0.f;", body)
        self.assertIn("int32 CompletedWindows = 0;", body)
        self.assertNotIn("bActive = true", body)
        self.assertNotIn("RemainingSeconds = 0.0f", body)
        self.assertNotIn("CoveredSeconds = 0.0f", body)
        self.assertEqual(len(defaults), 4, defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = hoist_window_body(origin_main_header())
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("Error", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_readiness_target_or_wave_types(self) -> None:
        body = hoist_window_body(origin_main_header())
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("FSkyguardMission08IntegrationReadiness", body)
        self.assertNotIn("FSkyguardMission08ProtectedTargetRuntime", body)
        self.assertNotIn("ESkyguardMission08WaveState", body)
        self.assertNotIn("ESkyguardMission08ProtectedTarget", body)
        self.assertNotIn("bYakRuntimeReady", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = hoist_window_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = hoist_window_body(origin_main_header()).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardHoistWindowRuntime contains {banned}",
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
