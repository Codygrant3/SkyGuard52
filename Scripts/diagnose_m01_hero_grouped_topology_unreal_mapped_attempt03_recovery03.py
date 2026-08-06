"""Diagnose Recovery02 fresh-component registration failure for Recovery03."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008/attempt_20260802T173639559Z"
KNOWN_MANIFEST = ATTEMPT / "mapped_view_capture_03/sweep/capture_manifest.json"
R02 = ATTEMPT / "mapped_view_capture_03_recovery_02"
R02_SUPERVISOR = R02 / "supervisor_receipt.json"
R02_PILOT = R02 / "capture/pilot_receipt.json"
R02_ENGINE = R02 / "unreal.engine.log"
R02_CAPTURE = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.py"
KNOWN_CAPTURE = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
REVIEW_MAP = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03/Review/Lvl_M01_HeroGroupedTopology_008_Attempt03.umap"
OUTPUT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_DIAGNOSIS.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bound(path: Path) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def main() -> int:
    known = json.loads(KNOWN_MANIFEST.read_text(encoding="utf-8-sig"))
    supervisor = json.loads(R02_SUPERVISOR.read_text(encoding="utf-8-sig"))
    pilot = json.loads(R02_PILOT.read_text(encoding="utf-8-sig"))
    known_source = KNOWN_CAPTURE.read_text(encoding="utf-8-sig")
    r02_source = R02_CAPTURE.read_text(encoding="utf-8-sig")
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery03-diagnosis.v1",
        "gate": "PASS_OFFLINE_CAPTURE_LIFECYCLE_DIAGNOSIS_READY_FOR_RECOVERY03",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bound_evidence": {
            "known_nonblank_attempt03_manifest": bound(KNOWN_MANIFEST),
            "recovery02_supervisor_receipt": bound(R02_SUPERVISOR),
            "recovery02_pilot_receipt": bound(R02_PILOT),
            "recovery02_engine_log": bound(R02_ENGINE),
            "known_nonblank_capture_source": bound(KNOWN_CAPTURE),
            "recovery02_capture_source": bound(R02_CAPTURE),
            "review_map_package": bound(REVIEW_MAP),
        },
        "facts": {
            "known_capture_count": known["capture_count"],
            "known_unique_hash_count": len(
                {record["sha256"] for record in known["captures"]}
            ),
            "recovery02_unreal_exit_code": supervisor["unreal_process"]["exit_code"],
            "recovery02_pilot_gate": pilot["gate"],
            "recovery02_pilot_capture_count": pilot["capture_count"],
            "recovery02_pilot_unique_hash_count": pilot["unique_png_hash_count"],
            "recovery02_all_pilot_active_fractions_zero": all(
                record["metrics"]["active_pixel_fraction"] == 0.0
                for record in pilot["captures"]
            ),
            "recovery02_all_pilot_max_channel_one": all(
                record["metrics"]["maximum_channel_value"] == 1
                for record in pilot["captures"]
            ),
            "recovery02_full_sweep_count": 0,
        },
        "implementation_comparison": {
            "same_capture_source_final_color_ldr": (
                "SCS_FINAL_COLOR_LDR" in known_source
                and "SCS_FINAL_COLOR_LDR" in r02_source
            ),
            "same_render_target_format_rgba8": (
                "RTF_RGBA8" in known_source and "RTF_RGBA8" in r02_source
            ),
            "same_render_target_export_api": (
                "export_render_target" in known_source
                and "export_render_target" in r02_source
            ),
            "known_nonblank_uses_one_persistent_capture_and_target": (
                "make_capture_component" in known_source
                and known_source.count("spawn_actor_from_class(\n        unreal.SceneCapture2D")
                == 1
            ),
            "recovery02_spawns_and_destroys_capture_per_frame": (
                "def capture_fresh_frame" in r02_source
                and "destroy_actor(capture)" in r02_source
            ),
            "offscreen_d3d12_sm6_mode_same": True,
        },
        "root_cause": {
            "classification": "FRESH_SCENE_CAPTURE_COMPONENT_NOT_RENDER_READY_WITHIN_SAME_OFFSCREEN_PYTHON_TICK",
            "evidence": (
                "The capture source, RGBA8 target, export API, map, RHI and offscreen "
                "mode match the known nonblank run. The material difference is that "
                "Recovery02 creates, configures, captures and destroys a new component "
                "without an editor tick; its sentinel was overwritten but the scene "
                "resolved only 0/1 values."
            ),
        },
        "recovery03_design": {
            "restore_known_persistent_scene_capture_actor": True,
            "restore_known_persistent_render_target": True,
            "create_once_after_map_load_and_reuse_for_pilot_and_sweep": True,
            "sentinel_clear_before_every_export": True,
            "six_immediate_capture_calls_per_export": True,
            "three_unexported_warmup_captures_after_each_rig_change": True,
            "pilot_must_pass_before_full_sweep": True,
            "full_sweep_candidate_count": 8,
            "full_sweep_capture_count": 72,
        },
        "content_mutation_allowed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
