from __future__ import annotations

import ast
import difflib
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
DOC = ROOT / "Docs/AAA_Review"
REPORT = ROOT / "Saved/Reports"
ISOLATED = Path(r"D:\SG52T08_ENV01")
R01_PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01"
PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY02"
R01_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY01"
CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY02"
R01_CLASS = "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION"
CLASSIFICATION = "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY02_AUTHORIZATION"
R01_SCRIPTS = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01_recovery01"
SCRIPTS = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01_recovery02"
R01_TERMINAL = DOC / f"{R01_PREFIX}_TERMINAL_FREEZE.json"
EXPECTED_R01_TERMINAL_BYTES = 1976
EXPECTED_R01_TERMINAL_SHA256 = "5e806e31cd0367da32cf5139501ca2d04da6eb92fd52ae6a4d447304aeca09c0"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def record(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing record target: {path}")
    try:
        identity = {"file": path.relative_to(ROOT).as_posix()}
    except ValueError:
        identity = {"absolute_path": str(path)}
    return {**identity, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def path_for_record(item: dict[str, Any]) -> Path:
    return Path(item["absolute_path"]) if "absolute_path" in item else ROOT / item["file"]


def verify_record(item: dict[str, Any]) -> None:
    path = path_for_record(item)
    require(path.is_file(), f"Missing authority: {path}")
    require(path.stat().st_size == int(item["bytes"]), f"Byte mismatch: {path}")
    require(sha256_file(path) == item["sha256"], f"Hash mismatch: {path}")


def verify_r01_terminal() -> dict[str, Any]:
    require(R01_TERMINAL.stat().st_size == EXPECTED_R01_TERMINAL_BYTES, "Recovery01 terminal bytes changed")
    require(sha256_file(R01_TERMINAL) == EXPECTED_R01_TERMINAL_SHA256, "Recovery01 terminal hash changed")
    terminal = load_json(R01_TERMINAL)
    require(terminal["classification"] == "FAILED_WITH_EVIDENCE", "Recovery01 terminal classification")
    for item in terminal["members"]:
        verify_record(item)
    return terminal


def future_paths() -> list[Path]:
    return [
        ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01",
        ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01",
        REPORT / f"{PREFIX}_EXECUTION_PREFLIGHT.json",
        REPORT / f"{PREFIX}_TERMINAL_SUPERVISOR.json",
        REPORT / f"{PREFIX}_EMERGENCY_RECEIPT.jsonl",
        REPORT / f"{PREFIX}_POSTFLIGHT.json",
        ISOLATED / "Saved/Profiling/CSV/Recovery07MappedVisualProof01Recovery02.csv",
    ]


def version_source(text: str) -> str:
    replacements = [
        ("environment_authoring01_recovery07_mapped_visual_proof01_recovery01", "environment_authoring01_recovery07_mapped_visual_proof01_recovery02"),
        (R01_PREFIX, PREFIX),
        (R01_ID, CONTRACT_ID),
        ("capture_recovery07_mapped_visual_proof01_recovery01.py", "capture_recovery07_mapped_visual_proof01_recovery02.py"),
        ("invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1", "invoke_recovery07_mapped_visual_proof01_recovery02_once.ps1"),
        ("adjudicate_recovery07_mapped_visual_proof01_recovery01_once.py", "adjudicate_recovery07_mapped_visual_proof01_recovery02_once.py"),
        ("verify_recovery07_mapped_visual_proof01_recovery01_offline.py", "verify_recovery07_mapped_visual_proof01_recovery02_offline.py"),
        ("test_recovery07_mapped_visual_proof01_recovery01.py", "test_recovery07_mapped_visual_proof01_recovery02.py"),
        ("Recovery07MappedVisualProof01Recovery01.csv", "Recovery07MappedVisualProof01Recovery02.csv"),
        (R01_CLASS, CLASSIFICATION),
        ("recovery07-mapped-proof01-recovery01", "recovery07-mapped-proof01-recovery02"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def derive_sources() -> dict[str, tuple[Path, Path]]:
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    pairs = {
        "executor": (R01_SCRIPTS / "capture_recovery07_mapped_visual_proof01_recovery01.py", SCRIPTS / "capture_recovery07_mapped_visual_proof01_recovery02.py"),
        "supervisor": (R01_SCRIPTS / "invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1", SCRIPTS / "invoke_recovery07_mapped_visual_proof01_recovery02_once.ps1"),
        "adjudicator": (R01_SCRIPTS / "adjudicate_recovery07_mapped_visual_proof01_recovery01_once.py", SCRIPTS / "adjudicate_recovery07_mapped_visual_proof01_recovery02_once.py"),
        "verifier": (R01_SCRIPTS / "verify_recovery07_mapped_visual_proof01_recovery01_offline.py", SCRIPTS / "verify_recovery07_mapped_visual_proof01_recovery02_offline.py"),
        "tests": (R01_SCRIPTS / "test_recovery07_mapped_visual_proof01_recovery01.py", SCRIPTS / "test_recovery07_mapped_visual_proof01_recovery02.py"),
    }
    rendered = {name: version_source(source.read_text(encoding="utf-8")) for name, (source, _) in pairs.items()}

    executor = rendered["executor"]
    require('"MAPPED_VISUAL_PROOF01_CONTRACT.json"' in executor, "Recovery01 split contract path changed")
    require('"MAPPED_VISUAL_PROOF01_CAMERAS.json"' in executor, "Recovery01 split cameras path changed")
    executor = executor.replace('"MAPPED_VISUAL_PROOF01_CONTRACT.json"', '"MAPPED_VISUAL_PROOF01_RECOVERY02_CONTRACT.json"', 1)
    executor = executor.replace('"MAPPED_VISUAL_PROOF01_CAMERAS.json"', '"MAPPED_VISUAL_PROOF01_RECOVERY02_CAMERAS.json"', 1)
    rendered["executor"] = executor

    verifier = rendered["verifier"]
    anchor = '    require("csv_stable_polls" in executor_text, "Evidence-driven CSV flush")\n'
    require(anchor in verifier, "Verifier path-check anchor changed")
    verifier = verifier.replace(
        anchor,
        anchor
        + '    require("MAPPED_VISUAL_PROOF01_RECOVERY02_CONTRACT.json" in executor_text, "Recovery02 contract path")\n'
        + '    require("MAPPED_VISUAL_PROOF01_RECOVERY02_CAMERAS.json" in executor_text, "Recovery02 cameras path")\n'
        + '    require("\\\"MAPPED_VISUAL_PROOF01_CONTRACT.json\\\"" not in executor_text, "Stale original contract path")\n'
        + '    require("\\\"MAPPED_VISUAL_PROOF01_CAMERAS.json\\\"" not in executor_text, "Stale original cameras path")\n',
        1,
    )
    rendered["verifier"] = verifier

    tests = rendered["tests"]
    test_anchor = "\n\nif __name__ == \"__main__\":\n"
    require(test_anchor in tests, "Test append anchor changed")
    tests = tests.replace(
        test_anchor,
        '''
    def test_recovery02_executor_uses_versioned_contract_and_cameras(self) -> None:
        executor = (HERE / "capture_recovery07_mapped_visual_proof01_recovery02.py").read_text(encoding="utf-8")
        self.assertIn("MAPPED_VISUAL_PROOF01_RECOVERY02_CONTRACT.json", executor)
        self.assertIn("MAPPED_VISUAL_PROOF01_RECOVERY02_CAMERAS.json", executor)
        self.assertNotIn('"MAPPED_VISUAL_PROOF01_CONTRACT.json"', executor)
        self.assertNotIn('"MAPPED_VISUAL_PROOF01_CAMERAS.json"', executor)


if __name__ == "__main__":
''',
        1,
    )
    rendered["tests"] = tests

    for name, (_, destination) in pairs.items():
        destination.write_text(rendered[name], encoding="utf-8")
        if destination.suffix == ".py":
            ast.parse(rendered[name], filename=str(destination))
    return pairs


def version_json(value: dict[str, Any]) -> dict[str, Any]:
    rendered = json.dumps(value)
    replacements = [
        (R01_PREFIX, PREFIX),
        (R01_ID, CONTRACT_ID),
        ("Recovery07MappedVisualProof01Recovery01.csv", "Recovery07MappedVisualProof01Recovery02.csv"),
        ("FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK_RECOVERY01", "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK_RECOVERY02"),
        ("recovery07-mapped-proof01-recovery01", "recovery07-mapped-proof01-recovery02"),
    ]
    for old, new in replacements:
        rendered = rendered.replace(old, new)
    output = json.loads(rendered)
    require(isinstance(output, dict), "Versioned JSON root")
    return output


def create_contract() -> Path:
    value = version_json(load_json(DOC / f"{R01_PREFIX}_CONTRACT.json"))
    value["created_utc"] = utc_now()
    value["locked_inputs"].append(record(R01_TERMINAL))
    value["correction_scope"].append("restore required selected_lifecycle compatibility and bind executor to the versioned contract/camera files")
    path = DOC / f"{PREFIX}_CONTRACT.json"
    write_json(path, value)
    return path


def create_runtime_report() -> Path:
    value = load_json(DOC / f"{R01_PREFIX}_RUNTIME_COMPATIBILITY_REPORT.json")
    value["schema"] = "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-runtime.v1"
    value["created_utc"] = utc_now()
    value["classification"] = "PASS"
    value["recovery01_terminal_authority"] = record(R01_TERMINAL)
    value["selected_lifecycle"] = "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK"
    value["selected_reason"] = "Full UnrealEditor with deferred ExecCmds Python tick lifecycle; editor-only APIs remain available because -game is forbidden."
    value["rejected_lifecycle"] = "UNREALEDITOR_CMD_EXECUTE_PYTHON_SCRIPT_AUTO_QUIT"
    value["recovery02_corrections"] = [
        "restore selected_lifecycle required by the verifier",
        "bind executor to the Recovery02 contract and camera authorities",
    ]
    path = DOC / f"{PREFIX}_RUNTIME_COMPATIBILITY_REPORT.json"
    write_json(path, value)
    return path


def copy_authority(name: str) -> Path:
    source = DOC / f"{R01_PREFIX}_{name}.json"
    destination = DOC / f"{PREFIX}_{name}.json"
    destination.write_bytes(source.read_bytes())
    require(sha256_file(source) == sha256_file(destination), f"Copy parity failed: {name}")
    return destination


def create_diff(pairs: dict[str, tuple[Path, Path]], contract: Path) -> Path:
    source_diffs = []
    for name, (source, destination) in pairs.items():
        source_diffs.append({
            "name": name,
            "source": record(source),
            "destination": record(destination),
            "unified_diff": list(difflib.unified_diff(source.read_text(encoding="utf-8").splitlines(), destination.read_text(encoding="utf-8").splitlines(), fromfile=str(source), tofile=str(destination), lineterm="")),
        })
    old_contract = load_json(DOC / f"{R01_PREFIX}_CONTRACT.json")
    new_contract = load_json(contract)
    require(old_contract["world"] == new_contract["world"], "World contract changed")
    require(old_contract["capture"] == new_contract["capture"], "Capture contract changed")
    for key in ("warmup_seconds", "measurement_seconds", "minimum_frame_samples", "stable_shader_polls", "csv_flush"):
        require(old_contract["runtime"][key] == new_contract["runtime"][key], f"Runtime bound changed: {key}")
    path = DOC / f"{PREFIX}_SOURCE_DIFF_REPORT.json"
    write_json(path, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-diff.v1",
        "classification": "PASS_BOUNDED_CORRECTION",
        "allowed_changes": ["fresh Recovery02 namespaces", "selected_lifecycle report field", "versioned executor contract/camera paths", "strengthened tests and verifier"],
        "forbidden_semantics_unchanged": {"world": True, "captures": True, "shader_readiness": True, "warmup_measurement": True, "performance": True, "no_save": True, "one_launch_zero_retry": True},
        "source_diffs": source_diffs,
    })
    return path


def create_prompt(freeze: Path, acceptance: Path | None = None) -> Path:
    path = DOC / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    authority = acceptance if acceptance and acceptance.is_file() else freeze
    text = f"""Resume only the canonical Unreal Engine 5.8 / Blender 5.2 AAA project at `D:\\Skyguard52`. Do not use Three.js, external/generated substitutes, external AI models, or subagents.

Treat Recovery01 as immutable and terminal. Treat this Recovery02 authority as the sole execution authority:

- File: `{authority}`
- Bytes: `{authority.stat().st_size}`
- SHA-256: `{sha256_file(authority)}`
- Classification: `{CLASSIFICATION}`

I explicitly authorize exactly one Recovery07 Mapped Visual Proof01 Recovery02 Unreal execution and its mandatory postflight adjudicator by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\\Skyguard52\\Scripts\\ToolchainWave08\\environment_authoring01_recovery07_mapped_visual_proof01_recovery02\\invoke_recovery07_mapped_visual_proof01_recovery02_once.ps1 -AuthorizeSingleUnrealProof`

Verify the Recovery02 terminal authority, offline freeze, prompt binding, all members, exact authored map/dependencies, full UE 5.8 editor, zero heavy processes and absence of every future Recovery02 namespace. Launch full `UnrealEditor.exe` exactly once without `-game`, with D3D12 SM6, deferred `-ExecCmds=py`, `-csvCompression=0`, one heavy process, zero retries and no namespace reuse.

Require the exact 59-actor map, real terrain material, sixteen landscape resources, empty compile queues, two stable readiness polls, 30-second warmup, 30-second capture-free measurement, at least 900 samples, stable nonempty CSV evidence, then exactly five static and three temporal 2560x1440 captures. Preserve process, log, CSV, frame, heartbeat, capture, restoration/no-mutation, terminal and mandatory postflight evidence. Never save or mutate the world.

On automatic pass inspect all eight original images directly at full resolution and classify `PASSED_RECOVERY07_MAPPED_VISUAL_PROOF_ACCEPTED` or `FAILED_WITH_EVIDENCE`. Do not integrate, promote, package or claim Mission 1/AAA completion.
"""
    write_text(path, text)
    return path


def run_command(arguments: list[str]) -> dict[str, Any]:
    completed = subprocess.run(arguments, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def validate(pairs: dict[str, tuple[Path, Path]], provisional: bool) -> dict[str, Any]:
    supervisor = pairs["supervisor"][1]
    tests = pairs["tests"][1]
    verifier = pairs["verifier"][1]
    parse_command = "$e=$null;$t=$null;[System.Management.Automation.Language.Parser]::ParseFile('" + str(supervisor) + "',[ref]$t,[ref]$e)|Out-Null;if($e.Count-ne0){$e|ForEach-Object{$_.Message};exit 1};exit 0"
    checks = {
        "powershell_51_parse": run_command(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", parse_command]),
        "unit_tests": run_command([os.fspath(Path(os.sys.executable)), "-m", "unittest", "-v", os.fspath(tests)]),
    }
    with tempfile.TemporaryDirectory(prefix="sg52_r07_proof_r02_") as temporary:
        checks["supervisor_offline_contract"] = run_command(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.fspath(supervisor), "-OfflineContractTest", "-OfflineEvidenceRoot", temporary])
    checks["independent_verifier"] = run_command([os.fspath(Path(os.sys.executable)), os.fspath(verifier)])
    passed = all(check["exit_code"] == 0 for check in checks.values())
    result = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-validation.v1",
        "created_utc": utc_now(),
        "classification": "PASS" if passed else "FAILED_WITH_EVIDENCE",
        "phase": "provisional" if provisional else "final",
        "checks": checks,
        "unreal_launched": False,
        "blender_launched": False,
    }
    require(passed, json.dumps(result, indent=2))
    return result


def build() -> dict[str, Any]:
    verify_r01_terminal()
    for path in future_paths():
        require(not path.exists(), f"Future Recovery02 namespace exists: {path}")
    pairs = derive_sources()
    contract = create_contract()
    cameras = copy_authority("CAMERAS")
    visual = copy_authority("VISUAL_RUBRIC")
    performance = copy_authority("PERFORMANCE_RUBRIC")
    runtime = create_runtime_report()
    diff = create_diff(pairs, contract)
    audit = DOC / f"PHASE1_8_COMPLETION_AUDIT_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    matrix = DOC / f"M01_PRODUCTION_VERTICAL_SLICE_ACCEPTANCE_MATRIX_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    write_text(audit, f"# Phase 1-8 audit addendum — mapped Proof01 Recovery02\n\n- Recovery01 terminal: `{EXPECTED_R01_TERMINAL_SHA256}`.\n- Recovery02 restores `selected_lifecycle` and binds the executor to versioned contract/camera files.\n- No Unreal or Blender process ran.\n- Classification: `{CLASSIFICATION}`.\n")
    write_text(matrix, "# Mission 1 acceptance matrix — mapped Proof01 Recovery02\n\n| Requirement | State |\n|---|---|\n| Recovery07 authored map | automatic pass, visual proof pending |\n| Recovery01 | immutable failed offline validation |\n| Recovery02 offline correction | pass |\n| Unreal mapped proof | requires separate explicit authorization |\n| Human full-resolution review | pending |\n")

    freeze = DOC / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
    binding = DOC / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    prompt = DOC / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    write_json(freeze, {"schema": "provisional", "classification": CLASSIFICATION, "members": []})
    create_prompt(freeze)
    write_json(binding, {"schema": "provisional", "classification": CLASSIFICATION, "members": [record(freeze), record(prompt)]})
    provisional_result = REPORT / f"{PREFIX}_PROVISIONAL_VALIDATION.json"
    write_json(provisional_result, validate(pairs, True))

    source_files = [destination for _, destination in pairs.values()] + [Path(__file__).resolve()]
    inventory = REPORT / f"{PREFIX}_SOURCE_INVENTORY.json"
    readiness = REPORT / f"{PREFIX}_READINESS.json"
    design_files = [contract, cameras, visual, performance, runtime, diff, audit, matrix, provisional_result] + source_files
    write_json(inventory, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-inventory.v1",
        "created_utc": utc_now(),
        "recovery01_terminal": record(R01_TERMINAL),
        "design_files": [record(path) for path in design_files],
        "future_namespaces_created": False,
    })
    write_json(readiness, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-readiness.v1",
        "created_utc": utc_now(),
        "classification": CLASSIFICATION,
        "selected_lifecycle_present": True,
        "versioned_executor_authorities": True,
        "full_editor_without_game_mode": True,
        "uncompressed_stable_csv": True,
        "future_namespaces_absent": True,
        "unreal_launched": False,
        "blender_launched": False,
    })
    members = [record(R01_TERMINAL)] + [record(path) for path in design_files + [inventory, readiness]]
    write_json(freeze, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-offline-freeze.v1",
        "created_utc": utc_now(),
        "classification": CLASSIFICATION,
        "contract_id": CONTRACT_ID,
        "member_count": len(members),
        "members": members,
        "recovery01_preserved": True,
        "future_namespaces_absent": True,
        "unreal_launched": False,
        "blender_launched": False,
    })
    prompt = create_prompt(freeze)
    write_json(binding, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-prompt-binding.v1",
        "created_utc": utc_now(),
        "classification": CLASSIFICATION,
        "contract_id": CONTRACT_ID,
        "members": [record(freeze), record(prompt)],
        "single_unreal_launch": True,
        "mandatory_postflight_adjudicator": True,
        "human_full_resolution_review_required": True,
    })
    final_validation = REPORT / f"{PREFIX}_FINAL_INDEPENDENT_VALIDATION.json"
    write_json(final_validation, validate(pairs, False))
    acceptance = DOC / f"{PREFIX}_TERMINAL_READINESS_FREEZE.json"
    write_json(acceptance, {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery02-terminal-readiness.v1",
        "created_utc": utc_now(),
        "classification": CLASSIFICATION,
        "members": [record(R01_TERMINAL), record(freeze), record(binding), record(final_validation)],
        "unreal_launched": False,
        "blender_launched": False,
        "next_gate": "EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY02_AUTHORIZATION",
    })
    return {
        "classification": CLASSIFICATION,
        "terminal_readiness_freeze": record(acceptance),
        "offline_freeze": record(freeze),
        "prompt_binding": record(binding),
        "execution_prompt": record(prompt),
        "member_count": len(members),
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
