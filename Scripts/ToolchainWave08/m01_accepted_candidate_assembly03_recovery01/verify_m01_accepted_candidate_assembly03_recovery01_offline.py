"""Strict offline verifier for the bounded Assembly03 Recovery01 correction."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE_AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03/author_m01_accepted_candidate_assembly03.py"
BASE_SUPERVISOR = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03/invoke_m01_accepted_candidate_assembly03_once.py"
AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03_recovery01/author_m01_accepted_candidate_assembly03_recovery01.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03_recovery01/invoke_m01_accepted_candidate_assembly03_recovery01_once.py"
FAILURE_FREEZE = ROOT / "Docs/AAA_Review/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_ATTEMPT01_TERMINAL_FREEZE.json"
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_AcceptedCandidateAssembly03_Recovery01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_TERMINAL_SUPERVISOR.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    require(BASE_AUTHOR.stat().st_size == 24920 and sha256(BASE_AUTHOR) == "1396ebac2dc3cd5ef605bc266a9b7f3157d306c3cbfa87ebb655e73cd930ae04", "Failed author authority changed")
    require(BASE_SUPERVISOR.stat().st_size == 12561 and sha256(BASE_SUPERVISOR) == "f526c03dc0f822054713e2e6796254623cb1e339068a7bd358cdc9b595787838", "Failed supervisor authority changed")
    require(FAILURE_FREEZE.stat().st_size == 1648 and sha256(FAILURE_FREEZE) == "9a257399acc069ea5cc3eec4e06adb96b717f8d49eb5fbb8793ff21b570acd44", "Attempt01 failure freeze changed")
    ast.parse(AUTHOR.read_text(encoding="utf-8"), filename=str(AUTHOR))
    ast.parse(SUPERVISOR.read_text(encoding="utf-8"), filename=str(SUPERVISOR))
    author = AUTHOR.read_text(encoding="utf-8")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require("copy the accepted StaticMesh object" in author, "Bounded ordering correction missing")
    require("M01_AcceptedCandidateAssembly03_Recovery01" in author, "Fresh output namespace missing")
    require("M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01/attempt_01" in author, "Fresh attempt namespace missing")
    require(supervisor.count("exec(compile(") == 1, "Supervisor binding execution count changed")
    require("M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_TERMINAL_SUPERVISOR" in supervisor, "Fresh terminal namespace missing")
    require(not OUTPUT.exists() and not ATTEMPT.exists() and not TERMINAL.exists(), "Recovery01 governed namespace is not absent")
    print("PASS_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_OFFLINE_VERIFIER")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAILED_WITH_EVIDENCE: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
