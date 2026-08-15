"""Offline verifier for the fresh Mission 1 accepted-candidate assembly gate."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
NAMESPACE = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03"
AUTHOR = NAMESPACE / "author_m01_accepted_candidate_assembly03.py"
SUPERVISOR = NAMESPACE / "invoke_m01_accepted_candidate_assembly03_once.py"
CONTRACT = ROOT / "Docs/AAA_Review/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_CONTRACT.json"
FREEZE = ROOT / "Docs/AAA_Review/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_OFFLINE_DESIGN_FREEZE.json"
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_AcceptedCandidateAssembly03.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_TERMINAL_SUPERVISOR.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    require(AUTHOR.is_file() and SUPERVISOR.is_file() and CONTRACT.is_file(), "Offline design member missing")
    ast.parse(AUTHOR.read_text(encoding="utf-8"), filename=str(AUTHOR))
    ast.parse(SUPERVISOR.read_text(encoding="utf-8"), filename=str(SUPERVISOR))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "PASSED_READY_FOR_EXPLICIT_SINGLE_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_AUTHORING", "Contract classification changed")
    author_source = AUTHOR.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    require("M01_AcceptedCandidateAssembly03" in author_source, "Fresh map namespace missing")
    require("M01_ACA03_Corridor_CONTACT" in author_source, "CONTACT correction missing")
    require("set_director_proxy_tiles_hidden" in author_source, "Legacy proxy-tile correction missing")
    require("runtime_promotion\": False" in author_source, "Runtime-promotion prohibition missing")
    require("retries\": 0" in supervisor_source, "Zero-retry evidence missing")
    require(supervisor_source.count("subprocess.Popen(") == 1, "Supervisor must contain exactly one Unreal Popen")
    require("UnrealEditor-Cmd.exe" in supervisor_source, "Frozen editor path missing")
    require("-nullrhi" in supervisor_source.lower(), "Structural authoring must use NullRHI")
    require(not OUTPUT.exists(), "Fresh output map exists before execution")
    require(not ATTEMPT.exists(), "Fresh attempt exists before execution")
    require(not TERMINAL.exists(), "Fresh terminal manifest exists before execution")
    if FREEZE.exists():
        freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        members = freeze.get("members", [])
        for row in members:
            path = Path(row["path"])
            require(path.is_file(), f"Frozen member missing: {path}")
            require(path.stat().st_size == row["bytes"], f"Frozen member bytes changed: {path}")
            require(sha256(path) == row["sha256"], f"Frozen member hash changed: {path}")
    print("PASS_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_OFFLINE_VERIFIER")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAILED_WITH_EVIDENCE: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
