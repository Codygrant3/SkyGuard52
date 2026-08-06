"""Run one proof-only Recovery03 after an externally proven full compile."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-03"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def locked_hashes(root: Path, items: dict) -> dict[str, str]:
    result = {}
    for name, item in items.items():
        path = root / item["file"]
        if (
            not path.is_file()
            or path.stat().st_size != item.get("bytes", path.stat().st_size)
        ):
            raise RuntimeError("Locked file missing or wrong size: " + str(path))
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise RuntimeError("Locked file hash failed: " + str(path))
        result[name] = digest
    return result


def active_heavy_processes() -> list[str]:
    process = subprocess.run(
        ["tasklist", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    names = []
    for line in process.stdout.splitlines():
        lowered = line.lower()
        if any(
            name in lowered
            for name in (
                "unrealeditor.exe",
                "unrealeditor-cmd.exe",
                "unrealbuildtool.exe",
                "blender.exe",
            )
        ):
            names.append(line)
    return names


def project_relative_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise RuntimeError(
            "Activation evidence escapes project root: " + value
        ) from error
    return path


def validate_source_inventory(
    root: Path, inventory_path: Path, inventory_hash: str
) -> dict:
    if (
        not inventory_path.is_file()
        or sha256_file(inventory_path) != inventory_hash
    ):
        raise RuntimeError("Full-module source inventory hash failed")
    inventory = read_json(inventory_path)
    if (
        inventory.get("schema")
        != "skyguard.full-module-source-inventory.v1"
        or inventory.get("root") != "Source"
    ):
        raise RuntimeError("Full-module source inventory schema/root failed")
    expected = {
        item["file"]: item for item in inventory.get("files", [])
    }
    actual_paths = sorted(
        path
        for path in (root / "Source").rglob("*")
        if path.is_file()
    )
    actual = {
        path.relative_to(root).as_posix(): path for path in actual_paths
    }
    if set(actual) != set(expected):
        raise RuntimeError(
            "Full-module source inventory is not exhaustive/current"
        )
    for relative, path in actual.items():
        item = expected[relative]
        if (
            path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise RuntimeError(
                "Full-module source inventory file drift: " + relative
            )
    return inventory


def validate_compile_activation(
    root: Path,
    contract: dict,
    activation_path: Path,
    activation_hash: str,
) -> dict:
    if not re.fullmatch(r"[0-9a-f]{64}", activation_hash):
        raise RuntimeError("Compile activation SHA256 is malformed")
    if (
        not activation_path.is_file()
        or sha256_file(activation_path) != activation_hash
    ):
        raise RuntimeError("Compile activation file/hash failed")
    activation = read_json(activation_path)
    prerequisite = contract["full_module_compile_prerequisite"]
    if (
        activation.get("schema") != prerequisite["activation_schema"]
        or activation.get("contract_id") != contract["contract_id"]
        or activation.get("gate") != prerequisite["required_gate"]
        or activation.get("target") != "Skyguard52Editor"
        or activation.get("platform") != "Win64"
        or activation.get("configuration") != "Development"
        or activation.get("build_exit_code") != 0
    ):
        raise RuntimeError("Compile activation identity/gate failed")

    for key in (
        "source_inventory",
        "compile_receipt",
        "build_stdout",
        "build_stderr",
    ):
        item = activation.get(key) or {}
        evidence_path = project_relative_path(root, item.get("file", ""))
        if (
            not evidence_path.is_file()
            or sha256_file(evidence_path) != item.get("sha256")
        ):
            raise RuntimeError(
                "Compile activation evidence failed: " + key
            )
    inventory_item = activation["source_inventory"]
    validate_source_inventory(
        root,
        project_relative_path(root, inventory_item["file"]),
        inventory_item["sha256"],
    )
    receipt = read_json(
        project_relative_path(
            root, activation["compile_receipt"]["file"]
        )
    )
    if (
        receipt.get("gate")
        != "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        or receipt.get("build_exit_code") != 0
        or receipt.get("target") != "Skyguard52Editor"
        or receipt.get("platform") != "Win64"
        or receipt.get("configuration") != "Development"
    ):
        raise RuntimeError("Full-module compile receipt failed")

    module = activation.get("compiled_module") or {}
    module_path = project_relative_path(root, module.get("file", ""))
    if (
        module.get("file") != "Binaries/Win64/UnrealEditor-Skyguard52.dll"
        or not module_path.is_file()
        or module_path.stat().st_size != module.get("bytes")
        or sha256_file(module_path) != module.get("sha256")
        or receipt.get("compiled_module_sha256") != module.get("sha256")
    ):
        raise RuntimeError("Activated compiled module hash failed")
    return activation


def run_stage(
    name: str,
    command: list[str],
    logs_root: Path,
    root: Path,
    timeout: int,
) -> dict:
    stdout_path = logs_root / f"{name}.stdout.log"
    stderr_path = logs_root / f"{name}.stderr.log"
    engine_log = logs_root / f"{name}.engine.log"
    final_command = [*command, f"-abslog={engine_log}"]
    started = utc_now()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, (
        stderr_path.open("w", encoding="utf-8")
    ) as stderr:
        process = subprocess.Popen(
            final_command,
            cwd=root,
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(
                ["taskkill", "/pid", str(process.pid), "/t", "/f"],
                capture_output=True,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            exit_code = process.wait(timeout=30)
    return {
        "name": name,
        "command": final_command,
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "timeout_seconds": timeout,
        "timed_out": timed_out,
        "process_exit_observed": process.poll() is not None,
        "exit_code": exit_code,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "engine_log": str(engine_log),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument(
        "--unreal-root", type=Path, default=Path(r"D:\UE_5.8")
    )
    parser.add_argument("--compile-activation", type=Path, required=True)
    parser.add_argument(
        "--compile-activation-sha256", required=True
    )
    parser.add_argument(
        "--authorize-single-recovery03-tiny-proof", action="store_true"
    )
    parser.add_argument("--proof-timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.authorize_single_recovery03_tiny_proof:
        raise RuntimeError(
            "Attempt07 Recovery03 requires "
            "--authorize-single-recovery03-tiny-proof"
        )

    root = args.project_root.resolve()
    unreal_root = args.unreal_root.resolve()
    contract = read_json(
        root
        / "Docs/AAA_Review/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY03_CONTRACT.json"
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery03 contract ID mismatch")
    if active_heavy_processes():
        raise RuntimeError("Exclusive heavy lane is not free")

    recovery02 = contract["immutable_recovery02_failure"]
    recovery02_root = root / recovery02["root"]
    recovery02_hashes = locked_hashes(
        recovery02_root, recovery02["files"]
    )
    recovery02_manifest = read_json(
        recovery02_root / "run_manifest.json"
    )
    if not (
        recovery02_manifest.get("terminal_state") == "FAILED"
        and len(recovery02_manifest.get("stages", [])) == 1
        and recovery02_manifest["stages"][0].get("exit_code") == 6
        and recovery02_manifest.get("author_stage_invoked") is False
        and recovery02_manifest.get("full_capture_invoked") is False
        and recovery02_manifest.get("profile_invoked") is False
    ):
        raise RuntimeError("Recovery02 immutable failure boundary changed")

    production_before = locked_hashes(
        root, contract["locked_production_packages"]
    )
    implementation_paths = {
        name: root / item["file"]
        for name, item in contract["implementation_files"].items()
    }
    for name, path in implementation_paths.items():
        expected = contract["implementation_files"][name]["sha256"]
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(
                "Attempt07 Recovery03 implementation hash failed: " + name
            )

    activation_path = args.compile_activation.resolve()
    activation_hash = args.compile_activation_sha256.lower()
    activation = validate_compile_activation(
        root, contract, activation_path, activation_hash
    )
    module_path = root / activation["compiled_module"]["file"]
    module_hash = activation["compiled_module"]["sha256"]

    execution_root = root / contract["tiny_live_proof"]["execution_root"]
    if execution_root.exists():
        raise RuntimeError(
            "Attempt07 Recovery03 execution root already exists"
        )
    project = root / "Skyguard52.uproject"
    editor = unreal_root / "Engine/Binaries/Win64/UnrealEditor.exe"
    proof_script = implementation_paths["recovery03_tiny_proof"]
    for path in (project, editor, proof_script):
        if not path.is_file():
            raise RuntimeError(
                "Attempt07 Recovery03 required file missing: " + str(path)
            )

    logs_root = execution_root / "logs"
    logs_root.mkdir(parents=True, exist_ok=False)
    manifest_path = execution_root / "run_manifest.json"
    proof_receipt = execution_root / "tiny_proof_receipt.json"
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery03-supervisor.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": utc_now(),
        "compile_activation": {
            "file": str(activation_path),
            "sha256": activation_hash,
            "compiled_module_sha256": module_hash,
        },
        "recovery02_hashes_before": recovery02_hashes,
        "locked_production_hashes_before": production_before,
        "locked_production_hashes_after": None,
        "compiled_module_before": module_hash,
        "compiled_module_after": None,
        "stages": [],
        "controls": {
            "build_stage_allowed": False,
            "author_stage_allowed": False,
            "proof_only": True,
            "deferred_editor_tick_wait_required": True,
            "full_capture_allowed": False,
            "profile_allowed": False,
            "automatic_retry_allowed": False,
            "promotion_allowed": False,
        },
        "terminal_state": "RUNNING",
        "errors": [],
    }
    write_json(manifest_path, manifest)
    try:
        proof_stage = run_stage(
            "recovery03_deferred_tiny_live_proof_d3d12_sm6",
            [
                str(editor),
                str(project),
                contract["locked_production_packages"]["candidate_map"][
                    "asset"
                ],
                f"-ExecutePythonScript={proof_script}",
                "-ScriptErrorsAreFatal",
                (
                    "-SkyguardAttempt07Recovery03ProofRoot="
                    + str(execution_root)
                ),
                (
                    "-SkyguardRecovery03CompileActivation="
                    + str(activation_path)
                ),
                (
                    "-SkyguardRecovery03CompileActivationSha256="
                    + activation_hash
                ),
                "-unattended",
                "-nop4",
                "-NoSplash",
                "-RenderOffscreen",
                "-windowed",
                "-ResX=640",
                "-ResY=360",
                "-d3d12",
                "-sm6",
            ],
            logs_root,
            root,
            args.proof_timeout,
        )
        manifest["stages"].append(proof_stage)
        if not proof_receipt.is_file():
            raise RuntimeError(
                "Attempt07 Recovery03 tiny proof receipt is missing"
            )
        proof = read_json(proof_receipt)
        if (
            proof_stage["timed_out"]
            or proof_stage["exit_code"] != 0
            or proof.get("gate") != "PASS"
        ):
            raise RuntimeError(
                "Attempt07 Recovery03 deferred tiny proof failed"
            )
        manifest["terminal_state"] = (
            "TINY_PROOF_PASS_STOPPED_BEFORE_FULL_CAPTURE_OR_PROFILE"
        )
    except Exception as error:
        manifest["errors"].append(str(error))
        manifest["terminal_state"] = "FAILED"
        raise
    finally:
        manifest["locked_production_hashes_after"] = locked_hashes(
            root, contract["locked_production_packages"]
        )
        manifest["recovery02_hashes_after"] = locked_hashes(
            recovery02_root, recovery02["files"]
        )
        manifest["compiled_module_after"] = sha256_file(module_path)
        manifest["finished_at_utc"] = utc_now()
        manifest["build_stage_invoked"] = False
        manifest["author_stage_invoked"] = False
        manifest["full_capture_invoked"] = False
        manifest["profile_invoked"] = False
        manifest["promotion_allowed"] = False
        write_json(manifest_path, manifest)
        remaining = active_heavy_processes()
        if remaining:
            raise RuntimeError(
                "Heavy processes remain after Attempt07 Recovery03: "
                + repr(remaining)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
