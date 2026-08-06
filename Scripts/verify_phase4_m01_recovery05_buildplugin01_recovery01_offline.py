from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/build_phase4_m01_recovery05_buildplugin01_recovery01_once.ps1"
FAILED = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_ATTEMPT01_TERMINAL_FREEZE.json"
POST = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_POST_MIGRATION_INVENTORY.json"
FUTURE = [
    Path(r"D:\SG52R05P02"),
    ROOT / "Saved/BuildAttempts/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01/build_attempt_01",
    ROOT / "Saved/BuildAttempts/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01/runtime_attempt_01",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_EMERGENCY_RECEIPT.jsonl",
]

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""): h.update(chunk)
    return h.hexdigest()

def req(ok: bool, message: str) -> None:
    if not ok: raise AssertionError(message)

def main() -> int:
    req(FAILED.stat().st_size==4578 and sha(FAILED)=="c7a9cda8d8bcefabb5b8466f5117ed318d893fb6e90382633b2c234901e73d42","failed freeze mismatch")
    post=json.loads(POST.read_text(encoding="utf-8"))
    req((post["record_count"],post["active_record_count"],post["quarantine_record_count"])==(23,5,18),"inventory counts mismatch")
    for r in post["records"]:
        p=Path(r["current_path"]); req(p.stat().st_size==r["bytes"] and sha(p)==r["sha256"],f"authority mismatch: {p}")
    s=SCRIPT.read_text(encoding="utf-8")
    req(s.count("Start-Process")==1,"exactly one Start-Process required")
    for forbidden in ("AutomationTool.exe","RunUAT.bat","cmd.exe"):
        req(forbidden not in s,f"forbidden launcher: {forbidden}")
    for token in (r"D:\SG52R05P02","OfflineContractTest","Normalize-PackagedDescriptor","EnabledByDefault",
                  "Assert-NumericSuccessExitCode","Assert-PackageOutputs","descriptor_semantic_diff.json",
                  "-TargetPlatforms=Win64","-Rocket","-StrictIncludes","-NoP4","retry_count = 0"):
        req(token in s,f"missing token: {token}")
    req("[System.IO.File]::Replace($temp, $Path, $backup)" in s and "normalize.backup" in s,"atomic replacement missing")
    req("while (-not $process.HasExited" in s,"single-process wait missing")
    req(not re.search(r"\b(retry|rerun)\s*\(",s,re.I),"retry path detected")
    for p in FUTURE: req(not p.exists(),f"future namespace exists: {p}")
    print(json.dumps({"classification":"PASS","start_process_count":1,"retry_count":0,"plugin_records":23,"future_namespaces_absent":True},indent=2))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e:
        print(json.dumps({"classification":"FAIL","error":str(e)},indent=2),file=sys.stderr)
        raise SystemExit(1)
