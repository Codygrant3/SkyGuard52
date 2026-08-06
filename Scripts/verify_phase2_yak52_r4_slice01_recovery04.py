import argparse,hashlib,json,sys
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(root):
 c=json.loads((root/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY04_OUTPUT_CONTRACT.json").read_text());e=[]
 expected={"datum":{"from":"CROSS","to":"PLAIN_AXES"},"render_engine":{"from":"BLENDER_EEVEE_NEXT","to":"BLENDER_EEVEE"},"world":{"precondition":"scene.world is None","action":"create WORLD_R4S01_Recovery04 and assign to scene.world before frozen configure_render"},"frozen_sources_modified":False}
 if c["compatibility"]!=expected:e.append("compatibility contract drift")
 for a in c["authority_inputs"]:
  p=root/a["path"]
  if not p.is_file() or p.stat().st_size!=a["bytes"] or sha(p)!=a["sha256"]:e.append("authority drift: "+a["path"])
 for key in ("authoring_script","launch_wrapper"):
  a=c[key];p=root/a["path"]
  if not p.is_file() or p.stat().st_size!=a["bytes"] or sha(p)!=a["sha256"]:e.append(key+" drift")
 text=(root/c["authoring_script"]["path"]).read_text()
 for m in ('o.empty_display_type="PLAIN_AXES"','patched["render_contract"]["engine"]="BLENDER_EEVEE"','if scene.world is None:scene.world=m.bpy.data.worlds.new("WORLD_R4S01_Recovery04")'):
  if m not in text:e.append("marker missing: "+m)
 wrapper=(root/c["launch_wrapper"]["path"]).read_text()
 for m in ("[System.Collections.Generic.List[string]]::new()","$lines.Add","WriteAllLines"):
  if m not in wrapper:e.append("checksum marker missing: "+m)
 for k,v in c["claims"].items():
  if v is not False:e.append("false claim: "+k)
 for k,p in c["outputs"].items():
  if (root/p).exists():e.append("output exists: "+k)
 if (root/"Saved/Reports/Phase2Yak52R4Slice01Recovery04Production").exists():e.append("production root exists")
 return c,e
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();c,e=run(a.root)
 print(json.dumps({"status":"PASS_RECOVERY04_READY_NOT_RUN" if not e else "FAIL","errors":e,"blender_launched":False,"unreal_launched":False},indent=2));sys.exit(0 if not e else 1)
