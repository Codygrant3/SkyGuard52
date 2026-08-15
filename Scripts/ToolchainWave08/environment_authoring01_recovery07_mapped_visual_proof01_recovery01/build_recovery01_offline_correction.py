"""Derive and freeze a bounded pre-launch correction to mapped Proof01.

The accepted original offline design is never edited.  Recovery01 removes the
full-editor-incompatible ``-game`` switch, forces uncompressed CSV output, and
waits for a stable, nonempty CSV file instead of using a blind flush delay.
"""

from __future__ import annotations

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
ISOLATED = Path(r"D:\SG52T08_ENV01")
ENGINE = Path(r"D:\UE_5.8")
ORIGINAL_PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01"
PREFIX = ORIGINAL_PREFIX + "_RECOVERY01"
ORIGINAL_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01"
CONTRACT_ID = ORIGINAL_ID + "-RECOVERY01"
CLASSIFICATION = "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION"
ORIGINAL_SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01"
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01_recovery01"
DOC_ROOT = ROOT / "Docs/AAA_Review"
REPORT_ROOT = ROOT / "Saved/Reports"
ORIGINAL_FREEZE = DOC_ROOT / f"{ORIGINAL_PREFIX}_OFFLINE_DESIGN_FREEZE.json"
ORIGINAL_BINDING = DOC_ROOT / f"{ORIGINAL_PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
EXPECTED_ORIGINAL_FREEZE = "10671bb9a836199c574c273a3e6401f24057a286a983a9756abd1f463a16ca31"
EXPECTED_ORIGINAL_BINDING = "7a897251cd8bce2893d31360385ab6dc842d0b7bda6883e10b8108cd3861877f"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def record(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing file: {path}")
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return {
            "absolute_path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return {
        "file": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def record_path(item: dict[str, Any]) -> Path:
    return Path(item["absolute_path"]) if "absolute_path" in item else ROOT / item["file"]


def verify_record(item: dict[str, Any]) -> None:
    path = record_path(item)
    require(path.is_file(), f"Missing frozen member: {path}")
    require(path.stat().st_size == int(item["bytes"]), f"Byte mismatch: {path}")
    require(sha256_file(path) == item["sha256"], f"Hash mismatch: {path}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def verify_original_authority() -> tuple[dict[str, Any], dict[str, Any]]:
    require(ORIGINAL_FREEZE.stat().st_size == 12885, "Original freeze byte count changed")
    require(sha256_file(ORIGINAL_FREEZE) == EXPECTED_ORIGINAL_FREEZE, "Original freeze hash changed")
    require(ORIGINAL_BINDING.stat().st_size == 1255, "Original binding byte count changed")
    require(sha256_file(ORIGINAL_BINDING) == EXPECTED_ORIGINAL_BINDING, "Original binding hash changed")
    freeze = load_json(ORIGINAL_FREEZE)
    binding = load_json(ORIGINAL_BINDING)
    for item in freeze["members"] + binding["members"]:
        verify_record(item)
    return freeze, binding


def version_text(text: str) -> str:
    text = text.replace(
        "environment_authoring01_recovery07_mapped_visual_proof01",
        "environment_authoring01_recovery07_mapped_visual_proof01_recovery01",
    )
    text = text.replace(ORIGINAL_PREFIX, PREFIX)
    text = text.replace(ORIGINAL_ID, CONTRACT_ID)
    text = text.replace(
        "invoke_recovery07_mapped_visual_proof01_once.ps1",
        "invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1",
    )
    text = text.replace(
        "adjudicate_recovery07_mapped_visual_proof01_once.py",
        "adjudicate_recovery07_mapped_visual_proof01_recovery01_once.py",
    )
    text = text.replace(
        "Recovery07MappedVisualProof01.csv",
        "Recovery07MappedVisualProof01Recovery01.csv",
    )
    text = text.replace(
        "recovery07_mapped_visual_proof01.",
        "recovery07_mapped_visual_proof01_recovery01.",
    )
    text = text.replace(
        "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF_AUTHORIZATION",
        CLASSIFICATION,
    )
    return text


def derive_sources() -> dict[str, tuple[Path, Path]]:
    SCRIPT_ROOT.mkdir(parents=True, exist_ok=True)
    pairs = {
        "executor": (
            ORIGINAL_SCRIPT_ROOT / "capture_recovery07_mapped_visual_proof01.py",
            SCRIPT_ROOT / "capture_recovery07_mapped_visual_proof01_recovery01.py",
        ),
        "supervisor": (
            ORIGINAL_SCRIPT_ROOT / "invoke_recovery07_mapped_visual_proof01_once.ps1",
            SCRIPT_ROOT / "invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1",
        ),
        "adjudicator": (
            ORIGINAL_SCRIPT_ROOT / "adjudicate_recovery07_mapped_visual_proof01_once.py",
            SCRIPT_ROOT / "adjudicate_recovery07_mapped_visual_proof01_recovery01_once.py",
        ),
        "verifier": (
            ORIGINAL_SCRIPT_ROOT / "verify_recovery07_mapped_visual_proof01_offline.py",
            SCRIPT_ROOT / "verify_recovery07_mapped_visual_proof01_recovery01_offline.py",
        ),
        "tests": (
            ORIGINAL_SCRIPT_ROOT / "test_recovery07_mapped_visual_proof01.py",
            SCRIPT_ROOT / "test_recovery07_mapped_visual_proof01_recovery01.py",
        ),
    }
    rendered: dict[str, str] = {}
    for name, (source, _) in pairs.items():
        rendered[name] = version_text(source.read_text(encoding="utf-8"))

    executor = rendered["executor"]
    anchor = "        self.csv_stopped = False\n        self.capture_index = 0"
    require(anchor in executor, "Executor CSV-state anchor changed")
    executor = executor.replace(
        anchor,
        "        self.csv_stopped = False\n"
        "        self.csv_last_size = -1\n"
        "        self.csv_stable_polls = 0\n"
        "        self.capture_index = 0",
        1,
    )
    old_flush = '''            if self.phase == "csv_flush":
                if now - self.phase_started >= 3.0:
                    self.phase = "capture"
                    self.phase_started = now
                    self.heartbeat("capture_phase_started")
                return
'''
    new_flush = '''            if self.phase == "csv_flush":
                csv_path = ISOLATED_ROOT / "Saved/Profiling/CSV" / CSV_FILENAME
                if now >= self.next_audit_at:
                    size = csv_path.stat().st_size if csv_path.is_file() else -1
                    if size >= 1024 and size == self.csv_last_size:
                        self.csv_stable_polls += 1
                    else:
                        self.csv_stable_polls = 0
                    self.csv_last_size = size
                    self.next_audit_at = now + 0.5
                    self.heartbeat(
                        "csv_flush_poll",
                        csv_file=str(csv_path),
                        csv_bytes=size,
                        stable_polls=self.csv_stable_polls,
                    )
                if self.csv_stable_polls >= 2:
                    self.phase = "capture"
                    self.phase_started = now
                    self.heartbeat("capture_phase_started", csv_bytes=self.csv_last_size)
                elif now - self.phase_started > 10.0:
                    raise RuntimeError("CSV profile did not become stable within ten seconds")
                return
'''
    require(old_flush in executor, "Executor flush block changed")
    executor = executor.replace(old_flush, new_flush, 1)
    rendered["executor"] = executor

    supervisor = rendered["supervisor"]
    require("            '-game',\n" in supervisor, "Original -game switch is absent")
    supervisor = supervisor.replace("            '-game',\n", "", 1)
    csv_anchor = "            '-csvNamedEvents',\n"
    require(csv_anchor in supervisor, "CSV argument anchor changed")
    supervisor = supervisor.replace(
        csv_anchor, csv_anchor + "            '-csvCompression=0',\n", 1
    )
    rendered["supervisor"] = supervisor

    verifier = rendered["verifier"]
    verifier_anchor = '    require("-ExecCmds=py" in supervisor_text, "ExecCmds Python lifecycle")\n'
    require(verifier_anchor in verifier, "Verifier supervisor anchor changed")
    verifier = verifier.replace(
        verifier_anchor,
        verifier_anchor
        + '    require("            \'-game\'," not in supervisor_text, "Forbidden game-mode flag")\n'
        + '    require("-csvCompression=0" in supervisor_text, "Forced uncompressed CSV")\n'
        + '    require("csv_stable_polls" in executor_text, "Evidence-driven CSV flush")\n',
        1,
    )
    rendered["verifier"] = verifier

    tests = rendered["tests"]
    tests_anchor = "\n\nif __name__ == \"__main__\":\n"
    require(tests_anchor in tests, "Test append anchor changed")
    tests = tests.replace(
        tests_anchor,
        '''
    def test_recovery01_supervisor_uses_editor_mode_and_stable_csv(self) -> None:
        supervisor = (HERE / "invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1").read_text(encoding="utf-8")
        executor = (HERE / "capture_recovery07_mapped_visual_proof01_recovery01.py").read_text(encoding="utf-8")
        self.assertNotIn("            '-game',", supervisor)
        self.assertIn("-csvCompression=0", supervisor)
        self.assertIn("csv_stable_polls", executor)
        self.assertIn("CSV profile did not become stable within ten seconds", executor)


if __name__ == "__main__":
''',
        1,
    )
    rendered["tests"] = tests

    for name, (_, destination) in pairs.items():
        destination.write_text(rendered[name], encoding="utf-8")
    return pairs


def copy_json_authority(source: Path, destination: Path) -> Path:
    destination.write_bytes(source.read_bytes())
    require(sha256_file(source) == sha256_file(destination), "Exact JSON copy failed")
    return destination


def create_contract(original_contract: dict[str, Any]) -> Path:
    value = json.loads(json.dumps(original_contract))
    value["schema"] = "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-contract.v1"
    value["contract_id"] = CONTRACT_ID
    value["created_utc"] = now()
    value["locked_inputs"] += [record(ORIGINAL_FREEZE), record(ORIGINAL_BINDING)]
    value["runtime"]["attempt_relative_path"] = f"Saved/BuildAttempts/{PREFIX}/attempt_01"
    value["runtime"]["lifecycle"] = "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK_RECOVERY01"
    value["runtime"]["editor_mode"] = True
    value["runtime"]["game_mode_flag_allowed"] = False
    value["runtime"]["csv_compression"] = 0
    value["runtime"]["csv_flush"] = {
        "minimum_bytes": 1024,
        "stable_polls": 2,
        "poll_interval_seconds": 0.5,
        "maximum_seconds": 10.0,
    }
    value["correction_scope"] = [
        "remove -game so editor-only Python and EditorLevelLibrary remain available",
        "force csv.CompressionMode 0 so the exact .csv evidence path is deterministic",
        "replace blind three-second CSV flush with two stable nonempty file-size polls",
        "version namespaces, contract identity, filenames and evidence paths",
    ]
    path = DOC_ROOT / f"{PREFIX}_CONTRACT.json"
    write_json(path, value)
    return path


def create_runtime_report() -> Path:
    main_frame = ENGINE / "Engine/Source/Editor/MainFrame/Private/MainFrameModule.cpp"
    csv_source = ENGINE / "Engine/Source/Runtime/Core/Private/ProfilingDebugging/CsvProfiler.cpp"
    python_source = ENGINE / "Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/PythonScriptPlugin.cpp"
    def lines(path: Path, markers: list[str]) -> list[dict[str, Any]]:
        source = path.read_text(encoding="utf-8", errors="replace").splitlines()
        result = []
        for marker in markers:
            found = [i + 1 for i, line in enumerate(source) if marker in line]
            require(found, f"Installed-engine marker missing: {marker}")
            result.append({"marker": marker, "lines": found[:10]})
        return result
    value = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-runtime.v1",
        "created_utc": now(),
        "classification": "PASS",
        "original_design": record(ORIGINAL_FREEZE),
        "findings": [
            {
                "issue": "-game requests game mode from UnrealEditor.exe",
                "risk": "editor-only Python/EditorLevelLibrary availability is not guaranteed",
                "correction": "omit -game and run the full unattended editor",
            },
            {
                "issue": "CSV extension may follow compression policy",
                "risk": "the adjudicator freezes an exact .csv path",
                "correction": "pass -csvCompression=0",
            },
            {
                "issue": "blind CSV flush wait",
                "risk": "asynchronous profiler writer may not be finished",
                "correction": "require a nonempty stable file size across two polls",
            },
        ],
        "installed_engine_authorities": [
            {**record(main_frame), "markers": lines(main_frame, ["!IsRunningGame()"] )},
            {**record(csv_source), "markers": lines(csv_source, ["csv.CompressionMode", "STARTFILE=", "GetDefaultDirectory()", "FPaths::SetExtension"] )},
            {**record(python_source), "markers": lines(python_source, ["Exec_Runtime", "DeferredCommands", "ExecPythonCommandEx"] )},
        ],
        "full_editor_required": True,
        "game_mode_allowed": False,
        "uncompressed_csv_required": True,
        "native_build_required": False,
        "unreal_launched": False,
    }
    path = DOC_ROOT / f"{PREFIX}_RUNTIME_COMPATIBILITY_REPORT.json"
    write_json(path, value)
    return path


def diff_report(pairs: dict[str, tuple[Path, Path]], contract: Path) -> Path:
    records = []
    for name, (source, destination) in pairs.items():
        old = source.read_text(encoding="utf-8").splitlines()
        new = destination.read_text(encoding="utf-8").splitlines()
        diff = list(
            difflib.unified_diff(old, new, fromfile=str(source), tofile=str(destination), lineterm="")
        )
        records.append(
            {
                "name": name,
                "source": record(source),
                "destination": record(destination),
                "unified_diff": diff,
            }
        )
    original_contract = load_json(DOC_ROOT / f"{ORIGINAL_PREFIX}_CONTRACT.json")
    new_contract = load_json(contract)
    require(original_contract["world"] == new_contract["world"], "World contract changed")
    require(original_contract["capture"] == new_contract["capture"], "Capture contract changed")
    for key in ("warmup_seconds", "measurement_seconds", "minimum_frame_samples", "stable_shader_polls"):
        require(original_contract["runtime"][key] == new_contract["runtime"][key], f"Runtime bound changed: {key}")
    value = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-diff.v1",
        "classification": "PASS_BOUNDED_CORRECTION",
        "allowed_changes": [
            "namespace and evidence identity versioning",
            "remove the single -game launch argument",
            "add -csvCompression=0",
            "add stable CSV flush state and polling",
            "strengthen tests and verifier for those corrections",
        ],
        "forbidden_semantics_unchanged": {
            "map": True,
            "materials": True,
            "actor_contract": True,
            "camera_contract": True,
            "capture_count_and_resolution": True,
            "shader_readiness": True,
            "warmup_and_measurement": True,
            "performance_thresholds": True,
            "world_save_prohibition": True,
            "one_launch_zero_retry": True,
        },
        "source_diffs": records,
    }
    path = DOC_ROOT / f"{PREFIX}_SOURCE_DIFF_REPORT.json"
    write_json(path, value)
    return path


def future_paths() -> list[Path]:
    return [
        ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01",
        ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01",
        REPORT_ROOT / f"{PREFIX}_EXECUTION_PREFLIGHT.json",
        REPORT_ROOT / f"{PREFIX}_TERMINAL_SUPERVISOR.json",
        REPORT_ROOT / f"{PREFIX}_EMERGENCY_RECEIPT.jsonl",
        REPORT_ROOT / f"{PREFIX}_POSTFLIGHT.json",
        ISOLATED / "Saved/Profiling/CSV/Recovery07MappedVisualProof01Recovery01.csv",
    ]


def create_prompt(freeze: Path) -> Path:
    path = DOC_ROOT / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    text = f"""Resume only the canonical Unreal Engine 5.8 / Blender 5.2 AAA project at `D:\\Skyguard52`. Do not use Three.js, external/generated substitutes, external AI models, or subagents.

Treat the original mapped-proof offline design as immutable and superseded before execution. Treat this Recovery01 freeze as the sole execution authority:

- File: `D:\\Skyguard52\\Docs\\AAA_Review\\{PREFIX}_OFFLINE_DESIGN_FREEZE.json`
- Bytes: `{freeze.stat().st_size}`
- SHA-256: `{sha256_file(freeze)}`
- Classification: `{CLASSIFICATION}`

I explicitly authorize exactly one Recovery07 Mapped Visual Proof01 Recovery01 Unreal execution and its mandatory automatic postflight adjudicator by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\\Skyguard52\\Scripts\\ToolchainWave08\\environment_authoring01_recovery07_mapped_visual_proof01_recovery01\\invoke_recovery07_mapped_visual_proof01_recovery01_once.ps1 -AuthorizeSingleUnrealProof`

Verify the Recovery01 prompt-binding freeze and every member, the original immutable design freezes, Recovery07 authoring authority, exact authored map and dependencies, full UE 5.8 editor, zero heavy processes, and absence of all future Recovery01 namespaces before launch.

Launch the full `UnrealEditor.exe` exactly once without `-game` and never use `UnrealEditor-Cmd.exe -ExecutePythonScript`. Use D3D12 SM6, unattended offscreen 2560x1440 rendering, deferred `-ExecCmds=py`, `-csvCompression=0`, disabled telemetry/network plugins, one heavy process, zero retries, and no failed-namespace reuse.

Require the exact 59-actor governed map, real terrain material, sixteen landscape components/resources/shader maps, empty compile queues, two stable readiness polls, 30-second warmup, 30-second capture-free measurement, at least 900 samples, and a fresh uncompressed CSV that becomes nonempty and stable across two polls before capture. Capture exactly five static and three temporal PNGs only after measurement.

Preserve complete process, log, CSV, frame, heartbeat, capture, no-mutation/restoration, terminal, supervisor and mandatory postflight evidence. Never save or mutate the map, assets, materials, transforms, PCG state or source. Never retry.

On automatic pass, inspect all eight original 2560x1440 PNGs directly at full resolution and apply the frozen visual rubric. Classify exactly `PASSED_RECOVERY07_MAPPED_VISUAL_PROOF_ACCEPTED` or `FAILED_WITH_EVIDENCE`. Freeze terminal evidence, update the production registry and Phase/Mission 1 audits, and stop. Do not integrate, promote, package, or claim Mission 1 or AAA completion.
"""
    write_text(path, text)
    return path


def run_offline_tests(supervisor: Path, tests: Path) -> dict[str, Any]:
    parse_command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{supervisor}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count-ne0){$e|ForEach-Object{$_.Message};exit 1};exit 0"
    )
    parse = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", parse_command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    unit = subprocess.run(
        [os.fspath(Path(os.sys.executable)), "-m", "unittest", "-v", os.fspath(tests)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    with tempfile.TemporaryDirectory(prefix="sg52_r07_proof_r01_") as temporary:
        offline = subprocess.run(
            [
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", os.fspath(supervisor), "-OfflineContractTest",
                "-OfflineEvidenceRoot", temporary,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        receipt_path = Path(temporary) / "offline_contract_test.json"
        receipt = load_json(receipt_path) if receipt_path.is_file() else None
    passed = parse.returncode == 0 and unit.returncode == 0 and offline.returncode == 0
    result = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-offline-tests.v1",
        "classification": "PASS" if passed else "FAILED_WITH_EVIDENCE",
        "powershell_51_parse": {"exit_code": parse.returncode, "stdout": parse.stdout, "stderr": parse.stderr},
        "unit_tests": {"exit_code": unit.returncode, "stdout": unit.stdout, "stderr": unit.stderr},
        "offline_contract_test": {"exit_code": offline.returncode, "stdout": offline.stdout, "stderr": offline.stderr, "receipt": receipt},
        "unreal_launched": False,
        "blender_launched": False,
    }
    require(passed, json.dumps(result, indent=2))
    return result


def build() -> dict[str, Any]:
    original_freeze, _ = verify_original_authority()
    for path in future_paths():
        require(not path.exists(), f"Future Recovery01 namespace exists: {path}")
    pairs = derive_sources()
    original_contract = load_json(DOC_ROOT / f"{ORIGINAL_PREFIX}_CONTRACT.json")
    contract = create_contract(original_contract)
    cameras = copy_json_authority(
        DOC_ROOT / f"{ORIGINAL_PREFIX}_CAMERAS.json",
        DOC_ROOT / f"{PREFIX}_CAMERAS.json",
    )
    visual = copy_json_authority(
        DOC_ROOT / f"{ORIGINAL_PREFIX}_VISUAL_RUBRIC.json",
        DOC_ROOT / f"{PREFIX}_VISUAL_RUBRIC.json",
    )
    performance = copy_json_authority(
        DOC_ROOT / f"{ORIGINAL_PREFIX}_PERFORMANCE_RUBRIC.json",
        DOC_ROOT / f"{PREFIX}_PERFORMANCE_RUBRIC.json",
    )
    runtime = create_runtime_report()
    diff = diff_report(pairs, contract)
    audit = DOC_ROOT / f"PHASE1_8_COMPLETION_AUDIT_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    matrix = DOC_ROOT / f"M01_PRODUCTION_VERTICAL_SLICE_ACCEPTANCE_MATRIX_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    write_text(audit, f"# Phase 1-8 audit addendum — mapped Proof01 Recovery01\n\n- Classification: `{CLASSIFICATION}`\n- Original freeze `{EXPECTED_ORIGINAL_FREEZE}` remains immutable and is superseded before execution.\n- Recovery01 removes `-game`, forces uncompressed CSV, and requires two stable nonempty CSV-size polls.\n- No Unreal, Blender, build, import, capture, integration, promotion or packaging process ran.\n- Next gate: one explicit Recovery01 Unreal proof authorization.")
    write_text(matrix, f"# Mission 1 acceptance matrix addendum — mapped Proof01 Recovery01\n\n| Requirement | State |\n|---|---|\n| Authored Recovery07 map | automatic pass awaiting visual proof |\n| Original proof design | immutable, superseded before execution |\n| Recovery01 lifecycle correction | offline pass |\n| Unreal visual proof | ready for separate explicit authorization |\n| Human full-resolution review | pending |\n| Integration/promotion/package | not authorized |")

    verifier = pairs["verifier"][1]
    supervisor = pairs["supervisor"][1]
    tests = pairs["tests"][1]
    source_files = [destination for _, destination in pairs.values()] + [Path(__file__).resolve()]
    for path in source_files:
        if path.suffix == ".py":
            compile(path.read_text(encoding="utf-8"), str(path), "exec")

    freeze = DOC_ROOT / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
    prompt = DOC_ROOT / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    binding = DOC_ROOT / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    write_json(freeze, {"schema": "provisional", "classification": CLASSIFICATION, "members": []})
    create_prompt(freeze)
    write_json(binding, {"schema": "provisional", "classification": CLASSIFICATION, "members": [record(freeze), record(prompt)]})

    test_result = REPORT_ROOT / f"{PREFIX}_OFFLINE_TEST_RESULT.json"
    write_json(test_result, run_offline_tests(supervisor, tests))
    inventory = REPORT_ROOT / f"{PREFIX}_SOURCE_INVENTORY.json"
    readiness = REPORT_ROOT / f"{PREFIX}_READINESS.json"
    design_files = [contract, cameras, visual, performance, runtime, diff, audit, matrix, test_result] + source_files
    write_json(
        inventory,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-inventory.v1",
            "created_utc": now(),
            "original_authority": [record(ORIGINAL_FREEZE), record(ORIGINAL_BINDING)],
            "inherited_locked_inputs": original_contract["locked_inputs"],
            "recovery01_design_files": [record(path) for path in design_files],
            "future_namespaces_created": False,
        },
    )
    write_json(
        readiness,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-readiness.v1",
            "created_utc": now(),
            "classification": CLASSIFICATION,
            "original_authority_verified": True,
            "full_editor_without_game_mode": True,
            "uncompressed_csv_forced": True,
            "stable_csv_flush_evidence": True,
            "one_unreal_launch": True,
            "automatic_retries": 0,
            "future_namespaces_absent": True,
            "unreal_launched": False,
            "blender_launched": False,
            "next_gate": "EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION",
        },
    )
    members = [record(ORIGINAL_FREEZE), record(ORIGINAL_BINDING)] + original_contract["locked_inputs"] + [record(path) for path in design_files + [inventory, readiness]]
    write_json(
        freeze,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-offline-freeze.v1",
            "created_utc": now(),
            "classification": CLASSIFICATION,
            "contract_id": CONTRACT_ID,
            "member_count": len(members),
            "members": members,
            "original_design_preserved": True,
            "future_namespaces_absent": True,
            "unreal_launched": False,
            "blender_launched": False,
            "next_gate": "EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION",
        },
    )
    prompt = create_prompt(freeze)
    write_json(
        binding,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery01-prompt-binding.v1",
            "created_utc": now(),
            "classification": CLASSIFICATION,
            "contract_id": CONTRACT_ID,
            "member_count": 2,
            "members": [record(freeze), record(prompt)],
            "single_unreal_launch": True,
            "mandatory_postflight_adjudicator": True,
            "human_full_resolution_review_required": True,
        },
    )
    return {
        "classification": CLASSIFICATION,
        "offline_freeze": record(freeze),
        "binding_freeze": record(binding),
        "execution_prompt": record(prompt),
        "member_count": len(members),
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
