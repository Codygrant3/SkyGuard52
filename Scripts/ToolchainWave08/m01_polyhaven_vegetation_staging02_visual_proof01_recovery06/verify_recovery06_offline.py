"""Offline verifier for Recovery06 proof design."""
from __future__ import annotations
import hashlib,json,py_compile,runpy
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";NAME="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    contract=DOC/f"{NAME}_CONTRACT.json";data=json.loads(contract.read_text(encoding="utf-8"));locked=data["locked_inputs"]
    paths=[str(row["absolute_path"]).casefold() for row in locked]
    if len(paths)!=15 or len(set(paths))!=15:raise RuntimeError(f"locked_inputs must contain exactly 15 unique paths, got {len(paths)}/{len(set(paths))}")
    for row in locked:
        path=Path(row["absolute_path"])
        if not path.is_file() or path.stat().st_size!=row["bytes"] or sha(path)!=row["sha256"]:raise RuntimeError(f"Locked authority mismatch: {path}")
    rubric=[row for row in locked if str(row["absolute_path"]).endswith("RECOVERY06_VISUAL_RUBRIC.json")]
    if len(rubric)!=1:raise RuntimeError("Recovery06 visual rubric must occur exactly once")
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        json.loads((DOC/f"{NAME}_{suffix}.json").read_text(encoding="utf-8"))
    freeze=DOC/f"{NAME}_OFFLINE_DESIGN_FREEZE.json"
    if freeze.exists():json.loads(freeze.read_text(encoding="utf-8"))
    for script in SROOT.glob("*.py"):py_compile.compile(str(script),doraise=True)
    for script in (SROOT/f"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06.py",SROOT/f"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06_once.py"):
        namespace=runpy.run_path(str(script),run_name="offline_verifier");compile(namespace["transform_source"](),str(script)+"::transformed","exec")
    attempt=ROOT/"Saved/BuildAttempts"/NAME;terminal=ROOT/"Saved/Reports"/f"{NAME}_TERMINAL_SUPERVISOR.json"
    if attempt.exists() or terminal.exists():raise RuntimeError("Governed Recovery06 runtime namespace exists during offline design")
    print(json.dumps({"classification":"PASS","locked_inputs":len(paths),"unique_locked_inputs":len(set(paths)),"visual_rubric_records":len(rubric)},indent=2))
    return 0
if __name__=="__main__":raise SystemExit(main())
