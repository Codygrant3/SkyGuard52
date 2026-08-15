#!/usr/bin/env python3
"""Offline verifier for the Mission 1 UE 5.8 Landscape grounding bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ENGINE = Path(r"D:\UE_5.8")
DOC_ROOT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08" / "M01LandscapeGroundingBridge01"
SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "environment_visual_remediation01"
PARITY = ROOT / "Saved" / "Reports" / "M01_LANDSCAPE_GROUNDING_BRIDGE01_SOURCE_PARITY_CONTRACT.json"

AUTHORITIES = {
    ROOT / "Source" / "Skyguard52" / "SkyguardMission01EnvironmentAuthoringLibrary.h": (
        10648,
        "1110d71f33813b212ed880ea21f3126369089de1f59fda6358161dfff46397f1",
    ),
    ROOT / "Source" / "Skyguard52" / "SkyguardMission01EnvironmentAuthoringLibrary.cpp": (
        38847,
        "ba6c399dd462ff771067eb243bbae914095029992a5abc24f184529e9b54b6c8",
    ),
    ROOT / "Source" / "Skyguard52" / "Skyguard52.Build.cs": (
        1058,
        "f6657c2bd89e0038c78308cb3cca65a7de4e5a2e1f868a441492fe1b99461270",
    ),
    ENGINE / "Engine" / "Source" / "Runtime" / "Landscape" / "Classes" / "LandscapeProxy.h": (
        88633,
        "2b8e9f811e244db01b37d0b468f1d835257a99b2a77b7441aec6692ccdb0dab7",
    ),
    ENGINE
    / "Engine"
    / "Source"
    / "Runtime"
    / "Landscape"
    / "Classes"
    / "LandscapeHeightfieldCollisionComponent.h": (
        14493,
        "03faadb2e67a314953ff5eabea3a3eca058a62da77a81605dd3edf6cc15d7d8a",
    ),
    ENGINE / "Engine" / "Source" / "Runtime" / "Landscape" / "Private" / "LandscapeCollision.cpp": (
        108879,
        "d9d8a47ec72921fccf1d62846f6717045b53f1c48611420d060506e9e805e7a0",
    ),
}

FUTURE_PATHS = [
    Path(r"D:\SG52M01GROUND01"),
    ROOT
    / "Saved"
    / "BuildAttempts"
    / "M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD"
    / "attempt_01",
    ROOT
    / "Saved"
    / "Reports"
    / "M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD_TERMINAL_MANIFEST.json",
    ROOT
    / "Saved"
    / "Reports"
    / "M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD_EMERGENCY_RECEIPT.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def exact_file(path: Path, size: int, digest: str, failures: list[str]) -> dict:
    if not path.is_file():
        failures.append(f"Missing authority: {path}")
        return {"path": str(path), "exists": False}
    actual_size = path.stat().st_size
    actual_digest = sha256(path)
    require(actual_size == size, f"Byte mismatch: {path}", failures)
    require(actual_digest == digest, f"SHA-256 mismatch: {path}", failures)
    return {
        "path": str(path),
        "exists": True,
        "bytes": actual_size,
        "sha256": actual_digest,
    }


def load_json(path: Path, failures: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:  # evidence is recorded in the result
        failures.append(f"Invalid JSON {path}: {error}")
        return {}


def verify(output: Path | None = None) -> dict:
    failures: list[str] = []
    authority_records = [
        exact_file(path, size, digest, failures)
        for path, (size, digest) in AUTHORITIES.items()
    ]

    authority_report = load_json(DOC_ROOT / "installed_ue58_authority_report.json", failures)
    source_contract = load_json(DOC_ROOT / "source_contract.json", failures)
    parity = load_json(PARITY, failures)

    require(authority_report.get("classification") == "PASS", "Installed authority report did not pass", failures)
    require(
        source_contract.get("classification") == "OFFLINE_SOURCE_IMPLEMENTED_AWAITING_NATIVE_BUILD",
        "Source contract classification mismatch",
        failures,
    )
    require(parity.get("record_count") == len(parity.get("records", [])), "Parity record count mismatch", failures)
    require(parity.get("record_count", 0) >= 170, "Parity contract is unexpectedly incomplete", failures)

    header_path = ROOT / "Source" / "Skyguard52" / "SkyguardMission01LandscapeGroundingLibrary.h"
    cpp_path = ROOT / "Source" / "Skyguard52" / "SkyguardMission01LandscapeGroundingLibrary.cpp"
    tests_path = ROOT / "Source" / "Skyguard52" / "SkyguardMission01LandscapeGroundingTests.cpp"
    for path in (header_path, cpp_path, tests_path):
        require(path.is_file() and path.stat().st_size > 0, f"Missing source: {path}", failures)

    header = header_path.read_text(encoding="utf-8") if header_path.is_file() else ""
    cpp = cpp_path.read_text(encoding="utf-8") if cpp_path.is_file() else ""
    tests = tests_path.read_text(encoding="utf-8") if tests_path.is_file() else ""
    build_cs = (ROOT / "Source" / "Skyguard52" / "Skyguard52.Build.cs").read_text(encoding="utf-8")

    include_lines = [line.strip() for line in header.splitlines() if line.strip().startswith("#include")]
    require(
        bool(include_lines) and include_lines[-1] == '#include "SkyguardMission01LandscapeGroundingLibrary.generated.h"',
        "Generated include is not the final header include",
        failures,
    )
    for token in (
        "FSkyguardLandscapeHeightSample",
        "FSkyguardLandscapeFootprintSampleResult",
        "USkyguardMission01LandscapeGroundingLibrary",
        "SampleLandscapeHeight",
        "SampleLandscapeFootprint",
        "UFUNCTION(BlueprintPure",
    ):
        require(token in header, f"Missing header token: {token}", failures)

    for token in (
        "GetHeightAtLocation",
        "EHeightfieldSource::Editor",
        "EHeightfieldSource::Complex",
        "ContainsNaN()",
        "FMath::IsFinite",
        "Count == 5 || Count == 9 || Count == 13",
        "DuplicateXYToleranceCentimeters",
        "Result.ValidSampleCount != Result.RequiredSampleCount",
        "Result.SupportedFraction",
    ):
        require(token in cpp, f"Missing implementation token: {token}", failures)

    for forbidden in (
        "SetActorLocation",
        "SetWorldLocation",
        "SavePackage",
        "LineTrace",
        "Landscape->Modify",
        "automatic retry",
    ):
        require(forbidden not in cpp, f"Forbidden implementation token: {forbidden}", failures)

    require(re.search(r'"Landscape"', build_cs) is not None, "Landscape module dependency is missing", failures)
    for test_name in (
        "Skyguard.Mission01.Environment.Grounding.NullLandscapeFailsClosed",
        "Skyguard.Mission01.Environment.Grounding.FootprintCountsAreGoverned",
    ):
        require(test_name in tests, f"Missing automation test: {test_name}", failures)

    parity_paths = {record.get("relative_path") for record in parity.get("records", [])}
    for relative in (
        "Source/Skyguard52/SkyguardMission01LandscapeGroundingLibrary.h",
        "Source/Skyguard52/SkyguardMission01LandscapeGroundingLibrary.cpp",
        "Source/Skyguard52/SkyguardMission01LandscapeGroundingTests.cpp",
    ):
        require(relative in parity_paths, f"Parity contract omits {relative}", failures)

    existing_future = [str(path) for path in FUTURE_PATHS if path.exists()]
    require(not existing_future, f"Future governed namespaces already exist: {existing_future}", failures)

    result = {
        "schema": "skyguard.m01-landscape-grounding-bridge01.offline-verification.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "authority_records": authority_records,
        "parity_record_count": parity.get("record_count"),
        "new_source_records": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (header_path, cpp_path, tests_path)
            if path.is_file()
        ],
        "future_namespaces_absent": not existing_future,
        "heavy_processes_launched_by_verifier": 0,
        "unreal_launches": 0,
        "blender_launches": 0,
        "build_launches": 0,
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.output)
    print(result["classification"])
    if result["failures"]:
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["classification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
