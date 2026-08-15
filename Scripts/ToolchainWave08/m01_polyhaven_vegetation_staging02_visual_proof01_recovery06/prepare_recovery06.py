"""Freeze the Recovery05 immutable-preflight failure and prepare Recovery06.

Recovery06 is derived from the clean Stage02 proof authority.  It deliberately
rebuilds ``locked_inputs`` from unique absolute paths so a transformed stale
rubric record cannot survive into the governed Unreal run.
"""

from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOC = ROOT / "Docs" / "AAA_Review"
REPORT = ROOT / "Saved" / "Reports"
BASE = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
FAILED = BASE + "_RECOVERY05"
NEW = BASE + "_RECOVERY06"
BASE_SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "m01_polyhaven_vegetation_staging02_visual_proof01"
SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"
FAILED_ATTEMPT_ROOT = ROOT / "Saved" / "BuildAttempts" / FAILED
NEW_ATTEMPT_ROOT = ROOT / "Saved" / "BuildAttempts" / NEW
NEW_TERMINAL = REPORT / f"{NEW}_TERMINAL_SUPERVISOR.json"
MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PolyHavenVegetationStaging02.umap")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"Missing immutable authority: {path}")
    return {
        "absolute_path": str(path),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
    }


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise RuntimeError(f"Fresh namespace already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json_new(path: Path, value: object) -> None:
    write_new(path, json.dumps(value, indent=2) + "\n")


def replace_base_tokens(text: str) -> str:
    replacements = (
        (BASE, NEW),
        ("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01", "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06"),
        ("M01PolyHavenVegetationStaging02VisualProof01.csv", "M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv"),
        ("m01_polyhaven_vegetation_staging02_visual_proof01", "m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"),
        ("polyhaven-vegetation-staging02-visual-proof01", "polyhaven-vegetation-staging02-visual-proof01-recovery06"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def capture_binder_source() -> str:
    return r'''"""Bind the clean Stage02 proof executor to fresh Recovery06 evidence paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
SOURCE=Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\capture_m01_polyhaven_vegetation_staging02_visual_proof01.py")
EXPECTED_BYTES=6895
EXPECTED_SHA256="0b2f184a3937bf87c56127957bd36101ae633e3ab3f252beb916291bd6851f96"
REPLACEMENTS=(("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01","M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06"),("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01","M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06"),("M01PolyHavenVegetationStaging02VisualProof01.csv","M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv"))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def transform_source():
    if not SOURCE.is_file() or SOURCE.stat().st_size!=EXPECTED_BYTES or sha256(SOURCE)!=EXPECTED_SHA256:raise RuntimeError("Frozen Stage02 executor binder changed")
    namespace={"__name__":"authority","__file__":str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec"),namespace,namespace)
    source=namespace["transform_source"]()
    for old,new in REPLACEMENTS:
        if old not in source:raise RuntimeError(f"Recovery06 executor token absent: {old}")
        source=source.replace(old,new)
    if "RECOVERY06_RECOVERY06" in source:raise RuntimeError("Duplicate Recovery06 executor suffix")
    return source
if __name__=="__main__":exec(compile(transform_source(),str(SOURCE)+"::recovery06","exec"),globals(),globals())
'''


def adjudicator_binder_source() -> str:
    return r'''"""Bind the clean Stage02 adjudicator to fresh Recovery06 evidence paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
SOURCE=Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_once.py")
EXPECTED_BYTES=2041
EXPECTED_SHA256="7437136494396f93c956bd7a2d729ba5470fc87dfebf767a0f64024c07593c33"
REPLACEMENTS=(("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01","M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06"),("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01","M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06"),("M01PolyHavenVegetationStaging02VisualProof01.csv","M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv"),("m01_polyhaven_vegetation_staging02_visual_proof01","m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"),("polyhaven-vegetation-staging02-visual-proof01","polyhaven-vegetation-staging02-visual-proof01-recovery06"))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def transform_source():
    if not SOURCE.is_file() or SOURCE.stat().st_size!=EXPECTED_BYTES or sha256(SOURCE)!=EXPECTED_SHA256:raise RuntimeError("Frozen Stage02 adjudicator binder changed")
    namespace={"__name__":"authority","__file__":str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec"),namespace,namespace)
    source=namespace["transform_source"]()
    for old,new in REPLACEMENTS:
        if old not in source:raise RuntimeError(f"Recovery06 adjudicator token absent: {old}")
        source=source.replace(old,new)
    if "RECOVERY06_RECOVERY06" in source or "recovery06_recovery06" in source:raise RuntimeError("Duplicate Recovery06 adjudicator suffix")
    return source
if __name__=="__main__":exec(compile(transform_source(),str(SOURCE)+"::recovery06","exec"),globals(),globals())
'''


def supervisor_source() -> str:
    return r'''[CmdletBinding()]
param([switch]$AuthorizeSingleUnrealProof,[switch]$OfflineContractTest,[string]$OfflineEvidenceRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source='D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\invoke_m01_polyhaven_vegetation_staging02_visual_proof01_once.ps1'
$expectedBytes=3410
$expectedSha256='31f0ab182d5334029b44d8c6a07cc9f5af9d44ec500fe3154f6200742d421523'
function Get-LowerSha256([string]$Path){$stream=$null;$algorithm=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$algorithm=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne $algorithm){$algorithm.Dispose()};if($null-ne $stream){$stream.Dispose()}}}
if(-not(Test-Path -LiteralPath $source -PathType Leaf)){throw 'Frozen Stage02 supervisor is missing'}
$item=Get-Item -LiteralPath $source
if($item.Length-ne $expectedBytes-or(Get-LowerSha256 $source)-ne $expectedSha256){throw 'Frozen Stage02 supervisor changed'}
# Child scope prevents the base binder's OfflineContractTest parameter from
# leaking into the authorized Recovery06 invocation.
try{& $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot}catch{}
$transformed=$global:SkyguardTransformedSupervisorSource
if([string]::IsNullOrWhiteSpace($transformed)){throw 'Transformed base supervisor unavailable'}
$pairs=@(
 @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION','__READY__'),
 @('M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01','__UPPER__'),
 @('M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01','__KEBAB__'),
 @('M01PolyHavenVegetationStaging02VisualProof01.csv','__CSV__'),
 @('m01_polyhaven_vegetation_staging02_visual_proof01','__LOWER__'),
 @('polyhaven-vegetation-staging02-visual-proof01','__LOWER_KEBAB__')
)
foreach($pair in $pairs){if(-not $transformed.Contains($pair[0])){throw "Missing Recovery06 source token: $($pair[0])"};$transformed=$transformed.Replace($pair[0],$pair[1])}
$pairs=@(
 @('__READY__','PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06_EXECUTION'),
 @('__UPPER__','M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06'),
 @('__KEBAB__','M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06'),
 @('__CSV__','M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv'),
 @('__LOWER__','m01_polyhaven_vegetation_staging02_visual_proof01_recovery06'),
 @('__LOWER_KEBAB__','polyhaven-vegetation-staging02-visual-proof01-recovery06')
)
foreach($pair in $pairs){$transformed=$transformed.Replace($pair[0],$pair[1])}
if($transformed.Contains('RECOVERY06_RECOVERY06')-or$transformed.Contains('recovery06_recovery06')){throw 'Duplicate Recovery06 suffix'}
if([regex]::Matches($transformed,[regex]::Escape('Start-Process -FilePath $editor')).Count-ne 1){throw 'Transformed supervisor must contain exactly one Unreal launch'}
$block=[ScriptBlock]::Create($transformed)
$arguments=@{}
if($AuthorizeSingleUnrealProof){$arguments['AuthorizeSingleUnrealProof']=$true}
if($OfflineContractTest){$arguments['OfflineContractTest']=$true;if($OfflineEvidenceRoot){$arguments['OfflineEvidenceRoot']=$OfflineEvidenceRoot}}
& $block @arguments
'''


def verifier_source() -> str:
    return r'''"""Offline verifier for Recovery06 proof design."""
from __future__ import annotations
import hashlib,json,py_compile,runpy
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";NAME="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    contract=DOC/f"{NAME}_CONTRACT.json";data=json.loads(contract.read_text(encoding="utf-8"));locked=data["locked_inputs"]
    paths=[str(row["absolute_path"]).casefold() for row in locked]
    if len(paths)!=15 or len(set(paths))!=15:raise RuntimeError(f"locked_inputs must contain exactly 15 unique paths, got {len(paths)}/{len(set(paths))}")
    for row in locked:
        path=Path(row["absolute_path"])
        if not path.is_file() or path.stat().st_size!=row["bytes"] or sha(path)!=row["sha256"]:raise RuntimeError(f"Locked authority mismatch: {path}")
    rubric=[row for row in locked if str(row["absolute_path"]).endswith("RECOVERY06_VISUAL_RUBRIC.json")]
    if len(rubric)!=1:raise RuntimeError("Recovery06 visual rubric must occur exactly once")
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        json.loads((DOC/f"{NAME}_{suffix}.json").read_text(encoding="utf-8"))
    freeze=DOC/f"{NAME}_OFFLINE_DESIGN_FREEZE.json"
    if freeze.exists():json.loads(freeze.read_text(encoding="utf-8"))
    for script in SROOT.glob("*.py"):py_compile.compile(str(script),doraise=True)
    for script in (SROOT/f"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06.py",SROOT/f"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06_once.py"):
        namespace=runpy.run_path(str(script),run_name="offline_verifier");compile(namespace["transform_source"](),str(script)+"::transformed","exec")
    attempt=ROOT/"Saved/BuildAttempts"/NAME;terminal=ROOT/"Saved/Reports"/f"{NAME}_TERMINAL_SUPERVISOR.json"
    if attempt.exists() or terminal.exists():raise RuntimeError("Governed Recovery06 runtime namespace exists during offline design")
    print(json.dumps({"classification":"PASS","locked_inputs":len(paths),"unique_locked_inputs":len(set(paths)),"visual_rubric_records":len(rubric)},indent=2))
    return 0
if __name__=="__main__":raise SystemExit(main())
'''


def assert_powershell_parse(path: Path) -> None:
    escaped = str(path).replace("'", "''")
    command = (
        "$tokens=$null;$errors=$null;"
        f"[Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$tokens,[ref]$errors)|Out-Null;"
        "if($errors.Count){$errors|ForEach-Object{[Console]::Error.WriteLine($_)};exit 1}else{exit 0}"
    )
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], check=True)


def main() -> int:
    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    failure_freeze = DOC / f"{FAILED}_ATTEMPT01_TERMINAL_FREEZE.json"
    if failure_freeze.exists():
        raise RuntimeError(f"Terminal freeze already exists: {failure_freeze}")
    for path in (
        NEW_ATTEMPT_ROOT,
        NEW_TERMINAL,
        DOC / f"{NEW}_CONTRACT.json",
        DOC / f"{NEW}_OFFLINE_DESIGN_FREEZE.json",
        DOC / f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json",
    ):
        if path.exists():
            raise RuntimeError(f"Recovery06 namespace is not fresh: {path}")

    # Freeze the already-completed Recovery05 attempt before creating Recovery06.
    attempt_members = [record(path) for path in sorted(FAILED_ATTEMPT_ROOT.rglob("*")) if path.is_file()]
    failed_contract = json.loads((DOC / f"{FAILED}_CONTRACT.json").read_text(encoding="utf-8"))
    stale_rubrics = [row for row in failed_contract["locked_inputs"] if str(row["absolute_path"]).endswith("RECOVERY05_VISUAL_RUBRIC.json")]
    write_json_new(
        failure_freeze,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery05-attempt01-terminal-freeze.v1",
            "created_utc": created,
            "classification": "FAILED_WITH_EVIDENCE",
            "failure_stage": "IMMUTABLE_PREFLIGHT_DUPLICATE_STALE_VISUAL_RUBRIC_RECORD",
            "failure_message": "Unreal launched once but the executor stopped before map load because the Recovery05 contract contained the same visual-rubric path twice; the first record retained the obsolete 1505-byte authority while the current rubric is 1516 bytes.",
            "root_cause_scope": "OFFLINE_CONTRACT_GENERATION_ONLY",
            "artwork_or_runtime_rejected": False,
            "proof_performed": False,
            "unreal_launch_count": 1,
            "automatic_retries": 0,
            "adjudicator_launch_count": 0,
            "captures_produced": 0,
            "stale_duplicate_locked_records": stale_rubrics,
            "terminal_supervisor": record(REPORT / f"{FAILED}_TERMINAL_SUPERVISOR.json"),
            "attempt_members": attempt_members,
            "failed_contract": record(DOC / f"{FAILED}_CONTRACT.json"),
            "failed_visual_rubric": record(DOC / f"{FAILED}_VISUAL_RUBRIC.json"),
            "map_pre_post_unchanged": record(MAP),
            "next_gate": "FRESH_RECOVERY06_UNIQUE_LOCKED_INPUT_CONTRACT",
        },
    )

    # Create fresh runtime binders and verifier.
    capture = SCRIPT_ROOT / "capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06.py"
    adjudicator = SCRIPT_ROOT / "adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06_once.py"
    supervisor = SCRIPT_ROOT / "invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery06_once.ps1"
    verifier = SCRIPT_ROOT / "verify_recovery06_offline.py"
    write_new(capture, capture_binder_source())
    write_new(adjudicator, adjudicator_binder_source())
    write_new(supervisor, supervisor_source())
    write_new(verifier, verifier_source())

    # Create transformed cameras/rubrics from clean base authorities.
    docs: dict[str, Path] = {}
    for suffix in ("CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC"):
        source = DOC / f"{BASE}_{suffix}.json"
        target = DOC / f"{NEW}_{suffix}.json"
        value = json.loads(replace_base_tokens(source.read_text(encoding="utf-8")))
        write_json_new(target, value)
        docs[suffix] = target

    # Rebuild the contract from the clean base and append each governed proof
    # artifact exactly once.  Do not transform Recovery05's contaminated list.
    base_contract = json.loads((DOC / f"{BASE}_CONTRACT.json").read_text(encoding="utf-8"))
    transformed = json.loads(replace_base_tokens(json.dumps(base_contract)))
    stable_inputs = []
    for row in base_contract["locked_inputs"]:
        path = str(row["absolute_path"])
        if path.casefold().startswith(str(BASE_SCRIPT_ROOT).casefold() + "\\"):
            continue
        if any(path.casefold() == str(DOC / f"{BASE}_{suffix}.json").casefold() for suffix in ("CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC")):
            continue
        stable_inputs.append(row)
    runtime_scripts = [capture, adjudicator, supervisor]
    transformed["locked_inputs"] = stable_inputs + [record(path) for path in runtime_scripts] + [record(docs[suffix]) for suffix in ("CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC")]
    locked_paths = [str(row["absolute_path"]).casefold() for row in transformed["locked_inputs"]]
    if len(locked_paths) != 15 or len(set(locked_paths)) != 15:
        raise RuntimeError(f"Recovery06 locked_inputs are not 15 unique paths: {len(locked_paths)}/{len(set(locked_paths))}")
    contract = DOC / f"{NEW}_CONTRACT.json"
    write_json_new(contract, transformed)

    # Static and exact-host offline validation before freezing design.
    for script in (Path(__file__), capture, adjudicator, verifier):
        py_compile.compile(str(script), doraise=True)
    assert_powershell_parse(supervisor)
    subprocess.run(["python", str(verifier)], check=True)
    with tempfile.TemporaryDirectory(prefix="sg52_recovery06_offline_") as temp:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(supervisor),
                "-OfflineContractTest",
                "-OfflineEvidenceRoot",
                temp,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Recovery06 offline contract test failed ({result.returncode}): {result.stderr}")

    classification = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06_EXECUTION"
    freeze = DOC / f"{NEW}_OFFLINE_DESIGN_FREEZE.json"
    binding = DOC / f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    freeze_members = [
        contract,
        docs["CAMERAS"],
        docs["VISUAL_RUBRIC"],
        docs["PERFORMANCE_RUBRIC"],
        capture,
        adjudicator,
        supervisor,
        verifier,
        Path(__file__),
        failure_freeze,
        DOC / f"{FAILED}_OFFLINE_DESIGN_FREEZE.json",
        DOC / f"{FAILED}_EXECUTION_PROMPT_BINDING_FREEZE.json",
        ROOT / "Production" / "standing_heavy_process_authorization.json",
    ]
    write_json_new(
        freeze,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery06-offline-design-freeze.v1",
            "created_utc": created,
            "classification": classification,
            "correction_scope": "REBUILD_CONTRACT_FROM_CLEAN_BASE_WITH_EXACTLY_15_UNIQUE_LOCKED_INPUT_PATHS",
            "recovery05_failure": record(failure_freeze),
            "locked_input_count": 15,
            "unique_locked_input_count": 15,
            "visual_rubric_locked_record_count": 1,
            "offline_contract_test": "PASS",
            "powershell_5_1_parse": "PASS",
            "python_compile": "PASS",
            "unreal_launches_during_design": 0,
            "automatic_retries": 0,
            "members": [record(path) for path in freeze_members],
            "runtime_promotion": False,
        },
    )
    write_json_new(
        binding,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery06-execution-prompt-binding-freeze.v1",
            "created_utc": created,
            "classification": classification,
            "one_shot_command": f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {supervisor} -AuthorizeSingleUnrealProof",
            "members": [record(contract), record(capture), record(adjudicator), record(supervisor), record(freeze), record(ROOT / "Production" / "standing_heavy_process_authorization.json")],
            "single_unreal_launch": True,
            "automatic_retries": 0,
            "failed_namespace_reuse": False,
            "runtime_promotion": False,
        },
    )
    print(
        json.dumps(
            {
                "classification": classification,
                "recovery05_terminal_freeze": record(failure_freeze),
                "recovery06_offline_freeze": record(freeze),
                "recovery06_binding": record(binding),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
