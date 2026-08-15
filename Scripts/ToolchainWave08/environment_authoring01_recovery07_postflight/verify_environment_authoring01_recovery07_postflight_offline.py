import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AAA = ROOT / r"Docs\AAA_Review"
ADJUDICATOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07_postflight\adjudicate_environment_authoring01_recovery07_once.py"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07_postflight\test_environment_authoring01_recovery07_postflight.py"
AUTHORING = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\author_m01_environment_authoring01_recovery07.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\invoke_environment_authoring01_recovery07_once.ps1"
OFFLINE_FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_OFFLINE_DESIGN_FREEZE.json"
BINDING = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_EXECUTION_PROMPT_BINDING_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
RUNTIME = (
    ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07\attempt_01",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_ATTEMPT01_POSTFLIGHT.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"),
    AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_ATTEMPT01_TERMINAL_FREEZE.json",
)

EXPECTED = {
    ADJUDICATOR: (23072, "103140642709b3a93216d37002ab9e0ddb64593a5b98f33ad62d37312ea0a914"),
    TESTS: (5267, "02fd0c4138f83dcfe412b4a446ba11a6b32505fe056d97a26b42b14d1eb15411"),
    AUTHORING: (22741, "faf3120733e9fcd3a8c10244a1cf72a9018944422b7a0588689ad892531bb6a1"),
    SUPERVISOR: (18935, "48985d6c578a8f48ee7db0856297bf9b70a22066201e9ce8b3d7ba11abefbd1a"),
    OFFLINE_FREEZE: (4766, "602ba028acb18218ee8596a5a8813085abb65e8b9405adb1b7ff1f848edf44ef"),
    INPUT_MAP: (8681, "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(value, message: str) -> None:
    if not value:
        raise RuntimeError(message)


for path, (expected_bytes, expected_hash) in EXPECTED.items():
    require(path.is_file(), f"required file missing: {path}")
    require(path.stat().st_size == expected_bytes, f"byte-count mismatch: {path}")
    require(digest(path) == expected_hash, f"hash mismatch: {path}")

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
    "verify_execution_binding()",
    "freeze_missing_manifest()",
    "OFFLINE_ONLY_RECOVERY08_CORRECTION_DESIGN",
):
    require(token in source, f"missing adjudication token: {token}")
require("UnrealEditor" not in source and "Start-Process" not in source, "postflight tool contains a heavy launch path")
require("FAILED_WITH_EVIDENCE" in tests and "success_without_receipt" in tests, "bounded failure tests are missing")
require("preserves_partial_output" in tests, "partial-output preservation test is missing")

require(BINDING.is_file(), "Recovery07 execution binding is missing")
binding = json.loads(BINDING.read_text(encoding="utf-8"))
require(
    binding.get("classification") == "PASSED_READY_FOR_EXPLICIT_SINGLE_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_AUTHORIZATION",
    "Recovery07 binding classification mismatch",
)
members = binding.get("members") or []
require(binding.get("member_count") == len(members), "Recovery07 binding member count mismatch")
for expected in members:
    path = Path(expected["path"])
    require(path.is_file(), f"binding member missing: {path}")
    require(path.stat().st_size == int(expected["bytes"]), f"binding member byte mismatch: {path}")
    require(digest(path) == expected["sha256"], f"binding member hash mismatch: {path}")

for path in RUNTIME:
    require(not path.exists(), f"runtime namespace unexpectedly exists: {path}")
print("PASS")
