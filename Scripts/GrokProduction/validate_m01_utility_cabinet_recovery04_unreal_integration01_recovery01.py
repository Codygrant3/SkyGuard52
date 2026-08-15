from __future__ import annotations

import hashlib
import json
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"

FAILED_FREEZE = ROOT / r"Docs\AAA_Review\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_ATTEMPT01_TERMINAL_FREEZE.json"
FAILED_FREEZE_BYTES = 1_391
FAILED_FREEZE_SHA256 = "df4e321e649edcaaec34bb8dccb49b13a3517a108ab322a8845513f8e2de932f"
ADJUDICATION = ROOT / r"Docs\AAA_Review\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_ADJUDICATION.json"
ADJUDICATION_BYTES = 986
ADJUDICATION_SHA256 = "11dc448aabb2d05dcc57ad60be775476c3756bdeb19e5df880c6bf085220a379"
FAILED_RECEIPT = ROOT / r"Saved\BuildAttempts\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01\attempt_01\integration_receipt.json"
FAILED_RECEIPT_BYTES = 9_363
FAILED_RECEIPT_SHA256 = "d850d8271ac9ab0744f5e042d6e4ca09ef44536368224b2213c55969ad3b7b71"
FAILED_TERMINAL = ROOT / r"Saved\Reports\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json"
FAILED_TERMINAL_BYTES = 6_583
FAILED_TERMINAL_SHA256 = "2a0170d0d9046c2f398528774b3ca6e17d6b2355f084c55327fc23aa8553d4d2"

INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01.umap"
INPUT_BYTES = 765_110
INPUT_SHA256 = "1a1636e225d8192309e62b5da4c4df7e7b7adffbcc2a3fc65c8cd8372c6cdc3c"

MESH_ASSET = "/Game/M01/PromenadeUtilityCabinetRecovery04/StaticMeshes/SM_M01_Promenade_UtilityCabinet_A"
MATERIAL_ASSETS = [
    "/Game/M01/PromenadeUtilityCabinetRecovery04/Materials/M_M01_UtilCab_Concrete",
    "/Game/M01/PromenadeUtilityCabinetRecovery04/Materials/M_M01_UtilCab_Hardware",
    "/Game/M01/PromenadeUtilityCabinetRecovery04/Materials/M_M01_UtilCab_PaintDark",
    "/Game/M01/PromenadeUtilityCabinetRecovery04/Materials/M_M01_UtilCab_PaintSteel",
    "/Game/M01/PromenadeUtilityCabinetRecovery04/Materials/M_M01_UtilCab_RubberGasket",
]
ASSET_FILES = [
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\Materials\M_M01_UtilCab_Concrete.uasset", 49_297, "8dfa06adb24342ab453396427aa7f5999f01919f449132a9b3e8b7982a7663f1"),
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\Materials\M_M01_UtilCab_Hardware.uasset", 50_413, "c83ef20ef818b1bb3a17f213dcc072f34c942c5a39f896781b1efc5e324ae227"),
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\Materials\M_M01_UtilCab_PaintDark.uasset", 49_337, "628879edac77ff2eb3a6f6058f3dcc947bff08f2d134b5e7be9fa14b29a6fccd"),
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\Materials\M_M01_UtilCab_PaintSteel.uasset", 49_348, "916a3011bec411a01c8835d7d7231b75fb85492c69271af513440e37584baa54"),
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\Materials\M_M01_UtilCab_RubberGasket.uasset", 49_802, "6e71ff53a23c8aa496e7f811e7513dfa10b55d858e872dfe028c8bb592c44195"),
    (ISOLATED / r"Content\M01\PromenadeUtilityCabinetRecovery04\StaticMeshes\SM_M01_Promenade_UtilityCabinet_A.uasset", 217_943, "b8d2b2bf4311ed139cb692295a91dfe67f15d0e4124d7d844b9560e2f84f09b1"),
]

ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01\attempt_01"
RECEIPT = ATTEMPT / "validation_receipt.json"
EXPECTED_ACTOR_COUNT = 126
EXPECTED_LABELS = [f"M01_Promenade_UtilityCabinet_{index:02d}" for index in range(1, 6)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_authority(path: Path, size: int, digest: str) -> dict[str, object]:
    require(path.is_file(), f"Missing authority: {path}")
    actual = record(path)
    require(actual["bytes"] == size and actual["sha256"] == digest, f"Authority mismatch: {actual}")
    return actual


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite evidence: {path}")
    temporary.replace(path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def offline_contract_test() -> int:
    source = Path(__file__).read_text(encoding="utf-8")
    required = [
        "new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
        "EXPECTED_ACTOR_COUNT = 126",
        "len(cabinet_actors) == 5",
        "find_socket(\"M01_UtilityCabinet_Origin\")",
        "save_current_level()",
    ]
    forbidden = ["AssetImportTask", "Interchange", "import_asset_tasks", "replace_existing"]
    runtime_source = source[source.index("def run_unreal") :]
    require(all(token in source for token in required), "Recovery01 author contract is incomplete")
    require(not any(token in runtime_source for token in forbidden), "Recovery01 author contains an import path")
    for path, size, digest in [
        (PROJECT, PROJECT_BYTES, PROJECT_SHA256),
        (FAILED_FREEZE, FAILED_FREEZE_BYTES, FAILED_FREEZE_SHA256),
        (ADJUDICATION, ADJUDICATION_BYTES, ADJUDICATION_SHA256),
        (FAILED_RECEIPT, FAILED_RECEIPT_BYTES, FAILED_RECEIPT_SHA256),
        (FAILED_TERMINAL, FAILED_TERMINAL_BYTES, FAILED_TERMINAL_SHA256),
        (INPUT_FILE, INPUT_BYTES, INPUT_SHA256),
        *ASSET_FILES,
    ]:
        require_authority(path, size, digest)
    require(not OUTPUT_FILE.exists(), "Fresh Recovery01 map already exists")
    print("PASS_M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-utility-cabinet-recovery04.unreal-integration01-recovery01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "error": None,
        "traceback": None,
        "authorities": [],
        "asset_validation": {},
        "cabinet_actors": [],
        "accepted_inputs_mutated": None,
    }
    authorities = [
        (PROJECT, PROJECT_BYTES, PROJECT_SHA256),
        (FAILED_FREEZE, FAILED_FREEZE_BYTES, FAILED_FREEZE_SHA256),
        (ADJUDICATION, ADJUDICATION_BYTES, ADJUDICATION_SHA256),
        (FAILED_RECEIPT, FAILED_RECEIPT_BYTES, FAILED_RECEIPT_SHA256),
        (FAILED_TERMINAL, FAILED_TERMINAL_BYTES, FAILED_TERMINAL_SHA256),
        (INPUT_FILE, INPUT_BYTES, INPUT_SHA256),
        *ASSET_FILES,
    ]
    before = {str(path): record(path) for path, _, _ in authorities}
    try:
        result["authorities"] = [require_authority(path, size, digest) for path, size, digest in authorities]
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Recovery01 output map exists")

        mesh = unreal.EditorAssetLibrary.load_asset(MESH_ASSET)
        require(mesh is not None and isinstance(mesh, unreal.StaticMesh), "Staged utility-cabinet StaticMesh failed to load")
        bounds = mesh.get_bounds()
        extent = vector(bounds.box_extent)
        require(47.0 <= extent[0] <= 52.0 and 24.0 <= extent[1] <= 28.0 and 70.0 <= extent[2] <= 75.0, f"Utility-cabinet bounds changed: {extent}")
        materials = list(mesh.get_editor_property("static_materials"))
        require(len(materials) == 5, f"Utility-cabinet material-slot count changed: {len(materials)}")
        require(mesh.find_socket("M01_UtilityCabinet_Origin") is not None, "Canonical utility-cabinet origin socket is missing")
        body_setup = mesh.get_editor_property("body_setup")
        require(body_setup is not None, "Utility-cabinet BodySetup is missing")
        require(body_setup.get_editor_property("collision_trace_flag") == unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE, "Utility-cabinet collision contract changed")
        loaded_materials = []
        for asset_path in MATERIAL_ASSETS:
            material = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(material is not None and material.get_class().get_name() in {"Material", "MaterialInstanceConstant"}, f"Material failed to load: {asset_path}")
            loaded_materials.append({"path": material.get_path_name(), "class": material.get_class().get_name()})
        result["asset_validation"] = {
            "mesh": mesh.get_path_name(),
            "bounds_origin_cm": vector(bounds.origin),
            "bounds_extent_cm": extent,
            "material_slot_count": len(materials),
            "socket": "M01_UtilityCabinet_Origin",
            "collision": "CTF_USE_COMPLEX_AS_SIMPLE",
            "materials": loaded_materials,
        }

        failed_receipt = json.loads(FAILED_RECEIPT.read_text(encoding="utf-8"))
        expected_surfaces = {row["label"]: float(row["surface_target_z_cm"]) for row in failed_receipt["placements"]}
        require(sorted(expected_surfaces) == EXPECTED_LABELS, "Frozen placement labels changed")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to duplicate staged cabinet map into Recovery01")
        actors = list(actors_api.get_all_level_actors())
        require(len(actors) == EXPECTED_ACTOR_COUNT, f"Recovery01 actor count changed: {len(actors)}")
        cabinet_actors = sorted(
            [actor for actor in actors if actor.get_actor_label().startswith("M01_Promenade_UtilityCabinet_")],
            key=lambda actor: actor.get_actor_label(),
        )
        require(len(cabinet_actors) == 5, f"Utility-cabinet actor count changed: {len(cabinet_actors)}")
        require([actor.get_actor_label() for actor in cabinet_actors] == EXPECTED_LABELS, "Utility-cabinet actor labels changed")
        for actor in cabinet_actors:
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
            actor_mesh = component.get_editor_property("static_mesh")
            require(actor_mesh is not None and actor_mesh.get_path_name() == mesh.get_path_name(), f"Wrong mesh binding: {actor.get_actor_label()}")
            origin, actor_extent = actor.get_actor_bounds(False)
            bottom = float(origin.z - actor_extent.z)
            target = expected_surfaces[actor.get_actor_label()]
            require(abs(bottom - target) <= 1.0, f"Grounding changed for {actor.get_actor_label()}: {bottom} vs {target}")
            result["cabinet_actors"].append({
                "label": actor.get_actor_label(),
                "location_cm": vector(actor.get_actor_location()),
                "scale": vector(actor.get_actor_scale3d()),
                "bounds_extent_cm": vector(actor_extent),
                "bottom_cm": bottom,
                "surface_target_z_cm": target,
            })

        require(levels.save_current_level(), "Failed to save fresh Recovery01 map")
        require(OUTPUT_FILE.is_file(), "Fresh Recovery01 map file is missing")
        after = {str(path): record(path) for path, _, _ in authorities}
        require(before == after, "A frozen staged input changed during Recovery01")
        result["accepted_inputs_mutated"] = False
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    raise RuntimeError(result["error"] or "Utility-cabinet Recovery01 validation failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

run_unreal()
