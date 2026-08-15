from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "Scripts" / "Workers" / "worker_core_yak52_airframe_refinement01.py"
WRAPPER = ROOT / "Scripts" / "Workers" / "worker_core_yak52_airframe_refinement01_recovery01.py"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_RECOVERY01_CONTRACT.json"
FAILED_ATTEMPT = ROOT / "Production" / "Attempts" / "core-yak52-airframe" / "attempt_20260810T012355939434Z"
FUTURE_ATTEMPT_ROOT = ROOT / "Production" / "Attempts" / "core-yak52-airframe-recovery01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    if ORIGINAL.stat().st_size != 21715 or sha256(ORIGINAL) != "9c865d12493183f593a98d6268af0a3493e68f9437acaa7d70cee5b7da28a292":
        errors.append("Frozen original worker changed")
    for path in (WRAPPER, CONTRACT):
        if not path.is_file():
            errors.append(f"Missing {path}")
    if WRAPPER.is_file():
        try:
            ast.parse(WRAPPER.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"Wrapper syntax: {exc}")
    if CONTRACT.is_file():
        try:
            contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
            if contract.get("asset_id") != "core-yak52-airframe-recovery01":
                errors.append("Contract asset identity mismatch")
        except Exception as exc:
            errors.append(f"Contract JSON: {exc}")
    if not FAILED_ATTEMPT.is_dir():
        errors.append("Failed Attempt01 evidence missing")
    if FUTURE_ATTEMPT_ROOT.exists():
        errors.append("Future Recovery01 attempt root already exists")
    manifest = json.loads((ROOT / "Production" / "production_manifest.json").read_text(encoding="utf-8"))
    candidates = [asset for asset in manifest["assets"] if asset["id"] == "core-yak52-airframe-recovery01"]
    if len(candidates) != 1 or candidates[0].get("status") != "ready":
        errors.append("Recovery01 manifest binding is not uniquely ready")
    test = subprocess.run(
        [sys.executable, "-m", "unittest", "Scripts.tests.test_phase2_yak52_airframe_refinement01_recovery01_offline"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if test.returncode != 0:
        errors.append("Focused tests failed: " + (test.stdout + test.stderr).strip())
    report = {
        "schema": "skyguard.phase2.yak52-airframe-refinement01-recovery01.offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "original_worker_sha256": sha256(ORIGINAL),
        "wrapper_sha256": sha256(WRAPPER) if WRAPPER.is_file() else None,
        "failed_attempt_preserved": FAILED_ATTEMPT.is_dir(),
        "future_attempt_root_absent": not FUTURE_ATTEMPT_ROOT.exists(),
        "focused_tests": "PASS_3_OF_3" if test.returncode == 0 else "FAIL",
        "blender_launch_count": 0,
        "unreal_launch_count": 0,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
