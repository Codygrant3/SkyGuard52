import ast
import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ADJUDICATOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06_postflight\adjudicate_environment_authoring01_recovery06_once.py"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06_postflight\test_environment_authoring01_recovery06_postflight.py"
OFFLINE_FREEZE = ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_OFFLINE_DESIGN_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
RUNTIME = (
    ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06\attempt_01",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_TERMINAL_SUPERVISOR_MANIFEST.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery06.umap"),
)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


require(digest(OFFLINE_FREEZE) == "ea3ad66bf3fa440fdd1802c170ba19bdd6abc4e1fd373034031cc183e28f3632", "Recovery06 offline freeze mismatch")
require(INPUT_MAP.stat().st_size == 8681 and digest(INPUT_MAP) == "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4", "input map mismatch")
source = ADJUDICATOR.read_text(encoding="utf-8")
tests = TESTS.read_text(encoding="utf-8")
ast.parse(source, filename=str(ADJUDICATOR))
ast.parse(tests, filename=str(TESTS))
for token in (
    "def evaluate(",
    "SUCCESS_MANIFEST",
    "director_acquisition",
    "shore_contact_checks",
    "retry_count",
    "automatic_retry_performed",
    "OFFLINE_MAPPED_VISUAL_PROOF_DESIGN",
    "receipt_present",
    "crash_evidence",
    "artifact_integrity_failures",
):
    require(token in source, f"missing adjudication token: {token}")
require("UnrealEditor" not in source and "Start-Process" not in source, "postflight tool contains a heavy launch path")
require("FAILED_WITH_EVIDENCE" in tests and "success_without_receipt" in tests, "bounded failure tests are missing")
for path in RUNTIME:
    require(not path.exists(), f"runtime namespace unexpectedly exists: {path}")
print("PASS")
