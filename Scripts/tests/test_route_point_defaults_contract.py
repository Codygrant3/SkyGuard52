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
    "SkyguardRouteRuntime.h",
    "SkyguardRouteRuntime.cpp",
    "SkyguardRouteRuntimeFailClosedTests.cpp",
    "SkyguardRouteRuntimeTests.cpp",
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
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FName PointId;",
    "FVector WorldLocation = FVector::ZeroVector;",
    "float TargetAirspeedKph = 220.f;",
    "float LookAheadSeconds = 2.f;",
    "bool bAllowCombatOrbit = true;",
)
IN_CLASS_DEFAULTS = {
    "WorldLocation": "FVector::ZeroVector",
    "TargetAirspeedKph": "220.f",
    "LookAheadSeconds": "2.f",
    "bAllowCombatOrbit": "true",
}
BANNED = ("igla", "yak", "rifle")
OTHER_TYPES = (
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "ESkyguardMissionObjectiveType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardFormationType",
    "ESkyguardMissionWeather",
    "ESkyguardMissionDebriefState",
)
ROUTE_RUNTIME_FAIL_CLOSED = (
    "FindPointIndex",
    "INDEX_NONE",
    "HasRoute",
    "GetActiveRoute",
    "AdvanceToNextPoint",
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


def route_point_body(header: str) -> str:
    start = header.index("struct FSkyguardRoutePoint")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:FVector|float|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class RoutePointDefaultsContractTests(unittest.TestCase):
    def test_route_point_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardRoutePoint", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", route_point_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = route_point_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadOnly)"), 5)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = route_point_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("FVector WorldLocation = FVector::ZeroVector;", body)
        self.assertIn("float TargetAirspeedKph = 220.f;", body)
        self.assertIn("float LookAheadSeconds = 2.f;", body)
        self.assertIn("bool bAllowCombatOrbit = true;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = route_point_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("PointId =", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = route_point_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in ROUTE_RUNTIME_FAIL_CLOSED:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = route_point_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardRoutePoint contains {banned}",
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
