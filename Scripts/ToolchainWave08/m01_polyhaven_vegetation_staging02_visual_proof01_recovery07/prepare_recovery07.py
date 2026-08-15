"""Freeze Recovery06's offline-ordering failure and prepare executable Recovery07."""

from __future__ import annotations

import hashlib
import json
import py_compile
import runpy
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOC = ROOT / "Docs" / "AAA_Review"
REPORT = ROOT / "Saved" / "Reports"
BASE = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
FAILED = BASE + "_RECOVERY06"
NEW = BASE + "_RECOVERY07"
BASE_SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "m01_polyhaven_vegetation_staging02_visual_proof01"
FAILED_SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"
SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "m01_polyhaven_vegetation_staging02_visual_proof01_recovery07"
MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PolyHavenVegetationStaging02.umap")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rec(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"Missing authority: {path}")
    return {"absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def put_text(path: Path, text: str) -> None:
    if path.exists():
        raise RuntimeError(f"Fresh namespace already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def put_json(path: Path, value: object) -> None:
    put_text(path, json.dumps(value, indent=2) + "\n")


def replace_tokens(text: str) -> str:
    for old, new in (
        (BASE, NEW),
        ("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01", "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY07"),
        ("M01PolyHavenVegetationStaging02VisualProof01.csv", "M01PolyHavenVegetationStaging02VisualProof01Recovery07.csv"),
        ("m01_polyhaven_vegetation_staging02_visual_proof01", "m01_polyhaven_vegetation_staging02_visual_proof01_recovery07"),
        ("polyhaven-vegetation-staging02-visual-proof01", "polyhaven-vegetation-staging02-visual-proof01-recovery07"),
    ):
        text = text.replace(old, new)
    return text


def ps_parse(path: Path) -> None:
    escaped = str(path).replace("'", "''")
    command = (
        "$tokens=$null;$errors=$null;"
        f"[Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$tokens,[ref]$errors)|Out-Null;"
        "if($errors.Count){$errors|ForEach-Object{[Console]::Error.WriteLine($_)};exit 1}else{exit 0}"
    )
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], check=True)


def main() -> int:
    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    failed_freeze = DOC / f"{FAILED}_OFFLINE_DESIGN_ATTEMPT01_TERMINAL_FREEZE.json"
    contract = DOC / f"{NEW}_CONTRACT.json"
    cameras = DOC / f"{NEW}_CAMERAS.json"
    visual = DOC / f"{NEW}_VISUAL_RUBRIC.json"
    performance = DOC / f"{NEW}_PERFORMANCE_RUBRIC.json"
    freeze = DOC / f"{NEW}_OFFLINE_DESIGN_FREEZE.json"
    binding = DOC / f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    validation = REPORT / f"{NEW}_OFFLINE_VALIDATION_RECEIPT.json"
    attempt = ROOT / "Saved" / "BuildAttempts" / NEW
    terminal = REPORT / f"{NEW}_TERMINAL_SUPERVISOR.json"

    for path in (failed_freeze, contract, cameras, visual, performance, freeze, binding, validation, attempt, terminal):
        if path.exists():
            raise RuntimeError(f"Recovery07 namespace is not fresh: {path}")

    # Freeze the Recovery06 offline-only failure.  It created design files but
    # never created a governed attempt and never launched Unreal.
    failed_members = [rec(path) for path in sorted(FAILED_SCRIPT_ROOT.glob("*")) if path.is_file()]
    failed_members += [
        rec(DOC / f"{FAILED}_{suffix}.json")
        for suffix in ("CONTRACT", "CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC")
    ]
    put_json(
        failed_freeze,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery06-offline-design-attempt01-terminal-freeze.v1",
            "created_utc": created,
            "classification": "FAILED_WITH_EVIDENCE",
            "failure_stage": "OFFLINE_EXACT_HOST_TEST_ORDERING",
            "failure_message": "The clean Recovery06 contract passed 15-of-15 unique locked-input validation, then its inherited exact-host test correctly refused to pass before the required offline-design freeze existed.",
            "contract_uniqueness_validation": "PASS_15_OF_15_UNIQUE_ONE_VISUAL_RUBRIC",
            "unreal_launch_count": 0,
            "automatic_retries": 0,
            "governed_runtime_namespaces_created": 0,
            "members": failed_members,
            "map_unchanged": rec(MAP),
            "next_gate": "RECOVERY07_CREATE_FREEZE_AND_BINDING_BEFORE_EXACT_HOST_TEST",
        },
    )

    # Reuse only source-generator functions from the now-frozen Recovery06
    # preparation file, rebinding every namespace token to Recovery07.
    authority = runpy.run_path(str(FAILED_SCRIPT_ROOT / "prepare_recovery06.py"), run_name="recovery06_generator_authority")
    capture = SCRIPT_ROOT / "capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07.py"
    adjudicator = SCRIPT_ROOT / "adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07_once.py"
    supervisor = SCRIPT_ROOT / "invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07_once.ps1"
    verifier = SCRIPT_ROOT / "verify_recovery07_offline.py"
    put_text(capture, authority["capture_binder_source"]().replace("RECOVERY06", "RECOVERY07").replace("recovery06", "recovery07"))
    put_text(adjudicator, authority["adjudicator_binder_source"]().replace("RECOVERY06", "RECOVERY07").replace("recovery06", "recovery07"))
    put_text(supervisor, authority["supervisor_source"]().replace("RECOVERY06", "RECOVERY07").replace("recovery06", "recovery07"))

    verifier_source = r'''"""Verify the frozen Recovery07 design without creating runtime evidence."""
from __future__ import annotations
import hashlib,json,py_compile,runpy
from pathlib import Path
ROOT=Path(r"D:\Skyguard52");DOC=ROOT/"Docs/AAA_Review";NAME="M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY07";SROOT=ROOT/"Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery07"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    contract=DOC/f"{NAME}_CONTRACT.json";data=json.loads(contract.read_text(encoding="utf-8"));locked=data["locked_inputs"]
    paths=[str(row["absolute_path"]).casefold() for row in locked]
    if len(paths)!=15 or len(set(paths))!=15:raise RuntimeError(f"Expected 15 unique locked inputs; got {len(paths)}/{len(set(paths))}")
    for row in locked:
        path=Path(row["absolute_path"])
        if not path.is_file() or path.stat().st_size!=row["bytes"] or sha(path)!=row["sha256"]:raise RuntimeError(f"Locked authority mismatch: {path}")
    if sum(path.endswith("recovery07_visual_rubric.json") for path in paths)!=1:raise RuntimeError("Recovery07 visual rubric must be locked exactly once")
    for suffix in ("CONTRACT","CAMERAS","VISUAL_RUBRIC","PERFORMANCE_RUBRIC"):
        json.loads((DOC/f"{NAME}_{suffix}.json").read_text(encoding="utf-8"))
    for script in SROOT.glob("*.py"):py_compile.compile(str(script),doraise=True)
    for script in (SROOT/f"capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07.py",SROOT/f"adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery07_once.py"):
        namespace=runpy.run_path(str(script),run_name="verifier");compile(namespace["transform_source"](),str(script)+"::transformed","exec")
    attempt=ROOT/"Saved/BuildAttempts"/NAME;terminal=ROOT/"Saved/Reports"/f"{NAME}_TERMINAL_SUPERVISOR.json"
    if attempt.exists() or terminal.exists():raise RuntimeError("Recovery07 governed namespace already exists")
    print(json.dumps({"classification":"PASS","locked_inputs":15,"unique_locked_inputs":15,"visual_rubric_records":1},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
'''
    put_text(verifier, verifier_source)

    # Fresh docs and contract come only from the clean Stage02 proof authority.
    for suffix, target in (("CAMERAS", cameras), ("VISUAL_RUBRIC", visual), ("PERFORMANCE_RUBRIC", performance)):
        value = json.loads(replace_tokens((DOC / f"{BASE}_{suffix}.json").read_text(encoding="utf-8")))
        put_json(target, value)

    base_contract = json.loads((DOC / f"{BASE}_CONTRACT.json").read_text(encoding="utf-8"))
    value = json.loads(replace_tokens(json.dumps(base_contract)))
    stable = []
    for row in base_contract["locked_inputs"]:
        path = str(row["absolute_path"])
        if path.casefold().startswith(str(BASE_SCRIPT_ROOT).casefold() + "\\"):
            continue
        if any(path.casefold() == str(DOC / f"{BASE}_{suffix}.json").casefold() for suffix in ("CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC")):
            continue
        stable.append(row)
    value["locked_inputs"] = stable + [rec(capture), rec(adjudicator), rec(supervisor), rec(cameras), rec(visual), rec(performance)]
    unique = [str(row["absolute_path"]).casefold() for row in value["locked_inputs"]]
    if len(unique) != 15 or len(set(unique)) != 15:
        raise RuntimeError(f"Contract does not have 15 unique inputs: {len(unique)}/{len(set(unique))}")
    put_json(contract, value)

    # Structural validation precedes freeze creation.
    for path in (Path(__file__), capture, adjudicator, verifier):
        py_compile.compile(str(path), doraise=True)
    ps_parse(supervisor)
    subprocess.run(["python", str(verifier)], check=True)

    classification = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY07_EXECUTION"
    freeze_members = [
        contract, cameras, visual, performance, capture, adjudicator, supervisor, verifier,
        Path(__file__), failed_freeze,
        DOC / f"{BASE}_OFFLINE_DESIGN_FREEZE.json",
        DOC / f"{BASE}_EXECUTION_PROMPT_BINDING_FREEZE.json",
        ROOT / "Production" / "standing_heavy_process_authorization.json",
    ]
    # The inherited supervisor requires these two authorities during its own
    # exact-host test.  They are therefore frozen before that non-heavy test.
    put_json(
        freeze,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery07-offline-design-freeze.v1",
            "created_utc": created,
            "classification": classification,
            "correction_scope": "FREEZE_AND_BINDING_EXIST_BEFORE_INHERITED_EXACT_HOST_TEST",
            "locked_input_count": 15,
            "unique_locked_input_count": 15,
            "visual_rubric_locked_record_count": 1,
            "unreal_launches_during_design": 0,
            "automatic_retries": 0,
            "members": [rec(path) for path in freeze_members],
            "runtime_promotion": False,
        },
    )
    put_json(
        binding,
        {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery07-execution-prompt-binding-freeze.v1",
            "created_utc": created,
            "classification": classification,
            "one_shot_command": f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {supervisor} -AuthorizeSingleUnrealProof",
            "members": [rec(contract), rec(capture), rec(adjudicator), rec(supervisor), rec(freeze), rec(ROOT / "Production" / "standing_heavy_process_authorization.json")],
            "single_unreal_launch": True,
            "automatic_retries": 0,
            "failed_namespace_reuse": False,
            "runtime_promotion": False,
        },
    )

    # Now the exact-host test can validate both required immutable authorities.
    with tempfile.TemporaryDirectory(prefix="sg52_recovery07_offline_") as temp:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(supervisor), "-OfflineContractTest", "-OfflineEvidenceRoot", temp],
            capture_output=True,
            text=True,
            check=False,
        )
        receipt = {
            "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery07-offline-validation-receipt.v1",
            "created_utc": created,
            "classification": "PASS" if result.returncode == 0 else "FAILED_WITH_EVIDENCE",
            "exit_code": result.returncode,
            "exit_code_type": "System.Int32",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "powershell_5_1_parse": "PASS",
            "python_compile": "PASS",
            "static_verifier": "PASS",
            "contract_locked_inputs": 15,
            "contract_unique_locked_inputs": 15,
            "visual_rubric_locked_records": 1,
            "unreal_launch_count": 0,
            "automatic_retries": 0,
            "offline_freeze": rec(freeze),
            "binding_freeze": rec(binding),
        }
        put_json(validation, receipt)
        if result.returncode != 0:
            raise RuntimeError(f"Recovery07 exact-host test failed ({result.returncode}): {result.stderr}")

    print(json.dumps({"classification": classification, "recovery06_failure": rec(failed_freeze), "freeze": rec(freeze), "binding": rec(binding), "validation": rec(validation)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
