from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
ORIGINAL = PROJECT / "Scripts" / "invoke_p0_core_rifle_method04_stagea_once.ps1"
RECOVERY = PROJECT / "Scripts" / "invoke_p0_core_rifle_method04_stagea_recovery01_once.ps1"
ORIGINAL_SHA256 = "d11e089a25428186d528afbfd430ba7555a16f29d0ccb8c05cbfc824e48049c0"
PRODUCTION_NAMESPACES = (
    PROJECT / "Production" / "Sources" / "core-rifle" / "artist_grade_method_04_grok_blender",
    PROJECT / "Production" / "Attempts" / "core-rifle-artist-grade-method04" / "stage_A_attempt_01",
    PROJECT / "Blender" / "P0_CORE_RIFLE_ARTIST_GRADE_METHOD04" / "stage_A",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def block(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin)
    return text[begin:finish]


def main() -> int:
    errors: list[str] = []
    require(ORIGINAL.is_file(), "missing frozen original supervisor", errors)
    require(RECOVERY.is_file(), "missing Recovery01 supervisor", errors)
    if errors:
        print(json.dumps({"classification": "FAIL", "errors": errors}, indent=2))
        return 1

    original = ORIGINAL.read_text(encoding="utf-8")
    recovery = RECOVERY.read_text(encoding="utf-8")
    require(sha256(ORIGINAL) == ORIGINAL_SHA256, "frozen original hash mismatch", errors)
    require("[switch]$OfflineContractTest" in recovery, "offline test switch missing", errors)
    require("Invoke-GrokAuthenticationProbe" in recovery, "bounded auth probe missing", errors)
    require("Start-Process -FilePath $GrokExe -ArgumentList @(\"models\")" in recovery, "auth probe is not direct Start-Process", errors)
    require("-RedirectStandardOutput $stdoutPath" in recovery, "auth stdout redirection missing", errors)
    require("-RedirectStandardError $stderrPath" in recovery, "auth stderr redirection missing", errors)
    require(
        'Start-Process -FilePath $GrokExe -ArgumentList @("models")' in recovery
        and "-NoNewWindow -PassThru" in recovery
        and "$null = $process.Handle" in recovery
        and "$process.WaitForExit(30000)" in recovery
        and "$process.WaitForExit()" in recovery
        and "$process.Refresh()" in recovery
        and '$exitCode = $process.ExitCode' in recovery
        and '$null -eq $exitCode' in recovery,
        "direct bounded auth exit lifecycle missing",
        errors,
    )
    require("$process.Dispose()" in recovery, "authentication process disposal missing", errors)
    require("Remove-Item Env:XAI_API_KEY" in recovery, "child XAI_API_KEY removal missing", errors)
    require("synthetic_acceptances.warning_only_stderr" in recovery, "warning-only stderr acceptance evidence missing", errors)
    require("System.Web.Script.Serialization.JavaScriptSerializer" in recovery, "Windows PowerShell-safe JSON serializer missing", errors)
    require("function ConvertTo-PlainJsonData" in recovery, "plain JSON data converter missing", errors)
    require("$serializer.Serialize($plainValue)" in recovery, "plain receipt serialization call missing", errors)
    require("Write-Output (Get-Content -LiteralPath $receiptPath -Raw)" in recovery, "offline receipt output path is not serializer-safe", errors)
    require("New-Object System.Text.UTF8Encoding($false)" in recovery, "Windows PowerShell-safe UTF-8 writer missing", errors)
    require("C:\\Users\\chris\\.grok" in recovery, "child GROK_HOME authority missing", errors)
    require('SetEnvironmentVariable("HOME"' not in recovery, "supervisor mutates HOME", errors)
    require("P0_CORE_RIFLE_METHOD04_STAGEA_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json" in recovery, "Recovery01 terminal path missing", errors)
    require("P0_CORE_RIFLE_METHOD04_STAGEA_RECOVERY01_EMERGENCY_RECEIPT.jsonl" in recovery, "Recovery01 emergency path missing", errors)
    require(recovery.count("$BlenderProcess = Start-Process") == 1, "normal Blender launch count changed", errors)
    require(recovery.count("$GrokProcess = Start-Process") == 1, "normal Grok session launch count changed", errors)
    require("retry_count = 0" in recovery, "zero-retry evidence missing", errors)
    require("while ([DateTime]::UtcNow -lt $deadline)" in recovery, "bounded wait missing", errors)

    try:
        require(
            block(original, "$GrokArguments = @(", "    $originalXai =")
            == block(recovery, "$GrokArguments = @(", "    $originalXai ="),
            "normal Grok model-session arguments changed",
            errors,
        )
        original_blender = next(line.strip() for line in original.splitlines() if line.strip().startswith("$BlenderProcess = Start-Process"))
        recovery_blender = next(line.strip() for line in recovery.splitlines() if line.strip().startswith("$BlenderProcess = Start-Process"))
        require(original_blender == recovery_blender, "Blender launch command changed", errors)
    except (ValueError, StopIteration) as exc:
        errors.append(f"static contract extraction failed: {exc}")

    for namespace in PRODUCTION_NAMESPACES:
        require(not namespace.exists(), f"governed production namespace exists: {namespace}", errors)

    forbidden = (
        "RunUAT.bat",
        "AutomationTool.exe",
        "UnrealEditor-Cmd.exe",
        "--always-approve",
    )
    for token in forbidden:
        require(token not in recovery, f"forbidden token present: {token}", errors)

    result = {
        "schema": "skyguard.method04-stagea-recovery01-offline-verifier.v1",
        "classification": "PASS" if not errors else "FAIL",
        "original_sha256": sha256(ORIGINAL),
        "recovery_sha256": sha256(RECOVERY),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
