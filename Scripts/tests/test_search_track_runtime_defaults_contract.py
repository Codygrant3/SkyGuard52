from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission07IntegrationDirector.h"
STRUCT_NAME = "FSkyguardSearchTrackRuntime"
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
# Isolated-test drafts stay off this lane. Sibling defaults contracts
# and leftover #56-#64 surfaces are not this PR.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_configuration_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
)
# Apache CPG night-search sensor track. Lock the header's actual
# TrackId sentinel (NAME_None). Do not invent INDEX_NONE or Error.
PUBLIC_FIELDS = (
    "FName TrackId = NAME_None;",
    "ESkyguardSearchSector Sector = ESkyguardSearchSector::SectorA;",
    "bool bClassifiedFalse = false;",
)
IN_CLASS_DEFAULTS = {
    "TrackId": "NAME_None",
    "Sector": "ESkyguardSearchSector::SectorA",
    "bClassifiedFalse": "false",
}
READINESS_TARGET_AND_ENUMS_NOT_LOCKED = (
    "struct FSkyguardMission07IntegrationReadiness",
    "struct FSkyguardMission07ProtectedTargetRuntime",
    "enum class ESkyguardMission07WaveState",
    "enum class ESkyguardMission07ProtectedTarget",
    "enum class ESkyguardSearchSector",
    "bYakRuntimeReady",
    "NavigationStation",
    "FishingFleet",
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
)
# NAME_None is the real TrackId default on origin/main. Do not treat it
# as invented, and do not invent INDEX_NONE or Error string defaults.
INVENTED_DEFAULTS = (
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


def search_track_body(header: str) -> str:
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
            r"(?:FName|ESkyguardSearchSector|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class SearchTrackRuntimeDefaultsContractTests(unittest.TestCase):
    def test_search_track_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", search_track_body(header))

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            search_track_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = search_track_body(origin_main_header())
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
        body = search_track_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("FName TrackId = NAME_None;", body)
        self.assertIn(
            "ESkyguardSearchSector Sector = ESkyguardSearchSector::SectorA;",
            body,
        )
        self.assertIn("bool bClassifiedFalse = false;", body)
        self.assertEqual(defaults.get("TrackId"), "NAME_None")
        self.assertEqual(defaults.get("Sector"), "ESkyguardSearchSector::SectorA")
        self.assertEqual(defaults.get("bClassifiedFalse"), "false")
        self.assertNotIn("bClassifiedFalse = true", body)
        self.assertNotIn("TrackId = INDEX_NONE", body)
        self.assertNotIn("Sector = ESkyguardSearchSector::SectorB", body)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = search_track_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertEqual(defaults.get("TrackId"), "NAME_None")
        self.assertNotIn("Error =", body)
        self.assertNotIn("FString Error", body)
        self.assertNotIn("Error", defaults)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_readiness_target_or_sibling_enums(self) -> None:
        body = search_track_body(origin_main_header())
        for token in READINESS_TARGET_AND_ENUMS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission07IntegrationReadiness", body)
        self.assertNotIn("FSkyguardMission07ProtectedTargetRuntime", body)
        self.assertNotIn("ESkyguardMission07WaveState", body)
        self.assertNotIn("ESkyguardMission07ProtectedTarget", body)
        self.assertNotIn("enum class ESkyguardSearchSector", body)
        self.assertNotIn("SectorB", body)
        self.assertNotIn("Intercept", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = search_track_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = search_track_body(origin_main_header()).lower()
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
