"""Apply one bounded transform correction to the quarantined M01 assembly."""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
TARGET_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V1_INTEGRATION_GATE01_RECOVERY01"
    / "attempt_01"
)
RECEIPT = ATTEMPT / "correction_receipt.json"
WINDOW_Y = -3300.0
WINDOW_Z = 480.0
WATER_LOCATION = (25000.0, 1530.0, -20.0)
WATER_SCALE = (600.0, 100.0, 1.0)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def playable_record() -> dict[str, object]:
    require(PLAYABLE_DISK.is_file(), f"Playable map missing: {PLAYABLE_DISK}")
    result = record(PLAYABLE_DISK)
    require(result["bytes"] == PLAYABLE_BYTES, "Playable map byte count changed")
    require(result["sha256"] == PLAYABLE_SHA256, "Playable map SHA-256 changed")
    return result


def vector_row(value: unreal.Vector) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def main() -> None:
    result: dict[str, object] = {
        "schema": "skyguard.m01-assembly.integration-gate01-recovery01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "bounded_correction": "align_window_row_and_water_to_corridor_bounds",
        "source_visual_attempt": (
            "Saved/BuildAttempts/"
            "M01_ACCEPTED_MODULE_ASSEMBLY_V1_INTEGRATION_GATE01/attempt_01"
        ),
        "runtime_promotion": False,
        "blender_used": False,
        "playable_before": None,
        "playable_after": None,
        "target_before": None,
        "target_after": None,
        "transforms": [],
        "error": None,
        "traceback": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=False)
        result["playable_before"] = playable_record()
        require(TARGET_DISK.is_file(), f"Assembly map missing: {TARGET_DISK}")
        result["target_before"] = record(TARGET_DISK)
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
        require(loaded is not None, f"Failed to load {TARGET_MAP}")
        actors = {
            actor.get_actor_label(): actor
            for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        }
        window_actors = [
            actor
            for label, actor in actors.items()
            if label.startswith("M01_AcceptedWindowBay_")
        ]
        require(len(window_actors) == 12, "Expected exactly twelve window actors")
        transforms: list[dict[str, object]] = []
        for actor in window_actors:
            before = actor.get_actor_location()
            after = unreal.Vector(before.x, WINDOW_Y, WINDOW_Z)
            actor.set_actor_location(after, False, False)
            transforms.append(
                {
                    "label": actor.get_actor_label(),
                    "before_location_cm": vector_row(before),
                    "after_location_cm": vector_row(after),
                }
            )
        water = actors.get("M01_Polish01_CoastalWaterPlane")
        require(water is not None, "Coastal water actor missing")
        water_before = water.get_actor_location()
        scale_before = water.get_actor_scale3d()
        water_after = unreal.Vector(*WATER_LOCATION)
        scale_after = unreal.Vector(*WATER_SCALE)
        water.set_actor_location(water_after, False, False)
        water.set_actor_scale3d(scale_after)
        transforms.append(
            {
                "label": water.get_actor_label(),
                "before_location_cm": vector_row(water_before),
                "after_location_cm": vector_row(water_after),
                "before_scale": vector_row(scale_before),
                "after_scale": vector_row(scale_after),
            }
        )
        require(
            unreal.EditorLevelLibrary.save_current_level(),
            f"Failed to save {TARGET_MAP}",
        )
        result["transforms"] = transforms
        result["playable_after"] = playable_record()
        result["target_after"] = record(TARGET_DISK)
        require(
            result["playable_before"] == result["playable_after"],
            "Playable map changed during bounded correction",
        )
        result["classification"] = (
            "PASSED_BOUNDED_ASSEMBLY_TRANSFORM_CORRECTION_AWAITING_VISUAL_RECOVERY01"
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        if PLAYABLE_DISK.is_file():
            result["playable_after"] = record(PLAYABLE_DISK)
        if TARGET_DISK.is_file():
            result["target_after"] = record(TARGET_DISK)
    finally:
        write_json_atomic(RECEIPT, result)
    if str(result["classification"]).startswith("PASSED_"):
        return
    raise RuntimeError(result["error"] or result["classification"])


main()
