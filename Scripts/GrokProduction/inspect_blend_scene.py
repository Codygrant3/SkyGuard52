import json

import bpy


def mesh_record(obj):
    mesh = obj.data
    material_names = [slot.material.name if slot.material else None for slot in obj.material_slots]
    dimensions = [round(float(value), 6) for value in obj.dimensions]
    return {
        "name": obj.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "dimensions_m": dimensions,
        "materials": material_names,
        "modifiers": [modifier.type for modifier in obj.modifiers],
        "hidden_render": bool(obj.hide_render),
    }


records = {
    "blender_version": bpy.app.version_string,
    "filepath": bpy.data.filepath,
    "objects": [],
}

for scene_object in sorted(bpy.data.objects, key=lambda item: item.name.lower()):
    if scene_object.type == "MESH":
        records["objects"].append(mesh_record(scene_object))
    else:
        records["objects"].append(
            {
                "name": scene_object.name,
                "type": scene_object.type,
                "hidden_render": bool(scene_object.hide_render),
            }
        )

print("SKYGUARD_BLEND_INSPECTION_BEGIN")
print(json.dumps(records, sort_keys=True))
print("SKYGUARD_BLEND_INSPECTION_END")
