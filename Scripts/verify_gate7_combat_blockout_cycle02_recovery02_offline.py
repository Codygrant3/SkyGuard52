from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
SOURCE = PROJECT / (
    r"References\CombatAssets\CombatBlockout_Cycle02_Recovery02_OfflineDesign"
    r"\source\blender_gate7_combat_blockout_cycle02_recovery02_attempt01.py"
)
OLD_SOURCE = PROJECT / (
    r"References\CombatAssets\CombatBlockout_Cycle02_Recovery01_OfflineDesign"
    r"\source\blender_gate7_combat_blockout_cycle02_recovery01_attempt01.py"
)
SUPERVISOR = PROJECT / r"Scripts\invoke_gate7_combat_blockout_cycle02_recovery02_once.ps1"
CONTRACT = PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_SUPERVISOR_CONTRACT.json"
DIFF = PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_SOURCE_DIFF.json"
PATH_REPORT = PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_PROJECTED_PATH_REPORT.json"
RECONCILIATION = PROJECT / (
    r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_TERMINAL_EVIDENCE_RECONCILIATION.json"
)

AUTHORITIES = {
    PROJECT / r"Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json":
        (2983, "81eb4be461f2a5ecbd55733c25182d352d646f28d9b9201302b12257502073b9"),
    PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01\terminal_manifest.json":
        (3143, "e68a07a513785e003d625aec1a3a858d286a5d4ffbd14f7b278978bc980d77ff"),
    PROJECT / r"Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_OFFLINE_DESIGN_FREEZE.json":
        (1597, "7f277d78100c05c7e725b8669f30d5ddf5ca221285a86a39d789194919e148bc"),
    OLD_SOURCE:
        (19609, "40b3997ebc6075e702ee659722a90503320e019dc13af3c5d5bec67d67f79a71"),
    PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_CONTRACT.json":
        (1651, "172a57c3dddbf08def6d22b04a1835d831cdc4f3629338bf2de8a68ca6942414"),
    PROJECT / r"Docs\AAA_Review\GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_FREEZE.json":
        (16226, "e6f0acc05ed81f397e7f6d98ecce02f060154fe8d6ef694c3fd314fa3eae4ce3"),
    PROJECT / r"Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_ATTEMPT01_TERMINAL_FREEZE.json":
        (2224, "84b989ec02eee076d4f212d98fb49c10a46041190bd20bd17f8739386adeb632"),
    Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"):
        (112975320, "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7"),
}

FUTURE_NAMESPACES = (
    PROJECT / r"Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02\attempt_01",
    PROJECT / r"Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01",
    PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_TERMINAL_SUPERVISOR_MANIFEST.json",
    PROJECT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_EMERGENCY_RECEIPT.jsonl",
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    failures: list[str] = []
    checks: dict[str, object] = {}

    for path, (expected_bytes, expected_hash) in AUTHORITIES.items():
        require(path.is_file(), f"Missing authority: {path}", failures)
        if path.is_file():
            require(path.stat().st_size == expected_bytes, f"Byte mismatch: {path}", failures)
            require(digest(path) == expected_hash, f"Hash mismatch: {path}", failures)

    for json_path in (CONTRACT, DIFF, PATH_REPORT, RECONCILIATION):
        try:
            json.loads(json_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Invalid JSON {json_path}: {exc}")

    require(SOURCE.is_file(), f"Missing Recovery02 source: {SOURCE}", failures)
    require(SOURCE.stat().st_size == 19609, "Recovery02 source byte count changed", failures)
    require(
        digest(SOURCE) == "7123bd7c45ceb6a7fc299b2ac34ab7eb2749bd89cb1ee1cc66b81cb2a31c2b45",
        "Recovery02 source hash changed",
        failures,
    )
    try:
        ast.parse(SOURCE.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        failures.append(f"Recovery02 Python syntax invalid: {exc}")

    old_lines = OLD_SOURCE.read_text(encoding="utf-8").splitlines()
    new_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    changed = [
        (index + 1, before, after)
        for index, (before, after) in enumerate(zip(old_lines, new_lines, strict=True))
        if before != after
    ]
    require(len(changed) == 1, "Source diff is not exactly one changed line", failures)
    if changed:
        _, before, after = changed[0]
        require(
            before == 'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01"',
            "Unexpected source-diff before value",
            failures,
        )
        require(
            after == 'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01"',
            "Unexpected source-diff after value",
            failures,
        )
    require('scene.render.engine = "BLENDER_EEVEE"' in "\n".join(new_lines), "EEVEE binding missing", failures)

    require(SUPERVISOR.is_file(), f"Missing supervisor: {SUPERVISOR}", failures)
    supervisor_text = SUPERVISOR.read_text(encoding="utf-8-sig")
    require(supervisor_text.count("Start-Process") == 1, "Supervisor must contain exactly one Start-Process", failures)
    forbidden_hash_command = "Get-" + "FileHash"
    require(forbidden_hash_command not in supervisor_text, "Supervisor contains forbidden hash cmdlet", failures)
    require("System.Security.Cryptography.SHA256" in supervisor_text, "Internal SHA-256 implementation missing", failures)
    require("System.IO.File" in supervisor_text, "Internal file API missing", failures)
    require("[switch]$OfflineContractTest" in supervisor_text, "Offline contract-test switch missing", failures)
    require("[switch]$AuthorizeSingleBlender" in supervisor_text, "Explicit execution authorization missing", failures)
    require("Write-TerminalEvidence" in supervisor_text, "Terminal evidence lifecycle missing", failures)
    require("EMERGENCY_RECEIPT" in supervisor_text.upper(), "Emergency receipt path missing", failures)
    require("while (-not $process.HasExited" in supervisor_text, "Process polling loop missing", failures)
    require("$process.WaitForExit()" in supervisor_text, "WaitForExit call missing", failures)
    require("$process.Refresh()" in supervisor_text, "Refresh call missing", failures)
    require("retry_count = 0" in supervisor_text, "Zero-retry contract missing", failures)
    require("blender-mcp" not in supervisor_text.lower(), "Supervisor must not launch Blender MCP", failures)
    require("-FilePath $BlenderExecutable" in supervisor_text, "Exact Blender launch binding missing", failures)
    require(
        supervisor_text.find("$State = [ordered]@{") < supervisor_text.find("try {", supervisor_text.find("function Invoke-OfflineTest")),
        "Terminal state is not established before executable lifecycle",
        failures,
    )

    for path in FUTURE_NAMESPACES:
        require(not path.exists(), f"Future governed namespace exists: {path}", failures)

    path_data = json.loads(PATH_REPORT.read_text(encoding="utf-8-sig"))
    require(path_data.get("classification") == "PASS", "Projected path report failed", failures)
    require(path_data.get("longest_characters", 9999) < 240, "Projected path exceeds hard limit", failures)

    checks["authority_count"] = len(AUTHORITIES)
    checks["source_diff_count"] = len(changed)
    checks["future_namespaces_absent"] = all(not path.exists() for path in FUTURE_NAMESPACES)
    checks["supervisor_start_process_count"] = supervisor_text.count("Start-Process")
    result = {
        "classification": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": checks,
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
