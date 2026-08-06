"""Offline, source-only audit for the Mission 09 playable integration."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "boss_h": ROOT / "Source/Skyguard52/SkyguardIronRainBoss.h",
    "boss_cpp": ROOT / "Source/Skyguard52/SkyguardIronRainBoss.cpp",
    "director_h": ROOT / "Source/Skyguard52/SkyguardMission09IntegrationDirector.h",
    "director_cpp": ROOT / "Source/Skyguard52/SkyguardMission09IntegrationDirector.cpp",
    "tests": ROOT / "Source/Skyguard52/SkyguardMission09IntegrationTests.cpp",
    "builder": ROOT / "Scripts/build_skyguard_m09_playable_integration.py",
    "verifier": ROOT / "Scripts/verify_skyguard_m09_playable_integration.py",
    "gate": ROOT / "Scripts/run_skyguard_m09_playable_integration_gate_root_only.ps1",
    "runbook": ROOT / "Docs/AAA_Review/M09_PLAYABLE_INTEGRATION_V1.md",
}
EXPECTED_TESTS = [
    "Skyguard52.Mission09.Integration.GovernedContractEscalationAndPoolBounds",
    "Skyguard52.Mission09.IronRain.DispensersClimbCrossAndSecondIgla",
    "Skyguard52.Mission09.IronRain.DifficultRifleFuelControlFinish",
    "Skyguard52.Mission09.Integration.DeterministicSuccessAndInfrastructureFailure",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: dict[str, bool] = {
        "all_owned_files_present": all(path.is_file() for path in FILES.values())
    }
    if not checks["all_owned_files_present"]:
        missing = [str(path) for path in FILES.values() if not path.is_file()]
        print(json.dumps({"gate": "FAIL", "missing": missing}, indent=2))
        return 2

    text = {name: path.read_text(encoding="utf-8") for name, path in FILES.items()}
    python_syntax = True
    for name in ("builder", "verifier"):
        try:
            ast.parse(text[name], filename=str(FILES[name]))
        except SyntaxError:
            python_syntax = False
    checks["python_syntax"] = python_syntax
    checks["separate_preserved_map"] = all(
        marker in text["builder"]
        for marker in (
            "Lvl_M09_SaturationAttack_Assembly_v1",
            "Lvl_M09_SaturationAttack_Playable_v1",
            "source_preserved",
        )
    ) and "delete_asset(SOURCE_MAP)" not in text["builder"]
    checks["dense_metropolitan_route_audit"] = all(
        marker in text["verifier"]
        for marker in (
            "distinct_dense_canyon_route",
            "DenseMetroSkylineProxy",
            "PowerInfrastructureProxy",
            "BridgeInfrastructureProxy",
            "route_x_span >= 90000.0",
            "route_y_span >= 25000.0",
        )
    )
    boss_markers = (
        "DispenserPort", "DispenserCenter", "DispenserStarboard",
        "CommandAntennaPort", "CommandAntennaStarboard",
        "DecoyController", "EnginePodPort", "EnginePodCenter",
        "EnginePodStarboard", "FuelControlPort", "FuelControlStarboard",
        "IssueClimbCommand", "IssueCrossCommand", "ApplySecondIglaFinish",
        "ArmFuelControlRifleFinish", "MaxDefeatDebrisPieces = 3",
        "RefreshAuthoredWeakPointRegistry", "WeakPoints = {",
    )
    checks["iron_rain_complete"] = all(
        marker in text["boss_h"] + text["boss_cpp"] for marker in boss_markers
    )
    director_markers = (
        "MetropolitanSkyline", "CoastalPowerStation", "MajorBridge",
        "CalculateWaveThreatCount(0) == 8",
        "CalculateWaveThreatCount(1) == 12",
        "CalculateWaveThreatCount(2) == 16",
        "MaxActiveThreats = 24", "PoolCapacity = 48",
        "MaxActiveDecoys = 12", "MaxSimultaneousExplosions = 6",
        "GetSurvivingTargetCount() < 2",
    )
    checks["bounded_deterministic_integration"] = all(
        marker in text["director_h"] + text["director_cpp"]
        for marker in director_markers
    )
    checks["no_unsupported_algo_helpers"] = (
        "Algo::CountIf" not in text["director_cpp"] + text["boss_cpp"]
        and "Algo::AllOf" not in text["director_cpp"] + text["boss_cpp"]
    )
    checks["complete_weakpoint_include"] = (
        '#include "SkyguardBossWeakPointComponent.h"' in text["director_cpp"]
    )
    tests_found = re.findall(
        r'"(Skyguard52\.Mission09\.[^"]+)"', text["tests"]
    )
    unique_tests = sorted(set(tests_found))
    checks["exactly_four_focused_tests"] = (
        text["tests"].count("IMPLEMENT_SIMPLE_AUTOMATION_TEST(") == 4
        and sorted(EXPECTED_TESTS) == unique_tests
    )
    checks["root_only_serialized_gate"] = all(
        marker in text["gate"]
        for marker in (
            "[switch]$RootAuthorized",
            "RootAuthorized",
            "Shared Unreal lane is active",
            "Automation RunTests Skyguard52.Mission09",
            "Automation Test Queue Empty 4 tests performed",
        )
    )
    protected_text = text["builder"] + text["verifier"] + text["gate"]
    checks["no_config_or_soak_mutation"] = all(
        marker not in protected_text
        for marker in (
            "DefaultGame.ini",
            "PHASE8_MISSION_SOAK_MATRIX.json",
            "MapsToCook",
        )
    )
    audit_source = Path(__file__).read_text(encoding="utf-8")
    checks["no_engine_execution_in_source_audit"] = not re.search(
        r"^\s*(?:import\s+subprocess|from\s+subprocess\s+import)",
        audit_source,
        re.MULTILINE,
    )
    report = {
        "schema": "skyguard.m09-playable-source-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "files": {
            name: {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for name, path in FILES.items()
        },
        "protected_files_not_owned": [
            "Config/DefaultGame.ini",
            "Docs/AAA_Review/PHASE8_MISSION_SOAK_MATRIX.json",
            "Content/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1.umap",
        ],
        "execution_status": "SOURCE_ONLY_NOT_RUN",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
