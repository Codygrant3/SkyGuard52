"""Prepare the collision-free Recovery03 proof binding."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOC = ROOT / "Docs/AAA_Review"
OLD = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
NEW = OLD + "_RECOVERY03"
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery03"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def rec(path: Path) -> dict[str, object]:
    if not path.is_file(): raise RuntimeError(f"Missing file: {path}")
    return {"absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
def write_new(path: Path, value: object) -> None:
    if path.exists(): raise RuntimeError(f"Fresh artifact exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    failure = DOC / f"{OLD}_RECOVERY02_OFFLINE_CONTRACT_FAILURE_FREEZE.json"
    write_new(failure, {"schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery02-offline-contract-failure.v1", "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "classification": "FAILED_WITH_EVIDENCE", "unreal_launch_count": 0, "automatic_retries": 0, "failure_stage": "RECOVERY02_OFFLINE_CONTRACT_TEST", "failure_message": "Nested readiness token was replaced twice and was rejected before Unreal launch.", "recovery02_freeze": rec(DOC / f"{OLD}_RECOVERY02_OFFLINE_DESIGN_FREEZE.json"), "recovery02_binding": rec(DOC / f"{OLD}_RECOVERY02_EXECUTION_PROMPT_BINDING_FREEZE.json"), "next_gate": "FRESH_RECOVERY03_SIMULTANEOUS_TOKEN_BINDING"})
    replacements = {OLD: NEW, "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01": "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY03", "M01PolyHavenVegetationStaging02VisualProof01.csv": "M01PolyHavenVegetationStaging02VisualProof01Recovery03.csv"}
    docs=[]
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        text=(DOC/f"{OLD}_{suffix}.json").read_text(encoding="utf-8")
        for old,new in replacements.items(): text=text.replace(old,new)
        target=DOC/f"{NEW}_{suffix}.json"; write_new(target,json.loads(text)); docs.append(target)
    scripts=[SCRIPT_ROOT/"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery03.py",SCRIPT_ROOT/"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery03_once.py",SCRIPT_ROOT/"invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery03_once.ps1"]
    contract=json.loads(docs[0].read_text(encoding="utf-8")); filtered=[]
    for record in contract["locked_inputs"]:
        path=record.get("absolute_path","")
        if "m01_polyhaven_vegetation_staging02_visual_proof01\\" in path.lower(): continue
        if any(path.endswith(f"{OLD}_{s}.json") for s in ("CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC")): continue
        filtered.append(record)
    contract["locked_inputs"]=filtered+[*(rec(p) for p in scripts),*(rec(p) for p in docs[1:])]
    docs[0].write_text(json.dumps(contract,indent=2)+"\n",encoding="utf-8")
    for script in scripts[:2]:
        n=runpy.run_path(str(script),run_name="not_main"); transformed=n["transform_source"](); compile(transformed,str(script)+"::transformed","exec")
    parse="$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('"+str(scripts[2]).replace("'","''")+"',[ref]$null,[ref]$e)|Out-Null;if($e.Count){exit 1}else{exit 0}"
    subprocess.run(["powershell.exe","-NoProfile","-Command",parse],check=True)
    classification="PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY03_EXECUTION"; created=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    freeze=DOC/f"{NEW}_OFFLINE_DESIGN_FREEZE.json"; binding=DOC/f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    write_new(freeze,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery03-offline-design-freeze.v1","classification":classification,"created_utc":created,"correction":"COLLISION_FREE_PLACEHOLDER_SUBSTITUTION_PLUS_AUTHORIZE_FORWARDING","unreal_launches_during_design":0,"automatic_retries":0,"members":[*(rec(p) for p in docs),*(rec(p) for p in scripts),rec(failure),rec(DOC/f"{OLD}_OFFLINE_DESIGN_FREEZE.json"),rec(DOC/f"{OLD}_EXECUTION_PROMPT_BINDING_FREEZE.json"),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"runtime_promotion":False})
    write_new(binding,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery03-binding-freeze.v1","classification":classification,"created_utc":created,"members":[rec(docs[0]),*(rec(p) for p in scripts),rec(freeze),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"one_shot_command":f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {scripts[2]} -AuthorizeSingleUnrealProof","runtime_promotion":False})
    print(json.dumps({"classification":classification,"failure":rec(failure),"freeze":rec(freeze),"binding":rec(binding)},indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
