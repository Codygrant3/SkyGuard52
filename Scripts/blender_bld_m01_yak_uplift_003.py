"""Build the isolated BLD-M01-YAK-UPLIFT-003 comparison candidate.

This is deliberately an uplift of the richer L88 scene, not a replacement.
The immutable L88 .blend is byte-copied first and Blender opens only that
isolated copy.  Production-002 is used only as Python construction source for
the cowl, propeller and wheel-well donors.

Run only through the command documented in the Uplift 003 runbook.  The script
refuses to overwrite any prior Uplift 003 artifact.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector


BUILD_ID = "BLD-M01-YAK-UPLIFT-003"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
LEDGER_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
)
L88_BLEND_PATH = (
    ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "L88"
    / "YAK52_L88_MASTER_BLOCKOUT.blend"
)
L88_RUNTIME_CONTRACT_PATH = ROOT / "Saved" / "Reports" / "L88_RUNTIME_ASSEMBLY_CONTRACT.json"
DONOR_SOURCE_PATH = ROOT / "Scripts" / "blender_bld_m01_yak_prod_002.py"
OUTPUT_DIR = (
    ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01"
    / "Yak52_Uplift_003"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_UPLIFT_003_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_uplift_003.glb"
MANIFEST_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_YAK_UPLIFT_003_MANIFEST.json"
COMPARISON_DIR = ROOT / "Saved" / "Screenshots" / "BLD_M01_YAK_UPLIFT_003"
DONOR_COLLECTION_NAME = "BLD_M01_YAK_UPLIFT_003_DONORS"
GOVERNANCE_COLLECTION_NAME = "BLD_M01_YAK_UPLIFT_003_GOVERNANCE"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verify_record(path: Path, record: dict, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} missing: {path}")
    if path.stat().st_size != record["bytes"]:
        raise RuntimeError(f"{label} byte count drifted: {path}")
    if sha256_file(path) != record["sha256"]:
        raise RuntimeError(f"{label} hash drifted: {path}")


def load_and_verify_governance() -> tuple[dict, dict, dict]:
    contract = load_json(CONTRACT_PATH)
    ledger = load_json(LEDGER_PATH)
    runtime = load_json(L88_RUNTIME_CONTRACT_PATH)
    if contract["build_id"] != BUILD_ID or ledger["build_id"] != BUILD_ID:
        raise RuntimeError("Uplift 003 governance build id mismatch")
    if contract["status"] != "source_only_not_run":
        raise RuntimeError("Source contract must remain source_only_not_run")
    sources = contract["immutable_sources"]
    verify_record(L88_BLEND_PATH, sources["l88_blend"], "immutable L88 blend")
    verify_record(
        L88_RUNTIME_CONTRACT_PATH,
        sources["l88_runtime_contract"],
        "L88 runtime contract",
    )
    verify_record(DONOR_SOURCE_PATH, sources["donor_002_source"], "002 donor source")
    verify_record(
        ROOT / sources["visual_review"]["path"],
        sources["visual_review"],
        "002 visual review",
    )
    if len(runtime["entries"]) != ledger["source_contract"]["expected_component_count"]:
        raise RuntimeError("L88 component count drifted")
    return contract, ledger, runtime


def refuse_overwrite() -> None:
    protected_outputs = [BLEND_PATH, GLB_PATH, MANIFEST_PATH]
    existing = [str(path) for path in protected_outputs if path.exists()]
    if existing:
        raise RuntimeError(
            "Uplift 003 is immutable once emitted; refusing overwrite: " + ", ".join(existing)
        )
    if COMPARISON_DIR.exists() and any(COMPARISON_DIR.iterdir()):
        raise RuntimeError("Uplift 003 comparison directory is not empty")


def require_blender_52() -> None:
    if bpy.app.version[:2] != (5, 2):
        raise RuntimeError(
            f"{BUILD_ID} requires Blender 5.2, found "
            f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        )


def isolated_copy_and_open(contract: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(L88_BLEND_PATH, BLEND_PATH)
    if sha256_file(BLEND_PATH) != contract["immutable_sources"]["l88_blend"]["sha256"]:
        raise RuntimeError("Isolated L88 copy failed hash verification")
    bpy.ops.wm.open_mainfile(filepath=str(BLEND_PATH))
    if sha256_file(L88_BLEND_PATH) != contract["immutable_sources"]["l88_blend"]["sha256"]:
        raise RuntimeError("Immutable L88 source changed while opening isolated copy")


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def link_exclusively(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)


def aim_camera(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    collection: bpy.types.Collection,
    *,
    clip_start: float = 0.04,
    orthographic_scale: float | None = None,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.clip_start = clip_start
    if orthographic_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = orthographic_scale
    camera = bpy.data.objects.new(name, data)
    collection.objects.link(camera)
    camera.location = location
    aim_camera(camera, Vector(target))
    camera["SKG_BuildId"] = BUILD_ID
    camera["SKG_PromotionAllowed"] = False
    return camera


def create_volume(
    name: str,
    spec: dict,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = 1.0
    obj.location = spec["center_m"]
    obj.scale = spec["half_extents_m"]
    obj["SKG_BuildId"] = BUILD_ID
    obj["SKG_GovernanceRole"] = spec["role"]
    obj["SKG_HalfExtentsM"] = list(spec["half_extents_m"])
    obj["SKG_PromotionAllowed"] = False
    return obj


def stage_camera_and_clearance(contract: dict) -> list[str]:
    collection = ensure_collection(GOVERNANCE_COLLECTION_NAME)
    camera_spec = contract["first_stage_camera"]
    create_camera(
        camera_spec["name"],
        tuple(camera_spec["location_m"]),
        tuple(camera_spec["target_m"]),
        float(camera_spec["lens_mm"]),
        collection,
        clip_start=float(camera_spec["clip_start_m"]),
    )
    names = []
    for name, spec in contract["required_safety_and_clearance_volumes"].items():
        create_volume(name, spec, collection)
        names.append(name)
    return names


def resolve_ledger(ledger: dict, runtime: dict) -> list[dict]:
    entries = runtime["entries"]
    names = {entry["name"] for entry in entries}
    unknown_overrides = sorted(set(ledger["component_overrides"]) - names)
    if unknown_overrides:
        raise RuntimeError(f"Unknown ledger overrides: {unknown_overrides}")
    allowed = set(ledger["allowed_classifications"])
    resolved = []
    seen = set()
    for entry in entries:
        name = entry["name"]
        bundle = entry["bundle"]
        if name in seen:
            raise RuntimeError(f"Duplicate L88 component in runtime contract: {name}")
        seen.add(name)
        if bundle not in ledger["bundle_defaults"]:
            raise RuntimeError(f"Unclassified L88 bundle: {bundle}")
        classification = ledger["component_overrides"].get(
            name, ledger["bundle_defaults"][bundle]
        )
        if classification not in allowed:
            raise RuntimeError(f"Forbidden classification for {name}: {classification}")
        if ledger["classification_policy"][classification]["promotion_allowed"] is not False:
            raise RuntimeError(f"Silent promotion is forbidden: {name}")
        resolved.append({**entry, "classification": classification})
    if len(resolved) != ledger["source_contract"]["expected_component_count"]:
        raise RuntimeError("Resolved component ledger is incomplete")
    return resolved


def stage_component_ledger_tags(ledger: dict, runtime: dict) -> list[dict]:
    resolved = resolve_ledger(ledger, runtime)
    missing = []
    for entry in resolved:
        obj = bpy.data.objects.get(entry["name"])
        if obj is None:
            missing.append(entry["name"])
            continue
        obj["SKG_UpliftClass"] = entry["classification"]
        obj["SKG_PromotionAllowed"] = False
        obj["SKG_InheritedFrom"] = "L88"
        obj["SKG_OriginalNamePreserved"] = True
    if missing:
        raise RuntimeError(f"L88 objects missing from isolated blend: {missing}")
    return resolved


def load_donor_module():
    spec = importlib.util.spec_from_file_location(
        "skyguard_bld_m01_yak_prod_002_donor_source", DONOR_SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load governed 002 donor source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def tag_donor(obj: bpy.types.Object, source_name: str) -> None:
    obj["SKG_UpliftClass"] = "donor_from_002"
    obj["SKG_PromotionAllowed"] = False
    obj["SKG_DonorSource"] = "BLD-M01-YAK-PROD-002 Python construction"
    obj["SKG_DonorSourceName"] = source_name
    obj["SKG_BuildId"] = BUILD_ID


def add_datum(
    name: str,
    location: tuple[float, float, float],
    role: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.location = location
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = 0.18
    tag_donor(obj, role)
    obj["SKG_DatumRole"] = role
    return obj


def stage_selective_002_donors(contract: dict, ledger: dict) -> list[str]:
    donor = load_donor_module()
    collection = ensure_collection(DONOR_COLLECTION_NAME)
    mats = donor.build_materials()
    before = set(bpy.data.objects)
    donor.create_radial_cowling(collection, mats)
    donor.create_propeller(collection, mats)
    created = [obj for obj in bpy.data.objects if obj not in before]
    rename = {
        "GEO_PROD002_CowlingShell": "GEO_UPLIFT003_DONOR_CowlingShell",
        "GEO_PROD002_CowlingFrontRing": "GEO_UPLIFT003_DONOR_CowlingFrontRing",
        "GEO_PROD002_CowlingShutters": "GEO_UPLIFT003_DONOR_CowlingShutters",
        "GEO_PROD002_CowlingInletCone": "GEO_UPLIFT003_DONOR_CowlingInletCone",
        "GEO_PROD002_Spinner": "GEO_UPLIFT003_DONOR_Spinner",
        "GEO_PROD002_PropBlade_A": "GEO_UPLIFT003_DONOR_PropBlade_A",
        "GEO_PROD002_PropBlade_B": "GEO_UPLIFT003_DONOR_PropBlade_B",
    }
    for obj in created:
        source_name = obj.name
        if source_name not in rename:
            continue
        obj.name = rename[source_name]
        link_exclusively(obj, collection)
        tag_donor(obj, source_name)

    for side, suffix in ((-1.0, "L"), (1.0, "R")):
        obj = donor.base.add_cylinder(
            f"GEO_UPLIFT003_DONOR_MainWheelWell_{suffix}",
            0.33,
            0.08,
            (0.75, side * 1.05, 0.04),
            (0.0, 1.5707963267948966, 0.0),
            collection,
            [mats["MAT002_WheelWell"]],
            64,
            0.01,
        )
        tag_donor(obj, f"GEO_PROD002_MainWheelWell_{suffix}")
    nose_well = donor.base.add_cylinder(
        "GEO_UPLIFT003_DONOR_NoseWheelWell",
        0.23,
        0.07,
        (3.05, 0.0, -0.18),
        (0.0, 1.5707963267948966, 0.0),
        collection,
        [mats["MAT002_WheelWell"]],
        64,
        0.01,
    )
    tag_donor(nose_well, "GEO_PROD002_NoseWheelWell")

    add_datum(
        "DATUM_UPLIFT003_DONOR_CanopyTravel",
        (-1.25, 0.0, 1.33),
        "canopy_travel_only_l88_canopy_preserved",
        collection,
    )
    add_datum(
        "DATUM_UPLIFT003_DONOR_MainGearPivot_L",
        (0.78, -0.92, 0.15),
        "main_gear_pivot_L_only_l88_gear_preserved",
        collection,
    )
    add_datum(
        "DATUM_UPLIFT003_DONOR_MainGearPivot_R",
        (0.78, 0.92, 0.15),
        "main_gear_pivot_R_only_l88_gear_preserved",
        collection,
    )
    add_datum(
        "DATUM_UPLIFT003_DONOR_NoseGearPivot",
        (3.02, 0.0, 0.04),
        "nose_gear_pivot_only_l88_gear_preserved",
        collection,
    )

    retired_targets = set(ledger["donor_replacement_map"])
    for target_name in retired_targets:
        target = bpy.data.objects.get(target_name)
        if target is None:
            raise RuntimeError(f"Donor target missing from preserved L88 copy: {target_name}")
        target.hide_render = True
        target.hide_set(True)
        target["SKG_RetiredForComparisonOnly"] = True
        target["SKG_PromotionAllowed"] = False

    missing = [name for name in contract["required_donor_objects"] if name not in bpy.data.objects]
    if missing:
        raise RuntimeError(f"Required selective donors were not created: {missing}")
    return list(contract["required_donor_objects"])


def stage_matched_comparison_setup(contract: dict) -> dict[str, bpy.types.Object]:
    collection = ensure_collection(GOVERNANCE_COLLECTION_NAME)
    specs = {
        "beauty": ((11.5, -11.5, 6.7), (0.0, 0.0, -0.05), 58.0, None),
        "side": ((0.0, -15.0, 0.4), (0.0, 0.0, 0.0), 58.0, 10.8),
        "top": ((0.0, 0.0, 15.0), (0.0, 0.0, 0.0), 58.0, 10.8),
        "rear_cockpit": ((-1.20, -1.10, 1.10), (0.30, -0.55, 0.68), 38.0, None),
        "rear_gunner_eye": ((-0.90, -0.64, 1.08), (1.58, -0.64, 1.06), 46.0, None),
    }
    cameras = {}
    for slot in contract["matched_comparison_slots"]:
        name = f"CAM_UPLIFT003_{slot['slot']}"
        location, target, lens, ortho = specs[slot["slot"]]
        cameras[slot["slot"]] = create_camera(
            name, location, target, lens, collection, orthographic_scale=ortho
        )
    return cameras


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.045, 0.06, 0.085)
    if "LIGHT_UPLIFT003_Key" not in bpy.data.objects:
        light_data = bpy.data.lights.new("LIGHT_UPLIFT003_Key", "AREA")
        light_data.energy = 1800.0
        light_data.shape = "DISK"
        light_data.size = 7.0
        light = bpy.data.objects.new("LIGHT_UPLIFT003_Key", light_data)
        ensure_collection(GOVERNANCE_COLLECTION_NAME).objects.link(light)
        light.location = (5.5, -7.0, 8.0)
        light.rotation_euler = (0.55, 0.0, 0.72)


def save_export_and_render(
    contract: dict,
    cameras: dict[str, bpy.types.Object],
) -> list[dict]:
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    configure_render()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_animations=False,
    )
    comparisons = []
    scene = bpy.context.scene
    for slot in contract["matched_comparison_slots"]:
        candidate = ROOT / slot["candidate"]
        scene.camera = cameras[slot["slot"]]
        scene.render.filepath = str(candidate)
        bpy.ops.render.render(write_still=True)
        comparisons.append(
            {
                "slot": slot["slot"],
                "baseline": slot["baseline"],
                "candidate": {
                    "path": slot["candidate"],
                    "bytes": candidate.stat().st_size,
                    "sha256": sha256_file(candidate),
                },
            }
        )
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    return comparisons


def write_manifest(
    contract: dict,
    ledger: dict,
    resolved: list[dict],
    stages: list[str],
    comparison_records: list[dict],
    clearance_names: list[str],
    donor_names: list[str],
    started: float,
) -> None:
    object_records = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if (
            obj.name in {item["name"] for item in resolved}
            or obj.name in donor_names
            or obj.name in clearance_names
            or obj.name == contract["first_stage_camera"]["name"]
        ):
            object_records.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "uplift_class": obj.get("SKG_UpliftClass"),
                    "promotion_allowed": obj.get("SKG_PromotionAllowed"),
                    "inherited_from": obj.get("SKG_InheritedFrom"),
                    "governance_role": obj.get("SKG_GovernanceRole"),
                    "donor_source": obj.get("SKG_DonorSource"),
                }
            )
    manifest = {
        "schema": "skyguard.bld-m01-yak-uplift-003.artifact-manifest.v1",
        "build_id": BUILD_ID,
        "status": "provisional_uplift_candidate_not_accepted_not_final_not_aaa",
        "promotion_allowed": False,
        "source_only_contract_status": contract["status"],
        "stage_order": stages,
        "immutable_sources": contract["immutable_sources"],
        "outputs": {
            "blend": {
                "path": contract["outputs"]["blend"],
                "bytes": BLEND_PATH.stat().st_size,
                "sha256": sha256_file(BLEND_PATH),
            },
            "glb": {
                "path": contract["outputs"]["glb"],
                "bytes": GLB_PATH.stat().st_size,
                "sha256": sha256_file(GLB_PATH),
            },
        },
        "resolved_component_ledger": resolved,
        "object_records": object_records,
        "classification_counts": dict(
            sorted(Counter(item["classification"] for item in resolved).items())
        ),
        "clearance_volumes": clearance_names,
        "first_stage_camera": contract["first_stage_camera"]["name"],
        "donor_objects": donor_names,
        "preserved_bundles": contract["preserved_bundles"],
        "matched_comparisons": comparison_records,
        "silent_promotion_forbidden": ledger["silent_promotion_forbidden"],
        "original_l88_unchanged": (
            sha256_file(L88_BLEND_PATH)
            == contract["immutable_sources"]["l88_blend"]["sha256"]
        ),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "claims": {
            "final": False,
            "aaa": False,
            "unreal_accepted": False,
            "matched_visual_review_accepted": False,
        },
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    started = time.perf_counter()
    require_blender_52()
    contract, ledger, runtime = load_and_verify_governance()
    refuse_overwrite()
    isolated_copy_and_open(contract)
    stages = []
    clearance_names = stage_camera_and_clearance(contract)
    stages.append("camera_and_clearance")
    resolved = stage_component_ledger_tags(ledger, runtime)
    stages.append("component_ledger_tags")
    donor_names = stage_selective_002_donors(contract, ledger)
    stages.append("selective_002_donors")
    cameras = stage_matched_comparison_setup(contract)
    stages.append("matched_comparison_setup")
    comparisons = save_export_and_render(contract, cameras)
    stages.append("isolated_save_export_and_comparison")
    if stages != contract["required_stage_order"]:
        raise RuntimeError("Uplift stage order drifted")
    write_manifest(
        contract,
        ledger,
        resolved,
        stages,
        comparisons,
        clearance_names,
        donor_names,
        started,
    )
    print(f"[{BUILD_ID}] provisional comparison candidate emitted")
    print(f"[{BUILD_ID}] blend={BLEND_PATH}")
    print(f"[{BUILD_ID}] manifest={MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
