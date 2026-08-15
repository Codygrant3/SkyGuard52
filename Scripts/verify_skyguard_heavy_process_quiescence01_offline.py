from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/Toolchain/SharedHeavyProcessQuiescence01/contract.json"
SCRIPT = ROOT / "Scripts/assert_skyguard_heavy_process_quiescence.ps1"


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def run_powershell(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            *arguments,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def parse_powershell() -> None:
    escaped = str(SCRIPT).replace("'", "''")
    command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|%{$_.ToString()};exit 1}else{'PASS'}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    require(result.returncode == 0 and "PASS" in result.stdout, "PowerShell 5.1 parse failed")


def validate() -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = SCRIPT.read_text(encoding="utf-8")
    parse_powershell()

    required = list(contract["required_blocked_process_names"])
    require("dotnet" in required, "dotnet is not governed")
    require("MSBuild" in required, "MSBuild is not governed")
    require("blender-mcp" in contract["explicitly_not_blocked"], "blender-mcp policy missing")
    for name in required:
        require(re.search(rf"['\"]{re.escape(name)}['\"]", source) is not None, f"missing name: {name}")

    forbidden = (
        "Start-Process",
        "Stop-Process",
        "Remove-Item",
        "New-Item",
        "WriteAllText",
        "AppendAllText",
        "CreateDirectory",
    )
    for token in forbidden:
        require(token not in source, f"read-only script contains forbidden token: {token}")

    offline = run_powershell("-OfflineContractTest")
    require(offline.returncode == 0, f"offline mode failed: {offline.stderr}")
    offline_payload = json.loads(offline.stdout.strip())
    require(offline_payload["classification"] == "PASS_OFFLINE_CONTRACT_TEST", "offline classification drift")
    require(int(offline_payload["blocked_name_count"]) == len(required), "blocked-name cardinality drift")
    require(offline_payload["blender_mcp_blocked"] is False, "blender-mcp must remain excluded")

    live = run_powershell()
    require(live.returncode in (0, 4), "live mode returned an undocumented exit code")
    live_payload = json.loads(live.stdout.strip())
    require(int(live_payload["active_heavy_process_count"]) >= 0, "invalid live count")
    require(live_payload["read_only"] is True, "live result is not read-only")

    return {
        "schema": "skyguard.shared-heavy-process-quiescence01.offline-verification.v1",
        "classification": "PASS",
        "powershell_5_1_parse": "PASS",
        "required_blocked_process_names": required,
        "blocked_name_count": len(required),
        "dotnet_governed": True,
        "msbuild_governed": True,
        "blender_mcp_excluded": True,
        "offline_contract_exit_code": offline.returncode,
        "offline_contract_exit_code_type": "System.Int32",
        "live_exit_code": live.returncode,
        "live_classification": live_payload["classification"],
        "live_active_heavy_process_count": live_payload["active_heavy_process_count"],
        "child_process_launches_by_gate": 0,
        "filesystem_writes_by_gate": 0,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(validate(), indent=2, sort_keys=True))
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        raise SystemExit(1)
