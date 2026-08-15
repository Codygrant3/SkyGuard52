from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\GrokProduction\recover_m01_utility_cabinet_recovery02_scene.py")
SOURCE_BYTES = 9122
SOURCE_SHA256 = "543de177dffc3392550273d59471960b4216dbd109c57a62e79a11d0507d84ce"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if SOURCE.stat().st_size != SOURCE_BYTES or sha256(SOURCE) != SOURCE_SHA256:
    raise RuntimeError("Recovery02 source authority changed")

text = SOURCE.read_text(encoding="utf-8")
start_marker = "    def corrected_vent_bank(name, side):\n"
end_marker = "    def corrected_make_hinge(name, location, side):\n"
if text.count(start_marker) != 1 or text.count(end_marker) != 1:
    raise RuntimeError("Unable to isolate governed vent-bank correction block")
start = text.index(start_marker)
end = text.index(end_marker)
replacement = '''    def corrected_vent_bank(name, side):
        x_face = -module.WIDTH * 0.5 if side == "left" else module.WIDTH * 0.5
        outward = -1.0 if side == "left" else 1.0
        vent_h = 0.42
        vent_d = 0.22
        zc = module.PLINTH_H + 0.55
        yc = 0.0
        back = module.box_mesh(module.BUILD_PREFIX + name + "_back", (0.006, vent_d + 0.02, vent_h + 0.02), (x_face + outward * 0.006, yc, zc))
        feature_x = x_face + outward * 0.014
        parts = [back]
        parts.append(module.box_mesh(module.BUILD_PREFIX + name + "_frame_top", (0.012, vent_d + 0.032, 0.020), (feature_x, yc, zc + vent_h * 0.5 + 0.010)))
        parts.append(module.box_mesh(module.BUILD_PREFIX + name + "_frame_bottom", (0.012, vent_d + 0.032, 0.020), (feature_x, yc, zc - vent_h * 0.5 - 0.010)))
        parts.append(module.box_mesh(module.BUILD_PREFIX + name + "_frame_front", (0.012, 0.018, vent_h + 0.020), (feature_x, yc - vent_d * 0.5 - 0.009, zc)))
        parts.append(module.box_mesh(module.BUILD_PREFIX + name + "_frame_rear", (0.012, 0.018, vent_h + 0.020), (feature_x, yc + vent_d * 0.5 + 0.009, zc)))
        pitch = vent_h / (module.VENT_ROWS + 1)
        for index in range(module.VENT_ROWS):
            z = zc - vent_h * 0.5 + pitch * (index + 1)
            blade = module.box_mesh(module.BUILD_PREFIX + name + f"_L{index}", (0.016, vent_d - 0.025, 0.016), (feature_x + outward * 0.008, yc, z))
            blade.rotation_euler = (0.0, module.math.radians(outward * -24.0), 0.0)
            module.apply_transforms(blade, location=False)
            parts.append(blade)
        module.ensure_active(back)
        for item in parts[1:]:
            item.select_set(True)
        module.bpy.ops.object.join()
        obj = module.bpy.context.view_layer.objects.active
        obj.name = name
        obj.data.name = name
        module.apply_transforms(obj, location=True)
        module.ensure_active(obj)
        bevel = obj.modifiers.new("VentEdgeBevel", "BEVEL")
        bevel.width = 0.0012
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        module.bpy.ops.object.modifier_apply(modifier=bevel.name)
        module.set_smooth(obj)
        module.ensure_active(obj)
        module.bpy.ops.object.mode_set(mode="EDIT")
        module.bpy.ops.mesh.select_all(action="SELECT")
        module.bpy.ops.mesh.remove_doubles(threshold=0.0002)
        module.bpy.ops.mesh.normals_make_consistent(inside=False)
        module.bpy.ops.object.mode_set(mode="OBJECT")
        return obj

'''
text = text[:start] + replacement + text[end:]

replacements = {
    '"m01-utility-cabinet-deterministic-recovery02"': '"m01-utility-cabinet-deterministic-recovery04"',
    '"attempt_20260811T093000000000Z"': '"attempt_20260811T095000000000Z"',
    '"M01_Promenade_UtilityCabinet_Recovery02.blend"': '"M01_Promenade_UtilityCabinet_Recovery04.blend"',
    '"M01_Promenade_UtilityCabinet_Recovery02.glb"': '"M01_Promenade_UtilityCabinet_Recovery04.glb"',
    'if left_min[0] >= -0.500:': 'if left_min[0] >= -0.465:',
    'if right_max[0] <= 0.500:': 'if right_max[0] <= 0.465:',
    'skyguard.m01-utility-cabinet.deterministic-recovery02.report.v1': 'skyguard.m01-utility-cabinet.deterministic-recovery04.report.v1',
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one governed replacement for {old!r}, found {count}")
    text = text.replace(old, new, 1)

namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(compile(text, str(SOURCE), "exec"), namespace, namespace)
