"""Recovery01 binding for Assembly03's bounded mesh-capture ordering defect."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_accepted_candidate_assembly03\author_m01_accepted_candidate_assembly03.py"
)
BASE_BYTES = 24_920
BASE_SHA256 = "1396ebac2dc3cd5ef605bc266a9b7f3157d306c3cbfa87ebb655e73cd930ae04"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen failed Assembly03 author authority changed")

source = BASE.read_text(encoding="utf-8")
for old, new in (
    ("M01_AcceptedCandidateAssembly03", "M01_AcceptedCandidateAssembly03_Recovery01"),
    ("M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01", "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01/attempt_01"),
    ("M01_ACA03_", "M01_ACA03R01_"),
    ("accepted-candidate-assembly03.authoring.v1", "accepted-candidate-assembly03-recovery01.authoring.v1"),
    ("ASSEMBLY03_OFFLINE_CONTRACT", "ASSEMBLY03_RECOVERY01_OFFLINE_CONTRACT"),
    ("ASSEMBLY03_READY_FOR_STRUCTURAL_ADJUDICATION", "ASSEMBLY03_RECOVERY01_READY_FOR_STRUCTURAL_ADJUDICATION"),
):
    if old not in source:
        raise RuntimeError(f"Recovery01 binding token absent: {old}")
    source = source.replace(old, new)

old_block = '''        result["removed_labels"] = sorted(actor.get_actor_label() for actor in removals)
        require(len(result["removed_labels"]) == 84, f"Unexpected removal count: {len(result['removed_labels'])}")
        for actor in removals:
            require(actors_api.destroy_actor(actor), f"Failed to remove rejected presentation actor: {actor.get_actor_label()}")

        # Preserve and validate all accepted repeated props already staged.'''
new_block = '''        result["removed_labels"] = sorted(actor.get_actor_label() for actor in removals)
        require(len(result["removed_labels"]) == 84, f"Unexpected removal count: {len(result['removed_labels'])}")

        # Recovery01 bounded correction: copy the accepted StaticMesh object
        # references while the inherited actors are still valid. The original
        # attempt destroyed these actors first and then dereferenced them.
        family_sources: dict[str, dict[str, object]] = {}
        for placement, triplet in city_groups.items():
            family = city_metadata[placement]["family"]
            if family not in family_sources:
                family_sources[family] = {}
                for group_name, actor in triplet.items():
                    _component, mesh = static_mesh_component(actor)
                    family_sources[family][group_name] = mesh
        require(set(family_sources) == {"ApartmentA", "MidriseB", "CornerC"}, "Accepted family mesh authority incomplete")

        for actor in removals:
            label = actor.get_actor_label()
            require(actors_api.destroy_actor(actor), f"Failed to remove rejected presentation actor: {label}")

        # Preserve and validate all accepted repeated props already staged.'''
if source.count(old_block) != 1:
    raise RuntimeError("Recovery01 ordering anchor changed")
source = source.replace(old_block, new_block)

duplicate_block = '''        # Reuse the accepted imported building meshes, but not the rejected 3x9
        # placement pattern. Source triplets are discovered from inherited actors.
        family_sources: dict[str, dict[str, object]] = {}
        for placement, triplet in city_groups.items():
            family = city_metadata[placement]["family"]
            if family not in family_sources:
                family_sources[family] = {}
                for group_name, actor in triplet.items():
                    component, mesh = static_mesh_component(actor)
                    family_sources[family][group_name] = mesh
        require(set(family_sources) == {"ApartmentA", "MidriseB", "CornerC"}, "Accepted family mesh authority incomplete")

'''
if source.count(duplicate_block) != 1:
    raise RuntimeError("Recovery01 obsolete post-destruction capture block changed")
source = source.replace(
    duplicate_block,
    "        # Accepted family mesh references were captured before actor destruction.\n\n",
)

if "Lvl_M01_AcceptedCandidateAssembly03.umap" in source:
    raise RuntimeError("Recovery01 retains failed output namespace")
if "M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01" in source:
    raise RuntimeError("Recovery01 retains failed attempt namespace")

exec(compile(source, __file__ + "::bound", "exec"), globals(), globals())
