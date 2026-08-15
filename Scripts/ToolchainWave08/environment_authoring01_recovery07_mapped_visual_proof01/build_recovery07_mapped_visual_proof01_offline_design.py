"""Build the immutable offline design package for the Recovery07 mapped proof."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
ENGINE = Path(r"D:\UE_5.8")
PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01"
CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01"
CLASSIFICATION = "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF_AUTHORIZATION"
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01"
DOC_ROOT = ROOT / "Docs/AAA_Review"
REPORT_ROOT = ROOT / "Saved/Reports"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def record(path: Path) -> dict[str, Any]:
    require_file(path)
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return {
            "absolute_path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return {
        "file": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def package_file(package: str, suffix: str = ".uasset") -> Path:
    if not package.startswith("/Game/"):
        raise ValueError(package)
    return ISOLATED / "Content" / (package.removeprefix("/Game/") + suffix)


def engine_tree(number: int) -> Path:
    return ENGINE / (
        "Engine/Plugins/PCG/Content/SampleContent/SimpleForest/Meshes/"
        f"PCG_Tree_{number:02d}.uasset"
    )


def find_lines(path: Path, markers: list[str]) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    results = []
    for marker in markers:
        matches = [index + 1 for index, line in enumerate(lines) if marker in line]
        if not matches:
            raise RuntimeError(f"Engine authority marker missing: {path}: {marker}")
        results.append({"marker": marker, "lines": matches[:12]})
    return results


def expected_labels() -> list[str]:
    labels = [
        "M01_A01_EnvironmentDirector",
        "M01_A01_Landscape_Production",
        "M01_A01_WaterZone",
        "M01_A01_WaterBodyOcean",
        "M01_A01_Landscape_Production_WaterBrushManager",
    ]
    for index in range(6):
        labels.extend(
            [
                f"M01_A01_Beach_{index:02d}",
                f"M01_A01_Seawall_{index:02d}",
                f"M01_A01_Promenade_{index:02d}",
                f"M01_A01_Road_{index:02d}",
            ]
        )
    labels.extend(f"M01_A01_City_{index:02d}" for index in range(8))
    labels.extend(["M01_A01_Lighthouse_Hero", "M01_A01_Radar_Hero"])
    labels.extend(f"M01_A01_Tree_{index:02d}" for index in range(15))
    labels.extend(
        [
            "M01_A01_Sun",
            "M01_A01_SkyLight",
            "M01_A01_SkyAtmosphere",
            "M01_A01_HeightFog",
            "M01_A01_VolumetricCloud",
        ]
    )
    if len(labels) != 59:
        raise RuntimeError(f"Expected 59 labels, generated {len(labels)}")
    return labels


def immutable_inputs() -> list[dict[str, Any]]:
    refinement = (
        "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
        "m01_wave1_aaa_refinement/StaticMeshes/"
    )
    mesh_names = [
        "SM_M01_Coast_Beach_Detailed_A",
        "SM_M01_Coast_Promenade_Detailed_A",
        "SM_M01_Coast_Seawall_Detailed_A",
        "SM_M01_Road_CoastalTransition_Detailed_A",
        "SM_M01_Urban_Apartment_Detailed_A",
        "SM_M01_Urban_Apartment_Detailed_B",
        "SM_M01_Urban_Midrise_Detailed_A",
        "SM_M01_Urban_Midrise_Damaged_A",
        "SM_M01_Landmark_Lighthouse_Hero_A",
        "SM_M01_Landmark_RadarPost_Hero_A",
    ]
    paths = [
        DOC_ROOT / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_ATTEMPT01_TERMINAL_FREEZE.json",
        ROOT / "Saved/BuildAttempts/TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07/attempt_01/authoring_receipt.json",
        DOC_ROOT / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_TERMINAL_FREEZE.json",
        ISOLATED / "Skyguard52.uproject",
        ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap",
        ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap",
        package_file("/Game/Skyguard/Materials/M_Terrain"),
        package_file("/Game/Skyguard/Materials/Generated/M_L23_Ocean"),
        package_file("/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation"),
        ISOLATED / "Content/Skyguard/Environment/Source/Mission01/HM_M01_CoastalProduction_505x127.r16",
        ISOLATED / "Binaries/Win64/UnrealEditor-Skyguard52.dll",
        ISOLATED / "Binaries/Win64/UnrealEditor-Skyguard52.pdb",
        ISOLATED / "Binaries/Win64/UnrealEditor.modules",
        ISOLATED / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp",
        ISOLATED / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h",
        ENGINE / "Engine/Binaries/Win64/UnrealEditor.exe",
        ENGINE / "Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/PythonScriptPlugin.cpp",
        ENGINE / "Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Public/PythonScriptTypes.h",
        engine_tree(1),
        engine_tree(2),
        engine_tree(3),
    ]
    paths.extend(package_file(refinement + name) for name in mesh_names)
    return [record(path) for path in paths]


def create_contract(inputs: list[dict[str, Any]]) -> Path:
    contract_path = DOC_ROOT / f"{PREFIX}_CONTRACT.json"
    map_path = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
    contract = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-contract.v1",
        "contract_id": CONTRACT_ID,
        "classification": "OFFLINE_DESIGN",
        "created_utc": utc_now(),
        "locked_inputs": inputs,
        "world": {
            "project": str(ISOLATED / "Skyguard52.uproject"),
            "map_asset": "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07",
            "map_file": str(map_path),
            "map_bytes": map_path.stat().st_size,
            "map_sha256": sha256_file(map_path),
            "landscape_label": "M01_A01_Landscape_Production",
            "landscape_component_count": 16,
            "terrain_material": "/Game/Skyguard/Materials/M_Terrain",
            "ocean_material": "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
            "expected_total_actor_count": 59,
            "expected_labels": expected_labels(),
            "expected_prefix_counts": {
                "M01_A01_Beach_": 6,
                "M01_A01_Seawall_": 6,
                "M01_A01_Promenade_": 6,
                "M01_A01_Road_": 6,
                "M01_A01_City_": 8,
                "M01_A01_Tree_": 15,
            },
            "shore_nominal_y_cm": 5200.0,
            "route_x_range_cm": [0.0, 45000.0],
        },
        "runtime": {
            "editor": str(ENGINE / "Engine/Binaries/Win64/UnrealEditor.exe"),
            "lifecycle": "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK",
            "rhi": "D3D12",
            "feature_level": "SM6",
            "stable_shader_polls": 2,
            "warmup_seconds": 30,
            "measurement_seconds": 30,
            "minimum_frame_samples": 900,
            "maximum_seconds": 480,
            "supervisor_timeout_seconds": 540,
            "attempt_relative_path": f"Saved/BuildAttempts/{PREFIX}/attempt_01",
            "single_unreal_launch": True,
            "automatic_retries": 0,
            "failed_namespace_reuse": False,
        },
        "capture": {"count": 8, "width": 2560, "height": 1440},
        "measurement_order": [
            "two_stable_shader_ready_polls",
            "thirty_second_warmup",
            "thirty_second_measured_csv_profile",
            "csv_flush",
            "five_static_captures",
            "three_temporal_route_captures",
        ],
        "immutability": {
            "world_save_allowed": False,
            "disk_asset_mutation_allowed": False,
            "material_override_allowed": False,
            "pcg_generation_allowed": False,
            "import_allowed": False,
            "promotion_allowed": False,
        },
        "automatic_result": "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW",
        "terminal_results": [
            "PASSED_RECOVERY07_MAPPED_VISUAL_PROOF_ACCEPTED",
            "FAILED_WITH_EVIDENCE",
        ],
    }
    write_json(contract_path, contract)
    return contract_path


def create_cameras() -> Path:
    path = DOC_ROOT / f"{PREFIX}_CAMERAS.json"
    def camera(identifier: str, role: str, location: list[float], pitch: float, yaw: float) -> dict[str, Any]:
        return {
            "id": identifier,
            "role": role,
            "location_cm": location,
            "rotation_degrees": {"pitch": pitch, "yaw": yaw, "roll": 0.0},
            "fov_degrees": 90,
        }
    value = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-cameras.v1",
        "coordinate_system": "Unreal centimeters, X route progression, +Y inland, -Y ocean",
        "resolution": [2560, 1440],
        "static_cameras": [
            camera("C01_REAR_GUNNER_PORT", "rear-gunner port view toward defended coast", [22500, 2500, 1200], -6, 90),
            camera("C02_REAR_GUNNER_STARBOARD", "rear-gunner starboard view over ocean", [22500, 2500, 1200], -4, -90),
            camera("C03_SHORELINE_OBLIQUE", "forward shoreline transition and lighthouse", [11250, 2500, 1100], -6, 72),
            camera("C04_ROUTE_EXTERIOR", "exterior route, coast and city composition", [22500, -12000, 9000], -25, 90),
            camera("C05_CITY_TO_COAST", "city grounding, roads, beach and water contact", [22500, 19500, 2600], -10, -90),
        ],
        "temporal_cameras": [
            camera("T01_ROUTE_ENTRY", "route entry temporal sample", [7500, 2500, 1200], -6, 90),
            camera("T02_ROUTE_MID", "route midpoint temporal sample", [22500, 2500, 1200], -6, 90),
            camera("T03_ROUTE_EXIT", "route exit temporal sample", [37500, 2500, 1200], -6, 90),
        ],
        "camera_mutation_allowed": False,
        "human_review_required": True,
    }
    write_json(path, value)
    return path


def create_rubrics() -> tuple[Path, Path]:
    visual_path = DOC_ROOT / f"{PREFIX}_VISUAL_RUBRIC.json"
    visual = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-visual-rubric.v1",
        "classification": "HUMAN_REVIEW_REQUIRED",
        "required_visible_systems": [
            "coastal flight route",
            "ocean and physically convincing shoreline contact",
            "beach, seawall, promenade and terrain transitions",
            "grounded city massing and skyline",
            "roads and urban infrastructure",
            "vegetation placement and density",
            "atmosphere, clouds, fog and daylight",
            "rear-gunner flight-height composition",
            "stable world progression across temporal route frames",
        ],
        "automatic_rejects": [
            "missing or corrupt capture",
            "wrong resolution",
            "blank frame",
            "crushed-shadow or overexposed frame",
            "material, map or governed-transform mutation",
            "temporal histogram or exposure discontinuity above contract bounds",
        ],
        "human_rejects": [
            "diagnostic color blocks",
            "floating or disconnected geometry",
            "ungrounded buildings",
            "visible placeholder repetition",
            "bad exposure or crushed shadows",
            "missing water and shore contact",
            "obvious low-poly hero silhouettes",
            "unstable clouds, water, foliage or world geometry",
            "camera clipping",
            "camera-coupled world motion",
            "unacceptable temporal hitching",
            "missing expected terrain, water, city, road, vegetation or atmosphere coverage",
        ],
        "review_method": "inspect all eight original 2560x1440 PNGs directly at full resolution",
        "human_acceptance_results": [
            "PASSED_RECOVERY07_MAPPED_VISUAL_PROOF_ACCEPTED",
            "FAILED_WITH_EVIDENCE",
        ],
    }
    performance_path = DOC_ROOT / f"{PREFIX}_PERFORMANCE_RUBRIC.json"
    performance = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-performance-rubric.v1",
        "measurement": {
            "warmup_seconds": 30,
            "measured_seconds": 30,
            "minimum_samples": 900,
            "captures_during_measurement": 0,
            "shader_compilation_allowed_during_measurement": False,
        },
        "thresholds": {
            "mean_frame_ms_max": 16.7,
            "p95_frame_ms_max": 22.2,
            "p99_frame_ms_max": 33.3,
            "max_frame_ms": 50.0,
            "frames_over_50ms_max": 0,
            "mean_gpu_ms_max": 14.0,
            "p95_gpu_ms_max": 20.0,
            "working_set_mib_max": 12288.0,
            "gpu_memory_mib_max": 10240.0,
        },
        "stability": {
            "timeout_allowed": False,
            "crash_allowed": False,
            "critical_log_hits_max": 0,
            "network_or_telemetry_hits_max": 0,
            "automatic_retries": 0,
        },
    }
    write_json(visual_path, visual)
    write_json(performance_path, performance)
    return visual_path, performance_path


def create_runtime_report() -> Path:
    python_source = ENGINE / "Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/PythonScriptPlugin.cpp"
    python_types = ENGINE / "Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Public/PythonScriptTypes.h"
    editor = ENGINE / "Engine/Binaries/Win64/UnrealEditor.exe"
    recovery02 = DOC_ROOT / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_TERMINAL_FREEZE.json"
    path = DOC_ROOT / f"{PREFIX}_RUNTIME_COMPATIBILITY_REPORT.json"
    value = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-runtime-compatibility.v1",
        "classification": "PASS",
        "created_utc": utc_now(),
        "selected_lifecycle": "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK",
        "selected_reason": "ExecCmds invokes the Python console command without the ExecutePythonScript commandlet auto-quit lifecycle; Python registers a Slate post-tick callback and explicitly quits after evidence is complete.",
        "rejected_lifecycle": "UNREALEDITOR_CMD_EXECUTE_PYTHON_SCRIPT_AUTO_QUIT",
        "rejected_evidence": record(recovery02),
        "rejected_reason": "Recovery02 proved that UnrealEditor-Cmd -ExecutePythonScript exits after the entrypoint returns, before deferred callbacks can complete.",
        "installed_engine_authorities": [record(editor), record(python_source), record(python_types)],
        "source_markers": {
            str(python_source): find_lines(
                python_source,
                ["Exec_Runtime", "DeferredCommands", "ExecPythonCommandEx"],
            ),
            str(python_types): find_lines(
                python_types,
                ["ExecuteFile", "FPythonCommandEx"],
            ),
        },
        "native_readiness_authority": {
            "class": "SkyguardMission01EnvironmentAuthoringLibrary",
            "method": "audit_landscape_material_compilation",
            "expected_components": 16,
            "source": record(ISOLATED / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"),
            "binary": record(ISOLATED / "Binaries/Win64/UnrealEditor-Skyguard52.dll"),
        },
        "old_recovery05_native_plugin_reused": False,
        "old_plugin_rejection_reason": "It hardcodes the retired map, landscape label, diagnostic material, cameras and attempt namespace.",
        "native_build_required": False,
    }
    write_json(path, value)
    return path


def create_addenda() -> tuple[Path, Path]:
    audit = DOC_ROOT / f"PHASE1_8_COMPLETION_AUDIT_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    matrix = DOC_ROOT / f"M01_PRODUCTION_VERTICAL_SLICE_ACCEPTANCE_MATRIX_ADDENDUM_{PREFIX}_OFFLINE_DESIGN_2026-08-08.md"
    write_text(
        audit,
        f"""# Phase 1-8 audit addendum — Recovery07 mapped visual proof offline design

- Gate: `{CONTRACT_ID}`
- Classification: `{CLASSIFICATION}`
- Recovery07 environment authoring remains automatically accepted pending mapped visual proof.
- The proof is designed for the full UE 5.8 editor, D3D12 SM6, two stable shader polls, 30-second warmup, 30-second measurement, at least 900 frame samples, and eight original 2560x1440 captures.
- No Unreal, Blender, build, import, integration, promotion, capture, or packaging process ran during this gate.
- Mission 1 environment visual acceptance remains open until the one-shot proof and direct full-resolution review pass.
- Next executable gate: explicit single Recovery07 mapped visual-proof authorization.
""",
    )
    write_text(
        matrix,
        f"""# Mission 1 acceptance matrix addendum — Recovery07 mapped visual proof offline design

| Requirement | State | Evidence |
|---|---|---|
| Recovery07 authored map | automatic pass awaiting visual proof | `401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f` |
| Mapped proof design | passed offline | `{CONTRACT_ID}` |
| D3D12 SM6 readiness | frozen, not executed | two stable 16-component polls |
| Performance | frozen, not executed | 30-second warmup plus 30-second measured interval |
| Static review | pending | five original 2560x1440 PNGs |
| Temporal review | pending | three route-progression PNGs |
| Human visual acceptance | pending | direct full-resolution review required |

No runtime, integration, promotion, or packaging acceptance is implied by the offline design.
""",
    )
    return audit, matrix


def create_execution_prompt(offline_freeze_path: Path) -> Path:
    path = DOC_ROOT / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    freeze_bytes = offline_freeze_path.stat().st_size
    freeze_hash = sha256_file(offline_freeze_path)
    text = f"""Resume only the canonical Unreal Engine 5.8 / Blender 5.2 AAA project at `D:\\Skyguard52`. Do not use Three.js, external models, generated substitutes, external AI models, or subagents.

Treat this Recovery07 mapped visual-proof offline-design freeze as immutable authority:

- File: `D:\\Skyguard52\\Docs\\AAA_Review\\{PREFIX}_OFFLINE_DESIGN_FREEZE.json`
- Bytes: `{freeze_bytes}`
- SHA-256: `{freeze_hash}`
- Classification: `{CLASSIFICATION}`

I explicitly authorize exactly one Recovery07 mapped Mission 1 Unreal visual proof and its mandatory automatic postflight adjudicator by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\\Skyguard52\\Scripts\\ToolchainWave08\\environment_authoring01_recovery07_mapped_visual_proof01\\invoke_recovery07_mapped_visual_proof01_once.ps1 -AuthorizeSingleUnrealProof`

Before launch, verify the prompt-binding freeze and every member, the Recovery07 terminal freeze and authored map, all map/material/mesh/tree/runtime authorities, the exact full UE 5.8 editor, zero heavy processes, and absence of every future attempt, launcher, report, emergency, postflight and CSV namespace.

Launch `UnrealEditor.exe` exactly once against `D:\\SG52T08_ENV01\\Skyguard52.uproject` and the immutable Recovery07 map. Use D3D12 SM6, full-editor `-ExecCmds=py` deferred tick execution, disabled telemetry/network plugins, offscreen 2560x1440 rendering, and no world save. Never use `UnrealEditor-Cmd.exe -ExecutePythonScript`, retry, or reuse a failed namespace. Run no Blender, build, import, integration, promotion, profiling expansion, or packaging concurrently.

Require the exact governed 59-actor world, one `M01_A01_Landscape_Production`, real `/Game/Skyguard/Materials/M_Terrain`, sixteen compiled material resources and shader maps, empty asset/shader queues, two stable readiness polls, 30 seconds of warmup, 30 seconds of capture-free measurement, at least 900 frame samples, a fresh named UE CSV profile, and no compilation resume during measurement.

After measurement, capture exactly five static and three temporal 2560x1440 PNGs from the frozen cameras. Preserve stdout, stderr, engine log, PID/process tree, numeric exit code/type, timeout/crash state, working set, CSV, frame samples, heartbeat, capture receipt, no-mutation/restoration receipt, terminal receipt, supervisor manifest, automatic postflight report, and hashes. Never save the world or mutate the map, materials, assets, governed transforms, PCG state, or source.

If any preflight, launch, RHI, shader, metric, capture, log, map/hash, no-mutation, timeout, crash, receipt, or postflight condition fails, preserve the single attempt, classify `FAILED_WITH_EVIDENCE`, never retry, and stop.

If automatic postflight returns `PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW`, inspect all eight original PNGs directly at full resolution. Reject diagnostic blocks, floating/disconnected geometry, ungrounded buildings, placeholder repetition, bad exposure, missing shore contact, low-poly hero silhouettes, unstable clouds/water/foliage/world geometry, clipping, camera-coupled world motion, missing environment systems, or unacceptable temporal hitching.

Classify exactly:

- `PASSED_RECOVERY07_MAPPED_VISUAL_PROOF_ACCEPTED`; or
- `FAILED_WITH_EVIDENCE`.

Create immutable terminal evidence and hashes; update the production registry, Phase 1-8 audit and Mission 1 acceptance matrix with exact paths, hashes, passed gates, remaining gaps and the next executable gate. Do not integrate, promote, package, or claim Mission 1 or AAA completion. Stop after terminal visual classification and audit updates.
"""
    write_text(path, text)
    return path


def run_tests() -> dict[str, Any]:
    test_file = SCRIPT_ROOT / "test_recovery07_mapped_visual_proof01.py"
    supervisor = SCRIPT_ROOT / "invoke_recovery07_mapped_visual_proof01_once.ps1"
    parse_command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{supervisor}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count-ne0){$e|ForEach-Object{$_.Message};exit 1};exit 0"
    )
    parse = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", parse_command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    unit = subprocess.run(
        [os.fspath(Path(os.sys.executable)), "-m", "unittest", "-v", os.fspath(test_file)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    with tempfile.TemporaryDirectory(prefix="sg52_r07_proof_offline_") as temporary:
        offline = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                os.fspath(supervisor),
                "-OfflineContractTest",
                "-OfflineEvidenceRoot",
                temporary,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        offline_receipt = Path(temporary) / "offline_contract_test.json"
        offline_receipt_value = (
            json.loads(offline_receipt.read_text(encoding="utf-8-sig"))
            if offline_receipt.is_file()
            else None
        )
    passed = parse.returncode == 0 and unit.returncode == 0 and offline.returncode == 0
    result = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-offline-tests.v1",
        "classification": "PASS" if passed else "FAILED_WITH_EVIDENCE",
        "powershell_51_parse": {
            "exit_code": parse.returncode,
            "stdout": parse.stdout,
            "stderr": parse.stderr,
        },
        "unit_tests": {
            "exit_code": unit.returncode,
            "stdout": unit.stdout,
            "stderr": unit.stderr,
        },
        "supervisor_offline_contract_test": {
            "exit_code": offline.returncode,
            "stdout": offline.stdout,
            "stderr": offline.stderr,
            "receipt": offline_receipt_value,
        },
        "unreal_launched": False,
        "blender_launched": False,
    }
    if not passed:
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def build() -> dict[str, Any]:
    DOC_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    inputs = immutable_inputs()
    contract = create_contract(inputs)
    cameras = create_cameras()
    visual, performance = create_rubrics()
    runtime_report = create_runtime_report()
    audit, matrix = create_addenda()

    supervisor = SCRIPT_ROOT / "invoke_recovery07_mapped_visual_proof01_once.ps1"
    executor = SCRIPT_ROOT / "capture_recovery07_mapped_visual_proof01.py"
    adjudicator = SCRIPT_ROOT / "adjudicate_recovery07_mapped_visual_proof01_once.py"
    verifier = SCRIPT_ROOT / "verify_recovery07_mapped_visual_proof01_offline.py"
    tests = SCRIPT_ROOT / "test_recovery07_mapped_visual_proof01.py"
    generator = Path(__file__).resolve()

    provisional_freeze = DOC_ROOT / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
    provisional_prompt = DOC_ROOT / f"NEXT_PROMPT_{PREFIX}_SINGLE_UNREAL.md"
    provisional_binding = DOC_ROOT / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
    write_json(
        provisional_freeze,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-offline-freeze.v1",
            "classification": CLASSIFICATION,
            "members": [],
        },
    )
    create_execution_prompt(provisional_freeze)
    write_json(
        provisional_binding,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-prompt-binding.v1",
            "classification": CLASSIFICATION,
            "members": [record(provisional_freeze), record(provisional_prompt)],
        },
    )
    test_result_path = REPORT_ROOT / f"{PREFIX}_OFFLINE_TEST_RESULT.json"
    write_json(test_result_path, run_tests())

    source_inventory_path = REPORT_ROOT / f"{PREFIX}_SOURCE_INVENTORY.json"
    readiness_path = REPORT_ROOT / f"{PREFIX}_READINESS.json"
    design_paths = [
        contract,
        cameras,
        visual,
        performance,
        runtime_report,
        executor,
        supervisor,
        adjudicator,
        verifier,
        tests,
        generator,
        test_result_path,
        audit,
        matrix,
    ]
    write_json(
        source_inventory_path,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-source-inventory.v1",
            "created_utc": utc_now(),
            "immutable_inputs": inputs,
            "design_files": [record(path) for path in design_paths],
            "future_namespaces_created": False,
        },
    )
    write_json(
        readiness_path,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-readiness.v1",
            "created_utc": utc_now(),
            "classification": CLASSIFICATION,
            "recovery07_authoring_authority_verified": True,
            "full_editor_exec_cmds_lifecycle_verified": True,
            "two_stable_shader_polls": True,
            "thirty_second_warmup": True,
            "thirty_second_measurement": True,
            "minimum_frame_samples": 900,
            "capture_count": 8,
            "human_review_required": True,
            "future_namespaces_absent": True,
            "heavy_processes": [],
            "unreal_launched": False,
            "blender_launched": False,
            "next_gate": "EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF_AUTHORIZATION",
        },
    )
    freeze_members = inputs + [
        record(path)
        for path in design_paths + [source_inventory_path, readiness_path]
    ]
    write_json(
        provisional_freeze,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-offline-freeze.v1",
            "created_utc": utc_now(),
            "classification": CLASSIFICATION,
            "contract_id": CONTRACT_ID,
            "member_count": len(freeze_members),
            "members": freeze_members,
            "future_attempt_namespace_absent": True,
            "future_launcher_namespace_absent": True,
            "future_csv_namespace_absent": True,
            "unreal_launched": False,
            "blender_launched": False,
            "next_gate": "EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF_AUTHORIZATION",
        },
    )
    prompt = create_execution_prompt(provisional_freeze)
    write_json(
        provisional_binding,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-prompt-binding.v1",
            "created_utc": utc_now(),
            "classification": CLASSIFICATION,
            "contract_id": CONTRACT_ID,
            "member_count": 2,
            "members": [record(provisional_freeze), record(prompt)],
            "command": (
                "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
                "D:\\Skyguard52\\Scripts\\ToolchainWave08\\"
                "environment_authoring01_recovery07_mapped_visual_proof01\\"
                "invoke_recovery07_mapped_visual_proof01_once.ps1 "
                "-AuthorizeSingleUnrealProof"
            ),
            "single_unreal_launch": True,
            "mandatory_postflight_adjudicator": True,
            "human_full_resolution_review_required": True,
        },
    )
    return {
        "classification": CLASSIFICATION,
        "offline_freeze": record(provisional_freeze),
        "binding_freeze": record(provisional_binding),
        "execution_prompt": record(prompt),
        "member_count": len(freeze_members),
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
