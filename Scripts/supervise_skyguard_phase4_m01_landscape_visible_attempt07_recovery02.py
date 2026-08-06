"""Build once, run one deferred Recovery02 tiny proof, and stop."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-02"


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


def run_stage(
    name: str,
    command: list[str],
    logs_root: Path,
    root: Path,
    timeout: int,
    engine_log_argument: bool = False,
) -> dict:
    stdout_path = logs_root / f"{name}.stdout.log"
    stderr_path = logs_root / f"{name}.stderr.log"
    engine_log = logs_root / f"{name}.engine.log"
    final_command = list(command)
    if engine_log_argument:
        final_command.append(f"-abslog={engine_log}")
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
    result = {
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
    }
    if engine_log_argument:
        result["engine_log"] = str(engine_log)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument(
        "--unreal-root", type=Path, default=Path(r"D:\UE_5.8")
    )
    parser.add_argument(
        "--authorize-single-recovery02-tiny-proof", action="store_true"
    )
    parser.add_argument("--build-timeout", type=int, default=900)
    parser.add_argument("--proof-timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.authorize_single_recovery02_tiny_proof:
        raise RuntimeError(
            "Attempt07 Recovery02 requires "
            "--authorize-single-recovery02-tiny-proof"
        )

    root = args.project_root.resolve()
    unreal_root = args.unreal_root.resolve()
    contract = read_json(
        root
        / "Docs/AAA_Review/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY02_CONTRACT.json"
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery02 contract ID mismatch")
    if active_heavy_processes():
        raise RuntimeError("Exclusive heavy lane is not free")

    recovery01 = contract["immutable_recovery01_failure"]
    recovery01_root = root / recovery01["root"]
    recovery01_hashes = locked_hashes(
        recovery01_root, recovery01["files"]
    )
    recovery01_manifest = read_json(
        recovery01_root / "run_manifest.json"
    )
    if not (
        recovery01_manifest.get("terminal_state") == "FAILED"
        and len(recovery01_manifest.get("stages", [])) == 3
        and [
            stage.get("exit_code")
            for stage in recovery01_manifest["stages"]
        ]
        == [0, 0, 3]
        and not (
            recovery01_root / "tiny_proof_receipt.json"
        ).exists()
        and recovery01_manifest.get("full_capture_invoked") is False
        and recovery01_manifest.get("profile_invoked") is False
    ):
        raise RuntimeError("Recovery01 immutable failure boundary changed")

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
                "Attempt07 Recovery02 implementation hash failed: " + name
            )

    module_spec = contract["compiled_module_before_recovery02"]
    module = root / module_spec["file"]
    if not module.is_file() or sha256_file(module) != module_spec["sha256"]:
        raise RuntimeError(
            "Attempt07 Recovery02 pre-build module hash failed"
        )
    execution_root = root / contract["tiny_live_proof"]["execution_root"]
    if execution_root.exists():
        raise RuntimeError(
            "Attempt07 Recovery02 execution root already exists"
        )

    project = root / "Skyguard52.uproject"
    editor = unreal_root / "Engine/Binaries/Win64/UnrealEditor.exe"
    build_bat = unreal_root / "Engine/Build/BatchFiles/Build.bat"
    cmd = Path(r"C:\Windows\System32\cmd.exe")
    proof_script = implementation_paths["recovery02_tiny_proof"]
    for path in (project, editor, build_bat, cmd, proof_script):
        if not path.is_file():
            raise RuntimeError(
                "Attempt07 Recovery02 required file missing: " + str(path)
            )

    logs_root = execution_root / "logs"
    logs_root.mkdir(parents=True, exist_ok=False)
    manifest_path = execution_root / "run_manifest.json"
    proof_receipt = execution_root / "tiny_proof_receipt.json"
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery02-supervisor.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": utc_now(),
        "recovery01_hashes_before": recovery01_hashes,
        "locked_production_hashes_before": production_before,
        "locked_production_hashes_after": None,
        "compiled_module_before": module_spec["sha256"],
        "compiled_module_after": None,
        "stages": [],
        "artifacts": {
            "tiny_proof_receipt": str(proof_receipt),
            "captures_root": str(execution_root / "captures"),
        },
        "controls": {
            "single_native_build_allowed": True,
            "author_stage_allowed": False,
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
        build_arguments = [
            str(build_bat),
            "Skyguard52Editor",
            "Win64",
            "Development",
            str(project),
            "-WaitMutex",
            "-NoHotReloadFromIDE",
        ]
        build_stage = run_stage(
            "build_recovery02_deferred_material_bridge",
            [
                str(cmd),
                "/d",
                "/s",
                "/c",
                subprocess.list2cmdline(build_arguments),
            ],
            logs_root,
            root,
            args.build_timeout,
        )
        manifest["stages"].append(build_stage)
        write_json(manifest_path, manifest)
        if build_stage["timed_out"] or build_stage["exit_code"] != 0:
            raise RuntimeError(
                "Attempt07 Recovery02 native build stage failed"
            )
        module_after = sha256_file(module)
        manifest["compiled_module_after"] = module_after
        if module_after == module_spec["sha256"]:
            raise RuntimeError(
                "Recovery02 build did not replace the prior module"
            )

        proof_stage = run_stage(
            "recovery02_deferred_tiny_live_proof_d3d12_sm6",
            [
                str(editor),
                str(project),
                contract["locked_production_packages"]["candidate_map"][
                    "asset"
                ],
                f"-ExecutePythonScript={proof_script}",
                "-ScriptErrorsAreFatal",
                (
                    "-SkyguardAttempt07Recovery02ProofRoot="
                    + str(execution_root)
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
            engine_log_argument=True,
        )
        manifest["stages"].append(proof_stage)
        if not proof_receipt.is_file():
            raise RuntimeError(
                "Attempt07 Recovery02 tiny proof receipt is missing"
            )
        proof = read_json(proof_receipt)
        if (
            proof_stage["timed_out"]
            or proof_stage["exit_code"] != 0
            or proof.get("gate") != "PASS"
        ):
            raise RuntimeError(
                "Attempt07 Recovery02 deferred tiny proof failed"
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
        manifest["recovery01_hashes_after"] = locked_hashes(
            recovery01_root, recovery01["files"]
        )
        manifest["finished_at_utc"] = utc_now()
        manifest["author_stage_invoked"] = False
        manifest["full_capture_invoked"] = False
        manifest["profile_invoked"] = False
        manifest["promotion_allowed"] = False
        write_json(manifest_path, manifest)
        remaining = active_heavy_processes()
        if remaining:
            raise RuntimeError(
                "Heavy processes remain after Attempt07 Recovery02: "
                + repr(remaining)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
