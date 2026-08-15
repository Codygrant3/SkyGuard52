"""Material-preserving Recovery02 consolidation derived from frozen UnrealReady01 source."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\build_visible_environment_unreal_ready01.py"
EXPECTED_SOURCE = "9dc543d6443e35f12cb9d50e7d577f58d869447f7bdcdcd907389d94599eb21b"


def replace_exact(source: str, old: str, new: str, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} occurrences of {old!r}; found {actual}")
    return source.replace(old, new)


def build_transformed_source() -> str:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE:
        raise RuntimeError("Frozen UnrealReady01 generator hash mismatch")
    source = raw.decode("utf-8")
    source = replace_exact(source, "import bpy\n", "import bmesh\nimport bpy\n")
    source = source.replace("VisibleEnvironmentProductionReset01_UnrealReady01", "VisibleEnvironmentProductionReset01_UnrealReady02")
    source = source.replace("M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_UNREAL_READY01.blend", "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_UNREAL_READY02.blend")
    source = source.replace("unreal-ready01", "unreal-ready02")
    source = replace_exact(source, 'mesh.name = name + "_MESH"', 'mesh.name = name')
    source = replace_exact(source, 'socket = bpy.data.objects.new(f"SOCKET_{asset}_Origin", None)', 'socket = bpy.data.objects.new(f"TMP_SOCKET_{asset}_Origin", None)')
    source = replace_exact(source, 'world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32', 'world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55')
    source = replace_exact(source, 'sun_data.energy = 2.2', 'sun_data.energy = 2.6')
    source = replace_exact(source, 'area_data.energy = 850.0', 'area_data.energy = 1300.0')

    start = source.index("def join_group(")
    end = source.index("\ndef copy_collision", start)
    replacement = '''def join_group(asset: str, group: str, sources: list[bpy.types.Object], origin: Vector, target: bpy.types.Collection) -> tuple[bpy.types.Object, dict[str, object]]:
    require(sources, f"No sources for required group {asset}:{group}")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    combined = bmesh.new()
    materials: list[bpy.types.Material] = []
    material_lookup: dict[int, int] = {}
    expected_triangles = 0
    source_materials: dict[str, int] = {}
    try:
        for source in sources:
            evaluated = source.evaluated_get(depsgraph)
            mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            require(mesh is not None, f"Could not evaluate mesh {source.name}")
            try:
                mesh.transform(Matrix.Translation(-origin) @ source.matrix_world)
                mesh.update()
                expected_triangles += triangle_count(mesh)
                local_to_global: dict[int, int] = {}
                for local_index, material in enumerate(mesh.materials):
                    require(material is not None, f"Null render material on {source.name}")
                    key = material.as_pointer()
                    if key not in material_lookup:
                        material_lookup[key] = len(materials)
                        materials.append(material)
                    local_to_global[local_index] = material_lookup[key]
                require(local_to_global, f"No material slots on render mesh {source.name}")
                for polygon in mesh.polygons:
                    require(polygon.material_index in local_to_global, f"Invalid material index on {source.name}")
                    polygon.material_index = local_to_global[polygon.material_index]
                    material_name = materials[polygon.material_index].name
                    source_materials[material_name] = source_materials.get(material_name, 0) + 1
                combined.from_mesh(mesh)
            finally:
                bpy.data.meshes.remove(mesh)

        final_mesh = bpy.data.meshes.new(f"{asset}_{group}")
        combined.to_mesh(final_mesh)
    finally:
        combined.free()
    for material in materials:
        final_mesh.materials.append(material)
    final_mesh.validate(verbose=False, clean_customdata=False)
    final_mesh.update()
    joined = bpy.data.objects.new(f"{asset}_{group}", final_mesh)
    target.objects.link(joined)
    joined["skyguard_asset_family"] = asset
    joined["skyguard_semantic_group"] = group
    joined["skyguard_source_object_count"] = len(sources)
    actual_triangles = triangle_count(final_mesh)
    used_indices = {polygon.material_index for polygon in final_mesh.polygons}
    require(actual_triangles == expected_triangles, f"Triangle mismatch {asset}:{group} expected={expected_triangles} actual={actual_triangles}")
    require(used_indices == set(range(len(materials))), f"Material usage mismatch {asset}:{group} used={sorted(used_indices)} slots={len(materials)}")
    require(len(materials) <= 16, f"Material-slot budget exceeded {asset}:{group}: {len(materials)}")
    return joined, {
        "group": group,
        "source_object_count": len(sources),
        "triangle_count_before": expected_triangles,
        "triangle_count_after": actual_triangles,
        "material_slot_count": len(materials),
        "material_names": [material.name for material in materials],
        "material_polygon_usage": source_materials,
        "uv_layer_count": len(final_mesh.uv_layers),
        "vertex_count": len(final_mesh.vertices),
        "polygon_count": len(final_mesh.polygons),
    }

'''
    source = source[:start] + replacement + source[end + 1 :]
    source = replace_exact(
        source,
        "    remove_source_scene(keep)\n    camera, lights = configure_review_scene()\n",
        "    remove_source_scene(keep)\n"
        "    for asset in ASSETS:\n"
        "        socket = next(obj for obj in export_objects[asset] if obj.type == 'EMPTY')\n"
        "        socket.name = f'SOCKET_{asset}_Origin'\n"
        "        records[asset]['socket'] = socket.name\n"
        "    camera, lights = configure_review_scene()\n",
    )
    return source


def offline_contract_test() -> int:
    source = build_transformed_source()
    compile(source, str(SOURCE) + "::UnrealReady02Offline", "exec")
    required = (
        "import bmesh",
        "combined.from_mesh(mesh)",
        "material_polygon_usage",
        "used_indices == set(range(len(materials)))",
        "SOCKET_{asset}_Origin",
        "VisibleEnvironmentProductionReset01_UnrealReady02",
    )
    if not all(token in source for token in required):
        raise RuntimeError("UnrealReady02 transformation incomplete")
    if "mesh.name = name + \"_MESH\"" in source or "VisibleEnvironmentProductionReset01_UnrealReady01" in source:
        raise RuntimeError("UnrealReady02 retains a superseded output or mesh-name binding")
    print("PASS_TRANSFORMATION_COMPILE")
    return 0


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

transformed = build_transformed_source()
code = compile(transformed, str(SOURCE) + "::UnrealReady02", "exec")
namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(code, namespace, namespace)
