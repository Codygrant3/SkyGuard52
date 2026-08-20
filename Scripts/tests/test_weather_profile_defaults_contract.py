from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionTypes.h"
LOCKED = {
    "SkyguardMissionTypes.h",
    "SkyguardMissionTypesDefaultsTests.cpp",
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirectorTests.cpp",
    "SkyguardCoastalWeatherIdentityTests.cpp",
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
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_route_point_defaults_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
)
PUBLIC_FIELDS = (
    "FName ProfileId;",
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
    "float TimeOfDayHours = 12.f;",
    "float WindSpeedMetersPerSecond = 5.f;",
    "float Precipitation = 0.f;",
    "float CloudCoverage = 0.25f;",
)
IN_CLASS_DEFAULTS = {
    "Weather": "ESkyguardMissionWeather::Clear",
    "TimeOfDayHours": "12.f",
    "WindSpeedMetersPerSecond": "5.f",
    "Precipitation": "0.f",
    "CloudCoverage": "0.25f",
}
BANNED = ("igla", "yak", "rifle")
WEATHER_ENUMERATORS_OWNED_BY_155 = (
    "Overcast",
    "Rain",
    "Storm",
    "NightClear",
    "NightOvercast",
)
OTHER_TYPES = (
    "FSkyguardRoutePoint",
    "FSkyguardObjectiveDefinition",
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "ESkyguardMissionObjectiveType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardFormationType",
    "ESkyguardMissionDebriefState",
)
HARBOR_TUNING = ("40.f", "80.f")


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def weather_profile_body(header: str) -> str:
    start = header.index("struct FSkyguardWeatherProfile")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:ESkyguardMissionWeather|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class WeatherProfileDefaultsContractTests(unittest.TestCase):
    def test_weather_profile_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardWeatherProfile", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", weather_profile_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = weather_profile_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadOnly)"), 6)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = weather_profile_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
            body,
        )
        self.assertIn("float TimeOfDayHours = 12.f;", body)
        self.assertIn("float WindSpeedMetersPerSecond = 5.f;", body)
        self.assertIn("float Precipitation = 0.f;", body)
        self.assertIn("float CloudCoverage = 0.25f;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = weather_profile_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("ProfileId =", body)

    def test_struct_does_not_re_lock_weather_enumerator_list(self) -> None:
        body = weather_profile_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardMissionWeather", body)
        self.assertIn("ESkyguardMissionWeather::Clear", body)
        self.assertEqual(body.count("ESkyguardMissionWeather::"), 1)
        for enumerator in WEATHER_ENUMERATORS_OWNED_BY_155:
            self.assertNotIn(enumerator, body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = weather_profile_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = weather_profile_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardWeatherProfile contains {banned}",
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
