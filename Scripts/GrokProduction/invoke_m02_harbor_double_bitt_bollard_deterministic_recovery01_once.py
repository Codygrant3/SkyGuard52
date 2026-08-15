from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
SOURCE = PROJECT / r"Content\Skyguard\Meshes\Source\Mission01\Coastal_Production_001\BLD_M01_COAST_PROD_001_MASTER.blend"
CREATE_SCRIPT_SRC = PROJECT / r"Production\Attempts\m02-harbor-double-bitt-bollard-grok-mcp-production01\attempt_20260811T1245000000000Z\output\scripts\create_m02_harbor_double_bitt_bollard_production01.py"
FINALIZER_SRC = PROJECT / r"Scripts\GrokProduction\finalize_m02_harbor_double_bitt_bollard_production01_scene.py"
ATTEMPT = PROJECT / r"Production\Attempts\m02-harbor-double-bitt-bollard-deterministic-recovery01\attempt_20260811T1308000000000Z"
OUTPUT = ATTEMPT / "output"
CREATE_SCRIPT = OUTPUT / "scripts" / "create_m02_harbor_double_bitt_bollard_production01.py"
FINALIZER = ATTEMPT / "finalize_m02_harbor_double_bitt_bollard_production01_scene.py"
TERMINAL = ATTEMPT / "terminal_manifest.json"

SOURCE_BYTES = 201_985
SOURCE_SHA = "4cb6bc2acc06310c4328687d65c808db6adfe5b1c5e49774a81bec60bf4a08cb"
CREATE_SRC_BYTES = 30_610
CREATE_SRC_SHA = "PLACEHOLDER"
FINALIZER_SRC_BYTES = 17_357
FINALIZER_SRC_SHA = "7a60023ec34c2c74d01c9ecd65b7bdcbb5b014a2f1aecc4abbd564926fab0be3"


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


def rewrite_create_script(text: str) -> str:
    old = r"D:\Skyguard52\Production\Attempts\m02-harbor-double-bitt-bollard-grok-mcp-production01\attempt_20260811T1245000000000Z\output"
    new = str(OUTPUT)
    if old not in text:
        raise RuntimeError("Creation script missing expected attempt output path")
    return text.replace(old, new)


def rewrite_finalizer(text: str) -> str:
    old = r"D:\Skyguard52\Production\Attempts\m02-harbor-double-bitt-bollard-grok-mcp-production01\attempt_20260811T1245000000000Z\output"
    new = str(OUTPUT)
    if old not in text:
        raise RuntimeError("Finalizer missing expected attempt output path")
    return text.replace(old, new)


def run_blender(script: Path, stdout_path: Path, stderr_path: Path) -> int:
    cmd = [str(BLENDER), str(SOURCE), "--background", "--python", str(script)]
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, cwd=str(PROJECT), stdout=out, stderr=err, text=True)
    return int(proc.returncode)


def main() -> int:
    started = utc_now()
    if ATTEMPT.exists():
        raise RuntimeError(f"Attempt namespace already exists: {ATTEMPT}")
    if not BLENDER.is_file():
        raise RuntimeError(f"Missing Blender: {BLENDER}")

    create_src_sha = sha256(CREATE_SCRIPT_SRC)
    create_src_bytes = CREATE_SCRIPT_SRC.stat().st_size
    require_authority(SOURCE, SOURCE_BYTES, SOURCE_SHA)
    require_authority(CREATE_SCRIPT_SRC, create_src_bytes, create_src_sha)
    require_authority(FINALIZER_SRC, FINALIZER_SRC_BYTES, FINALIZER_SRC_SHA)

    heavy = heavy_running()
    if heavy:
        raise RuntimeError(f"Heavy processes active: {heavy}")

    for path in (
        OUTPUT,
        OUTPUT / "checkpoint",
        OUTPUT / "renders",
        OUTPUT / "exports",
        OUTPUT / "receipts",
        OUTPUT / "scripts",
    ):
        path.mkdir(parents=True, exist_ok=True)

    CREATE_SCRIPT.write_text(rewrite_create_script(CREATE_SCRIPT_SRC.read_text(encoding="utf-8")), encoding="utf-8")
    FINALIZER.write_text(rewrite_finalizer(FINALIZER_SRC.read_text(encoding="utf-8")), encoding="utf-8")

    create_stdout = ATTEMPT / "create_stdout.log"
    create_stderr = ATTEMPT / "create_stderr.log"
    final_stdout = ATTEMPT / "finalizer_stdout.log"
    final_stderr = ATTEMPT / "finalizer_stderr.log"

    create_code = run_blender(CREATE_SCRIPT, create_stdout, create_stderr)
    final_code = None
    if create_code == 0:
        final_code = run_blender(FINALIZER, final_stdout, final_stderr)

    expected_blend = OUTPUT / "M02_Harbor_DoubleBittBollard_Production01.blend"
    expected_glb = OUTPUT / "exports" / "M02_Harbor_DoubleBittBollard_Production01.glb"
    expected_report = OUTPUT / "grok_implementation_report.json"
    checkpoint_review = OUTPUT / "checkpoint" / "checkpoint_visual_review.json"
    checkpoint_renders = sorted((OUTPUT / "checkpoint").glob("*.png"))
    final_renders = sorted((OUTPUT / "renders").glob("*.png"))

    classification = "FAILED_WITH_EVIDENCE"
    if (
        create_code == 0
        and final_code == 0
        and expected_blend.is_file()
        and expected_glb.is_file()
        and expected_report.is_file()
        and checkpoint_review.is_file()
        and len(checkpoint_renders) >= 4
        and len(final_renders) >= 8
    ):
        classification = "PASSED_AWAITING_DIRECT_VISUAL_REVIEW"

    artifacts = []
    for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file()):
        artifacts.append(file_record(path))

    terminal = {
        "schema": "skyguard.m02-harbor-double-bitt-bollard.deterministic-recovery01.terminal.v1",
        "created_at_utc": utc_now(),
        "started_at_utc": started,
        "classification": classification,
        "asset": "M02 harbor double-bitt mooring bollard",
        "attempt_root": str(ATTEMPT),
        "execution": {
            "blender_launches": 1 if final_code is None else 2,
            "grok_launches": 0,
            "unreal_launches": 0,
            "retries": 0,
            "create_exit_code": create_code,
            "create_exit_code_type": "System.Int32",
            "finalizer_exit_code": final_code,
            "finalizer_exit_code_type": None if final_code is None else "System.Int32",
        },
        "authorities": {
            "source": file_record(SOURCE),
            "create_script_source": file_record(CREATE_SCRIPT_SRC),
            "finalizer_source": file_record(FINALIZER_SRC),
            "create_script_used": file_record(CREATE_SCRIPT),
            "finalizer_used": file_record(FINALIZER),
        },
        "outputs": {
            "blend": str(expected_blend) if expected_blend.is_file() else None,
            "glb": str(expected_glb) if expected_glb.is_file() else None,
            "implementation_report": str(expected_report) if expected_report.is_file() else None,
            "checkpoint_review": str(checkpoint_review) if checkpoint_review.is_file() else None,
            "checkpoint_render_count": len(checkpoint_renders),
            "final_render_count": len(final_renders),
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
