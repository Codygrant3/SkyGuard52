"""Verify the frozen Recovery07 design without creating runtime evidence."""
from __future__ import annotations
import hashlib,json,py_compile,runpy
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";NAME="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY07";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery07"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    contract=DOC/f"{NAME}_CONTRACT.json";data=json.loads(contract.read_text(encoding="utf-8"));locked=data["locked_inputs"]
    paths=[str(row["absolute_path"]).casefold() for row in locked]
    if len(paths)!=15 or len(set(paths))!=15:raise RuntimeError(f"Expected 15 unique locked inputs; got {len(paths)}/{len(set(paths))}")
    for row in locked:
        path=Path(row["absolute_path"])
        if not path.is_file() or path.stat().st_size!=row["bytes"] or sha(path)!=row["sha256"]:raise RuntimeError(f"Locked authority mismatch: {path}")
    if sum(path.endswith("recovery07_visual_rubric.json") for path in paths)!=1:raise RuntimeError("Recovery07 visual rubric must be locked exactly once")
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        json.loads((DOC/f"{NAME}_{suffix}.json").read_text(encoding="utf-8"))
    for script in SROOT.glob("*.py"):py_compile.compile(str(script),doraise=True)
    for script in (SROOT/f"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07.py",SROOT/f"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07_once.py"):
        namespace=runpy.run_path(str(script),run_name="verifier");compile(namespace["transform_source"](),str(script)+"::transformed","exec")
    attempt=ROOT/"Saved/BuildAttempts"/NAME;terminal=ROOT/"Saved/Reports"/f"{NAME}_TERMINAL_SUPERVISOR.json"
    if attempt.exists() or terminal.exists():raise RuntimeError("Recovery07 governed namespace already exists")
    print(json.dumps({"classification":"PASS","locked_inputs":15,"unique_locked_inputs":15,"visual_rubric_records":1},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
