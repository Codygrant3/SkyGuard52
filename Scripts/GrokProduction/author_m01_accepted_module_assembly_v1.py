"""M01 accepted-module assembly: Phase A Candidates + Phase B fresh map.

NullRHI structural author for Skyguard52.uproject.
- Does not mutate Lvl_M01_CoastalIntercept_Playable_v1
- Does not mutate isolated GW02 on SG52T08_ENV01
- Does not promote Candidates into Hero / runtime
- No Blender
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ROOT / "Skyguard52.uproject"
CONTRACT = ROOT / r"Docs\Toolchain\M01_ACCEPTED_MODULE_ASSEMBLY_REVERSIBLE_CONTRACT.json"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1_RECOVERY01\attempt_01"
PRIOR_FAILED_ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1\attempt_01"
RECEIPT = ATTEMPT / "assembly_receipt.json"
PHASE_A_RECEIPT = ATTEMPT / "phase_a_receipt.json"
PHASE_B_RECEIPT = ATTEMPT / "phase_b_receipt.json"
ARTIFACT_INVENTORY = ATTEMPT / "artifact_inventory.json"
TERMINAL_RECEIPT = ATTEMPT / "terminal_receipt.json"

PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_GAME = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"

MAP_ASSET = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
MAP_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
ACTOR_FOLDER = "M01/AcceptedModules"

GW02_SOURCE = ISOLATED / r"Content\T08\GW02"
GW02_MOUNT = ROOT / r"Content\T08\GW02"
GW02_GAME = "/Game/T08/GW02"
WINDOW_CANDIDATES_GAME = "/Game/Skyguard/Candidates/M01/WindowBayR06"
WINDOW_CANDIDATES_DISK = ROOT / r"Content\Skyguard\Candidates\M01\WindowBayR06"

CORRIDOR_SOURCE = (
    ISOLATED / r"Content\M01\CoastalCorridorC06R01\M01_CoastalCorridor_C06R01_UNREAL_READY"
)
CORRIDOR_MOUNT = (
    ROOT / r"Content\M01\CoastalCorridorC06R01\M01_CoastalCorridor_C06R01_UNREAL_READY"
)
CORRIDOR_GAME = "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY"
CORRIDOR_CANDIDATES_GAME = "/Game/Skyguard/Candidates/M01/CoastalCorridorC06R01"
CORRIDOR_CANDIDATES_DISK = ROOT / r"Content\Skyguard\Candidates\M01\CoastalCorridorC06R01"

WINDOW_MESHES = (
    "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "SM_M01_PrewarWindowBay_A01_Glass",
    "SM_M01_PrewarWindowBay_A01_Interior",
)
CORRIDOR_MESHES = (
    "SM_M01_CoastalCorridor_C06R01_TERRAIN",
    "SM_M01_CoastalCorridor_C06R01_HARDSCAPE",
    "SM_M01_CoastalCorridor_C06R01_DETAILS",
    "SM_M01_CoastalCorridor_C06R01_CONTACT",
)

FACADE_ROW_COUNT = 4
BAY_SPACING_CM = 420.0
COASTAL_OFFSET = (0.0, 2400.0, 0.0)
FACADE_YAW = 180.0


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
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def hash_tree(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    if not root.is_dir():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
    return result


def ensure_junction(mount: Path, source: Path) -> dict[str, object]:
    """Create a reversible Windows directory junction for soft-reference."""
    info: dict[str, object] = {
        "mount": str(mount),
        "source": str(source),
        "created": False,
        "already_present": False,
        "mode": None,
    }
    require(source.is_dir(), f"Soft-ref source missing: {source}")
    if mount.exists():
        info["already_present"] = True
        info["mode"] = "existing"
        return info
    mount.parent.mkdir(parents=True, exist_ok=True)
    # Directory junction does not require elevation on Windows.
    completed = os.system(f'cmd /c mklink /J "{mount}" "{source}"')
    require(completed == 0 and mount.exists(), f"Failed to create junction {mount} -> {source}")
    info["created"] = True
    info["mode"] = "junction"
    return info


def ensure_candidate_dirs() -> None:
    for path in (
        WINDOW_CANDIDATES_DISK / "StaticMeshes",
        WINDOW_CANDIDATES_DISK / "Materials",
        WINDOW_CANDIDATES_DISK / "Textures",
        CORRIDOR_CANDIDATES_DISK / "StaticMeshes",
        CORRIDOR_CANDIDATES_DISK / "Materials",
        CORRIDOR_CANDIDATES_DISK / "Textures",
        MAP_DISK.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)


def write_binding(path: Path, payload: dict[str, object]) -> None:
    write_json_atomic(path, payload)


def validate_playable_immutable() -> dict[str, object]:
    require(PLAYABLE_DISK.is_file(), f"Playable map missing: {PLAYABLE_DISK}")
    observed = record(PLAYABLE_DISK)
    require(int(observed["bytes"]) == PLAYABLE_BYTES, "Playable map byte count changed")
    require(str(observed["sha256"]) == PLAYABLE_SHA256, "Playable map hash changed")
    return observed


def mesh_source_path(game_root: str, name: str) -> str:
    return f"{game_root}/StaticMeshes/{name}.{name}"


def candidate_mesh_path(candidates_root: str, name: str) -> str:
    return f"{candidates_root}/StaticMeshes/{name}"


def load_static_mesh(unreal: object, object_path: str) -> object | None:
    asset = unreal.EditorAssetLibrary.load_asset(object_path)
    if asset is None:
        # Retry package path without duplicate name suffix.
        package = object_path.split(".", 1)[0]
        asset = unreal.EditorAssetLibrary.load_asset(package)
    if asset is None:
        return None
    if not isinstance(asset, unreal.StaticMesh):
        return None
    return asset


def duplicate_mesh(
    unreal: object, source_object_path: str, dest_package_path: str
) -> dict[str, object]:
    # UE 5.8 EditorAssetLibrary.duplicate_asset(source_path, destination_path)
    source_package = source_object_path.split(".", 1)[0]
    dest_dir = dest_package_path.rsplit("/", 1)[0]
    unreal.EditorAssetLibrary.make_directory(dest_dir)
    if unreal.EditorAssetLibrary.does_asset_exist(dest_package_path):
        asset = unreal.EditorAssetLibrary.load_asset(dest_package_path)
        require(asset is not None, f"Existing candidate failed to load: {dest_package_path}")
        return {
            "source": source_object_path,
            "destination": dest_package_path,
            "action": "already_present",
            "class": asset.get_class().get_name(),
        }
    duplicated = unreal.EditorAssetLibrary.duplicate_asset(
        source_package, dest_package_path
    )
    require(
        duplicated is not None,
        f"duplicate_asset failed: {source_package} -> {dest_package_path}",
    )
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(duplicated, only_if_is_dirty=False)
    except TypeError:
        unreal.EditorAssetLibrary.save_loaded_asset(duplicated)
    return {
        "source": source_object_path,
        "destination": dest_package_path,
        "action": "duplicated",
        "class": duplicated.get_class().get_name(),
        "path_name": duplicated.get_path_name(),
    }


def phase_a(unreal: object) -> dict[str, object]:
    ensure_candidate_dirs()
    gw02_before = hash_tree(GW02_SOURCE)
    corridor_before = hash_tree(CORRIDOR_SOURCE / "StaticMeshes")
    mounts = {
        "gw02": ensure_junction(GW02_MOUNT, GW02_SOURCE),
        "corridor": ensure_junction(CORRIDOR_MOUNT, CORRIDOR_SOURCE),
    }
    write_binding(
        WINDOW_CANDIDATES_DISK / "SOURCE_GW02_BINDING.json",
        {
            "schema": "skyguard.m01-windowbayr06.gw02-softref-binding.v1",
            "gw02_source": str(GW02_SOURCE),
            "gw02_game_path": GW02_GAME,
            "mount": mounts["gw02"],
            "runtime_promotion": False,
            "immutable_source": True,
            "source_inventory_count": len(gw02_before),
        },
    )
    write_binding(
        CORRIDOR_CANDIDATES_DISK / "SOURCE_CORRIDOR_BINDING.json",
        {
            "schema": "skyguard.m01-corridor-c06r01.softref-binding.v1",
            "corridor_source": str(CORRIDOR_SOURCE),
            "corridor_game_path": CORRIDOR_GAME,
            "mount": mounts["corridor"],
            "asset_id": "m01-coastal-corridor-correction06-recovery01-unrealready01",
            "runtime_promotion": False,
            "immutable_source": True,
            "source_staticmesh_inventory_count": len(corridor_before),
        },
    )

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous(
        [GW02_GAME, CORRIDOR_GAME, WINDOW_CANDIDATES_GAME, CORRIDOR_CANDIDATES_GAME],
        True,
        False,
    )

    window_rows: list[dict[str, object]] = []
    missing_windows: list[str] = []
    for name in WINDOW_MESHES:
        source_path = mesh_source_path(GW02_GAME, name)
        mesh = load_static_mesh(unreal, source_path)
        if mesh is None:
            missing_windows.append(source_path)
            continue
        dest = candidate_mesh_path(WINDOW_CANDIDATES_GAME, name)
        window_rows.append(duplicate_mesh(unreal, mesh.get_path_name(), dest))

    corridor_rows: list[dict[str, object]] = []
    missing_corridor: list[str] = []
    for name in CORRIDOR_MESHES:
        source_path = mesh_source_path(CORRIDOR_GAME, name)
        mesh = load_static_mesh(unreal, source_path)
        if mesh is None:
            missing_corridor.append(source_path)
            continue
        dest = candidate_mesh_path(CORRIDOR_CANDIDATES_GAME, name)
        corridor_rows.append(duplicate_mesh(unreal, mesh.get_path_name(), dest))

    try:
        unreal.EditorAssetLibrary.save_directory(
            WINDOW_CANDIDATES_GAME, only_if_is_dirty=False, recursive=True
        )
    except TypeError:
        unreal.EditorAssetLibrary.save_directory(WINDOW_CANDIDATES_GAME)
    try:
        unreal.EditorAssetLibrary.save_directory(
            CORRIDOR_CANDIDATES_GAME, only_if_is_dirty=False, recursive=True
        )
    except TypeError:
        unreal.EditorAssetLibrary.save_directory(CORRIDOR_CANDIDATES_GAME)

    gw02_after = hash_tree(GW02_SOURCE)
    require(gw02_before == gw02_after, "Accepted GW02 source tree mutated during Phase A")

    result = {
        "schema": "skyguard.m01-accepted-module-assembly.phase-a.v1",
        "mounts": mounts,
        "window_duplicates": window_rows,
        "corridor_duplicates": corridor_rows,
        "missing_window_sources": missing_windows,
        "missing_corridor_sources": missing_corridor,
        "candidates": {
            "window": WINDOW_CANDIDATES_GAME,
            "corridor": CORRIDOR_CANDIDATES_GAME,
        },
        "runtime_promotion": False,
        "gw02_immutable_preserved": True,
    }
    if missing_windows:
        result["classification"] = "PHASE_A_BLOCKED_MISSING_GW02_MESHES"
        result["blocker"] = (
            "GW02 StaticMeshes could not be loaded under Skyguard52 even after soft-ref mount. "
            "Candidates folders and bindings were created; migrate via Interchange into "
            f"{WINDOW_CANDIDATES_GAME} before Phase B facade spawn."
        )
    elif missing_corridor:
        result["classification"] = "PHASE_A_PARTIAL_WINDOW_OK_CORRIDOR_SOFTREF_GAP"
        result["blocker"] = (
            "Window Candidates duplicated; corridor StaticMeshes missing after soft-ref mount."
        )
    else:
        result["classification"] = "PHASE_A_PASSED_CANDIDATES_READY"
        result["blocker"] = None
    write_json_atomic(PHASE_A_RECEIPT, result)
    return result


def spawn_mesh_actor(
    unreal: object,
    mesh: object,
    label: str,
    location: tuple[float, float, float],
    yaw: float = 0.0,
) -> object:
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
        unreal.Rotator(0.0, yaw, 0.0),
    )
    require(actor is not None, f"Failed to spawn {label}")
    actor.set_actor_label(label)
    actor.set_folder_path(ACTOR_FOLDER)
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    return actor


def phase_b(unreal: object, phase_a_result: dict[str, object]) -> dict[str, object]:
    require(not MAP_DISK.exists(), f"Fresh assembly map already exists: {MAP_DISK}")
    require(
        not unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET),
        f"Fresh assembly map asset already exists: {MAP_ASSET}",
    )
    unreal.EditorAssetLibrary.make_directory("/Game/Skyguard/Maps/Assembly")
    require(unreal.EditorLevelLibrary.new_level(MAP_ASSET), f"Failed to create {MAP_ASSET}")

    spawned: list[dict[str, object]] = []
    blockers: list[str] = []

    # Prefer Candidates; fall back to immutable GW02 soft-ref mount paths.
    mesh_origin = "candidates"
    frame_path = candidate_mesh_path(
        WINDOW_CANDIDATES_GAME, "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"
    )
    glass_path = candidate_mesh_path(
        WINDOW_CANDIDATES_GAME, "SM_M01_PrewarWindowBay_A01_Glass"
    )
    interior_path = candidate_mesh_path(
        WINDOW_CANDIDATES_GAME, "SM_M01_PrewarWindowBay_A01_Interior"
    )
    frame = load_static_mesh(unreal, frame_path)
    glass = load_static_mesh(unreal, glass_path)
    interior = load_static_mesh(unreal, interior_path)
    if frame is None or glass is None or interior is None:
        mesh_origin = "gw02_softref"
        frame = load_static_mesh(
            unreal, mesh_source_path(GW02_GAME, "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware")
        )
        glass = load_static_mesh(
            unreal, mesh_source_path(GW02_GAME, "SM_M01_PrewarWindowBay_A01_Glass")
        )
        interior = load_static_mesh(
            unreal, mesh_source_path(GW02_GAME, "SM_M01_PrewarWindowBay_A01_Interior")
        )
    if frame is None or glass is None or interior is None:
        blockers.append(
            "Window meshes unavailable from Candidates and GW02 soft-ref; "
            "assembly map created empty under M01/AcceptedModules contract."
        )
    else:
        base_x = -1.5 * BAY_SPACING_CM
        for index in range(FACADE_ROW_COUNT):
            x = base_x + index * BAY_SPACING_CM
            y = COASTAL_OFFSET[1]
            z = COASTAL_OFFSET[2]
            for mesh, suffix in (
                (frame, "Frame"),
                (glass, "Glass"),
                (interior, "Interior"),
            ):
                label = f"M01_AcceptedWindowBay_{index:02d}_{suffix}"
                actor = spawn_mesh_actor(
                    unreal, mesh, label, (x, y, z), yaw=FACADE_YAW
                )
                spawned.append(
                    {
                        "label": label,
                        "mesh": mesh.get_path_name(),
                        "mesh_origin": mesh_origin,
                        "location_cm": [x, y, z],
                        "yaw_degrees": FACADE_YAW,
                        "folder": ACTOR_FOLDER,
                    }
                )
                _ = actor

    terrain_origin = "candidates"
    terrain_path = candidate_mesh_path(
        CORRIDOR_CANDIDATES_GAME, "SM_M01_CoastalCorridor_C06R01_TERRAIN"
    )
    terrain = load_static_mesh(unreal, terrain_path)
    if terrain is None:
        terrain_origin = "corridor_softref"
        terrain = load_static_mesh(
            unreal, mesh_source_path(CORRIDOR_GAME, "SM_M01_CoastalCorridor_C06R01_TERRAIN")
        )
    if terrain is None:
        blockers.append("Corridor TERRAIN unavailable; skipped grounding spawn.")
    else:
        actor = spawn_mesh_actor(
            unreal,
            terrain,
            "M01_AcceptedCorridor_TERRAIN_Grounding",
            (0.0, 0.0, 0.0),
            yaw=0.0,
        )
        spawned.append(
            {
                "label": "M01_AcceptedCorridor_TERRAIN_Grounding",
                "mesh": terrain.get_path_name(),
                "mesh_origin": terrain_origin,
                "location_cm": [0.0, 0.0, 0.0],
                "yaw_degrees": 0.0,
                "folder": ACTOR_FOLDER,
            }
        )
        _ = actor

    require(unreal.EditorLevelLibrary.save_current_level(), "Failed to save fresh assembly map")
    require(MAP_DISK.is_file(), f"Assembly map disk file missing after save: {MAP_DISK}")

    # Guard: never touch playable.
    playable_after = validate_playable_immutable()
    result = {
        "schema": "skyguard.m01-accepted-module-assembly.phase-b.v1",
        "map_asset": MAP_ASSET,
        "map_disk": str(MAP_DISK),
        "map_record": record(MAP_DISK),
        "actor_folder": ACTOR_FOLDER,
        "spawned_actors": spawned,
        "spawned_count": len(spawned),
        "facade_row_count_contracted": FACADE_ROW_COUNT,
        "coastal_facing_offset_cm": list(COASTAL_OFFSET),
        "window_mesh_origin": mesh_origin if spawned else None,
        "corridor_mesh_origin": terrain_origin if terrain is not None else None,
        "phase_a_classification": phase_a_result.get("classification"),
        "blockers": blockers,
        "playable_immutable_after": playable_after,
        "runtime_promotion": False,
        "source_playable_mutated": False,
    }
    if not spawned:
        result["classification"] = "PHASE_B_MAP_CREATED_NO_MESH_ACTORS"
    elif blockers and any("window" in b.lower() for b in blockers):
        result["classification"] = "PHASE_B_PARTIAL_CORRIDOR_ONLY"
    elif blockers:
        result["classification"] = "PHASE_B_PARTIAL_WINDOW_FACADE_OK"
    else:
        result["classification"] = "PHASE_B_PASSED_ASSEMBLY_MAP_READY_FOR_REVIEW"
    write_json_atomic(PHASE_B_RECEIPT, result)
    return result


def inventory_attempt() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    if ATTEMPT.is_dir():
        for path in sorted(ATTEMPT.rglob("*")):
            if path.is_file():
                rows.append(record(path))
    payload = {
        "schema": "skyguard.m01-accepted-module-assembly.artifact-inventory.v1",
        "attempt": str(ATTEMPT),
        "files": rows,
        "file_count": len(rows),
    }
    write_json_atomic(ARTIFACT_INVENTORY, payload)
    return payload


def run_offline_contract_test() -> int:
    require(CONTRACT.is_file(), f"Missing contract: {CONTRACT}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(
        contract["fresh_derived_map"]["game_path"] == MAP_ASSET,
        "Contract fresh map path mismatch",
    )
    require(contract["rules"]["runtime_promotion"] is False, "runtime_promotion must be false")
    require(
        contract["source_playable_map"]["mutation_allowed"] is False,
        "Playable must remain immutable",
    )
    require(PROJECT.is_file(), "Skyguard52.uproject missing")
    require(GW02_SOURCE.is_dir(), "GW02 source missing on SG52T08")
    require(CORRIDOR_SOURCE.is_dir(), "Corridor UNREAL_READY missing on SG52T08")
    validate_playable_immutable()
    ensure_candidate_dirs()
    require(PRIOR_FAILED_ATTEMPT.is_dir(), "Prior failed attempt_01 evidence missing")
    require(not ATTEMPT.exists(), f"Fresh Recovery01 attempt already exists: {ATTEMPT}")
    require(not MAP_DISK.exists(), f"Fresh assembly map already exists: {MAP_DISK}")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_ACCEPTED_MODULE_ASSEMBLY_V1_OFFLINE_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-accepted-module-assembly.assembly-receipt.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "project": str(PROJECT),
        "contract": str(CONTRACT),
        "attempt": str(ATTEMPT),
        "runtime_promotion": False,
        "blender_used": False,
        "source_playable_mutated": False,
        "phase_a": None,
        "phase_b": None,
        "playable_before": None,
        "playable_after": None,
        "error": None,
        "traceback": None,
        "blocker": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=True)
        result["playable_before"] = validate_playable_immutable()
        require(CONTRACT.is_file(), "Assembly contract missing")
        require(not MAP_DISK.exists(), "Fresh assembly map namespace already exists")

        phase_a_result = phase_a(unreal)
        result["phase_a"] = phase_a_result

        # Phase B always creates the fresh map package even if Phase A is partial,
        # so structural evidence exists for review. Facade spawn requires Candidates.
        phase_b_result = phase_b(unreal, phase_a_result)
        result["phase_b"] = phase_b_result
        result["playable_after"] = validate_playable_immutable()
        require(
            result["playable_before"]["sha256"] == result["playable_after"]["sha256"],
            "Playable map hash changed during assembly",
        )

        inventory_attempt()
        phase_a_ok = str(phase_a_result.get("classification", "")).startswith("PHASE_A_PASSED")
        phase_b_ok = str(phase_b_result.get("classification", "")).startswith("PHASE_B_PASSED")
        if phase_a_ok and phase_b_ok:
            result["classification"] = (
                "PASSED_M01_ACCEPTED_MODULE_ASSEMBLY_STRUCTURAL_READY_FOR_REVIEW"
            )
        elif phase_b_result.get("spawned_count", 0):
            result["classification"] = (
                "PASSED_PARTIAL_M01_ACCEPTED_MODULE_ASSEMBLY_STRUCTURAL_WITH_BLOCKERS"
            )
            result["blocker"] = phase_a_result.get("blocker") or "; ".join(
                phase_b_result.get("blockers") or []
            )
        else:
            result["classification"] = "FAILED_WITH_EVIDENCE_ASSEMBLY_MAP_OR_CANDIDATES_INCOMPLETE"
            result["blocker"] = phase_a_result.get("blocker") or "; ".join(
                phase_b_result.get("blockers") or []
            ) or "No mesh actors spawned"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        result["blocker"] = result["error"]
        try:
            result["playable_after"] = record(PLAYABLE_DISK) if PLAYABLE_DISK.is_file() else None
        except Exception:
            pass
    finally:
        write_json_atomic(RECEIPT, result)
        write_json_atomic(
            TERMINAL_RECEIPT,
            {
                "schema": "skyguard.m01-accepted-module-assembly.terminal-receipt.v1",
                "classification": result["classification"],
                "runtime_promotion": False,
                "map_asset": MAP_ASSET,
                "candidates_window": WINDOW_CANDIDATES_GAME,
                "candidates_corridor": CORRIDOR_CANDIDATES_GAME,
                "receipt": str(RECEIPT),
                "blocker": result.get("blocker"),
            },
        )

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result.get("error") or result.get("blocker") or "Assembly failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
