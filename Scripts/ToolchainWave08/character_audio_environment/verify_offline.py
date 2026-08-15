#!/usr/bin/env python3
"""Offline verifier for Toolchain Wave 08 character/audio/environment tooling."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "character_audio_environment"
DOC_ROOT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08"
CONTRACTS = {
    "character": DOC_ROOT / "character_prototype_contract.json",
    "audio": DOC_ROOT / "audio_prototype_contract.json",
    "environment": DOC_ROOT / "environment_prototype_contract.json",
}
PREPARE_SCRIPTS = {
    "character": SCRIPT_ROOT / "prepare_character_view_once.ps1",
    "audio": SCRIPT_ROOT / "prepare_audio_view_once.ps1",
    "environment": SCRIPT_ROOT / "prepare_environment_view_once.ps1",
}
CANONICAL_DISABLED = {
    "Water": False,
    "WaterAdvanced": False,
    "Landmass": False,
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: pathlib.Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_contract(lane: str, path: pathlib.Path, errors: list[str]) -> dict:
    data = load_json(path)
    require(data.get("schema") == "skyguard.toolchain-wave08.isolated-view-contract.v1", f"{lane}: schema", errors)
    require(data.get("lane") == lane, f"{lane}: lane", errors)
    target = pathlib.Path(data["target_root"])
    attempt = pathlib.Path(data["attempt_root"])
    terminal = pathlib.Path(data["terminal_report_path"])
    require(not target.exists(), f"{lane}: target already exists: {target}", errors)
    require(not attempt.exists(), f"{lane}: attempt already exists: {attempt}", errors)
    require(not terminal.exists(), f"{lane}: terminal report already exists: {terminal}", errors)
    require(data.get("canonical_root") == str(ROOT), f"{lane}: canonical root", errors)
    require(data.get("canonical_uproject") == str(ROOT / "Skyguard52.uproject"), f"{lane}: canonical project", errors)
    require(data.get("success_classification", "").startswith("PASSED_ISOLATED_"), f"{lane}: success classification", errors)
    for authority in data.get("authorities", []):
        authority_path = pathlib.Path(authority["path"])
        require(authority_path.is_file(), f"{lane}: missing authority {authority_path}", errors)
        if authority_path.is_file():
            require(authority_path.stat().st_size == authority["bytes"], f"{lane}: byte mismatch {authority_path}", errors)
            require(sha256(authority_path) == authority["sha256"], f"{lane}: hash mismatch {authority_path}", errors)
    return data


def main() -> int:
    errors: list[str] = []
    common = SCRIPT_ROOT / "common.ps1"
    require(common.is_file(), "missing common.ps1", errors)
    common_text = common.read_text(encoding="utf-8") if common.is_file() else ""
    require("Start-Process" not in common_text, "common must not launch child processes", errors)
    require("CreateSymbolicLink" not in common_text and "CreateHardLink" not in common_text, "links are forbidden", errors)
    require("-AuthorizeSinglePrepare" in common_text, "authorization guard missing", errors)
    require("retry_count = 0" in common_text, "zero retry evidence missing", errors)
    require("canonical_uproject_post_sha256" in common_text, "canonical post-hash missing", errors)
    require("externalTerminalPath" in common_text, "preflight terminal lifecycle missing", errors)
    require("[System.IO.File]::Copy" in common_text, "deterministic copy implementation missing", errors)

    contract_data: dict[str, dict] = {}
    for lane, contract in CONTRACTS.items():
        require(contract.is_file(), f"missing contract: {contract}", errors)
        if contract.is_file():
            contract_data[lane] = verify_contract(lane, contract, errors)
        script = PREPARE_SCRIPTS[lane]
        require(script.is_file(), f"missing prepare script: {script}", errors)
        if script.is_file():
            text = script.read_text(encoding="utf-8")
            require("Start-Process" not in text, f"{lane}: wrapper launches a process", errors)
            require("AuthorizeSinglePrepare" in text, f"{lane}: explicit authorization absent", errors)
            require("OfflineContractTest" in text, f"{lane}: offline test absent", errors)

    if contract_data:
        require(contract_data["character"].get("copy_content") is False, "character must use empty content", errors)
        require(contract_data["audio"].get("copy_content") is False, "audio must use empty content", errors)
        require(contract_data["environment"].get("copy_content") is True, "environment must copy content", errors)
        for lane, data in contract_data.items():
            prohibitions = " ".join(data.get("prohibitions", [])).lower()
            require("external models" in prohibitions, f"{lane}: external model prohibition missing", errors)
            require("canonical" in prohibitions, f"{lane}: canonical mutation prohibition missing", errors)

    project = load_json(ROOT / "Skyguard52.uproject")
    states = {entry["Name"]: bool(entry["Enabled"]) for entry in project.get("Plugins", [])}
    for name, expected in CANONICAL_DISABLED.items():
        require(states.get(name) is expected, f"canonical {name} must remain disabled", errors)
    for must_not_be_explicitly_enabled in ("MetaHumanCharacter", "AudioMotorSim", "Soundscape", "PCGGeometryScriptInterop"):
        require(states.get(must_not_be_explicitly_enabled) is not True, f"canonical {must_not_be_explicitly_enabled} unexpectedly enabled", errors)

    all_source = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPT_ROOT.glob("*.ps1"))
    for forbidden in ("UnrealEditor-Cmd.exe", "blender.exe", "AutomationTool.dll", "UnrealBuildTool.dll", "mklink"):
        require(forbidden not in all_source, f"forbidden executable/tool in preparation source: {forbidden}", errors)
    require(not re.search(r"while\s*\([^)]*retry", all_source, flags=re.IGNORECASE), "retry loop detected", errors)

    result = {
        "schema": "skyguard.toolchain-wave08.offline-verification.v1",
        "classification": "PASS" if not errors else "FAILED_WITH_EVIDENCE",
        "contract_count": len(contract_data),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
