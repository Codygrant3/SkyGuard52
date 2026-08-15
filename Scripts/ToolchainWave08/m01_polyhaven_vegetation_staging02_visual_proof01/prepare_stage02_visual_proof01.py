"""Prepare and freeze the fresh Stage02 D3D12 proof contract."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02_visual_proof01"
DOC = ROOT / "Docs/AAA_Review"
PREFIX = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
CONTRACT = DOC / f"{PREFIX}_CONTRACT.json"
CAMERAS = DOC / f"{PREFIX}_CAMERAS.json"
VISUAL = DOC / f"{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE = DOC / f"{PREFIX}_PERFORMANCE_RUBRIC.json"
FREEZE = DOC / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
BINDING = DOC / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"Required file is absent: {path}")
    return {"absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_new(path: Path, value: object) -> None:
    if path.exists():
        raise RuntimeError(f"Fresh artifact exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    map_file = ISOLATED / "Content/M01/Lvl_M01_PolyHavenVegetationStaging02.umap"
    stage_freeze = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_TERMINAL_FREEZE.json"
    stage_inventory = ROOT / "Saved/Reports/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_ARTIFACT_INVENTORY.json"
    scripts = [
        SCRIPT_ROOT / "capture_m01_polyhaven_vegetation_staging02_visual_proof01.py",
        SCRIPT_ROOT / "adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_once.py",
        SCRIPT_ROOT / "invoke_m01_polyhaven_vegetation_staging02_visual_proof01_once.ps1",
    ]
    for path in scripts + [stage_freeze, stage_inventory, map_file]:
        record(path)

    actor_counts = {
        "M01_ACA03R01_City_": 9,
        "M01_Promenade_Bollard_": 13,
        "M01_Promenade_BicycleRack_": 8,
        "M01_Promenade_UtilityCabinet_": 5,
        "M01_Promenade_StormDrain_": 12,
        "M01_Promenade_LitterBin_": 10,
        "M01_HSSC01R01_Window_": 36,
        "M01_HSSC01R01_Prop_": 11,
        "M01_HSSC02_CoastalA_": 2,
        "M01_HSSC03_City_": 6,
        "M01_HSSC03_RearWindow_": 36,
        "M01_PHV02_fir_sapling_": 2,
        "M01_PHV02_pine_sapling_small_": 2,
        "M01_PHV02_shrub_02_": 6,
        "M01_PHV02_shrub_04_": 8,
        "M01_PHV02_grass_medium_02_": 10,
        "M01_VEK02_City_": 0,
        "M01_VEK02_Lighthouse_": 0,
        "M01_RS01_Tree_": 0,
    }
    expected_labels = [
        "M01_A01_EnvironmentDirector", "M01_A01_Landscape_Production", "M01_A01_WaterZone",
        "M01_A01_WaterBodyOcean", "M01_A01_Landscape_Production_WaterBrushManager", "M01_RS01_Sun",
        "M01_RS01_SkyLight", "M01_RS01_SkyAtmosphere", "M01_RS01_HeightFog", "M01_RS01_VolumetricCloud",
        "M01_RS01_PostProcess", "M01_PR01_FillSun", "M01_C06R01_Corridor_TERRAIN",
        "M01_C06R01_Corridor_HARDSCAPE", "M01_C06R01_Corridor_DETAILS", "M01_ACA03R01_Corridor_CONTACT",
        "M01_HSSC02_CoastalA_TERRAIN", "M01_HSSC02_CoastalA_HARDSCAPE",
    ]
    locked = [
        record(stage_freeze), record(stage_inventory), record(map_file),
        record(ISOLATED / "Skyguard52.uproject"),
        record(ISOLATED / "Binaries/Win64/UnrealEditor-Skyguard52.dll"),
        record(ISOLATED / "Binaries/Win64/UnrealEditor-Skyguard52.pdb"),
        record(ISOLATED / "Binaries/Win64/UnrealEditor.modules"),
        record(Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe")),
        record(ROOT / "Production/standing_heavy_process_authorization.json"),
        *(record(path) for path in scripts),
    ]
    contract = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-contract.v1",
        "contract_id": "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01",
        "classification": "OFFLINE_DESIGN",
        "automatic_result": "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW",
        "capture": {"count": 8, "width": 2560, "height": 1440},
        "runtime": {
            "editor": r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe", "editor_mode": True,
            "rhi": "D3D12", "feature_level": "SM6", "stable_shader_polls": 2,
            "warmup_seconds": 30, "measurement_seconds": 30, "minimum_frame_samples": 900,
            "maximum_seconds": 900, "supervisor_timeout_seconds": 1200, "single_unreal_launch": True,
            "automatic_retries": 0, "failed_namespace_reuse": False,
            "attempt_relative_path": f"Saved/BuildAttempts/{PREFIX}/attempt_01",
            "executor_startup_receipt_relative_path": f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01/executor_startup_receipt.json",
            "runtime_actor_inventory_receipt_relative_path": f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01/runtime_actor_inventory.json",
            "executor_early_terminal_receipt_relative_path": f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01/executor_early_terminal.json",
            "csv_flush": {"maximum_seconds": 10, "minimum_bytes": 1024, "poll_interval_seconds": 0.5, "stable_polls": 2},
        },
        "world": {
            "project": str(ISOLATED / "Skyguard52.uproject"),
            "map_asset": "/Game/M01/Lvl_M01_PolyHavenVegetationStaging02",
            "map_file": str(map_file), "map_bytes": map_file.stat().st_size, "map_sha256": sha256(map_file),
            "terrain_material": "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_UrbanGround_Tiled",
            "landscape_label": "M01_A01_Landscape_Production", "landscape_component_count": 16,
            "raw_full_editor_actor_count_is_exact": True, "raw_full_editor_actor_count": 193,
            "maximum_ungoverned_editor_actors": 1, "expected_total_governed_actor_count": 192,
            "expected_labels": expected_labels, "expected_prefix_counts": actor_counts,
        },
        "presentation_assertions": {
            "source_backed_vegetation_species": 5, "explicit_unreal_materials": 7,
            "grounded_vegetation_placements": 28, "retained_cell03_governed_actors": 164,
            "vegetation_staging_only": True, "known_debt_is_not_acceptance": True,
        },
        "immutability": {"disk_asset_mutation_allowed": False, "world_save_allowed": False, "material_override_allowed": False, "import_allowed": False, "pcg_generation_allowed": False, "promotion_allowed": False},
        "locked_inputs": locked,
        "terminal_results": ["PASSED_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_ACCEPTED", "FAILED_WITH_EVIDENCE"],
    }
    write_new(CONTRACT, contract)

    cameras = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-cameras.v1",
        "coordinate_system": "Unreal centimeters, X route progression, +Y inland, -Y ocean",
        "resolution": [2560, 1440], "camera_mutation_allowed": False, "human_review_required": True,
        "comparison_authority": "Cell03 cameras retained; C02 and C05 directly expose the new inland vegetation placements",
        "static_cameras": [
            {"id": "C01_REAR_GUNNER_PORT", "role": "flight-height vegetation silhouette and grounded skyline", "location_cm": [12500, 3000, 1600], "rotation_degrees": {"pitch": -7, "yaw": 90, "roll": 0}, "fov_degrees": 82},
            {"id": "C02_FACADE_DISTRICT_OBLIQUE", "role": "oblique source-backed trees, shrubs, grass, facade and terrain proof", "location_cm": [7800, 6500, 1700], "rotation_degrees": {"pitch": -7, "yaw": 48, "roll": 0}, "fov_degrees": 72},
            {"id": "C03_SHORE_CONTACT", "role": "shoreline and vegetation context", "location_cm": [9000, 1200, 1800], "rotation_degrees": {"pitch": -9, "yaw": 82, "roll": 0}, "fov_degrees": 72},
            {"id": "C04_CELL_EXTERIOR", "role": "elevated distribution, skyline, route and coastal composition", "location_cm": [12500, -4200, 5200], "rotation_degrees": {"pitch": -25, "yaw": 90, "roll": 0}, "fov_degrees": 70},
            {"id": "C05_INLAND_DISTRICT_TO_COAST", "role": "direct inland vegetation material, scale, grounding and density proof", "location_cm": [12500, 18500, 3600], "rotation_degrees": {"pitch": -14, "yaw": -90, "roll": 0}, "fov_degrees": 74},
        ],
        "temporal_cameras": [
            {"id": "T01_CELL_ENTRY", "role": "route-entry temporal vegetation sample", "location_cm": [7500, 3000, 1600], "rotation_degrees": {"pitch": -7, "yaw": 90, "roll": 0}, "fov_degrees": 82},
            {"id": "T02_CELL_MID", "role": "route-midpoint temporal vegetation sample", "location_cm": [12500, 3000, 1600], "rotation_degrees": {"pitch": -7, "yaw": 90, "roll": 0}, "fov_degrees": 82},
            {"id": "T03_CELL_EXIT", "role": "route-exit temporal vegetation sample", "location_cm": [17500, 3000, 1600], "rotation_degrees": {"pitch": -7, "yaw": 90, "roll": 0}, "fov_degrees": 82},
        ],
    }
    write_new(CAMERAS, cameras)
    visual = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-rubric.v1",
        "classification": "HUMAN_REVIEW_REQUIRED",
        "automatic_rejects": ["missing or wrong-resolution capture", "map or governed-transform mutation", "fewer than 900 frame samples", "wrong vegetation actor counts or mesh identities", "missing terminal, capture, performance or log evidence"],
        "human_rejects": ["opaque foliage cards or rectangular alpha halos", "inside-out, black, unlit or fluorescent foliage", "floating, buried, implausibly scaled or intersecting vegetation", "obvious duplicate rotation or density pattern", "source-backed vegetation materially degrades the Cell03 composition", "camera clipping, camera-coupled motion, exposure instability or hitching"],
        "required_pass_observations": ["five species visually resolve", "masked foliage edges are clean", "branches and bark retain PBR detail", "28 placements are grounded", "sparse review density remains plausible", "runtime remains within performance bounds"],
        "honest_deferred_scope": ["final production vegetation density", "vehicles", "signage and street life", "architectural variation", "accepted lighthouse landmark", "final water and beach treatment"],
        "human_acceptance_results": ["PASSED_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_ACCEPTED", "FAILED_WITH_EVIDENCE"],
    }
    write_new(VISUAL, visual)
    performance = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-performance.v1",
        "measurement": {"warmup_seconds": 30, "measured_seconds": 30, "minimum_samples": 900, "captures_during_measurement": 0, "shader_compilation_allowed_during_measurement": False},
        "thresholds": {"mean_frame_ms_max": 16.7, "p95_frame_ms_max": 22.2, "p99_frame_ms_max": 33.3, "max_frame_ms": 50.0, "frames_over_50ms_max": 0, "mean_gpu_ms_max": 14.0, "p95_gpu_ms_max": 20.0, "working_set_mib_max": 12288.0, "gpu_memory_mib_max": 10240.0},
        "stability": {"timeout_allowed": False, "crash_allowed": False, "automatic_retries": 0, "critical_log_hits_max": 0, "network_or_telemetry_hits_max": 0},
    }
    write_new(PERFORMANCE, performance)

    # Contract must lock the now-final camera/rubric files.
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract["locked_inputs"].extend([record(CAMERAS), record(VISUAL), record(PERFORMANCE)])
    CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    for script in scripts[:2]:
        namespace = runpy.run_path(str(script), run_name="not_main")
        compile(namespace["transform_source"](), str(script) + "::transformed", "exec")
    parse_command = (
        "$e=$null;[System.Management.Automation.Language.Parser]::ParseFile(" +
        "'" + str(scripts[2]).replace("'", "''") + "',[ref]$null,[ref]$e)|Out-Null;" +
        "if($e.Count){$e|%{$_.Message};exit 1}else{exit 0}"
    )
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", parse_command], check=True)

    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    members = [record(CONTRACT), record(CAMERAS), record(VISUAL), record(PERFORMANCE), *(record(path) for path in scripts), record(stage_freeze), record(stage_inventory), record(map_file), record(ROOT / "Production/standing_heavy_process_authorization.json")]
    classification = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION"
    freeze = {"schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-offline-design-freeze.v1", "classification": classification, "standing_authorization_classification": classification, "created_utc": created, "members": members, "offline_validation": {"python_ast": "PASS_2_OF_2", "transformed_python_compile": "PASS_2_OF_2", "powershell_parse": "PASS", "json_parse": "PASS_4_OF_4", "one_unreal_start_process_path": True, "automatic_retries": 0, "future_namespaces_absent": True}, "execution": {"unreal_launches": 1, "automatic_retries": 0, "rhi": "D3D12", "feature_level": "SM6", "warmup_seconds": 30, "measurement_seconds": 30, "minimum_frame_samples": 900, "captures": 8, "resolution": [2560, 1440], "supervisor_timeout_seconds": 1200}, "one_shot_command": f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {scripts[2]} -AuthorizeSingleUnrealProof", "runtime_promotion": False}
    write_new(FREEZE, freeze)
    binding_members = [record(CONTRACT), *(record(path) for path in scripts), record(FREEZE), record(ROOT / "Production/standing_heavy_process_authorization.json")]
    binding = {"schema": "skyguard.m01-polyhaven-vegetation-staging02.visual-proof01-execution-binding-freeze.v1", "classification": classification, "standing_authorization_classification": classification, "created_utc": created, "members": binding_members, "one_shot_command": freeze["one_shot_command"], "runtime_promotion": False}
    write_new(BINDING, binding)
    print(json.dumps({"classification": classification, "freeze": record(FREEZE), "binding": record(BINDING)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
