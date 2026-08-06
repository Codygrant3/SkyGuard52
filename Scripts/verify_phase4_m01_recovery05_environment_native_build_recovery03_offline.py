from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
REPORTS = ROOT / "Saved" / "Reports"
DOCS = ROOT / "Docs" / "AAA_Review"
SCRIPTS = ROOT / "Scripts"

RECOVERY02_FREEZE = (
    DOCS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SUPERVISOR_ATTEMPT01_TERMINAL_FREEZE.json"
)
OFFLINE02_FREEZE = (
    DOCS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_OFFLINE_DESIGN_FREEZE.json"
)
PARITY_CONTRACT = (
    REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json"
)
SUPERVISOR02 = (
    SCRIPTS
    / "build_phase4_m01_recovery05_environment_native_build_recovery02_once.ps1"
)
SUPERVISOR03 = (
    SCRIPTS
    / "build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1"
)
MISSION_SOURCE = (
    ROOT / "Source" / "Skyguard52" / "SkyguardMission01EnvironmentDirector.cpp"
)

AUTHORITIES = {
    RECOVERY02_FREEZE: (
        4535,
        "61dca86176e04d7a0aef6f3d30488630009d5dbcd4665ea07d070836aad98028",
    ),
    OFFLINE02_FREEZE: (
        4691,
        "6daa7c5f0860174567bd027c43c2e7273fda870e97226bb4fbb728d69b479818",
    ),
    PARITY_CONTRACT: (
        54738,
        "d241f6ecae392d96d18955edb8610fbdfb80518c1f7d85fbbd43084a6b37c1df",
    ),
    SUPERVISOR02: (
        16132,
        "5d42533af89f4223a60531168da446a471a9a26fce50961df4721ef8bc2465dd",
    ),
    MISSION_SOURCE: (
        15032,
        "73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44",
    ),
}

GOVERNED_FUTURE_PATHS = [
    Path(r"D:\SG52M01R03"),
    ROOT
    / "Saved"
    / "BuildAttempts"
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03"
    / "build_attempt_01",
    REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json",
    REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_EMERGENCY_RECEIPT.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def extract_start_process_block(text: str) -> str:
    match = re.search(
        r"(?ms)^\s*\$Process\s*=\s*Start-Process\b.*?"
        r"-RedirectStandardError\s+\$stderr\s*$",
        text,
    )
    require(match is not None, "normal build Start-Process block missing")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def normalize_build_block(text: str) -> str:
    return extract_start_process_block(text).replace("SG52M01R03", "SG52M01R02")


def main() -> int:
    for path, (expected_bytes, expected_hash) in AUTHORITIES.items():
        require(path.is_file(), f"missing authority: {path}")
        require(path.stat().st_size == expected_bytes, f"byte mismatch: {path}")
        require(sha256(path) == expected_hash, f"hash mismatch: {path}")

    terminal_freeze = json.loads(RECOVERY02_FREEZE.read_text(encoding="utf-8-sig"))
    members = list(terminal_freeze["immutable_authorities"]) + list(
        terminal_freeze["attempt_evidence"]
    )
    for record in members:
        path = Path(record["path"])
        require(path.is_file(), f"missing terminal-freeze member: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"byte mismatch: {path}")
        require(sha256(path) == record["sha256"], f"hash mismatch: {path}")

    parity = json.loads(PARITY_CONTRACT.read_text(encoding="utf-8-sig"))
    records = parity.get("records")
    require(isinstance(records, list), "parity records missing")
    require(len(records) == 170, f"expected 170 parity records, got {len(records)}")
    relative_paths: set[str] = set()
    for record in records:
        source = Path(record["source"])
        relative = str(record["relative_path"])
        require(relative not in relative_paths, f"duplicate parity path: {relative}")
        relative_paths.add(relative)
        require(source.is_file(), f"missing parity source: {source}")
        require(
            source.stat().st_size == int(record["bytes"]),
            f"parity byte mismatch: {source}",
        )
        require(sha256(source) == record["sha256"], f"parity hash mismatch: {source}")

    require(SUPERVISOR03.is_file(), f"missing Recovery03 supervisor: {SUPERVISOR03}")
    old_text = SUPERVISOR02.read_text(encoding="utf-8-sig")
    new_text = SUPERVISOR03.read_text(encoding="utf-8-sig")

    require(
        len(re.findall(r"(?m)^\s*\$Process\s*=\s*Start-Process\b", new_text)) == 1,
        "Recovery03 must contain exactly one normal-build Start-Process",
    )
    require(
        normalize_build_block(new_text) == extract_start_process_block(old_text),
        "normal build Start-Process block changed beyond Recovery03 view versioning",
    )
    require(
        not re.search(r"(?m)=\s*(?:true|false|null)\s*(?:#.*)?$", new_text),
        "bare true, false, or null PowerShell value expression found",
    )
    require("[switch]$OfflineContractTest" in new_text, "offline test switch missing")
    require(
        "function Invoke-OfflineContractTest" in new_text,
        "offline contract test function missing",
    )
    require(
        "$ActiveTerminalManifest" in new_text
        and "$ActiveEmergencyReceipt" in new_text,
        "active terminal-evidence routing missing",
    )
    require(
        new_text.index("$State = $null") < new_text.index("try {", new_text.index("$State = $null")),
        "outer try does not follow null state initialization",
    )
    main_try = new_text.index("try {", new_text.index("$State = $null"))
    full_state = new_text.index("$State = [ordered]@{", main_try)
    require(main_try < full_state, "full state construction is not inside the outer try")

    required_literals = [
        "$ViewRoot = 'D:\\SG52M01R03'",
        "-Project=D:\\SG52M01R03\\Skyguard52.uproject",
        "$TimeoutSeconds = 1200",
        "retry_count = 0",
        "automatic_retry = $false",
        "copy_back_performed = $false",
        "unreal_editor_launched = $false",
        "blender_launched = $false",
        "PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION",
    ]
    for literal in required_literals:
        require(literal in new_text, f"required build invariant missing: {literal}")

    forbidden = [
        "AutomationTool.exe",
        "RunUAT.bat",
        "UnrealEditor-Cmd.exe",
        "blender.exe",
        "Copy-Item",
        "Move-Item",
        "Remove-Item",
    ]
    for literal in forbidden:
        require(literal not in new_text, f"forbidden executable or mutation path: {literal}")

    for path in GOVERNED_FUTURE_PATHS:
        require(not path.exists(), f"governed future namespace exists: {path}")

    result = {
        "classification": "PASS",
        "parity_record_count": len(records),
        "terminal_freeze_member_count": len(members),
        "start_process_count": 1,
        "bare_literal_count": 0,
        "normal_build_block_preserved": True,
        "outer_terminal_lifecycle_present": True,
        "offline_contract_test_present": True,
        "future_governed_namespaces_absent": True,
        "build_launched": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
