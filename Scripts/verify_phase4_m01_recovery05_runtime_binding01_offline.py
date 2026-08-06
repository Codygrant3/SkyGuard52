from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(r"D:\Skyguard52")
SCRIPT=ROOT/"Scripts/invoke_phase4_m01_recovery05_runtime_binding01_once.ps1"
FREEZE=ROOT/"Docs/AAA_Review/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
TARGET=ROOT/"Plugins/SkyguardRecovery03NativeRecovery05/Binaries/Win64"
FUTURE=[TARGET,ROOT/"Saved/BuildAttempts/PHASE4_M01_RECOVERY05_RUNTIME_BINDING01/binding_attempt_01",ROOT/"Saved/Reports/PHASE4_M01_RECOVERY05_RUNTIME_BINDING01_TERMINAL_SUPERVISOR_MANIFEST.json",ROOT/"Saved/Reports/PHASE4_M01_RECOVERY05_RUNTIME_BINDING01_EMERGENCY_RECEIPT.jsonl"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def req(x,m):
 if not x:raise AssertionError(m)
def main():
 req(FREEZE.stat().st_size==5587 and sha(FREEZE)=="9aca763d4019d2b071b88575ed7b9e799a627d27c676bb8f04d19d70cd5633c0","accepted freeze mismatch")
 s=SCRIPT.read_text(encoding="utf-8")
 req("Start-Process" not in s,"binding supervisor must launch no child process")
 for token in ("AuthorizeSingleBinding","OfflineContractTest","Invoke-Binding","rollback_manifest.json","No-overwrite violation","copy_count=3","retry_count=0","Assert-NoHeavy"):
  req(token in s,f"missing token: {token}")
 for name in ("UnrealEditor-SkyguardRecovery03NativeRecovery05.dll","UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb","UnrealEditor.modules"):
  req(s.count(name)>=2,f"missing allowlisted file: {name}")
 req("Get-ChildItem -LiteralPath $Destination -File" in s,"unexpected-file validation missing")
 req("Remove-Item -LiteralPath $file -Force" in s,"rollback file removal missing")
 for p in FUTURE:req(not p.exists(),f"future namespace exists: {p}")
 print(json.dumps({"classification":"PASS","child_process_launches":0,"copy_allowlist_count":3,"retry_count":0,"future_namespaces_absent":True},indent=2));return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except Exception as e:print(json.dumps({"classification":"FAIL","error":str(e)},indent=2),file=sys.stderr);raise SystemExit(1)
