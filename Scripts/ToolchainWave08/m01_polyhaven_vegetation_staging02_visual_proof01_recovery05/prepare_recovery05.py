"""Freeze Recovery04 false-success and prepare child-scope Recovery05."""
from __future__ import annotations
import hashlib,json,runpy,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";OLD="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01";NEW=OLD+"_RECOVERY05";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery05"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):
    if not p.is_file():raise RuntimeError(f"Missing {p}")
    return {"absolute_path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def put(p,v):
    if p.exists():raise RuntimeError(f"Exists {p}")
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+"\n",encoding="utf-8")
def main():
    created=datetime.now(timezone.utc).isoformat().replace("+00:00","Z");failure=DOC/f"{OLD}_RECOVERY04_FALSE_SUCCESS_TERMINAL_FREEZE.json"
    put(failure,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery04-false-success-terminal-freeze.v1","created_utc":created,"classification":"FAILED_WITH_EVIDENCE","failure_stage":"RECOVERY04_SUPERVISOR_SCOPE_LEAK","failure_message":"Dot-sourced offline exposure leaked OfflineContractTest into Recovery04 scope; authorized call executed offline mode and returned 0 without launching Unreal.","reported_outer_exit_code":0,"unreal_launch_count":0,"governed_namespaces_created":0,"automatic_retries":0,"terminal_supervisor_present":False,"proof_performed":False,"recovery04_freeze":rec(DOC/f"{OLD}_RECOVERY04_OFFLINE_DESIGN_FREEZE.json"),"recovery04_binding":rec(DOC/f"{OLD}_RECOVERY04_EXECUTION_PROMPT_BINDING_FREEZE.json"),"next_gate":"FRESH_RECOVERY05_CHILD_SCOPE_BASE_EXPOSURE"})
    replacements={OLD:NEW,"M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01":"M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY05","M01PolyHavenVegetationStaging02VisualProof01.csv":"M01PolyHavenVegetationStaging02VisualProof01Recovery05.csv"};docs=[]
    for suffix in("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        t=(DOC/f"{OLD}_{suffix}.json").read_text(encoding="utf-8")
        for a,b in replacements.items():t=t.replace(a,b)
        p=DOC/f"{NEW}_{suffix}.json";put(p,json.loads(t));docs.append(p)
    scripts=[SROOT/"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery05.py",SROOT/"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery05_once.py",SROOT/"invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery05_once.ps1"]
    c=json.loads(docs[0].read_text(encoding="utf-8"));f=[]
    for r in c["locked_inputs"]:
        p=r.get("absolute_path","")
        if "m01_polyhaven_vegetation_staging02_visual_proof01\\" in p.lower() or any(p.endswith(f"{OLD}_{s}.json")for s in("CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC")):continue
        f.append(r)
    c["locked_inputs"]=f+[*(rec(p)for p in scripts),*(rec(p)for p in docs[1:])];docs[0].write_text(json.dumps(c,indent=2)+"\n",encoding="utf-8")
    for p in scripts[:2]:n=runpy.run_path(str(p),run_name="not_main");compile(n["transform_source"](),str(p)+"::x","exec")
    q="$e=$null;[Management.Automation.Language.Parser]::ParseFile('"+str(scripts[2]).replace("'","''")+"',[ref]$null,[ref]$e)|Out-Null;if($e.Count){exit 1}else{exit 0}";subprocess.run(["powershell.exe","-NoProfile","-Command",q],check=True)
    cls="PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY05_EXECUTION";freeze=DOC/f"{NEW}_OFFLINE_DESIGN_FREEZE.json";binding=DOC/f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    put(freeze,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery05-offline-design-freeze.v1","classification":cls,"created_utc":created,"correction":"CHILD_SCOPE_BASE_EXPOSURE_PLUS_COLLISION_FREE_SUBSTITUTION","unreal_launches_during_design":0,"automatic_retries":0,"members":[*(rec(p)for p in docs),*(rec(p)for p in scripts),rec(failure),rec(DOC/f"{OLD}_OFFLINE_DESIGN_FREEZE.json"),rec(DOC/f"{OLD}_EXECUTION_PROMPT_BINDING_FREEZE.json"),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"runtime_promotion":False})
    put(binding,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery05-binding-freeze.v1","classification":cls,"created_utc":created,"members":[rec(docs[0]),*(rec(p)for p in scripts),rec(freeze),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"one_shot_command":f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {scripts[2]} -AuthorizeSingleUnrealProof","runtime_promotion":False})
    print(json.dumps({"classification":cls,"failure":rec(failure),"freeze":rec(freeze),"binding":rec(binding)},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
