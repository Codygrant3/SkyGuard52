from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission06IntegrationDirector.h"
STRUCT_NAME = "FSkyguardAirfieldTargetRuntime"
LOCKED = {
    "SkyguardMission06IntegrationDirector.h",
    "SkyguardMission06IntegrationDirector.cpp",
    "SkyguardMission06IntegrationDirectorTests.cpp",
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
# Isolated-test drafts stay off this lane. Sibling defaults contracts
# are pending siblings, not this PR.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
)
# Apache CPG airfield integrity. Not Yak. Target default is enough;
# the full ESkyguardAirfieldTarget set stays unlocked.
PUBLIC_FIELDS = (
    "ESkyguardAirfieldTarget Target = ESkyguardAirfieldTarget::Runway;",
    "int32 Integrity = 100;",
    "bool bDestroyed = false;",
)
IN_CLASS_DEFAULTS = {
    "Target": "ESkyguardAirfieldTarget::Runway",
    "Integrity": "100",
    "bDestroyed": "false",
}
# Payload window (#215), readiness (bYakRuntimeReady), wave state,
# and the full airfield-target enumerator set stay on other drafts.
TYPES_NOT_LOCKED = (
    "struct FSkyguardPayloadWindowRuntime",
    "struct FSkyguardMission06IntegrationReadiness",
    "enum class ESkyguardMission06WaveState",
    "enum class ESkyguardAirfieldTarget",
    "bYakRuntimeReady",
    "bool bActive = false;",
    "float RemainingSeconds = 0.f;",
    "bool bJammed = false;",
    "Hangars",
    "ParkedAircraft",
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


def airfield_target_body(header: str) -> str:
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
            r"(?:bool|float|int32|ESkyguardAirfieldTarget)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class AirfieldTargetRuntimeDefaultsContractTests(unittest.TestCase):
    def test_airfield_target_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", airfield_target_body(header))

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            airfield_target_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = airfield_target_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 3)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            3,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = airfield_target_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Target"),
            "ESkyguardAirfieldTarget::Runway",
        )
        self.assertEqual(defaults.get("Integrity"), "100")
        self.assertEqual(defaults.get("bDestroyed"), "false")
        self.assertIn(
            "ESkyguardAirfieldTarget Target = ESkyguardAirfieldTarget::Runway;",
            body,
        )
        self.assertIn("int32 Integrity = 100;", body)
        self.assertIn("bool bDestroyed = false;", body)
        self.assertNotIn("bDestroyed = true", body)
        self.assertNotIn("Integrity = 0;", body)
        self.assertNotIn("Integrity = INDEX_NONE", body)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = airfield_target_body(origin_main_header())
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

    def test_contract_does_not_lock_payload_window_readiness_or_wave(self) -> None:
        body = airfield_target_body(origin_main_header())
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("FSkyguardPayloadWindowRuntime", body)
        self.assertNotIn("FSkyguardMission06IntegrationReadiness", body)
        self.assertNotIn("ESkyguardMission06WaveState", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("Hangars", body)
        self.assertNotIn("ParkedAircraft", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = airfield_target_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = airfield_target_body(origin_main_header()).lower()
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
