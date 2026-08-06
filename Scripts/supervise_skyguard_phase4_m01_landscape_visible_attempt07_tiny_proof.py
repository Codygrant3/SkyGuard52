"""Run one Attempt07 author stage and one tiny D3D12 proof, then stop."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
)


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
        if not path.is_file():
            raise RuntimeError("Locked file missing: " + str(path))
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
    executable: Path,
    arguments: list[str],
    logs_root: Path,
    root: Path,
    timeout: int,
) -> dict:
    stdout_path = logs_root / f"{name}.stdout.log"
    stderr_path = logs_root / f"{name}.stderr.log"
    engine_log = logs_root / f"{name}.engine.log"
    final_arguments = [*arguments, f"-abslog={engine_log}"]
    started = utc_now()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, (
        stderr_path.open("w", encoding="utf-8")
    ) as stderr:
        process = subprocess.Popen(
            [str(executable), *final_arguments],
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
        "command": [str(executable), *final_arguments],
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
    parser.add_argument("--unreal-root", type=Path, default=Path(r"D:\UE_5.8"))
    parser.add_argument("--authorize-single-tiny-proof", action="store_true")
    parser.add_argument("--author-timeout", type=int, default=180)
    parser.add_argument("--proof-timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.authorize_single_tiny_proof:
        raise RuntimeError(
            "Attempt07 requires --authorize-single-tiny-proof"
        )
    root = args.project_root.resolve()
    unreal_root = args.unreal_root.resolve()
    contract = read_json(
        root
        / "Docs/AAA_Review/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
    )
    if contract["contract_id"] != "P4.5-M01-LANDSCAPE-VISIBLE-007":
        raise RuntimeError("Attempt07 contract ID mismatch")
    if active_heavy_processes():
        raise RuntimeError("Exclusive heavy lane is not free")
    predecessor_root = (
        root / contract["immutable_predecessor"]["root"]
    )
    predecessor_hashes = locked_hashes(
        predecessor_root, contract["immutable_predecessor"]["files"]
    )
    predecessor_gate = read_json(predecessor_root / "gate_report.json")
    if not (
        predecessor_gate.get("gate")
        == contract["immutable_predecessor"]["required_gate"]
        and predecessor_gate.get("technical_gate")
        == contract["immutable_predecessor"]["required_technical_gate"]
    ):
        raise RuntimeError("Recovery02 formal failure boundary changed")
    production_before = locked_hashes(
        root, contract["locked_production_packages"]
    )
    implementation_paths = {
        "diagnostic_builder": (
            root
            / "Scripts/"
            "build_skyguard_phase4_m01_landscape_material_validation.py"
        ),
        "attempt07_author": (
            root
            / "Scripts/"
            "build_skyguard_phase4_m01_landscape_attempt07_diagnostics.py"
        ),
        "attempt07_tiny_proof": (
            root
            / "Scripts/"
            "prove_skyguard_phase4_m01_landscape_attempt07_tiny_live.py"
        ),
        "attempt07_supervisor": Path(__file__).resolve(),
    }
    for name, path in implementation_paths.items():
        expected = contract["implementation_hashes"][name]
        if not expected or sha256_file(path) != expected:
            raise RuntimeError("Attempt07 implementation hash failed: " + name)
    module_spec = contract["compiled_module"]
    module = root / module_spec["file"]
    if not module.is_file() or sha256_file(module) != module_spec["sha256"]:
        raise RuntimeError("Attempt07 compiled module hash failed")
    outputs = contract["new_immutable_outputs"]
    for name in ("coverage_material", "component_id_material"):
        if (root / outputs[name]["file"]).exists():
            raise RuntimeError(
                "Attempt07 output already exists: " + outputs[name]["file"]
            )
    execution_root = root / contract["tiny_live_proof"]["execution_root"]
    if execution_root.exists():
        raise RuntimeError(
            "Attempt07 tiny proof root already exists; refusing overwrite"
        )
    project = root / "Skyguard52.uproject"
    editor_cmd = (
        unreal_root / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
    )
    editor = unreal_root / "Engine/Binaries/Win64/UnrealEditor.exe"
    author_script = implementation_paths["attempt07_author"]
    proof_script = implementation_paths["attempt07_tiny_proof"]
    for path in (project, editor_cmd, editor, author_script, proof_script):
        if not path.is_file():
            raise RuntimeError("Attempt07 required file missing: " + str(path))
    logs_root = execution_root / "logs"
    logs_root.mkdir(parents=True, exist_ok=False)
    manifest_path = execution_root / "run_manifest.json"
    author_receipt = execution_root / "author_receipt.json"
    proof_receipt = execution_root / "tiny_proof_receipt.json"
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-tiny-proof-supervisor.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": utc_now(),
        "predecessor_hashes_before": predecessor_hashes,
        "locked_production_hashes_before": production_before,
        "locked_production_hashes_after": None,
        "stages": [],
        "artifacts": {
            "author_receipt": str(author_receipt),
            "tiny_proof_receipt": str(proof_receipt),
            "captures_root": str(execution_root / "captures"),
        },
        "controls": {
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
        author_stage = run_stage(
            "author_attempt07_diagnostic_materials",
            editor_cmd,
            [
                str(project),
                "-run=pythonscript",
                f"-script={author_script}",
                f"-SkyguardAttempt07AuthorReceipt={author_receipt}",
                "-unattended",
                "-nop4",
                "-NoSplash",
                "-NullRHI",
            ],
            logs_root,
            root,
            args.author_timeout,
        )
        manifest["stages"].append(author_stage)
        write_json(manifest_path, manifest)
        if (
            author_stage["timed_out"]
            or author_stage["exit_code"] != 0
            or not author_receipt.is_file()
        ):
            raise RuntimeError("Attempt07 author stage failed")
        author = read_json(author_receipt)
        if author.get("gate") != "PASS":
            raise RuntimeError("Attempt07 author receipt failed")
        proof_stage = run_stage(
            "attempt07_tiny_live_proof_d3d12_sm6",
            editor,
            [
                str(project),
                contract["locked_production_packages"]["candidate_map"][
                    "asset"
                ],
                f"-ExecutePythonScript={proof_script}",
                "-ScriptErrorsAreFatal",
                f"-SkyguardAttempt07TinyProofRoot={execution_root}",
                f"-SkyguardAttempt07AuthorReceipt={author_receipt}",
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
            raise RuntimeError("Attempt07 tiny proof receipt is missing")
        proof = read_json(proof_receipt)
        if (
            proof_stage["timed_out"]
            or proof_stage["exit_code"] != 0
            or proof.get("gate") != "PASS"
        ):
            raise RuntimeError("Attempt07 tiny live proof failed")
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
        manifest["predecessor_hashes_after"] = locked_hashes(
            predecessor_root, contract["immutable_predecessor"]["files"]
        )
        manifest["finished_at_utc"] = utc_now()
        manifest["full_capture_invoked"] = False
        manifest["profile_invoked"] = False
        manifest["promotion_allowed"] = False
        write_json(manifest_path, manifest)
        remaining = active_heavy_processes()
        if remaining:
            raise RuntimeError(
                "Heavy processes remain after Attempt07: " + repr(remaining)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
