"""Build only the isolated Attempt03 review-map assembly.

Future Unreal authorization is required. This script reuses the immutable
Build008 mesh/material packages, creates one new review map, and applies the
source-authoritative actor locations from the Attempt03 contract. It never
modifies geometry, UVs, bakes, materials, mesh settings, runtime maps, or config.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
REPORT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_BUILD.json"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03] " + message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def hash_tree(root: Path, suffixes: set[str] | None = None) -> dict[str, str]:
    records = {}
    if not root.exists():
        return records
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if suffixes and path.suffix.lower() not in suffixes:
            continue
        records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def verify_bound_inputs(contract: dict) -> None:
    for record in contract["bound_inputs"].values():
        path = ROOT / record["path"]
        if not path.is_file():
            fail("bound input is missing: " + str(path))
        if path.stat().st_size != record["bytes"]:
            fail("bound input byte count changed: " + str(path))
        if sha256_file(path) != record["sha256"]:
            fail("bound input hash changed: " + str(path))


def verify_existing_candidate_hashes(contract: dict) -> dict[str, str]:
    review = load_json(ROOT / contract["bound_inputs"]["failed_visual_review"]["path"])
    expected = review["persistence"]["current_package_hashes"]
    current = hash_tree(
        ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008",
        {".uasset", ".umap"},
    )
    if current != expected:
        fail("immutable existing candidate package hashes changed")
    return current


def vector(values: list[float]) -> unreal.Vector:
    return unreal.Vector(float(values[0]), float(values[1]), float(values[2]))


def main() -> None:
    if REPORT_PATH.exists():
        fail("immutable Attempt03 build report already exists")
    contract = load_json(CONTRACT_PATH)
    verify_bound_inputs(contract)
    candidate_before = verify_existing_candidate_hashes(contract)
    runtime_before = hash_tree(ROOT / "Content/Skyguard/Maps", {".uasset", ".umap"})
    config_before = hash_tree(ROOT / "Config")
    policy = contract["candidate"]
    attempt03_root = policy["attempt03_root"]
    review_map = policy["attempt03_review_map"]
    if unreal.EditorAssetLibrary.does_directory_exist(attempt03_root):
        existing = unreal.EditorAssetLibrary.list_assets(attempt03_root, True, False)
        if existing:
            fail("Attempt03 root is non-empty; never overwrite an attempt")
    if unreal.EditorAssetLibrary.does_asset_exist(review_map):
        fail("Attempt03 review map already exists")
    review_folder = attempt03_root + "/Review"
    if not unreal.EditorAssetLibrary.does_directory_exist(review_folder):
        unreal.EditorAssetLibrary.make_directory(review_folder)
    if not unreal.EditorLevelLibrary.new_level(review_map):
        fail("could not create isolated Attempt03 review map")

    created = []
    for record in contract["assembly"]["actors"]:
        mesh = unreal.EditorAssetLibrary.load_asset(record["mesh"])
        if not isinstance(mesh, unreal.StaticMesh):
            fail("immutable candidate mesh is unavailable: " + record["mesh"])
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            vector(record["actor_location_cm"]),
            unreal.Rotator(),
        )
        if not actor:
            fail("could not spawn Attempt03 review actor: " + record["key"])
        actor.set_actor_label("M01C008A03_" + record["key"].replace("/", "_"))
        actor.static_mesh_component.set_static_mesh(mesh)
        actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
        created.append(
            {
                "key": record["key"],
                "label": actor.get_actor_label(),
                "mesh": record["mesh"],
                "location_cm": [
                    float(actor.get_actor_location().x),
                    float(actor.get_actor_location().y),
                    float(actor.get_actor_location().z),
                ],
                "rotation_degrees": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
            }
        )
    if len(created) != 12:
        fail("Attempt03 actor count differs from exact contract")
    unreal.EditorLevelLibrary.save_current_level()

    candidate_after = verify_existing_candidate_hashes(contract)
    runtime_after = hash_tree(ROOT / "Content/Skyguard/Maps", {".uasset", ".umap"})
    config_after = hash_tree(ROOT / "Config")
    if candidate_before != candidate_after:
        fail("existing candidate packages changed while building Attempt03")
    if runtime_before != runtime_after:
        fail("runtime map packages changed while building Attempt03")
    if config_before != config_after:
        fail("config changed while building Attempt03")
    attempt03_files = hash_tree(
        ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03",
        {".uasset", ".umap"},
    )
    if len(attempt03_files) != policy["attempt03_new_package_count"]:
        fail("Attempt03 emitted an unexpected package count")

    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-build.v1",
        "gate": "PASS_ATTEMPT03_MAP_BUILD_REQUIRES_FRESH_TRANSFORM_AUDIT",
        "build_id": contract["build_id"],
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "review_map": review_map,
        "actors": created,
        "attempt03_packages": attempt03_files,
        "existing_candidate_package_count": len(candidate_after),
        "existing_candidate_packages_unchanged": True,
        "runtime_maps_unchanged": True,
        "config_unchanged": True,
        "geometry_changed": False,
        "uv_changed": False,
        "bakes_changed": False,
        "materials_changed": False,
        "mesh_settings_changed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01Grouped008Attempt03] " + report["gate"])


if __name__ == "__main__":
    main()
