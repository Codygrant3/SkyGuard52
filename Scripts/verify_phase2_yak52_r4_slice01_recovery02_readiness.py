"""Offline readiness gate for Yak-52 R4 Slice 01 Recovery02."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BUILD_ID="BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY02"
CONTRACT_REL=Path("Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY02_OUTPUT_CONTRACT.json")
SCRIPT_REL=Path("Scripts/blender_phase2_yak52_r4_slice01_recovery02.py")
FROZEN_REL=Path("Scripts/blender_phase2_yak52_r4_slice01_silhouette.py")
WRAPPER_REL=Path("Scripts/invoke_phase2_yak52_r4_slice01_recovery02.ps1")
REPORT_REL=Path("Saved/Reports/Phase2Yak52R4Slice01Recovery02Readiness")
EXPECTED_PATHS={"build_id","authority_inputs","authority_inputs[]","authority_inputs[].path","authority_inputs[].bytes","authority_inputs[].sha256","authoring_script","authoring_script.sha256","outputs","outputs.blend","outputs.glb","outputs.manifest","outputs.comparison_directory","claims","claims.silhouette_locked"}
SUPPORTED={"PLAIN_AXES","ARROWS","SINGLE_ARROW","CIRCLE","CUBE","SPHERE","CONE","IMAGE"}

def read_json(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8-sig"))
    if not isinstance(v,dict): raise ValueError(p)
    return v
def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def path_exists(d:dict[str,Any],path:str)->bool:
    cur:Any=d; parts=path.split(".")
    for i,part in enumerate(parts):
        if part.endswith("[]"):
            key=part[:-2]
            if not isinstance(cur,dict) or key not in cur:return False
            cur=cur[key]
            if not isinstance(cur,list) or not cur:return False
            rem=".".join(parts[i+1:])
            return not rem or all(isinstance(x,dict) and path_exists(x,rem) for x in cur)
        if not isinstance(cur,dict) or part not in cur:return False
        cur=cur[part]
    return True
def _chain(n:ast.AST,aliases:dict[str,tuple[str,...]])->tuple[str,...]|None:
    if isinstance(n,ast.Name) and n.id in aliases:return aliases[n.id]
    if isinstance(n,ast.Subscript):
        b=_chain(n.value,aliases)
        if b is not None and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str):return b+(n.slice.value,)
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="get" and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):
        b=_chain(n.func.value,aliases)
        if b is not None:return b+(n.args[0].value,)
    return None
def extract_paths(source:str)->set[str]:
    tree=ast.parse(source); aliases={"contract":()}
    for n in ast.walk(tree):
        if isinstance(n,ast.For) and isinstance(n.target,ast.Name):
            c=_chain(n.iter,aliases)
            if c: aliases[n.target.id]=c[:-1]+(c[-1]+"[]",)
    out=set()
    for n in ast.walk(tree):
        c=_chain(n,aliases)
        if c:out.add(".".join(c))
    return out
def validate_data(c:dict[str,Any])->list[str]:
    e=[]
    if c.get("schema")!="skyguard.phase2.yak52-r4-slice01-recovery02-output-contract.v1":e.append("schema mismatch")
    if c.get("build_id")!=BUILD_ID:e.append("build id mismatch")
    if c.get("current_status")!="RECOVERY02_AUTHORING_SOURCE_READY_NOT_RUN":e.append("status must remain ready-not-run")
    r=c.get("recovery_evidence",{})
    if r.get("receipt_status")!="FAILED_BLENDER_EXITED_ZERO_REQUIRED_OUTPUTS_MISSING":e.append("terminal receipt status mismatch")
    if r.get("blender_exit_code")!=0:e.append("terminal exit code mismatch")
    if r.get("required_outputs_created") is not False:e.append("terminal output truth mismatch")
    if r.get("recovery01_terminal") is not True or r.get("recovery01_retry_allowed") is not False:e.append("Recovery01 terminal boundary mismatch")
    comp=c.get("compatibility_contract",{})
    if comp.get("original_enum")!="CROSS":e.append("original enum mismatch")
    if comp.get("replacement_enum")!="PLAIN_AXES":e.append("replacement enum must be PLAIN_AXES")
    if set(comp.get("supported_blender_52_values",[]))!=SUPPORTED:e.append("Blender 5.2 enum set mismatch")
    if comp.get("override_scope")!="create_datums only" or comp.get("frozen_source_modified") is not False:e.append("compatibility scope mismatch")
    declared=set(c.get("frozen_contract_access_manifest",[]))
    if declared!=EXPECTED_PATHS:e.append("contract access manifest mismatch")
    for p in EXPECTED_PATHS:
        if not path_exists(c,p):e.append(f"contract path missing: {p}")
    outputs=c.get("outputs",{}); policy=c.get("output_policy",{}).get("paths",{})
    alias={"blend":policy.get("blend"),"glb":policy.get("glb"),"manifest":policy.get("manifest"),"comparison_directory":policy.get("screenshot_directory")}
    if outputs!=alias:e.append("output alias mismatch")
    if not all(isinstance(v,str) and "recovery02" in v.lower() for v in outputs.values()):e.append("Recovery02 output namespace mismatch")
    for k,v in c.get("claims",{}).items():
        if v is not False:e.append(f"claim must remain false: {k}")
    launch=c.get("launch_contract",{})
    if launch.get("wrapper")!=WRAPPER_REL.as_posix():e.append("wrapper path mismatch")
    if launch.get("launch_authorized") is not False or launch.get("launched") is not False:e.append("launch boundary mismatch")
    return e
def validate_files(root:Path,c:dict[str,Any])->list[str]:
    e=[]
    authorities=c.get("authority_inputs",[])
    if len(authorities)!=12:e.append("authority count mismatch")
    for a in authorities:
        p=root/a.get("path","")
        if not p.is_file():e.append(f"authority missing: {a.get('path')}");continue
        if p.stat().st_size!=a.get("bytes"):e.append(f"authority size drift: {a.get('path')}")
        if sha(p)!=a.get("sha256"):e.append(f"authority hash drift: {a.get('path')}")
    s=root/SCRIPT_REL; a=c.get("authoring_script",{})
    if not s.is_file() or s.stat().st_size!=a.get("bytes") or sha(s)!=a.get("sha256"):e.append("Recovery02 authoring script drift")
    else:
        text=s.read_text(encoding="utf-8")
        for marker in ('DATUM_EMPTY_DISPLAY_TYPE = "PLAIN_AXES"',"frozen.create_datums =","create_datums_blender52","frozen.main()"):
            if marker not in text:e.append(f"compatibility marker missing: {marker}")
        if 'empty_display_type = "CROSS"' in text:e.append("Recovery02 directly retains unsupported CROSS enum")
    frozen=(root/FROZEN_REL).read_text(encoding="utf-8")
    if extract_paths(frozen)!=EXPECTED_PATHS:e.append("frozen source contract access drift")
    w=root/WRAPPER_REL; l=c.get("launch_contract",{})
    if not w.is_file() or w.stat().st_size!=l.get("wrapper_bytes") or sha(w)!=l.get("wrapper_sha256"):e.append("Recovery02 wrapper drift")
    else:
        t=w.read_text(encoding="utf-8")
        for m in ("[switch]$AuthorizeProduction","--background","--factory-startup","-RedirectStandardOutput $stdout","-RedirectStandardError $stderr","launch_receipt.json","SHA256SUMS.txt"):
            if m not in t:e.append(f"wrapper marker missing: {m}")
    attempt=root/c["recovery_evidence"]["recovery01_attempt"]
    receipt=read_json(attempt/"launch_receipt.json")
    stderr=(attempt/"blender.stderr.log").read_text(encoding="utf-8-sig")
    if receipt.get("status")!=r"FAILED_BLENDER_EXITED_ZERO_REQUIRED_OUTPUTS_MISSING" or receipt.get("exit_code")!=0:e.append("Recovery01 receipt content mismatch")
    if 'enum "CROSS" not found' not in stderr or "'PLAIN_AXES'" not in stderr:e.append("Recovery01 stderr enum evidence mismatch")
    return e
def validate_absence(root:Path,c:dict[str,Any])->list[str]:
    e=[]
    for k,p in c.get("outputs",{}).items():
        if (root/p).exists():e.append(f"Recovery02 output must be absent: {k}")
    if (root/"Saved/Reports/Phase2Yak52R4Slice01Recovery02Production").exists():e.append("Recovery02 production root must be absent")
    return e
def run(root:Path)->tuple[dict[str,Any],list[str]]:
    c=read_json(root/CONTRACT_REL); e=validate_data(c)+validate_files(root,c)+validate_absence(root,c)
    if not Path(c["launch_contract"]["blender_executable"]).is_file():e.append("Blender 5.2 executable missing")
    return c,e
def write_report(root:Path,c:dict[str,Any],e:list[str])->Path:
    ch=sha(root/CONTRACT_REL); ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    d=root/REPORT_REL/f"attempt_{ts}_{ch[:8]}_{os.getpid():08x}";d.mkdir(parents=True,exist_ok=False)
    report={"schema":"skyguard.phase2.yak52-r4-slice01-recovery02-readiness-report.v1","build_id":BUILD_ID,"status":"PASS_RECOVERY02_READY_NOT_RUN" if not e else "FAIL_RECOVERY02_NOT_READY","generated_utc":datetime.now(timezone.utc).isoformat(),"contract":{"path":CONTRACT_REL.as_posix(),"bytes":(root/CONTRACT_REL).stat().st_size,"sha256":ch},"replacement_enum":"PLAIN_AXES","recovery01_preserved":True,"blender_launched_by_gate":False,"unreal_launched_by_gate":False,"production_started":False,"errors":e}
    p=d/"recovery02_readiness_report.json";p.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8");(d/"SHA256SUMS.txt").write_text(f"{sha(p)}  {p.name}\n",encoding="utf-8");return p
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument("--no-write",action="store_true");a=ap.parse_args()
    c,e=run(a.root.resolve());result={"build_id":BUILD_ID,"status":"PASS_RECOVERY02_READY_NOT_RUN" if not e else "FAIL_RECOVERY02_NOT_READY","error_count":len(e),"errors":e,"blender_launched_by_gate":False,"unreal_launched_by_gate":False,"production_started":False}
    if not a.no_write:result["report_path"]=str(write_report(a.root.resolve(),c,e).relative_to(a.root.resolve())).replace("\\","/")
    print(json.dumps(result,indent=2,sort_keys=True));return 0 if not e else 1
if __name__=="__main__":sys.exit(main())
