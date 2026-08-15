"""Freeze the bounded prelaunch Recovery01 supervisor correction."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOC = ROOT / "Docs/AAA_Review"
OLD = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
NEW = OLD + "_RECOVERY01"
OLD_DOCS = ["CONTRACT", "CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC"]
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01_recovery01"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rec(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"Missing file: {path}")
    return {"absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def write_new(path: Path, value: object) -> None:
    if path.exists():
        raise RuntimeError(f"Fresh artifact exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source_failure = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01.prelaunch-failure.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": "FAILED_WITH_EVIDENCE",
        "failure_stage": "OUTER_SUPERVISOR_PARAMETER_BINDING",
        "failure_message": "A parameter cannot be found that matches parameter name 'AuthorizeSingleUnrealProof'.",
        "unreal_launch_count": 0, "automatic_retries": 0, "governed_namespaces_created": 0,
        "visual_or_runtime_adjudication_performed": False,
        "source_supervisor": rec(ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01/invoke_m01_polyhaven_vegetation_staging02_visual_proof01_once.ps1"),
        "next_gate": "FRESH_RECOVERY01_OUTER_SUPERVISOR_BINDING_CORRECTION",
    }
    failure_path = DOC / f"{OLD}_PRELAUNCH_FAILURE_FREEZE.json"
    write_new(failure_path, source_failure)

    replacements = {
        OLD: NEW,
        "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01": "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY01",
        "M01PolyHavenVegetationStaging02VisualProof01.csv": "M01PolyHavenVegetationStaging02VisualProof01Recovery01.csv",
    }
    created_docs = []
    for suffix in OLD_DOCS:
        source = DOC / f"{OLD}_{suffix}.json"
        value = json.loads(source.read_text(encoding="utf-8"))
        encoded = json.dumps(value, indent=2) + "\n"
        for old, new in replacements.items():
            encoded = encoded.replace(old, new)
        target = DOC / f"{NEW}_{suffix}.json"
        write_new(target, json.loads(encoded))
        created_docs.append(target)

    # Rebind the contract's script records and remove the old circular document locks.
    contract_path = DOC / f"{NEW}_CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    scripts = [
        SCRIPT_ROOT / "capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery01.py",
        SCRIPT_ROOT / "adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery01_once.py",
        SCRIPT_ROOT / "invoke_m01_polyhaven_vegetation_staging02_visual_proof01_recovery01_once.ps1",
    ]
    filtered = []
    for record in contract["locked_inputs"]:
        path = record.get("absolute_path", "")
        if "m01_polyhaven_vegetation_staging02_visual_proof01\\" in path.lower():
            continue
        if any(path.endswith(f"{OLD}_{suffix}.json") for suffix in ("CAMERAS", "VISUAL_RUBRIC", "PERFORMANCE_RUBRIC")):
            continue
        filtered.append(record)
    contract["locked_inputs"] = filtered + [*(rec(path) for path in scripts), *(rec(path) for path in created_docs[1:])]
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    for script in scripts[:2]:
        namespace = runpy.run_path(str(script), run_name="not_main")
        compile(namespace["transform_source"](), str(script) + "::transformed", "exec")
    parse = "$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('" + str(scripts[2]).replace("'", "''") + "',[ref]$null,[ref]$e)|Out-Null;if($e.Count){exit 1}else{exit 0}"
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", parse], check=True)

    classification = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY01_EXECUTION"
    freeze_path = DOC / f"{NEW}_OFFLINE_DESIGN_FREEZE.json"
    binding_path = DOC / f"{NEW}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    members = [*(rec(path) for path in created_docs), *(rec(path) for path in scripts), rec(failure_path), rec(DOC / f"{OLD}_OFFLINE_DESIGN_FREEZE.json"), rec(DOC / f"{OLD}_EXECUTION_PROMPT_BINDING_FREEZE.json"), rec(ROOT / "Production/standing_heavy_process_authorization.json")]
    freeze = {"schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery01-offline-design-freeze.v1", "classification": classification, "created_utc": created, "correction": "FORWARD_AUTHORIZE_SWITCH_AND_USE_FULLY_TRANSFORMED_PROVEN_BASE", "unreal_launches_during_design": 0, "automatic_retries": 0, "members": members, "runtime_promotion": False}
    write_new(freeze_path, freeze)
    binding = {"schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-recovery01-binding-freeze.v1", "classification": classification, "created_utc": created, "members": [rec(contract_path), *(rec(path) for path in scripts), rec(freeze_path), rec(ROOT / "Production/standing_heavy_process_authorization.json")], "one_shot_command": f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {scripts[2]} -AuthorizeSingleUnrealProof", "runtime_promotion": False}
    write_new(binding_path, binding)
    print(json.dumps({"classification": classification, "failure": rec(failure_path), "freeze": rec(freeze_path), "binding": rec(binding_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
