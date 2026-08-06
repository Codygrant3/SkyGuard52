from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
R03 = ROOT / "Scripts/build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1"
R04 = ROOT / "Scripts/build_phase4_m01_recovery05_environment_native_build_recovery04_once.ps1"

AUTHORITIES = {
    ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json":
        (4836, "45a520e89726d863a8c64f252df1e7d88205bc9aa30f32df56c1e15ed841c087"),
    ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_OFFLINE_DESIGN_FREEZE.json":
        (6448, "c44c48b496b9d150dd8a7151f54e1e6d3099e84ab202b3fea9e46d3e7c8edca0"),
    R03:
        (21904, "07b94689525496afecb3867ee91898223f32c9b1327d45a709729767dfbd4eb4"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_ATTEMPT01_VIEW_INVENTORY.json":
        (49106, "4e40d2a3cd43aa662489b08538f873e4112a54d6853744f07bf207e4de0b13cc"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_ATTEMPT01_MODULERULES_ANALYSIS.json":
        (1475, "378ffab79356ac50c4dcc3bb1e19cf315f02cc314858b3011478bb6736b3b1d8"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json":
        (54738, "d241f6ecae392d96d18955edb8610fbdfb80518c1f7d85fbbd43084a6b37c1df"),
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp":
        (15032, "73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44"),
}

FUTURE_NAMESPACES = (
    Path(r"D:\SG52M01R04"),
    ROOT / "Saved/BuildAttempts/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04/build_attempt_01",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_EMERGENCY_RECEIPT.jsonl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_file(path: Path, expected_bytes: int, expected_hash: str) -> None:
    if not path.is_file():
        raise AssertionError(f"missing authority: {path}")
    if path.stat().st_size != expected_bytes:
        raise AssertionError(f"byte mismatch: {path}")
    if sha256(path) != expected_hash:
        raise AssertionError(f"hash mismatch: {path}")


def extract_start_process_block(text: str) -> str:
    match = re.search(
        r"(?ms)^\s*\$Process\s*=\s*Start-Process\s+`.*?"
        r"^\s*-RedirectStandardError\s+\$stderr\s*$",
        text,
    )
    if not match:
        raise AssertionError("normal-build Start-Process block missing")
    return match.group(0)


def normalize_recovery(text: str) -> str:
    protected_plugin = "__SKYGUARD_FROZEN_NATIVE_PLUGIN_TOKEN__"
    return (
        text.replace("SkyguardRecovery03NativeRecovery04", protected_plugin)
        .replace("SG52M01R04", "SG52M01R03")
        .replace("RECOVERY04", "RECOVERY03")
        .replace("Recovery04", "Recovery03")
        .replace("recovery04", "recovery03")
        .replace(protected_plugin, "SkyguardRecovery03NativeRecovery04")
    )


def extract_offline_function(text: str) -> tuple[str, str, str]:
    start = text.index("function Invoke-OfflineContractTest {")
    end = text.index("\n}\n\n$State = $null", start) + 2
    return text[:start], text[start:end], text[end:]


def strip_authorized_grouping_probes(function_text: str) -> str:
    probe_start = function_text.index("    $distinctClasses = @(")
    probe_end = function_text.index("    foreach ($path in @(", probe_start)
    stripped = function_text[:probe_start] + function_text[probe_end:]
    property_start = stripped.index("        grouping_tests = [ordered]@{")
    property_end = stripped.index(
        "        governed_namespaces_created = 0",
        property_start,
    )
    return stripped[:property_start] + stripped[property_end:]


def validate_parity_contract() -> int:
    contract_path = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json"
    data = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    records = data.get("records") or data.get("files")
    if not isinstance(records, list) or len(records) != 170:
        raise AssertionError("source-parity contract must contain 170 records")
    for record in records:
        relative = record.get("relative_path") or record.get("path")
        expected_bytes = record.get("bytes")
        expected_hash = record.get("sha256")
        if not relative or expected_bytes is None or not expected_hash:
            raise AssertionError("malformed source-parity record")
        assert_file(ROOT / relative, int(expected_bytes), str(expected_hash))
    return len(records)


def validate_failed_view() -> int:
    inventory_path = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_ATTEMPT01_VIEW_INVENTORY.json"
    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    records = data.get("records") or data.get("files")
    if not isinstance(records, list) or len(records) != 170:
        raise AssertionError("failed-view inventory must contain 170 records")
    view_root = Path(r"D:\SG52M01R03")
    for record in records:
        relative = record.get("relative_path") or record.get("path")
        expected_bytes = record.get("bytes")
        expected_hash = record.get("sha256")
        if not relative or expected_bytes is None or not expected_hash:
            raise AssertionError("malformed failed-view record")
        path = Path(relative)
        if not path.is_absolute():
            path = view_root / path
        assert_file(path, int(expected_bytes), str(expected_hash))
    return len(records)


def validate_supervisor() -> dict[str, object]:
    r03_text = R03.read_text(encoding="utf-8-sig")
    r04_text = R04.read_text(encoding="utf-8-sig")

    if len(re.findall(r"\bStart-Process\b", r04_text, flags=re.IGNORECASE)) != 1:
        raise AssertionError("Recovery04 must contain exactly one Start-Process")
    if r04_text.count("$classes += [pscustomobject][ordered]@{") != 1:
        raise AssertionError("normal ModuleRules collection must contain exactly one PSCustomObject cast")
    if "$classes += [ordered]@{" in r04_text:
        raise AssertionError("uncorrected ModuleRules dictionary append remains")
    if re.search(r"(?m)^\s*\w+\s*=\s*(?:true|false|null)\s*$", r04_text):
        raise AssertionError("bare PowerShell literal remains")
    if "Group-Object class" not in r04_text:
        raise AssertionError("ModuleRules grouping is missing")
    for token in (
        "distinct_duplicate_count",
        "expected_duplicate_name",
        "blank_rejection_count",
        "real_duplicate_count",
        "D:\\SG52M01R03\\Plugins\\SkyguardRecovery03\\Source\\SkyguardRecovery03\\SkyguardRecovery03.Build.cs",
        "D:\\SG52M01R03\\Plugins\\SkyguardRecovery03NativeRecovery05\\Source\\SkyguardRecovery03NativeRecovery05\\SkyguardRecovery03NativeRecovery05.Build.cs",
        "Skyguard52_Recovery04_OfflineContractTest",
        "D:\\SG52M01R04",
        "1200",
        "copy_back_performed = $false",
    ):
        if token not in r04_text:
            raise AssertionError(f"required Recovery04 token missing: {token}")
    for forbidden in (
        "UnrealEditor-Cmd.exe",
        "RunUAT.bat",
        "AutomationTool.exe",
        "Copy-Item",
        "Move-Item",
        "Remove-Item",
    ):
        if forbidden.lower() in r04_text.lower():
            raise AssertionError(f"forbidden executable or mutation path: {forbidden}")

    r03_block = extract_start_process_block(r03_text)
    r04_block = normalize_recovery(extract_start_process_block(r04_text))
    if r04_block != r03_block:
        raise AssertionError("normal-build Start-Process block changed beyond namespace versioning")

    r03_prefix, r03_offline, r03_suffix = extract_offline_function(r03_text)
    r04_prefix, r04_offline, r04_suffix = extract_offline_function(r04_text)
    normalized_non_test = normalize_recovery(r04_prefix + r04_suffix).replace(
        "$classes += [pscustomobject][ordered]@{",
        "$classes += [ordered]@{",
        1,
    )
    if normalized_non_test != r03_prefix + r03_suffix:
        raise AssertionError("non-test supervisor behavior changed outside the exact cast/version allowlist")
    if normalize_recovery(strip_authorized_grouping_probes(r04_offline)) != r03_offline:
        raise AssertionError("offline test changed outside the authorized grouping probes")
    if normalize_recovery(r04_text).count("$classes += [pscustomobject][ordered]@{") != 1:
        raise AssertionError("normalized Recovery04 correction is not singular")

    return {
        "start_process_count": 1,
        "normal_module_record_cast_count": 1,
        "normal_build_block_parity": True,
        "non_test_full_text_parity_after_allowlist": True,
        "offline_test_full_text_parity_after_probe_removal": True,
        "bare_literal_scan": "PASS",
    }


def main() -> int:
    for path, (expected_bytes, expected_hash) in AUTHORITIES.items():
        assert_file(path, expected_bytes, expected_hash)
    parity_count = validate_parity_contract()
    failed_view_count = validate_failed_view()
    for path in FUTURE_NAMESPACES:
        if path.exists():
            raise AssertionError(f"future governed namespace already exists: {path}")
    supervisor = validate_supervisor()
    result = {
        "classification": "PASS",
        "authority_count": len(AUTHORITIES),
        "parity_records": parity_count,
        "failed_view_records": failed_view_count,
        "future_namespaces_absent": True,
        "supervisor": supervisor,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": str(exc)}), file=sys.stderr)
        raise
