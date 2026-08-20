from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission05IntegrationDirector.h"
LOCKED = {
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardStormRainBeatKitTests.cpp",
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
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "float Turbulence = 0.f;",
    "bool bLightningActive = false;",
    "float LightningRemainingSeconds = 0.f;",
    "int32 LightningFlashCount = 0;",
    "bool bMaintainingAim = false;",
)
IN_CLASS_DEFAULTS = {
    "Turbulence": "0.f",
    "bLightningActive": "false",
    "LightningRemainingSeconds": "0.f",
    "LightningFlashCount": "0",
    "bMaintainingAim": "false",
}
BANNED = ("igla", "yak", "rifle")
SIBLING_TYPES = (
    "FSkyguardMission05IntegrationReadiness",
    "ESkyguardStormRainBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardMission05WaveState",
    "ESkyguardMission05ProtectedTarget",
)
HARBOR_TUNING = ("40.f", "80.f")
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "TEXT(",
    "FString()",
    'TEXT("")',
)


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def storm_runtime_body(header: str) -> str:
    marker = "struct FSkyguardStormRuntime"
    if marker not in header:
        raise AssertionError(
            "FSkyguardStormRuntime is missing from "
            f"origin/main:{HEADER_PATH}"
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


class StormRuntimeDefaultsContractTests(unittest.TestCase):
    def test_storm_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn("struct FSkyguardStormRuntime", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", storm_runtime_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = storm_runtime_body(origin_main_header())
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
        body = storm_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("float Turbulence = 0.f;", body)
        self.assertIn("bool bLightningActive = false;", body)
        self.assertIn("float LightningRemainingSeconds = 0.f;", body)
        self.assertIn("int32 LightningFlashCount = 0;", body)
        self.assertIn("bool bMaintainingAim = false;", body)
        self.assertNotIn("bLightningActive = true", body)
        self.assertNotIn("bMaintainingAim = true", body)
        self.assertEqual(len(defaults), 5, defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = storm_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_readiness_or_sibling_types(self) -> None:
        body = storm_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("enum class", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = storm_runtime_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = storm_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardStormRuntime contains {banned}",
            )
            self.assertNotIn(banned, defaults)

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
