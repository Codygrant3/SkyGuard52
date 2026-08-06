import argparse,hashlib,json,sys
from pathlib import Path
def sha(p):
 h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def run(root):
 c=json.loads((root/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY03_OUTPUT_CONTRACT.json").read_text());e=[]
 if c["compatibility"]!={"datum":{"from":"CROSS","to":"PLAIN_AXES"},"render_engine":{"from":"BLENDER_EEVEE_NEXT","to":"BLENDER_EEVEE"},"frozen_sources_modified":False}:e.append("compatibility contract drift")
 for a in c["authority_inputs"]:
  p=root/a["path"]
  if not p.is_file() or p.stat().st_size!=a["bytes"] or sha(p)!=a["sha256"]:e.append("authority drift: "+a["path"])
 s=root/c["authoring_script"]["path"]
 if not s.is_file() or s.stat().st_size!=c["authoring_script"]["bytes"] or sha(s)!=c["authoring_script"]["sha256"]:e.append("script drift")
 text=s.read_text()
 for x in ('DATUM_EMPTY_DISPLAY_TYPE="PLAIN_AXES"','RENDER_ENGINE="BLENDER_EEVEE"','patched["render_contract"]["engine"]=RENDER_ENGINE'): 
  if x not in text:e.append("compatibility marker missing: "+x)
 for k,v in c["claims"].items():
  if v is not False:e.append("false claim: "+k)
 for k,p in c["outputs"].items():
  if (root/p).exists():e.append("output exists: "+k)
 if (root/"Saved/Reports/Phase2Yak52R4Slice01Recovery03Production").exists():e.append("production root exists")
 return c,e
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();c,e=run(a.root)
 print(json.dumps({"status":"PASS_RECOVERY03_READY_NOT_RUN" if not e else "FAIL","errors":e,"blender_launched":False,"unreal_launched":False},indent=2));sys.exit(0 if not e else 1)
