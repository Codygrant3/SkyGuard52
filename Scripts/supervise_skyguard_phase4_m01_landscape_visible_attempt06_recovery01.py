"""Resume immutable Attempt06 after a D3D12 render-state gate.

No build or authoring stage exists in this supervisor. It creates only the new
recovery_01 evidence root, refuses duplicate execution, and stops before
capture unless the fresh D3D12|SM6 receipt proves 16 render states.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from supervise_skyguard_phase4_m01_landscape_visible_attempt06 import (
    active_heavy_processes,
    assert_locked_items,
    capture_manifest_pass,
    csv_files,
    newest_new_csv,
    run_stage,
    save_json,
    sha256_file,
    utc_now,
    wait_for_zero_heavy_processes,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_CONTRACT.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--unreal-root", type=Path, default=Path(r"D:\UE_5.8"))
    parser.add_argument("--authorize-single-recovery-run", action="store_true")
    parser.add_argument("--editor-timeout", type=int, default=300)
    parser.add_argument("--profile-timeout", type=int, default=150)
    args = parser.parse_args()
    if not args.authorize_single_recovery_run:
        raise RuntimeError(
            "Recovery01 requires --authorize-single-recovery-run"
        )
    root = args.project_root.resolve()
    unreal_root = args.unreal_root.resolve()
    contract = json.loads(
        (
            root
            / "Docs/AAA_Review/"
            "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_CONTRACT.json"
        ).read_text(encoding="utf-8-sig")
    )
    if contract["recovery_id"] != (
        "P4.5-M01-LANDSCAPE-VISIBLE-006-RECOVERY-01"
    ):
        raise RuntimeError("Recovery01 contract ID mismatch")
    if active_heavy_processes():
        raise RuntimeError("exclusive heavy lane is not free")
    failure = contract["failure_boundary"]
    assert_locked_items(
        root,
        {
            "failed_manifest": failure["failed_manifest"],
            "failed_acceptance": failure["failed_editor_acceptance"],
        },
    )
    failed_manifest = json.loads(
        (root / failure["failed_manifest"]["file"]).read_text(
            encoding="utf-8-sig"
        )
    )
    failed_acceptance = json.loads(
        (root / failure["failed_editor_acceptance"]["file"]).read_text(
            encoding="utf-8-sig"
        )
    )
    if not (
        failed_manifest.get("terminal_state") == "FAILED"
        and len(failed_manifest.get("stages", [])) == 2
        and failed_acceptance.get("gate") == "FAIL"
        and failed_acceptance["landscape_visible_audit"][
            "visible_component_count"
        ]
        == 16
        and failed_acceptance["landscape_visible_audit"][
            "registered_component_count"
        ]
        == 16
        and failed_acceptance["landscape_visible_audit"][
            "render_state_created_component_count"
        ]
        == 0
        and failed_acceptance["landscape_visible_audit"][
            "contract_camera_frustum_intersection_count"
        ]
        == 5
    ):
        raise RuntimeError("failed Attempt06 boundary no longer matches")
    package_hashes = assert_locked_items(
        root, contract["immutable_packages"]
    )
    module_spec = contract["compiled_module"]
    compiled_module = root / module_spec["file"]
    if (
        not compiled_module.is_file()
        or sha256_file(compiled_module) != module_spec["sha256"]
    ):
        raise RuntimeError("compiled module hash failed")
    newest_source_mtime = max(
        path.stat().st_mtime_ns
        for path in (root / "Source/Skyguard52").glob("*")
        if path.is_file() and path.suffix.lower() in {".h", ".cpp"}
    )
    if compiled_module.stat().st_mtime_ns < newest_source_mtime:
        raise RuntimeError("compiled module is stale relative to native sources")
    recovery_root = root / contract["recovery_execution"]["recovery_root"]
    if recovery_root.exists():
        raise RuntimeError(
            "Recovery01 root already exists; refusing duplicate or overwrite"
        )
    project = root / "Skyguard52.uproject"
    editor = unreal_root / "Engine/Binaries/Win64/UnrealEditor.exe"
    render_verifier = (
        root
        / "Scripts/"
        "verify_skyguard_phase4_m01_landscape_attempt06_"
        "recovery01_render_state.py"
    )
    capture_script = (
        root
        / "Scripts/"
        "capture_skyguard_phase4_m01_landscape_visible_review_attempt06.py"
    )
    gate_script = (
        root
        / "Scripts/"
        "verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt06.py"
    )
    for path in (
        project,
        editor,
        render_verifier,
        capture_script,
        gate_script,
    ):
        if not path.is_file():
            raise RuntimeError("required Recovery01 file missing: " + str(path))
    logs_root = recovery_root / "logs"
    artifacts_root = recovery_root / "artifacts"
    captures_root = artifacts_root / "captures"
    logs_root.mkdir(parents=True, exist_ok=False)
    captures_root.mkdir(parents=True, exist_ok=False)
    manifest_path = recovery_root / "recovery_manifest.json"
    gate_path = recovery_root / "gate_report.json"
    render_receipt = artifacts_root / "render_state_acceptance.json"
    latest_gate = (
        root
        / "Saved/Reports/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_"
        "ATTEMPT06_RECOVERY01_LATEST.json"
    )
    baseline = contract["immutable_packages"]["baseline_map"]
    candidate = contract["immutable_packages"]["candidate_map"]
    material = contract["immutable_packages"]["candidate_material"]
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt06-recovery01-supervisor.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "contract_id": contract["contract_id"],
        "created_at_utc": utc_now(),
        "baseline_map": baseline["asset"],
        "candidate_map": candidate["asset"],
        "baseline_sha256_before": baseline["sha256"],
        "baseline_sha256_after": None,
        "candidate_sha256_before": candidate["sha256"],
        "candidate_sha256_after": None,
        "candidate_material_sha256_before": material["sha256"],
        "candidate_material_sha256_after": None,
        "initial_package_hashes": package_hashes,
        "controls": {
            "authoring_forbidden": True,
            "build_forbidden": True,
            "null_rhi_forbidden": True,
            "active_rhi_required": "D3D12|SM6",
            "sequential_processes_only": True,
            "render_verification_required_before_capture": True,
            "capture_required_before_profile": True,
            "warmup_seconds": 30,
            "measured_seconds": 60,
            "boot_csv_capture_forbidden": True,
            "world_or_package_save_allowed": False,
            "pcg_generation_allowed": False,
            "network_download_allowed": False,
            "automatic_retry_allowed": False,
            "promotion_allowed": False,
        },
        "stages": [],
        "artifacts": {
            "editor_acceptance": str(render_receipt),
            "baseline_capture_root": str(captures_root / "baseline"),
            "candidate_capture_root": str(captures_root / "candidate"),
            "baseline_profile_receipt": str(
                artifacts_root / "baseline_profile_receipt.json"
            ),
            "candidate_profile_receipt": str(
                artifacts_root / "candidate_profile_receipt.json"
            ),
            "baseline_csv": None,
            "candidate_csv": None,
        },
        "terminal_state": "RUNNING",
        "errors": [],
    }
    save_json(manifest_path, manifest)
    try:
        manifest["stages"].append(
            run_stage(
                "verify_candidate_render_state_d3d12_sm6",
                editor,
                [
                    str(project),
                    candidate["asset"],
                    f"-ExecutePythonScript={render_verifier}",
                    "-ScriptErrorsAreFatal",
                    (
                        "-SkyguardAttempt06RecoveryReceipt="
                        + str(render_receipt)
                    ),
                    "-unattended",
                    "-nop4",
                    "-NoSplash",
                    "-RenderOffscreen",
                    "-windowed",
                    "-ResX=1920",
                    "-ResY=1080",
                    "-d3d12",
                    "-sm6",
                ],
                logs_root,
                root,
                args.editor_timeout,
            )
        )
        render = json.loads(
            render_receipt.read_text(encoding="utf-8-sig")
        )
        if not (
            render.get("gate") == "PASS"
            and render.get("rhi_validation") == "D3D12|SM6"
            and render["landscape_visible_audit"][
                "render_state_created_component_count"
            ]
            == 16
            and render.get("package_hashes_unchanged") is True
            and render.get("world_saved") is False
            and render.get("pcg_generation_invoked") is False
        ):
            raise RuntimeError(
                "Recovery01 render-state receipt did not pass"
            )
        save_json(manifest_path, manifest)
        for mode, map_path in (
            ("baseline", baseline["asset"]),
            ("candidate", candidate["asset"]),
        ):
            output_root = captures_root / mode
            manifest["stages"].append(
                run_stage(
                    f"{mode}_capture",
                    editor,
                    [
                        str(project),
                        map_path,
                        f"-ExecutePythonScript={capture_script}",
                        "-ScriptErrorsAreFatal",
                        f"-SkyguardReviewMode={mode}",
                        f"-SkyguardReviewMap={map_path}",
                        f"-SkyguardReviewOutput={output_root}",
                        "-unattended",
                        "-nop4",
                        "-NoSplash",
                        "-RenderOffscreen",
                        "-windowed",
                        "-ResX=1920",
                        "-ResY=1080",
                        "-d3d12",
                        "-sm6",
                    ],
                    logs_root,
                    root,
                    args.editor_timeout,
                )
            )
            expected = 5 if mode == "baseline" else 12
            if not capture_manifest_pass(
                output_root / "capture_manifest.json", expected
            ):
                raise RuntimeError(
                    f"{mode} Recovery01 capture manifest failed"
                )
            save_json(manifest_path, manifest)
        for mode, map_path in (
            ("baseline", baseline["asset"]),
            ("candidate", candidate["asset"]),
        ):
            before_csv = csv_files(root)
            started_epoch = time.time()
            receipt = Path(
                manifest["artifacts"][f"{mode}_profile_receipt"]
            )
            manifest["stages"].append(
                run_stage(
                    f"{mode}_profile_measured",
                    editor,
                    [
                        str(project),
                        map_path,
                        "-game",
                        "-windowed",
                        "-ResX=1920",
                        "-ResY=1080",
                        "-d3d12",
                        "-sm6",
                        "-NoVSync",
                        "-NoSplash",
                        "-NoLoadingScreen",
                        (
                            "-ExecCmds=r.SetRes 1920x1080w,"
                            "r.ScreenPercentage 100,"
                            "sg.ViewDistanceQuality 3,"
                            "sg.ShadowQuality 3,"
                            "sg.PostProcessQuality 3,"
                            "sg.TextureQuality 3,"
                            "sg.EffectsQuality 3,"
                            "sg.FoliageQuality 3,"
                            "BugItGo 25200 -8000 10000 -25.226895 90 0"
                        ),
                        "-csvCategories=Global",
                        "-csvGpuStats",
                        "-csvNamedEvents",
                        (
                            "-SkyguardP45ProfileContractId="
                            + contract["contract_id"]
                        ),
                        (
                            "-SkyguardP45ProfileRunId="
                            + contract["recovery_id"]
                            + "_"
                            + mode
                        ),
                        f"-SkyguardP45ProfileExpectedMap={map_path}",
                        f"-SkyguardP45ProfileReceipt={receipt}",
                        "-SkyguardP45ProfileWarmupSeconds=30",
                        "-SkyguardP45ProfileMeasuredSeconds=60",
                    ],
                    logs_root,
                    root,
                    args.profile_timeout,
                )
            )
            csv_path = newest_new_csv(root, before_csv, started_epoch)
            manifest["artifacts"][f"{mode}_csv"] = str(csv_path)
            profile = json.loads(receipt.read_text(encoding="utf-8-sig"))
            if not (
                profile.get("gate") == "PASS"
                and profile.get("contract_id") == contract["contract_id"]
                and profile.get("same_process_warmup_and_measurement")
                is True
                and profile.get("startup_frames_excluded") is True
                and profile.get("warmup_seconds") == 30
                and profile.get("measured_seconds") == 60
            ):
                raise RuntimeError(f"{mode} profile receipt failed")
            save_json(manifest_path, manifest)
        final_hashes = assert_locked_items(
            root, contract["immutable_packages"]
        )
        if final_hashes != package_hashes:
            raise RuntimeError("immutable package hash changed")
        manifest["baseline_sha256_after"] = final_hashes["baseline_map"]
        manifest["candidate_sha256_after"] = final_hashes["candidate_map"]
        manifest["candidate_material_sha256_after"] = final_hashes[
            "candidate_material"
        ]
        manifest["final_package_hashes"] = final_hashes
        manifest["terminal_state"] = "EVIDENCE_CAPTURED_PENDING_GATE"
        save_json(manifest_path, manifest)
        manifest["stages"].append(
            run_stage(
                "verify_recovery01_visible_gpu_gate",
                Path(sys.executable),
                [
                    str(gate_script),
                    "--manifest",
                    str(manifest_path),
                    "--output",
                    str(gate_path),
                    "--latest-output",
                    str(latest_gate),
                ],
                logs_root,
                root,
                120,
                accepted_exit_codes=(0, 2),
            )
        )
        gate = json.loads(gate_path.read_text(encoding="utf-8-sig"))
        if gate.get("technical_gate") != "PASS":
            raise RuntimeError("Recovery01 technical gate failed")
        manifest["terminal_state"] = (
            "GATE_COMPLETE"
            if gate.get("gate") == "PASS"
            else "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW"
        )
    except Exception as error:
        manifest["errors"].append(str(error))
        manifest["terminal_state"] = "FAILED"
        raise
    finally:
        manifest["finished_at_utc"] = utc_now()
        try:
            manifest["final_package_hashes"] = assert_locked_items(
                root, contract["immutable_packages"]
            )
        except Exception as lock_error:
            manifest["errors"].append(str(lock_error))
            manifest["terminal_state"] = "FAILED"
        save_json(manifest_path, manifest)
        remaining = wait_for_zero_heavy_processes(30)
        if remaining:
            raise RuntimeError(
                "heavy processes remain after Recovery01: "
                + repr(remaining)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
