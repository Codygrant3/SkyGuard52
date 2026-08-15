from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery10_Checkpoint01"
SUPERVISOR_TERMINAL = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01_TERMINAL_SUPERVISOR.json"
POSTFLIGHT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01_POSTFLIGHT.json"
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery10\build_m01_visible_environment_kit_refinement01_stagea_recovery10_checkpoint01.py"
WORKER_BYTES = 11271
WORKER_SHA256 = "097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba"
R09_POSTFLIGHT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery09_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery09_checkpoint01.py"


def load_common():
    spec = importlib.util.spec_from_file_location("skyguard_r09_postflight_common", R09_POSTFLIGHT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the Recovery09 postflight utilities")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
AdjudicationError = COMMON.AdjudicationError
require = COMMON.require
sha256 = COMMON.sha256
record = COMMON.record
png_dimensions = COMMON.png_dimensions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(POSTFLIGHT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.output).resolve()
    require(not target.exists(), f"Postflight namespace already exists: {target}")
    require(
        WORKER.is_file()
        and WORKER.stat().st_size == WORKER_BYTES
        and sha256(WORKER) == WORKER_SHA256,
        "Worker authority drift",
    )
    require(SUPERVISOR_TERMINAL.is_file(), "Supervisor terminal manifest is missing")
    supervisor = json.loads(SUPERVISOR_TERMINAL.read_text(encoding="utf-8-sig"))
    require(supervisor.get("terminal") is True, "Supervisor is not terminal")
    require(
        supervisor.get("classification")
        == "PASSED_AUTOMATIC_AWAITING_MANDATORY_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW",
        "Supervisor did not reach automatic checkpoint success",
    )
    require(
        supervisor.get("exit_code") == 0
        and supervisor.get("exit_code_type") == "System.Int32",
        "Blender exit-code authority failed",
    )
    require(
        supervisor.get("blender_launch_count") == 1
        and supervisor.get("retry_count") == 0
        and supervisor.get("unreal_launch_count") == 0,
        "Launch-count contract failed",
    )
    require(OUTPUT.is_dir(), "Checkpoint output root is missing")

    blend = sorted(OUTPUT.rglob("*.blend"))
    glbs = sorted(OUTPUT.rglob("*.glb"))
    checkpoints = sorted((OUTPUT / "renders" / "checkpoints").glob("*.png"))
    finals = [path for path in OUTPUT.rglob("*.png") if "renders\\final" in str(path)]
    textures = [path for path in OUTPUT.rglob("*.png") if "\\textures\\" in str(path)]
    require(len(blend) == 1, "Checkpoint blend cardinality is not one")
    require(not glbs and not finals and not textures, "Checkpoint output contains prohibited finalization artifacts")
    require(len(checkpoints) == 9, "Checkpoint PNG cardinality is not nine")
    png_records = []
    for path in checkpoints:
        width, height = png_dimensions(path)
        require((width, height) == (1920, 1080), f"Checkpoint dimensions failed: {path}")
        png_records.append({**record(path), "width": width, "height": height})

    required_receipts = [
        "dimension_receipt.json",
        "topology_uv_receipt.json",
        "checkpoint_receipt.json",
        "source_parity_receipt.json",
        "artifact_inventory.json",
        "terminal_receipt.json",
    ]
    receipts = {
        name: json.loads((OUTPUT / name).read_text(encoding="utf-8-sig"))
        for name in required_receipts
    }
    require(receipts["dimension_receipt.json"].get("passed") is True, "Dimension receipt failed")
    require(receipts["topology_uv_receipt.json"].get("passed") is True, "Topology receipt failed")
    require(
        receipts["topology_uv_receipt.json"].get("structural_counts")
        == {
            "buildings": 5,
            "vehicles": 8,
            "trees": 10,
            "streetlights": 10,
            "puddles": 6,
            "review_ocean": 1,
            "review_surf_foam": 1,
        },
        "Structural-count receipt failed",
    )
    checkpoint_receipt = receipts["checkpoint_receipt.json"]
    require(
        checkpoint_receipt.get("passed") is True and checkpoint_receipt.get("count") == 9,
        "Checkpoint receipt failed",
    )
    entries = checkpoint_receipt.get("checkpoints", [])
    require(len(entries) == 9, "Checkpoint receipt entry count failed")
    night_entries = [entry for entry in entries if entry.get("condition") == "night"]
    storm_entries = [entry for entry in entries if entry.get("condition") == "storm"]
    require(len(night_entries) == 3 and len(storm_entries) == 3, "Night/storm checkpoint count failed")
    require(
        all(entry.get("night_review_lighting_aimed") is True for entry in night_entries),
        "Camera-targeted night review lighting was not recorded for every night camera",
    )
    require(
        all(entry.get("storm_review_lighting_aimed") is True for entry in storm_entries),
        "Camera-targeted storm review lighting was not recorded for every storm camera",
    )
    for entry in night_entries:
        metrics = entry.get("metrics", {})
        require(float(metrics.get("mean_luma_linear", 0.0)) >= 0.008, f"Night luminance failed: {entry.get('camera')}")
        require(float(metrics.get("black_fraction_linear_0_01", 1.0)) <= 0.70, f"Night black fraction failed: {entry.get('camera')}")
        require(len(entry.get("calibration_passes", [])) <= 2, f"Night pass limit failed: {entry.get('camera')}")
        require(float(entry.get("exposure", 99.0)) <= 7.0, f"Night exposure ceiling failed: {entry.get('camera')}")
    for entry in storm_entries:
        metrics = entry.get("metrics", {})
        require(float(metrics.get("mean_luma_linear", 0.0)) >= 0.018, f"Storm luminance failed: {entry.get('camera')}")
        require(float(metrics.get("black_fraction_linear_0_01", 1.0)) <= 0.58, f"Storm black fraction failed: {entry.get('camera')}")
        require(len(entry.get("calibration_passes", [])) <= 2, f"Storm pass limit failed: {entry.get('camera')}")
        require(float(entry.get("exposure", 99.0)) <= 7.0, f"Storm exposure ceiling failed: {entry.get('camera')}")
    require(
        receipts["source_parity_receipt.json"].get("passed") is True
        and receipts["source_parity_receipt.json"].get("sha256") == WORKER_SHA256,
        "Source-parity receipt failed",
    )
    terminal = receipts["terminal_receipt.json"]
    require(terminal.get("automatic_validation_passed") is True, "Worker automatic validation failed")
    require(
        terminal.get("status") == "CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "Worker terminal status failed",
    )
    require(terminal.get("finalization_authorized") is False, "Worker improperly authorized finalization")
    produced = sorted(path for path in OUTPUT.rglob("*") if path.is_file())
    require(len(produced) == 16, f"Output file cardinality is not sixteen: {len(produced)}")

    payload = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery10-checkpoint01.postflight.v1",
        "gate": GATE,
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "supervisor_terminal": record(SUPERVISOR_TERMINAL),
        "worker": record(WORKER),
        "blend": record(blend[0]),
        "checkpoints": png_records,
        "night": {
            "checkpoint_count": 3,
            "all_camera_targets_aimed": True,
            "minimum_mean_luma_linear": min(float(entry["metrics"]["mean_luma_linear"]) for entry in night_entries),
            "maximum_black_fraction_linear_0_01": max(float(entry["metrics"]["black_fraction_linear_0_01"]) for entry in night_entries),
            "passed": True,
        },
        "storm": {
            "checkpoint_count": 3,
            "all_camera_targets_aimed": True,
            "minimum_mean_luma_linear": min(float(entry["metrics"]["mean_luma_linear"]) for entry in storm_entries),
            "maximum_black_fraction_linear_0_01": max(float(entry["metrics"]["black_fraction_linear_0_01"]) for entry in storm_entries),
            "passed": True,
        },
        "receipt_count": 6,
        "total_output_file_count": 16,
        "independent_png_header_validation": "PASS_9_OF_9",
        "recovery09_output_geometry_reused": False,
        "finalization_authorized": False,
        "stageb_binding_authorized": False,
        "unreal_import_authorized": False,
        "direct_full_resolution_visual_review_required": True,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(target)
    print(json.dumps({"classification": payload["classification"], "postflight": str(target)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": GATE, "classification": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}"}))
        raise
