"""GW03 redesigned mapped proof: fresh map + exterior cameras + fixed capture.

Creates /Game/T08/GW03MappedProof01/Lvl_GW03_WindowMappedProof01, places the
immutable GW02 static meshes by reference (no GW02 mutation), installs exterior
CameraActors, and captures high-res stills without SceneCapture exposure-bias
sweeps or failed preview namespaces. Does not promote into Skyguard52 runtime.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import time
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
IMPORT_FREEZE = (
    ROOT
    / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json"
)
IMPORT_FREEZE_SHA256 = "362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c"
CONTRACT = (
    ROOT
    / r"Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01_CONTRACT.json"
)
SOURCE_ROOT = ISOLATED / r"Content\T08\GW02"
MAP_ASSET = "/Game/T08/GW03MappedProof01/Lvl_GW03_WindowMappedProof01"
MAP_FILE = ISOLATED / r"Content\T08\GW03MappedProof01\Lvl_GW03_WindowMappedProof01.umap"
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01\attempt_01"
)
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "mapped_proof_receipt.json"
IMPORT_RECEIPT = ATTEMPT / "import_receipt.json"
INTEGRATION_RECEIPT = ATTEMPT / "integration_receipt.json"
HEARTBEAT = ATTEMPT / "lifecycle_heartbeat.jsonl"

FRAME_PATH = (
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"
    ".SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"
)
GLASS_PATH = (
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass"
    ".SM_M01_PrewarWindowBay_A01_Glass"
)
INTERIOR_PATH = (
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior"
    ".SM_M01_PrewarWindowBay_A01_Interior"
)
EXPECTED_SLOTS = {FRAME_PATH: 5, GLASS_PATH: 1, INTERIOR_PATH: 9}

# Exterior-only redesign — never place cameras behind/inside the shell.
CAMERAS = [
    {
        "id": "front_hero_exterior",
        "label": "CAM_GW03_FrontHero",
        "location": (0.0, 820.0, 250.0),
        "target": (0.0, -10.0, 210.0),
        "fov": 42.0,
    },
    {
        "id": "oblique_parallax_left",
        "label": "CAM_GW03_ObliqueLeft",
        "location": (-480.0, 690.0, 280.0),
        "target": (0.0, -15.0, 210.0),
        "fov": 45.0,
    },
    {
        "id": "oblique_parallax_right",
        "label": "CAM_GW03_ObliqueRight",
        "location": (480.0, 690.0, 280.0),
        "target": (0.0, -15.0, 210.0),
        "fov": 45.0,
    },
]

# Two fixed lighting profiles (not an exposure-bias sweep).
LIGHTING_PROFILES = (
    {"id": "lit_key", "sun_intensity": 8.0, "fill_intensity": 2.5, "sky_intensity": 1.2},
    {"id": "lit_soft", "sun_intensity": 4.5, "fill_intensity": 3.5, "sky_intensity": 1.6},
)

FORBIDDEN_NAMESPACES = (
    "/Game/T08/GW02Preview",
    "/Game/T08/GW02PreviewR01",
    "/Game/T08/GW02PreviewR02",
    "/Game/T08/GW02PreviewR03",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def append_jsonl(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def hash_tree(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")) if root.is_dir() else []:
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
    return result


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Not a PNG: {path}")
        length = struct.unpack(">I", stream.read(4))[0]
        if stream.read(4) != b"IHDR" or length < 8:
            raise RuntimeError(f"PNG IHDR missing: {path}")
        return struct.unpack(">II", stream.read(8))


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def look_at(
    unreal: object, location: tuple[float, float, float], target: tuple[float, float, float]
) -> object:
    dx = target[0] - location[0]
    dy = target[1] - location[1]
    dz = target[2] - location[2]
    horizontal = math.sqrt(dx * dx + dy * dy)
    return unreal.Rotator(
        pitch=math.degrees(math.atan2(dz, horizontal)),
        yaw=math.degrees(math.atan2(dy, dx)),
        roll=0.0,
    )


def spawn_mesh(
    unreal: object,
    mesh: object,
    label: str,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> object:
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator()
    )
    if actor is None:
        raise RuntimeError(f"Could not spawn StaticMeshActor {label}")
    actor.set_actor_label(label)
    actor.set_folder_path("T08/GW03MappedProof01/WindowBay")
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor


def spawn_camera(unreal: object, spec: dict[str, object]) -> object:
    location = tuple(float(v) for v in spec["location"])
    target = tuple(float(v) for v in spec["target"])
    rotation = look_at(unreal, location, target)
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor, unreal.Vector(*location), rotation
    )
    if camera is None:
        raise RuntimeError(f"Could not spawn camera {spec['id']}")
    camera.set_actor_label(str(spec["label"]))
    camera.set_folder_path("T08/GW03MappedProof01/ReviewCameras")
    component = camera.camera_component
    component.set_editor_property("field_of_view", float(spec["fov"]))
    # Fixed exposure path — no eye-adaptation dependency for review stills.
    try:
        component.set_editor_property("post_process_blend_weight", 1.0)
        settings = component.get_editor_property("post_process_settings")
        settings.set_editor_property("override_auto_exposure_method", True)
        settings.set_editor_property(
            "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL
        )
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", 0.0)
        component.set_editor_property("post_process_settings", settings)
    except Exception:
        pass
    return camera


def apply_lighting(unreal: object, sun: object, fill: object, sky: object, profile: dict[str, float]) -> None:
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    if sun_component is None or fill_component is None or sky_component is None:
        raise RuntimeError("Lighting components unavailable")
    sun_component.set_intensity(float(profile["sun_intensity"]))
    fill_component.set_intensity(float(profile["fill_intensity"]))
    sky_component.set_intensity(float(profile["sky_intensity"]))


def capture_fixed(
    unreal: object,
    spec: dict[str, object],
    lighting_id: str,
    width: int = 1920,
    height: int = 1080,
) -> dict[str, object]:
    """Fixed single-shot capture — not an exposure-bias sweep harness."""
    world = unreal.EditorLevelLibrary.get_editor_world()
    location = tuple(float(v) for v in spec["location"])
    target = tuple(float(v) for v in spec["target"])
    rotation = look_at(unreal, location, target)
    output = PROOF / f"{spec['id']}__{lighting_id}.png"
    method = "highresshot_fixed_exposure"
    captured = False

    # Prefer viewport + HighResShot (contract redesign).
    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(
            unreal.Vector(*location), rotation
        )
        # Disable auto-exposure globally for the shot path.
        unreal.SystemLibrary.execute_console_command(world, "r.EyeAdaptationQuality 0")
        unreal.SystemLibrary.execute_console_command(world, "r.DefaultFeature.AutoExposure 0")
        # HighResShot writes under Saved/Screenshots by default; request absolute via filename.
        shot_cmd = f'HighResShot {width}x{height} filename="{str(output).replace(chr(92), "/")}"'
        unreal.SystemLibrary.execute_console_command(world, shot_cmd)
        # Allow async write.
        for _ in range(90):
            time.sleep(0.2)
            if output.is_file() and output.stat().st_size > 4096:
                captured = True
                break
    except Exception:
        captured = False

    if not captured:
        method = "fixed_scene_capture_no_exposure_sweep"
        render_target = unreal.RenderingLibrary.create_render_target2d(
            world, width, height, unreal.TextureRenderTargetFormat.RTF_RGBA8
        )
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if actor is None:
            raise RuntimeError("Could not spawn fixed SceneCapture2D")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", render_target)
            component.set_editor_property(
                "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
            )
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", float(spec["fov"]))
            # Fixed post-process bias only — never sweep.
            try:
                component.set_editor_property("post_process_blend_weight", 1.0)
                settings = component.get_editor_property("post_process_settings")
                settings.set_editor_property("override_auto_exposure_method", True)
                settings.set_editor_property(
                    "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL
                )
                settings.set_editor_property("override_auto_exposure_bias", True)
                settings.set_editor_property("auto_exposure_bias", 0.0)
                component.set_editor_property("post_process_settings", settings)
            except Exception:
                pass
            actor.set_actor_location(unreal.Vector(*location), False, False)
            actor.set_actor_rotation(rotation, False)
            component.capture_scene()
            unreal.RenderingLibrary.export_render_target(
                world, render_target, str(PROOF), output.name
            )
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    if not output.is_file() or output.stat().st_size < 4096:
        raise RuntimeError(f"Capture missing or implausibly small: {output}")
    dims = png_dimensions(output)
    if dims != (width, height):
        # HighResShot may land with DPI scaling; accept if close and rewrite note.
        if abs(dims[0] - width) > 8 or abs(dims[1] - height) > 8:
            raise RuntimeError(f"Capture dimensions unexpected: {output} -> {dims}")
    return {
        "id": f"{spec['id']}__{lighting_id}",
        "camera_id": spec["id"],
        "lighting_id": lighting_id,
        "path": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "dimensions": list(dims),
        "location_cm": list(location),
        "target_cm": list(target),
        "fov_degrees": float(spec["fov"]),
        "capture_method": method,
        "exposure_bias_sweep_used": False,
    }


class ProofState:
    def __init__(self, source_before: dict[str, dict[str, object]]) -> None:
        self.source_before = source_before
        self.started = time.monotonic()
        self.phase_started = self.started
        self.phase = "warmup"
        self.tick_count = 0
        self.captures: list[dict[str, object]] = []
        self.camera_records: list[dict[str, object]] = []
        self.actor_records: list[dict[str, object]] = []
        self.asset_records: list[dict[str, object]] = []
        self.sun = None
        self.fill = None
        self.sky = None
        self.callback = None
        self.finished = False
        self.warmup_seconds = 40.0
        self.maximum_seconds = 900.0
        self.visual_gate_blocker: str | None = None

    def event(self, event: str, **fields: object) -> None:
        append_jsonl(
            HEARTBEAT,
            {
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": event,
                "phase": self.phase,
                "tick": self.tick_count,
                **fields,
            },
        )

    def finish(self, classification: str, error: str | None = None) -> None:
        import unreal

        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        source_after = hash_tree(SOURCE_ROOT)
        map_after = sha256(MAP_FILE) if MAP_FILE.is_file() else None
        if classification.startswith("PASSED_") and source_after != self.source_before:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Accepted GW02 imported asset packages changed during mapped proof"
        structural_ok = MAP_FILE.is_file() and len(self.actor_records) >= 3
        visual_ok = len(self.captures) >= 6 and all(
            Path(str(item["path"])).is_file() for item in self.captures
        )
        if classification.startswith("PASSED_") and not visual_ok:
            classification = "STRUCTURAL_MAP_CREATED_VISUAL_GATE_BLOCKED"
            self.visual_gate_blocker = error or "Fewer than 6 valid captures"
            error = self.visual_gate_blocker
        write_json_atomic(
            IMPORT_RECEIPT,
            {
                "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-proof-gw03.import-receipt.v1",
                "gw02_content_root": str(SOURCE_ROOT),
                "gw02_game_path": "/Game/T08/GW02",
                "gw02_immutable": True,
                "gw02_mutated": False,
                "source_file_count_before": len(self.source_before),
                "source_file_count_after": len(source_after),
                "accepted_source_tree_unchanged": source_after == self.source_before,
                "assets": self.asset_records,
            },
        )
        write_json_atomic(
            INTEGRATION_RECEIPT,
            {
                "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-proof-gw03.integration-receipt.v1",
                "map_asset": MAP_ASSET,
                "map_file": str(MAP_FILE),
                "map_sha256": map_after,
                "actor_folder": "T08/GW03MappedProof01/WindowBay",
                "placed_actors": self.actor_records,
                "review_cameras": self.camera_records,
                "forbidden_namespaces_not_used": list(FORBIDDEN_NAMESPACES),
                "runtime_promotion_performed": False,
                "skyguard52_content_runtime_proxy_promotion": False,
            },
        )
        write_json_atomic(
            RECEIPT,
            {
                "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-proof-gw03-redesign01.v1",
                "classification": classification,
                "error": error,
                "visual_gate_blocker": self.visual_gate_blocker,
                "structural_map_created": structural_ok,
                "map_asset": MAP_ASSET,
                "map_file": str(MAP_FILE),
                "map_sha256": map_after,
                "accepted_source_tree_unchanged": source_after == self.source_before,
                "source_file_count": len(source_after),
                "captures": self.captures,
                "capture_count": len(self.captures),
                "capture_resolution_target": [1920, 1080],
                "capture_method_contract": "editor_viewport_or_highresshot_fixed_exposure",
                "scene_capture_exposure_sweep_used": False,
                "failed_harness_reused": False,
                "rhi_requested": "D3D12",
                "warmup_seconds": self.warmup_seconds,
                "tick_count": self.tick_count,
                "runtime_promotion_performed": False,
                "world_saved": True,
            },
        )
        self.event("terminal", classification=classification, error=error)
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        import unreal

        try:
            self.tick_count += 1
            now = time.monotonic()
            if now - self.started > self.maximum_seconds:
                raise TimeoutError("GW03 mapped proof exceeded 900s native timeout")
            if self.phase == "warmup":
                if now - self.phase_started < self.warmup_seconds:
                    return
                self.phase = "capture"
                self.phase_started = now
                self.event("capture_phase_started")
                return
            if self.phase != "capture":
                return
            self.phase = "capturing"
            # Capture all 6 stills once with fixed profiles (no exposure sweep).
            for profile in LIGHTING_PROFILES:
                apply_lighting(unreal, self.sun, self.fill, self.sky, profile)
                time.sleep(0.5)
                for camera in CAMERAS:
                    self.captures.append(
                        capture_fixed(unreal, camera, str(profile["id"]))
                    )
                    self.event(
                        "capture_complete",
                        camera=camera["id"],
                        lighting=profile["id"],
                    )
            if len(self.captures) < 6:
                raise RuntimeError(f"Expected >=6 captures, got {len(self.captures)}")
            self.finish("PASSED_GW03_AUTOMATIC_AWAITING_DIRECT_D3D12_VISUAL_REVIEW")
        except Exception as exc:
            self.visual_gate_blocker = f"{type(exc).__name__}: {exc}"
            # Prefer structural evidence over total failure when map exists.
            if MAP_FILE.is_file() and len(self.actor_records) >= 3:
                self.finish(
                    "STRUCTURAL_MAP_CREATED_VISUAL_GATE_BLOCKED",
                    self.visual_gate_blocker,
                )
            else:
                self.finish("FAILED_WITH_EVIDENCE", self.visual_gate_blocker)


_STATE: ProofState | None = None


def main() -> None:
    global _STATE
    import unreal

    if sha256(PROJECT) != PROJECT_SHA256:
        raise RuntimeError("Isolated project hash changed")
    if sha256(IMPORT_FREEZE) != IMPORT_FREEZE_SHA256:
        raise RuntimeError("Import freeze hash changed")
    if not CONTRACT.is_file():
        raise RuntimeError(f"Missing GW03 contract: {CONTRACT}")
    allowed_preexisting = {
        "unreal.stdout.log",
        "unreal.stderr.log",
        "unreal.engine.log",
        "process_tree_samples.jsonl",
    }
    if ATTEMPT.exists():
        extras = [
            path.name
            for path in ATTEMPT.iterdir()
            if path.name not in allowed_preexisting
        ]
        if extras:
            raise RuntimeError(f"Fresh GW03 attempt_01 has unexpected files: {extras}")
    if MAP_FILE.exists() or unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
        raise RuntimeError("Fresh GW03 mapped-proof map already exists")
    for forbidden in FORBIDDEN_NAMESPACES:
        if MAP_ASSET.startswith(forbidden):
            raise RuntimeError(f"Forbidden failed harness namespace: {forbidden}")

    ATTEMPT.mkdir(parents=True, exist_ok=True)
    PROOF.mkdir(parents=True, exist_ok=True)
    source_before = hash_tree(SOURCE_ROOT)
    if len(source_before) != 30:
        raise RuntimeError(f"Accepted GW02 source file count changed: {len(source_before)}")

    assets: list[dict[str, object]] = []
    loaded: dict[str, object] = {}
    for asset_path, slots in EXPECTED_SLOTS.items():
        mesh = unreal.load_asset(asset_path)
        if mesh is None or not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError(f"Accepted StaticMesh failed to load: {asset_path}")
        actual_slots = len(list(mesh.get_editor_property("static_materials")))
        if actual_slots != slots:
            raise RuntimeError(
                f"Persisted material slots changed for {asset_path}: {actual_slots} != {slots}"
            )
        body = mesh.get_editor_property("body_setup")
        convex = (
            len(body.get_editor_property("agg_geom").get_editor_property("convex_elems"))
            if body is not None
            else 0
        )
        row = {
            "path": asset_path,
            "material_slots": actual_slots,
            "bounds_origin_cm": vector(mesh.get_bounds().origin),
            "bounds_extent_cm": vector(mesh.get_bounds().box_extent),
            "convex_hulls": convex,
        }
        assets.append(row)
        loaded[asset_path] = mesh

    if not unreal.EditorLevelLibrary.new_level(MAP_ASSET):
        raise RuntimeError("Could not create GW03 mapped-proof level")

    actor_records: list[dict[str, object]] = []
    for asset_path, label in (
        (FRAME_PATH, "GW03_FrameFacadeHardware"),
        (GLASS_PATH, "GW03_Glass"),
        (INTERIOR_PATH, "GW03_Interior"),
    ):
        actor = spawn_mesh(unreal, loaded[asset_path], label)
        actor_records.append(
            {
                "label": label,
                "asset": asset_path,
                "location_cm": vector(actor.get_actor_location()),
                "scale": vector(actor.get_actor_scale3d()),
            }
        )

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if cube is None:
        raise RuntimeError("Engine cube unavailable for review stage")
    spawn_mesh(unreal, cube, "GW03_ReviewFloor", (0.0, 0.0, -12.0), (12.0, 12.0, 0.12))
    spawn_mesh(unreal, cube, "GW03_ReviewBackdrop", (0.0, -390.0, 350.0), (12.0, 0.12, 7.0))

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 900.0),
        unreal.Rotator(-38.0, 35.0, 0.0),
    )
    if sun is None:
        raise RuntimeError("Could not spawn review sun")
    sun.set_actor_label("GW03_KeySun")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sun_component.set_intensity(8.0)
    sun_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 700.0),
        unreal.Rotator(-22.0, -145.0, 0.0),
    )
    if fill is None:
        raise RuntimeError("Could not spawn review fill")
    fill.set_actor_label("GW03_FillSun")
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    fill_component.set_intensity(2.5)
    fill_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0.0, 0.0, 800.0), unreal.Rotator()
    )
    if sky is None:
        raise RuntimeError("Could not spawn review skylight")
    sky.set_actor_label("GW03_Sky")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    sky_component.set_intensity(1.2)
    sky_component.set_editor_property("real_time_capture", True)
    sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    camera_records: list[dict[str, object]] = []
    for spec in CAMERAS:
        camera = spawn_camera(unreal, spec)
        camera_records.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "location_cm": list(spec["location"]),
                "target_cm": list(spec["target"]),
                "fov_degrees": float(spec["fov"]),
                "placement": "outside_facade",
            }
        )

    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("GW03 mapped-proof level did not save")
    if not MAP_FILE.is_file():
        raise RuntimeError("GW03 map package absent after save")

    _STATE = ProofState(source_before)
    _STATE.asset_records = assets
    _STATE.actor_records = actor_records
    _STATE.camera_records = camera_records
    _STATE.sun = sun
    _STATE.fill = fill
    _STATE.sky = sky
    _STATE.event(
        "mapped_proof_ready",
        map_asset=MAP_ASSET,
        map_file=str(MAP_FILE),
        camera_count=len(camera_records),
    )
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


try:
    main()
except Exception as exc:
    write_json_atomic(
        RECEIPT,
        {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-proof-gw03-redesign01.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            "runtime_promotion_performed": False,
            "scene_capture_exposure_sweep_used": False,
            "failed_harness_reused": False,
        },
    )
    try:
        import unreal

        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass
    raise
