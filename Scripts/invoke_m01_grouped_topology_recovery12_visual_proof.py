"""Run the one compile-gated Recovery12 mapped viewport proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
EDITOR = Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe")
UPROJECT = ROOT / "Skyguard52.uproject"
OUTPUT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY12_VISUAL"
REVIEW_MAP = "/Game/Skyguard/Maps/Review/M01_HeroGroupedTopology_008"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize-single-recovery12-visual-proof", action="store_true")
    parser.add_argument("--compile-receipt", required=True)
    args = parser.parse_args()
    if not args.authorize_single_recovery12_visual_proof:
        raise RuntimeError("Explicit Recovery12 visual-proof authorization is required")
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise RuntimeError("Recovery12 visual namespace already used; retry forbidden")

    compile_receipt_path = Path(args.compile_receipt)
    compile_receipt = json.loads(compile_receipt_path.read_text(encoding="utf-8"))
    if compile_receipt["gate"] != "PASS_RECOVERY12_FULL_MODULE_COMPILE":
        raise RuntimeError("Recovery12 visual proof requires an accepted compile receipt")
    module = compile_receipt["compiled_module"]
    module_path = ROOT / module["path"]
    if not module_path.is_file() or sha256(module_path) != module["sha256"]:
        raise RuntimeError("Compiled module no longer matches its receipt")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt = OUTPUT / f"attempt_{stamp}_{module['sha256'][:8]}"
    capture = attempt / "capture"
    attempt.mkdir(parents=True)
    stdout_path = attempt / "unreal.stdout.log"
    stderr_path = attempt / "unreal.stderr.log"
    engine_log = attempt / "unreal.engine.log"
    supervisor_receipt = attempt / "visual_proof_receipt.json"
    command = [
        str(EDITOR), str(UPROJECT), REVIEW_MAP, "-game",
        "-SkyguardM01Recovery12ContractId=M01-HERO-GROUPED-TOPOLOGY-ATTEMPT03-RECOVERY12",
        f"-SkyguardM01Recovery12ExpectedMap={REVIEW_MAP}",
        f"-SkyguardM01Recovery12Output={capture}",
        "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen",
        "-windowed", "-ForceRes", "-ResX=2048", "-ResY=2048",
        "-d3d12", "-sm6", "-NoVSync", "-stdout", "-FullStdOutLogOutput",
        f"-abslog={engine_log}", "-NoAssetRegistryCache",
        "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3",
    ]
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        try:
            exit_code = process.wait(timeout=600)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(["taskkill", "/pid", str(process.pid), "/t", "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            exit_code = 124

    native_receipt_path = capture / "capture_receipt.json"
    native = json.loads(native_receipt_path.read_text(encoding="utf-8")) if native_receipt_path.is_file() else None
    images = sorted(capture.rglob("*.png")) if capture.is_dir() else []
    combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in (stdout_path, stderr_path, engine_log) if path.is_file())
    critical = any(token in combined for token in ("Fatal error", "LowLevelFatalError", "Assertion failed", "GPU Crash", "DXGI_ERROR_DEVICE_", "Out of video memory"))
    success = (
        exit_code == 0 and not timed_out and not critical and native is not None
        and native.get("gate") == "PASS_RECOVERY12_HIGHRES_CAPTURE_AWAITING_OFFLINE_AUDIT"
        and len(native.get("pilot_captures", [])) == 3
        and len(native.get("full_view_captures", [])) == 9
        and len(images) >= 9
    )
    receipt = {
        "schema": "skyguard.m01.grouped-topology.recovery12-visual-proof.v1",
        "gate": "PASS_RECOVERY12_VISUAL_PROOF_AWAITING_HUMAN_REVIEW" if success else "FAIL_RECOVERY12_VISUAL_PROOF_TERMINAL",
        "compile_receipt": str(compile_receipt_path),
        "compile_receipt_sha256": sha256(compile_receipt_path),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "critical_log_signature": critical,
        "native_receipt": str(native_receipt_path) if native_receipt_path.is_file() else None,
        "native_receipt_sha256": sha256(native_receipt_path) if native_receipt_path.is_file() else None,
        "image_count": len(images),
        "images": [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in images],
        "automatic_retry_forbidden": True,
    }
    supervisor_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"attempt_root": str(attempt), "receipt": str(supervisor_receipt), **receipt}, indent=2, sort_keys=True))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
