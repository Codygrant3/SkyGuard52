import ast
import hashlib
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
ADJUDICATOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05_postflight\adjudicate_environment_authoring01_recovery05_once.py"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05_postflight\test_environment_authoring01_recovery05_postflight.py"
OFFLINE_FREEZE = ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_OFFLINE_DESIGN_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
RUNTIME = (
    ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05\attempt_01",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_TERMINAL_SUPERVISOR_MANIFEST.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery05.umap"),
)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def require(value,message):
    if not value: raise RuntimeError(message)

require(digest(ADJUDICATOR)=="ae047e2fbb6f1dcefefcc3cd8838f14e50e5b97bb7861304a49b65bac16cdfdc","adjudicator hash mismatch")
require(digest(TESTS)=="de430ec091897175591adea3c385cf42d530bc69ddc481f79e65c8a5eef9cd7f","tests hash mismatch")
require(digest(OFFLINE_FREEZE)=="9f3e4bc329b16b8d952b88035506ba29bb943aa56eafbb0aa9025eab7731e960","Recovery05 offline freeze mismatch")
require(INPUT_MAP.stat().st_size==8681 and digest(INPUT_MAP)=="5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4","input map mismatch")
source=ADJUDICATOR.read_text(encoding="utf-8")
ast.parse(source,filename=str(ADJUDICATOR))
for token in ("def evaluate(", "SUCCESS_MANIFEST", "director_acquisition", "shore_contact_checks", "retry_count", "automatic_retry_performed", "OFFLINE_MAPPED_VISUAL_PROOF_DESIGN"):
    require(token in source,f"missing adjudication token: {token}")
require("UnrealEditor" not in source and "Start-Process" not in source,"postflight tool contains a heavy launch path")
for path in RUNTIME: require(not path.exists(),f"runtime namespace unexpectedly exists: {path}")
print("PASS")
