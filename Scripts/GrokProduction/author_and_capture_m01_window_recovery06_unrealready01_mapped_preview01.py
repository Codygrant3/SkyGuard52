"""Build and capture one isolated UE 5.8 mapped preview of the accepted window.

The script creates a fresh review-only level, assembles the three accepted
StaticMeshes at a shared transform, lights the assembly, captures six original
2560x1440 PNGs through SceneCapture2D, and never promotes runtime content.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import time
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
IMPORT_FREEZE = ROOT / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json"
IMPORT_FREEZE_SHA256 = "362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c"
SOURCE_ROOT = ISOLATED / r"Content\T08\GW02"
MAP_ASSET = "/Game/T08/GW02Preview/Lvl_GW02_WindowPreview01"
MAP_FILE = ISOLATED / r"Content\T08\GW02Preview\Lvl_GW02_WindowPreview01.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01\attempt_01"
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "mapped_preview_receipt.json"

FRAME_PATH = "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"
GLASS_PATH = "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass.SM_M01_PrewarWindowBay_A01_Glass"
INTERIOR_PATH = "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior.SM_M01_PrewarWindowBay_A01_Interior"
EXPECTED_SLOTS = {FRAME_PATH: 5, GLASS_PATH: 1, INTERIOR_PATH: 9}
EXPECTED_SOCKETS = {
    "M01_Window_Origin": (0.0, 0.0, 0.0),
    "M01_Window_Center": (0.0, 0.0, 212.0),
    "M01_Window_Latch": (5.0, 5.2, 200.0),
}
CAMERAS = [
    {"id": "01_front_hero", "location": (0.0, 820.0, 225.0), "target": (0.0, 0.0, 210.0), "fov": 42.0},
    {"id": "02_front_left", "location": (-430.0, 690.0, 275.0), "target": (0.0, -15.0, 210.0), "fov": 45.0},
    {"id": "03_front_right", "location": (430.0, 690.0, 275.0), "target": (0.0, -15.0, 210.0), "fov": 45.0},
    {"id": "04_close_hardware", "location": (150.0, 370.0, 245.0), "target": (35.0, 0.0, 220.0), "fov": 34.0},
    {"id": "05_rear_interior", "location": (0.0, -720.0, 235.0), "target": (0.0, -55.0, 205.0), "fov": 46.0},
    {"id": "06_high_oblique", "location": (-360.0, 570.0, 520.0), "target": (0.0, -30.0, 205.0), "fov": 48.0},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def append_jsonl(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def hash_tree(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")) if root.is_dir() else []:
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return result


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Not a PNG: {path}")
        length = struct.unpack(">I", stream.read(4))[0]
        chunk = stream.read(4)
        if chunk != b"IHDR" or length < 8:
            raise RuntimeError(f"PNG IHDR missing: {path}")
        return struct.unpack(">II", stream.read(8))


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def look_at(unreal: object, location: tuple[float, float, float], target: tuple[float, float, float]) -> object:
    return unreal.KismetMathLibrary.find_look_at_rotation(unreal.Vector(*location), unreal.Vector(*target))


def spawn_mesh(unreal: object, mesh: object, label: str, location: tuple[float, float, float] = (0.0, 0.0, 0.0), scale: tuple[float, float, float] = (1.0, 1.0, 1.0)) -> object:
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator())
    if actor is None:
        raise RuntimeError(f"Could not spawn {label}")
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor


class PreviewState:
    def __init__(self, unreal: object, source_before: dict[str, dict[str, object]], asset_records: list[dict[str, object]], actor_records: list[dict[str, object]]) -> None:
        self.unreal = unreal
        self.source_before = source_before
        self.asset_records = asset_records
        self.actor_records = actor_records
        self.started = time.monotonic()
        self.warmup_seconds = 15.0
        self.capture_index = 0
        self.capture_gap_ticks = 0
        self.tick_count = 0
        self.captures: list[dict[str, object]] = []
        self.callback = None
        self.finished = False
        self.heartbeat = ATTEMPT / "lifecycle_heartbeat.jsonl"

    def record_event(self, event: str, **fields: object) -> None:
        append_jsonl(self.heartbeat, {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, "tick": self.tick_count, **fields})

    def capture(self, spec: dict[str, object]) -> None:
        unreal = self.unreal
        world = unreal.EditorLevelLibrary.get_editor_world()
        target = unreal.RenderingLibrary.create_render_target2d(world, 2560, 1440, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator())
        if actor is None:
            raise RuntimeError("Could not create transient SceneCapture2D")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", target)
            component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", float(spec["fov"]))
            location = tuple(float(value) for value in spec["location"])
            target_point = tuple(float(value) for value in spec["target"])
            actor.set_actor_location(unreal.Vector(*location), False, False)
            actor.set_actor_rotation(look_at(unreal, location, target_point), False)
            component.capture_scene()
            output = PROOF / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(world, target, str(PROOF), output.name)
            if not output.is_file() or output.stat().st_size < 4096:
                raise RuntimeError(f"Capture is missing or implausibly small: {output}")
            if png_dimensions(output) != (2560, 1440):
                raise RuntimeError(f"Capture dimensions changed: {output}")
            self.captures.append({"id": spec["id"], "path": str(output), "bytes": output.stat().st_size, "sha256": sha256(output), "location_cm": list(location), "target_cm": list(target_point), "fov_degrees": float(spec["fov"])})
            self.record_event("capture_complete", camera=spec["id"])
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def finish(self, classification: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            self.unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        source_after = hash_tree(SOURCE_ROOT)
        if classification.startswith("PASSED_") and source_after != self.source_before:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Accepted GW02 imported asset packages changed during mapped preview"
        receipt = {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01.v1",
            "classification": classification,
            "error": error,
            "map_asset": MAP_ASSET,
            "map_file": str(MAP_FILE),
            "map_file_bytes": MAP_FILE.stat().st_size if MAP_FILE.is_file() else None,
            "map_file_sha256": sha256(MAP_FILE) if MAP_FILE.is_file() else None,
            "accepted_source_tree_unchanged": source_after == self.source_before,
            "source_file_count": len(source_after),
            "asset_records": self.asset_records,
            "actor_records": self.actor_records,
            "captures": self.captures,
            "capture_count": len(self.captures),
            "resolution": [2560, 1440],
            "warmup_seconds": self.warmup_seconds,
            "tick_count": self.tick_count,
            "runtime_promotion_performed": False,
            "production_map_modified": False,
        }
        write_json_atomic(RECEIPT, receipt)
        self.record_event("terminal", classification=classification, error=error)
        self.unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            elapsed = time.monotonic() - self.started
            if elapsed > 180.0:
                raise TimeoutError("Mapped preview exceeded 180 seconds")
            if elapsed < self.warmup_seconds:
                return
            if self.capture_gap_ticks > 0:
                self.capture_gap_ticks -= 1
                return
            if self.capture_index < len(CAMERAS):
                self.capture(CAMERAS[self.capture_index])
                self.capture_index += 1
                self.capture_gap_ticks = 3
                return
            if len(self.captures) != len(CAMERAS):
                raise RuntimeError("Capture count changed")
            self.finish("PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW")
        except Exception as exc:
            self.finish("FAILED_WITH_EVIDENCE", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")


_STATE = None


def main() -> None:
    global _STATE
    import unreal

    if not IMPORT_FREEZE.is_file() or sha256(IMPORT_FREEZE) != IMPORT_FREEZE_SHA256:
        raise RuntimeError("Accepted Recovery02 import freeze changed")
    if not PROJECT.is_file() or sha256(PROJECT) != PROJECT_SHA256:
        raise RuntimeError("Isolated project descriptor changed")
    if not SOURCE_ROOT.is_dir():
        raise RuntimeError("Accepted GW02 source content is absent")
    if ATTEMPT.exists() and any(ATTEMPT.iterdir()):
        raise RuntimeError("Fresh mapped-preview attempt is not empty")
    if MAP_FILE.exists() or unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
        raise RuntimeError("Fresh mapped-preview map already exists")
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
            raise RuntimeError(f"Persisted material slots changed for {asset_path}: {actual_slots} != {slots}")
        body = mesh.get_editor_property("body_setup")
        convex = len(body.get_editor_property("agg_geom").get_editor_property("convex_elems")) if body is not None else 0
        row = {"path": asset_path, "material_slots": actual_slots, "bounds_origin_cm": vector(mesh.get_bounds().origin), "bounds_extent_cm": vector(mesh.get_bounds().box_extent), "convex_hulls": convex}
        assets.append(row)
        loaded[asset_path] = mesh

    frame = loaded[FRAME_PATH]
    for name, location in EXPECTED_SOCKETS.items():
        socket = frame.find_socket(name)
        if socket is None:
            raise RuntimeError(f"Persisted canonical socket is missing: {name}")
        actual = vector(socket.get_editor_property("relative_location"))
        if any(abs(actual[index] - location[index]) > 0.01 for index in range(3)):
            raise RuntimeError(f"Persisted socket transform changed: {name} -> {actual}")

    if not unreal.EditorLevelLibrary.new_level(MAP_ASSET):
        raise RuntimeError("Could not create isolated mapped-preview level")
    actor_records: list[dict[str, object]] = []
    for asset_path, label in ((FRAME_PATH, "GW02_FrameFacadeHardware"), (GLASS_PATH, "GW02_Glass"), (INTERIOR_PATH, "GW02_Interior")):
        actor = spawn_mesh(unreal, loaded[asset_path], label)
        actor_records.append({"label": label, "asset": asset_path, "location_cm": vector(actor.get_actor_location()), "scale": vector(actor.get_actor_scale3d())})

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if cube is None:
        raise RuntimeError("Engine cube is unavailable for review stage")
    spawn_mesh(unreal, cube, "GW02_ReviewFloor", (0.0, 0.0, -12.0), (12.0, 12.0, 0.12))
    spawn_mesh(unreal, cube, "GW02_ReviewBackdrop", (0.0, -390.0, 350.0), (12.0, 0.12, 7.0))

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 900.0), unreal.Rotator(-38.0, 35.0, 0.0))
    if sun is None:
        raise RuntimeError("Could not spawn review sun")
    sun.set_actor_label("GW02_KeySun")
    sun.directional_light_component.set_intensity(8.0)
    sun.directional_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 700.0), unreal.Rotator(-22.0, -145.0, 0.0))
    if fill is None:
        raise RuntimeError("Could not spawn review fill")
    fill.set_actor_label("GW02_FillSun")
    fill.directional_light_component.set_intensity(2.5)
    fill.directional_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, 800.0), unreal.Rotator())
    if sky is None:
        raise RuntimeError("Could not spawn review skylight")
    sky.set_actor_label("GW02_Sky")
    sky.light_component.set_intensity(1.2)
    sky.light_component.set_editor_property("real_time_capture", True)
    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    for index, (location, intensity, radius) in enumerate((((0.0, 340.0, 300.0), 18000.0, 1100.0), ((-260.0, 180.0, 310.0), 9000.0, 850.0), ((120.0, -130.0, 255.0), 4500.0, 650.0))):
        light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*location), unreal.Rotator())
        if light is None:
            raise RuntimeError(f"Could not spawn review point light {index}")
        light.set_actor_label(f"GW02_Point_{index:02d}")
        light.point_light_component.set_intensity(intensity)
        light.point_light_component.set_editor_property("attenuation_radius", radius)
        light.point_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Mapped-preview level did not save")
    if not MAP_FILE.is_file():
        raise RuntimeError("Mapped-preview map package is absent after save")

    _STATE = PreviewState(unreal, source_before, assets, actor_records)
    _STATE.record_event("mapped_preview_ready", map_asset=MAP_ASSET, map_file=str(MAP_FILE))
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


try:
    main()
except Exception as exc:
    write_json_atomic(RECEIPT, {"schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01.v1", "classification": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}", "runtime_promotion_performed": False})
    import unreal
    unreal.SystemLibrary.quit_editor()
    raise
