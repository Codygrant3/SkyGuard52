from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery09_Checkpoint01"
SUPERVISOR_TERMINAL = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01_TERMINAL_SUPERVISOR.json"
POSTFLIGHT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01_POSTFLIGHT.json"
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery09\build_m01_visible_environment_kit_refinement01_stagea_recovery09_checkpoint01.py"
WORKER_BYTES = 11322
WORKER_SHA256 = "0b8baf2524a1f864acdc84bb6c1ab83da45432d42fa84d8ad300fdb9aea30cab"


class AdjudicationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AdjudicationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    require(len(header) == 24, f"Truncated PNG header: {path}")
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature: {path}")
    require(header[12:16] == b"IHDR", f"Missing PNG IHDR chunk: {path}")
    width, height = struct.unpack(">II", header[16:24])
    require(width > 0 and height > 0, f"Invalid PNG dimensions: {path}")
    return width, height


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
    counts = receipts["topology_uv_receipt.json"].get("structural_counts", {})
    require(
        counts
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
    checkpoint_entries = checkpoint_receipt.get("checkpoints", [])
    require(len(checkpoint_entries) == 9, "Checkpoint receipt entry count failed")
    night_entries = [entry for entry in checkpoint_entries if entry.get("condition") == "night"]
    require(len(night_entries) == 3, "Night checkpoint receipt count failed")
    require(
        all(entry.get("night_review_lighting_aimed") is True for entry in night_entries),
        "Camera-targeted night review lighting was not recorded for every night camera",
    )
    for entry in night_entries:
        metrics = entry.get("metrics", {})
        require(
            float(metrics.get("mean_luma_linear", 0.0)) >= 0.008,
            f"Night mean luminance failed: {entry.get('camera')}",
        )
        require(
            float(metrics.get("black_fraction_linear_0_01", 1.0)) <= 0.70,
            f"Night black fraction failed: {entry.get('camera')}",
        )
        require(
            len(entry.get("calibration_passes", [])) <= 2,
            f"Night calibration pass limit failed: {entry.get('camera')}",
        )
        require(
            float(entry.get("exposure", 99.0)) <= 7.0,
            f"Night exposure ceiling failed: {entry.get('camera')}",
        )
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
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery09-checkpoint01.postflight.v1",
        "gate": GATE,
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "supervisor_terminal": record(SUPERVISOR_TERMINAL),
        "worker": record(WORKER),
        "blend": record(blend[0]),
        "checkpoints": png_records,
        "targeted_night_review_lighting": {
            "checkpoint_count": len(night_entries),
            "all_camera_targets_aimed": all(
                entry.get("night_review_lighting_aimed") is True for entry in night_entries
            ),
            "total_calibration_passes": sum(
                len(entry.get("calibration_passes", [])) for entry in night_entries
            ),
            "minimum_final_mean_luma_linear": min(
                float(entry["metrics"]["mean_luma_linear"]) for entry in night_entries
            ),
            "maximum_final_black_fraction_linear_0_01": max(
                float(entry["metrics"]["black_fraction_linear_0_01"]) for entry in night_entries
            ),
            "maximum_final_exposure": max(float(entry["exposure"]) for entry in night_entries),
            "passed": True,
        },
        "receipt_count": len(required_receipts),
        "total_output_file_count": len(produced),
        "independent_png_header_validation": "PASS_9_OF_9",
        "recovery08_output_geometry_reused": False,
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
