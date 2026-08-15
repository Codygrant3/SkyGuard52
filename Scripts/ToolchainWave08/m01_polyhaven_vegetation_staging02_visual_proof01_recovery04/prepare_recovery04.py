"""Prepare the PowerShell-safe Recovery04 proof binding."""
from __future__ import annotations
import hashlib,json,runpy,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";OLD="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01";NEW=OLD+"_RECOVERY04";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery04"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):
    if not p.is_file():raise RuntimeError(f"Missing: {p}")
    return {"absolute_path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def put(p,v):
    if p.exists():raise RuntimeError(f"Exists: {p}")
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+"\n",encoding="utf-8")
def main():
    failure=DOC/f"{OLD}_RECOVERY03_OFFLINE_DESIGN_ATTEMPT01_TERMINAL_FREEZE.json";created=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    partial=[DOC/f"{OLD}_RECOVERY03_{s}.json" for s in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC")]
    put(failure,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery03-offline-design-attempt01-terminal-freeze.v1","created_utc":created,"classification":"FAILED_WITH_EVIDENCE","unreal_launch_count":0,"automatic_retries":0,"failure_stage":"POWERSHELL_PARSE","failure_message":"Case-insensitive PowerShell hashtable rejected upper/lower token keys as duplicates.","partial_artifacts":[rec(p) for p in partial],"recovery03_scripts":[rec(p) for p in sorted((ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery03").glob("*")) if p.is_file()],"next_gate":"FRESH_RECOVERY04_ORDERED_PAIR_BINDING"})
    replacements={OLD:NEW,"M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01":"M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY04","M01PolyHavenVegetationStaging02VisualProof01.csv":"M01PolyHavenVegetationStaging02VisualProof01Recovery04.csv"};docs=[]
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        text=(DOC/f"{OLD}_{suffix}.json").read_text(encoding="utf-8")
        for old,new in replacements.items():text=text.replace(old,new)
        target=DOC/f"{NEW}_{suffix}.json";put(target,json.loads(text));docs.append(target)
    scripts=[SROOT/"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery04.py",SROOT/"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery04_once.py",SROOT/"invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery04_once.ps1"]
    contract=json.loads(docs[0].read_text(encoding="utf-8"));filtered=[]
    for record in contract["locked_inputs"]:
        path=record.get("absolute_path","")
        if "m01_polyhaven_vegetation_staging02_visual_proof01\\" in path.lower():continue
        if any(path.endswith(f"{OLD}_{s}.json") for s in ("CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC")):continue
        filtered.append(record)
    contract["locked_inputs"]=filtered+[*(rec(p) for p in scripts),*(rec(p) for p in docs[1:])];docs[0].write_text(json.dumps(contract,indent=2)+"\n",encoding="utf-8")
    for p in scripts[:2]:n=runpy.run_path(str(p),run_name="not_main");compile(n["transform_source"](),str(p)+"::transformed","exec")
    parse="$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('"+str(scripts[2]).replace("'","''")+"',[ref]$null,[ref]$e)|Out-Null;if($e.Count){$e|%{$_.Message};exit 1}else{exit 0}";subprocess.run(["powershell.exe","-NoProfile","-Command",parse],check=True)
    cls="PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY04_EXECUTION";freeze=DOC/f"{NEW}_OFFLINE_DESIGN_FREEZE.json";binding=DOC/f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    put(freeze,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery04-offline-design-freeze.v1","classification":cls,"created_utc":created,"correction":"ORDERED_PAIR_PLACEHOLDERS_PLUS_AUTHORIZE_FORWARDING","unreal_launches_during_design":0,"automatic_retries":0,"members":[*(rec(p) for p in docs),*(rec(p) for p in scripts),rec(failure),rec(DOC/f"{OLD}_OFFLINE_DESIGN_FREEZE.json"),rec(DOC/f"{OLD}_EXECUTION_PROMPT_BINDING_FREEZE.json"),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"runtime_promotion":False})
    put(binding,{"schema":"skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery04-binding-freeze.v1","classification":cls,"created_utc":created,"members":[rec(docs[0]),*(rec(p) for p in scripts),rec(freeze),rec(ROOT/"Production/standing_heavy_process_authorization.json")],"one_shot_command":f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {scripts[2]} -AuthorizeSingleUnrealProof","runtime_promotion":False})
    print(json.dumps({"classification":cls,"failure":rec(failure),"freeze":rec(freeze),"binding":rec(binding)},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
