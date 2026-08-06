"""Source-only repair generator for BLD-M01-YAK-UPLIFT-003-R3.

R3 preserves the 240-entry runtime ledger while treating the eight
underscore-spelled canopy hinge/seal entries that are absent from the L88
Blender source as ``source_absent_hold`` exceptions.  Those exceptions are
never looked up as required Blender objects, synthesized, renamed, or silently
matched to the dotted source objects.

This module writes only the isolated Uplift_003_R3 namespace and refuses to
overwrite any prior R1, R2, or R3 evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import struct
import sys
import time
from collections import Counter
from pathlib import Path

import bpy


BUILD_ID = "BLD-M01-YAK-UPLIFT-003-R3"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_R3_CONTRACT.json"
)
LEDGER_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "BLD_M01_YAK_UPLIFT_003_R3_COMPONENT_LEDGER.json"
)
SOURCE_AUDIT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_R3_SOURCE_AUDIT.json"
)
R1_HELPER_PATH = ROOT / "Scripts" / "blender_bld_m01_yak_uplift_003.py"
L88_BLEND_PATH = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "L88"
    / "YAK52_L88_MASTER_BLOCKOUT.blend"
)
L88_GLB_PATH = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "L88"
    / "yak52_l88_silhouette_blockout.glb"
)
L88_RUNTIME_CONTRACT_PATH = (
    ROOT / "Saved" / "Reports" / "L88_RUNTIME_ASSEMBLY_CONTRACT.json"
)
OUTPUT_DIR = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Uplift_003_R3"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_UPLIFT_003_R3_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_uplift_003_r3.glb"
MANIFEST_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_YAK_UPLIFT_003_R3_MANIFEST.json"
COMPARISON_DIR = ROOT / "Saved" / "Screenshots" / "BLD_M01_YAK_UPLIFT_003_R3"
DONOR_COLLECTION_NAME = "BLD_M01_YAK_UPLIFT_003_R3_DONORS"
GOVERNANCE_COLLECTION_NAME = "BLD_M01_YAK_UPLIFT_003_R3_GOVERNANCE"


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


def load_r1_helpers():
    spec = importlib.util.spec_from_file_location(
        "skyguard_uplift_003_r1_helpers", R1_HELPER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load governed R1 helper source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.BUILD_ID = BUILD_ID
    return module


r1 = load_r1_helpers()


def parse_glb_mesh_node_names(path: Path) -> list[str]:
    payload = path.read_bytes()
    if payload[:4] != b"glTF":
        raise RuntimeError("L88 GLB has invalid magic")
    offset = 12
    document = None
    while offset < len(payload):
        length, chunk_type = struct.unpack_from("<II", payload, offset)
        offset += 8
        chunk = payload[offset : offset + length]
        offset += length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.rstrip(b" \t\r\n\0"))
            break
    if document is None:
        raise RuntimeError("L88 GLB has no JSON chunk")
    return sorted(
        node["name"]
        for node in document.get("nodes", [])
        if node.get("mesh") is not None and node.get("name")
    )


def resolve_ledger(overlay: dict, base: dict, runtime: dict) -> list[dict]:
    entries = runtime["entries"]
    names = [entry["name"] for entry in entries]
    if len(entries) != overlay["governed_component_count"] or len(set(names)) != len(
        names
    ):
        raise RuntimeError("R3 runtime component inventory is not exactly 240 unique names")
    exceptions = overlay["classification_overrides"]
    if set(exceptions) - set(names):
        raise RuntimeError("R3 source-absent exception references unknown runtime component")
    if set(exceptions.values()) != {"source_absent_hold"}:
        raise RuntimeError("R3 exceptions must only use source_absent_hold")
    resolved = []
    for entry in entries:
        name = entry["name"]
        bundle = entry["bundle"]
        if bundle not in base["bundle_defaults"]:
            raise RuntimeError(f"R3 unknown source bundle: {bundle}")
        classification = exceptions.get(
            name,
            base["component_overrides"].get(name, base["bundle_defaults"][bundle]),
        )
        if classification not in overlay["allowed_classifications"]:
            raise RuntimeError(f"R3 forbidden classification: {classification}")
        resolved.append({**entry, "classification": classification})
    counts = Counter(item["classification"] for item in resolved)
    if counts["source_absent_hold"] != overlay["source_absent_hold_count"]:
        raise RuntimeError("R3 source_absent_hold accounting is not exactly eight")
    if len(resolved) - counts["source_absent_hold"] != overlay["exact_object_requirement_count"]:
        raise RuntimeError("R3 exact-object accounting is not exactly 232")
    return resolved


def load_and_verify_governance() -> tuple[dict, dict, dict, dict, list[dict]]:
    contract = load_json(CONTRACT_PATH)
    overlay = load_json(LEDGER_PATH)
    audit = load_json(SOURCE_AUDIT_PATH)
    inventory_audit = load_json(ROOT / overlay["source_inventory_audit"]["path"])
    base = load_json(ROOT / overlay["base_ledger"]["path"])
    runtime = load_json(L88_RUNTIME_CONTRACT_PATH)
    if contract["build_id"] != BUILD_ID or overlay["build_id"] != BUILD_ID:
        raise RuntimeError("R3 governance build id mismatch")
    if contract["status"] != "source_only_not_run":
        raise RuntimeError("R3 source contract must remain source_only_not_run")
    for key, record in contract["immutable_sources"].items():
        verify_record(ROOT / record["path"], record, key)
    inherited = audit["parent_source_inventory_audit"]["inherited_findings"]
    if (
        inherited["governed_component_count"] != 240
        or inherited["exact_object_requirement_count"] != 232
        or inherited["source_absent_hold_count"] != 8
    ):
        raise RuntimeError("R3 inherited source-inventory accounting drifted")
    resolved = resolve_ledger(overlay, base, runtime)
    actual_names = parse_glb_mesh_node_names(L88_GLB_PATH)
    normalized = ("\n".join(actual_names) + "\n").encode("utf-8")
    inventory = inventory_audit["evidence"]["l88_glb_mesh_inventory"]
    if len(actual_names) != inventory["mesh_node_count"]:
        raise RuntimeError("R3 actual L88 mesh-node count drifted")
    if len(normalized) != inventory["normalized_sorted_names_bytes"]:
        raise RuntimeError("R3 normalized actual L88 source inventory size drifted")
    if hashlib.sha256(normalized).hexdigest() != inventory["normalized_sorted_names_sha256"]:
        raise RuntimeError("R3 normalized actual L88 source inventory hash drifted")
    return contract, overlay, audit, runtime, resolved


def refuse_overwrite() -> None:
    existing = [
        str(path)
        for path in (BLEND_PATH, GLB_PATH, MANIFEST_PATH)
        if path.exists()
    ]
    if existing:
        raise RuntimeError("R3 immutable output already exists: " + ", ".join(existing))
    if COMPARISON_DIR.exists() and any(COMPARISON_DIR.iterdir()):
        raise RuntimeError("R3 comparison directory is not empty")


def isolated_copy_and_open(contract: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(L88_BLEND_PATH, BLEND_PATH)
    if sha256_file(BLEND_PATH) != contract["immutable_sources"]["l88_blend"]["sha256"]:
        raise RuntimeError("R3 isolated L88 copy failed hash verification")
    bpy.ops.wm.open_mainfile(filepath=str(BLEND_PATH))
    if sha256_file(L88_BLEND_PATH) != contract["immutable_sources"]["l88_blend"]["sha256"]:
        raise RuntimeError("R3 immutable L88 source changed")


def stage_source_inventory_exception_gate(
    overlay: dict, resolved: list[dict]
) -> list[dict]:
    records = []
    for entry in resolved:
        if entry["classification"] != "source_absent_hold":
            continue
        governed_name = entry["name"]
        if bpy.data.objects.get(governed_name) is not None:
            raise RuntimeError(
                f"R3 source-absent contract changed; create a new version: {governed_name}"
            )
        observed_name = overlay["actual_source_observations"][governed_name]
        records.append(
            {
                "governed_name": governed_name,
                "classification": "source_absent_hold",
                "required_as_object": False,
                "synthesized": False,
                "actual_source_name_observed": observed_name,
                "actual_source_object_present": bpy.data.objects.get(observed_name)
                is not None,
                "promotion_allowed": False,
            }
        )
    if len(records) != 8:
        raise RuntimeError("R3 did not account for exactly eight source-absent entries")
    return records


def stage_camera_and_clearance(contract: dict) -> list[str]:
    collection = r1.ensure_collection(GOVERNANCE_COLLECTION_NAME)
    camera_spec = contract["first_stage_camera"]
    r1.create_camera(
        camera_spec["name"],
        tuple(camera_spec["location_m"]),
        tuple(camera_spec["target_m"]),
        float(camera_spec["lens_mm"]),
        collection,
        clip_start=float(camera_spec["clip_start_m"]),
    )
    names = []
    for name, spec in contract["required_safety_and_clearance_volumes"].items():
        r1.create_volume(name, spec, collection)
        names.append(name)
    return names


def stage_component_ledger_tags(resolved: list[dict]) -> list[str]:
    tagged = []
    for entry in resolved:
        if entry["classification"] == "source_absent_hold":
            continue
        obj = bpy.data.objects.get(entry["name"])
        if obj is None:
            raise RuntimeError(f"R3 required exact L88 object missing: {entry['name']}")
        obj["SKG_UpliftClass"] = entry["classification"]
        obj["SKG_PromotionAllowed"] = False
        obj["SKG_InheritedFrom"] = "L88"
        obj["SKG_OriginalNamePreserved"] = True
        obj["SKG_R3ExactObjectRequirement"] = True
        tagged.append(entry["name"])
    if len(tagged) != 232:
        raise RuntimeError("R3 must tag exactly 232 exact source objects")
    return tagged


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


def stage_selective_002_donors(contract: dict, base_ledger: dict) -> list[str]:
    donor = r1.load_donor_module()
    collection = r1.ensure_collection(DONOR_COLLECTION_NAME)
    mats = donor.build_materials()
    before = {obj.name for obj in bpy.data.objects}
    donor.create_radial_cowling(collection, mats)
    donor.create_propeller(collection, mats)
    rename = {
        "GEO_PROD002_CowlingShell": "GEO_UPLIFT003R3_DONOR_CowlingShell",
        "GEO_PROD002_CowlingFrontRing": "GEO_UPLIFT003R3_DONOR_CowlingFrontRing",
        "GEO_PROD002_CowlingShutters": "GEO_UPLIFT003R3_DONOR_CowlingShutters",
        "GEO_PROD002_CowlingInletCone": "GEO_UPLIFT003R3_DONOR_CowlingInletCone",
        "GEO_PROD002_Spinner": "GEO_UPLIFT003R3_DONOR_Spinner",
        "GEO_PROD002_PropBlade_A": "GEO_UPLIFT003R3_DONOR_PropBlade_A",
        "GEO_PROD002_PropBlade_B": "GEO_UPLIFT003R3_DONOR_PropBlade_B",
    }
    for source_name, target_name in rename.items():
        obj = bpy.data.objects.get(source_name)
        if obj is None or source_name in before:
            raise RuntimeError(f"R3 donor helper did not create {source_name}")
        obj.name = target_name
        r1.link_exclusively(obj, collection)
        tag_donor(obj, source_name)
    for side, suffix in ((-1.0, "L"), (1.0, "R")):
        obj = donor.base.add_cylinder(
            f"GEO_UPLIFT003R3_DONOR_MainWheelWell_{suffix}",
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
    nose = donor.base.add_cylinder(
        "GEO_UPLIFT003R3_DONOR_NoseWheelWell",
        0.23,
        0.07,
        (3.05, 0.0, -0.18),
        (0.0, 1.5707963267948966, 0.0),
        collection,
        [mats["MAT002_WheelWell"]],
        64,
        0.01,
    )
    tag_donor(nose, "GEO_PROD002_NoseWheelWell")
    for name, location, role in (
        (
            "DATUM_UPLIFT003R3_DONOR_CanopyTravel",
            (-1.25, 0.0, 1.33),
            "canopy_travel_only_l88_canopy_preserved",
        ),
        (
            "DATUM_UPLIFT003R3_DONOR_MainGearPivot_L",
            (0.78, -0.92, 0.15),
            "main_gear_pivot_L_only_l88_gear_preserved",
        ),
        (
            "DATUM_UPLIFT003R3_DONOR_MainGearPivot_R",
            (0.78, 0.92, 0.15),
            "main_gear_pivot_R_only_l88_gear_preserved",
        ),
        (
            "DATUM_UPLIFT003R3_DONOR_NoseGearPivot",
            (3.02, 0.0, 0.04),
            "nose_gear_pivot_only_l88_gear_preserved",
        ),
    ):
        add_datum(name, location, role, collection)
    for target_name in base_ledger["donor_replacement_map"]:
        target = bpy.data.objects.get(target_name)
        if target is None:
            raise RuntimeError(f"R3 donor target missing: {target_name}")
        target.hide_render = True
        target.hide_set(True)
        target["SKG_RetiredForComparisonOnly"] = True
        target["SKG_PromotionAllowed"] = False
    missing = [name for name in contract["required_donor_objects"] if name not in bpy.data.objects]
    if missing:
        raise RuntimeError(f"R3 selective donor output missing: {missing}")
    return list(contract["required_donor_objects"])


def stage_matched_comparison_setup(contract: dict) -> dict[str, bpy.types.Object]:
    collection = r1.ensure_collection(GOVERNANCE_COLLECTION_NAME)
    specs = {
        "beauty": ((11.5, -11.5, 6.7), (0.0, 0.0, -0.05), 58.0, None),
        "side": ((0.0, -15.0, 0.4), (0.0, 0.0, 0.0), 58.0, 10.8),
        "top": ((0.0, 0.0, 15.0), (0.0, 0.0, 0.0), 58.0, 10.8),
        "rear_cockpit": ((-1.20, -1.10, 1.10), (0.30, -0.55, 0.68), 38.0, None),
        "rear_gunner_eye": ((-0.90, -0.64, 1.08), (1.58, -0.64, 1.06), 46.0, None),
    }
    cameras = {}
    for slot in contract["matched_comparison_slots"]:
        location, target, lens, ortho = specs[slot["slot"]]
        cameras[slot["slot"]] = r1.create_camera(
            f"CAM_UPLIFT003R3_{slot['slot']}",
            location,
            target,
            lens,
            collection,
            orthographic_scale=ortho,
        )
    return cameras


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.045, 0.06, 0.085)
    light_name = "LIGHT_UPLIFT003R3_Key"
    if light_name not in bpy.data.objects:
        light_data = bpy.data.lights.new(light_name, "AREA")
        light_data.energy = 1800.0
        light_data.shape = "DISK"
        light_data.size = 7.0
        light = bpy.data.objects.new(light_name, light_data)
        r1.ensure_collection(GOVERNANCE_COLLECTION_NAME).objects.link(light)
        light.location = (5.5, -7.0, 8.0)
        light.rotation_euler = (0.55, 0.0, 0.72)
        light["SKG_BuildId"] = BUILD_ID
        light["SKG_PromotionAllowed"] = False


def save_export_and_render(
    contract: dict, cameras: dict[str, bpy.types.Object]
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
    scene = bpy.context.scene
    comparisons = []
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
    resolved: list[dict],
    exception_records: list[dict],
    tagged_names: list[str],
    clearance_names: list[str],
    donor_names: list[str],
    stages: list[str],
    comparisons: list[dict],
    started: float,
) -> None:
    governed_names = set(tagged_names) | set(donor_names) | set(clearance_names) | {
        contract["first_stage_camera"]["name"]
    }
    object_records = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.name not in governed_names:
            continue
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
        "schema": "skyguard.bld-m01-yak-uplift-003-r3.artifact-manifest.v1",
        "build_id": BUILD_ID,
        "status": "provisional_uplift_candidate_not_accepted_not_final_not_aaa",
        "promotion_allowed": False,
        "stage_order": stages,
        "immutable_sources": contract["immutable_sources"],
        "component_accounting": {
            "governed_total": len(resolved),
            "exact_object_required": len(tagged_names),
            "source_absent_hold": len(exception_records),
            "equation_valid": len(tagged_names) + len(exception_records) == len(resolved),
        },
        "resolved_component_ledger": resolved,
        "classification_counts": dict(
            sorted(Counter(item["classification"] for item in resolved).items())
        ),
        "source_absent_hold_records": exception_records,
        "object_records": object_records,
        "donor_objects": donor_names,
        "matched_comparisons": comparisons,
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
        "original_l88_unchanged": (
            sha256_file(L88_BLEND_PATH)
            == contract["immutable_sources"]["l88_blend"]["sha256"]
        ),
        "claims": {
            "final": False,
            "aaa": False,
            "unreal_accepted": False,
            "matched_visual_review_accepted": False,
        },
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    started = time.perf_counter()
    r1.require_blender_52()
    contract, overlay, _audit, _runtime, resolved = load_and_verify_governance()
    base_ledger = load_json(ROOT / overlay["base_ledger"]["path"])
    refuse_overwrite()
    isolated_copy_and_open(contract)
    stages = []
    exception_records = stage_source_inventory_exception_gate(overlay, resolved)
    stages.append("source_inventory_exception_gate")
    clearance_names = stage_camera_and_clearance(contract)
    stages.append("camera_and_clearance")
    tagged_names = stage_component_ledger_tags(resolved)
    stages.append("component_ledger_tags")
    donor_names = stage_selective_002_donors(contract, base_ledger)
    stages.append("selective_002_donors")
    cameras = stage_matched_comparison_setup(contract)
    stages.append("matched_comparison_setup")
    comparisons = save_export_and_render(contract, cameras)
    stages.append("isolated_save_export_and_comparison")
    if stages != contract["required_stage_order"]:
        raise RuntimeError("R3 governed stage order drifted")
    write_manifest(
        contract,
        resolved,
        exception_records,
        tagged_names,
        clearance_names,
        donor_names,
        stages,
        comparisons,
        started,
    )
    print(f"[{BUILD_ID}] provisional R3 comparison candidate emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
