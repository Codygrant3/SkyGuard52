import ast
import hashlib
import re
from pathlib import Path

ROOT=Path(r"D:\Skyguard52")
SOURCE=ROOT/r"Scripts\ToolchainWave08\environment_authoring01_recovery06\author_m01_environment_authoring01_recovery06.py"
SUPERVISOR=ROOT/r"Scripts\ToolchainWave08\environment_authoring01_recovery06\invoke_environment_authoring01_recovery06_once.ps1"
TESTS=ROOT/r"Scripts\ToolchainWave08\environment_authoring01_recovery06\test_environment_authoring01_recovery06_offline.py"
TERMINAL05=ROOT/r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_TERMINAL_FREEZE.json"
INPUT_MAP=Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
FUTURE=(ROOT/r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06\attempt_01",ROOT/r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_TERMINAL_SUPERVISOR_MANIFEST.json",Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery06.umap"))

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def require(v,m):
 if not v:raise RuntimeError(m)

require(digest(SOURCE)=="d077cba756dc59149bc0411c46051aa5ff20acb86ac0f489a53fc1557f8d27c0","source hash mismatch")
require(digest(SUPERVISOR)=="332dbe0c35ad387eb527e8330b706a3f2806ef0bef2703cb3724a5a0fc049acc","supervisor hash mismatch")
require(digest(TESTS)=="9890616439ab523477a89bd5319677c606af4e977db65b1a80a27b43dea62eba","tests hash mismatch")
require(digest(TERMINAL05)=="4fb2b6375021bc74083faccd5c2ad55d5ee1c34119ccfd5853090f347bf0dccb","Recovery05 terminal freeze mismatch")
require(INPUT_MAP.stat().st_size==8681 and digest(INPUT_MAP)=="5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4","input map mismatch")
ast.parse(SOURCE.read_text(encoding="utf-8"),filename=str(SOURCE))
supervisor=SUPERVISOR.read_text(encoding="utf-8")
require(supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor")==1,"launch count is not one")
require('"-ExecutePythonScript=$AttemptAuthoring"' in supervisor,"regular-editor Python mode missing")
require("'-ScriptErrorsAreFatal'" in supervisor,"fatal script errors switch missing")
require("-run=pythonscript" not in supervisor,"commandlet mode remains")
require(not re.search(r"(?i)(for|while)\s*\([^\n]*retry",supervisor),"retry loop exists")
for path in FUTURE:require(not path.exists(),f"future namespace exists: {path}")
authorities={
 r"D:\UE_5.8\Engine\Source\Runtime\SlateCore\Public\Application\SlateApplicationBase.h":"0f2eedbcb0313c6c1c4e87e5231ed04400e883f1e2cf7b7ee31262c1076a4eb3",
 r"D:\UE_5.8\Engine\Source\Runtime\Launch\Private\LaunchEngineLoop.cpp":"c45991a136185130235e507c9bb9ec6e926d4f2006a384b2f61e7e6227742c6f",
 r"D:\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Source\PythonScriptPlugin\Private\EditorUtilities\EditorPythonExecuter.cpp":"ab9eb8f439aad66a18c632e8cda227a2252f737a9e4be8150407f9c6befca8b2",
 r"D:\UE_5.8\Engine\Plugins\Experimental\Water\Source\Editor\Private\WaterBodyActorFactory.cpp":"3b589abc03f0ee959206d43ce10ea7b5fa4248f6fe806060e46a49ec24514308",
}
for path,expected in authorities.items():require(digest(Path(path))==expected,f"installed source mismatch: {path}")
print("PASS")
