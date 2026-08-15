from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
CHECKPOINT_BLEND = PROJECT / r"Production\Attempts\m02-harbor-double-bitt-bollard-deterministic-recovery02\attempt_20260811T1310000000000Z\output\checkpoint\M02_Harbor_DoubleBittBollard_Production01_Checkpoint.blend"
FINALIZER = PROJECT / r"Scripts\GrokProduction\finalize_m02_harbor_double_bitt_bollard_deterministic_recovery06_scene.py"
ATTEMPT = PROJECT / r"Production\Attempts\m02-harbor-double-bitt-bollard-deterministic-recovery06\attempt_20260811T1325000000000Z"
OUTPUT = ATTEMPT / "output"
TERMINAL = ATTEMPT / "terminal_manifest.json"
SRC_CHECKPOINT_DIR = PROJECT / r"Production\Attempts\m02-harbor-double-bitt-bollard-deterministic-recovery02\attempt_20260811T1310000000000Z\output\checkpoint"

CHECKPOINT_BLEND_BYTES = 680_698
CHECKPOINT_BLEND_SHA = "890cfc57e2bce22844c107f82a5faa0524c6b170d3bbbfe25608837f0296f6f1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def require_authority(path: Path, size: int, digest: str) -> None:
    if not path.is_file() or path.stat().st_size != size or sha256(path) != digest:
        raise RuntimeError(f"Authority mismatch: {path}")


def heavy_running() -> list[str]:
    names = {"blender.exe", "unrealeditor.exe", "unrealeditor-cmd.exe", "shadercompileworker.exe", "automationtool.exe", "unrealbuildtool.exe"}
    rows = []
    try:
        import psutil
    except Exception:
        return rows
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if (proc.info.get("name") or "").lower() in names:
                rows.append(f"{proc.info['name']}:{proc.info['pid']}")
        except Exception:
            continue
    return rows


def main() -> int:
    started = utc_now()
    if ATTEMPT.exists():
        raise RuntimeError(f"Attempt namespace already exists: {ATTEMPT}")
    require_authority(CHECKPOINT_BLEND, CHECKPOINT_BLEND_BYTES, CHECKPOINT_BLEND_SHA)
    if not FINALIZER.is_file():
        raise RuntimeError(f"Missing finalizer: {FINALIZER}")
    finalizer_text = FINALIZER.read_text(encoding="utf-8")
    if "deterministic-recovery06" not in finalizer_text or "apply_object_transforms" not in finalizer_text:
        raise RuntimeError("Recovery06 finalizer contract missing")
    heavy = heavy_running()
    if heavy:
        raise RuntimeError(f"Heavy processes active: {heavy}")

    for path in (OUTPUT, OUTPUT / "checkpoint", OUTPUT / "renders", OUTPUT / "exports", OUTPUT / "receipts", OUTPUT / "scripts"):
        path.mkdir(parents=True, exist_ok=True)
    for item in SRC_CHECKPOINT_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, OUTPUT / "checkpoint" / item.name)

    stdout_path = ATTEMPT / "finalizer_stdout.log"
    stderr_path = ATTEMPT / "finalizer_stderr.log"
    cmd = [str(BLENDER), str(CHECKPOINT_BLEND), "--background", "--python", str(FINALIZER)]
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, cwd=str(PROJECT), stdout=out, stderr=err, text=True)
    final_code = int(proc.returncode)
    stdout_text = stdout_path.read_text(encoding="utf-8", errors="ignore")
    stderr_text = stderr_path.read_text(encoding="utf-8", errors="ignore")

    expected_blend = OUTPUT / "M02_Harbor_DoubleBittBollard_Production01.blend"
    expected_glb = OUTPUT / "exports" / "M02_Harbor_DoubleBittBollard_Production01.glb"
    expected_report = OUTPUT / "grok_implementation_report.json"
    final_renders = sorted((OUTPUT / "renders").glob("*.png"))
    success_marker = "PASSED_AWAITING_DIRECT_VISUAL_REVIEW" in stdout_text
    runtime_error = "RuntimeError" in stderr_text or "Traceback" in stderr_text

    classification = "FAILED_WITH_EVIDENCE"
    if success_marker and not runtime_error and expected_blend.is_file() and expected_glb.is_file() and expected_report.is_file() and len(final_renders) >= 8:
        classification = "PASSED_AWAITING_DIRECT_VISUAL_REVIEW"

    artifacts = [file_record(path) for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file())]
    terminal = {
        "schema": "skyguard.m02-harbor-double-bitt-bollard.deterministic-recovery06.terminal.v1",
        "created_at_utc": utc_now(),
        "started_at_utc": started,
        "classification": classification,
        "asset": "M02 harbor double-bitt mooring bollard",
        "attempt_root": str(ATTEMPT),
        "execution": {
            "blender_launches": 1,
            "grok_launches": 0,
            "unreal_launches": 0,
            "retries": 0,
            "finalizer_process_exit_code": final_code,
            "finalizer_process_exit_code_type": "System.Int32",
            "success_marker_present": success_marker,
            "runtime_error_present": runtime_error,
        },
        "authorities": {
            "checkpoint_blend": file_record(CHECKPOINT_BLEND),
            "finalizer": file_record(FINALIZER),
        },
        "outputs": {
            "blend": str(expected_blend) if expected_blend.is_file() else None,
            "glb": str(expected_glb) if expected_glb.is_file() else None,
            "implementation_report": str(expected_report) if expected_report.is_file() else None,
            "final_render_count": len(final_renders),
            "final_renders": [str(path) for path in final_renders],
        },
        "artifacts": artifacts,
        "runtime_promotion_performed": False,
        "next_gate": "Direct full-resolution visual review of eight final renders" if classification.startswith("PASSED") else "Preserve failure evidence; do not retry this namespace",
    }
    write_json(TERMINAL, terminal)
    print(classification)
    return 0 if classification.startswith("PASSED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
