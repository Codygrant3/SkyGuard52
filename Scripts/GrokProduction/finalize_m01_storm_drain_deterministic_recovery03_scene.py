from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\finalize_m01_storm_drain_recovery01_scene.py")
BASE_BYTES = 11_849
BASE_SHA256 = "3dcf1f8cd3f7ddc0c7b1ca79319e4b341c411cabf3209fea402913e8afc37cf7"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen storm-drain Recovery01 finalizer authority changed")

text = BASE.read_text(encoding="utf-8")
replacements = {
    'OUTPUT = ROOT / r"Production\\Attempts\\m01-storm-drain-grok-mcp-recovery01\\attempt_20260811T101500000000Z\\output"': 'OUTPUT = ROOT / r"Production\\Attempts\\m01-storm-drain-deterministic-recovery03\\attempt_20260811T104500000000Z\\output"',
    'CHECKPOINT = OUTPUT / "checkpoint"': 'CHECKPOINT = ROOT / r"Production\\Attempts\\m01-storm-drain-grok-mcp-recovery01\\attempt_20260811T101500000000Z\\output\\checkpoint"',
    'scene.render.engine = "BLENDER_EEVEE_NEXT"': 'scene.render.engine = "BLENDER_EEVEE"',
    'render_paths = [render_view(*view, camera, key, fill) for view in views]': 'render_paths = [render_view(view[0], view[1], camera, key, fill, *view[2:]) for view in views]',
    'M01_Promenade_StormDrain_Recovery01.blend': 'M01_Promenade_StormDrain_Recovery03.blend',
    'M01_Promenade_StormDrain_Recovery01.glb': 'M01_Promenade_StormDrain_Recovery03.glb',
    'skyguard.m01-storm-drain.grok-mcp.recovery01.implementation.v1': 'skyguard.m01-storm-drain.deterministic-recovery03.implementation.v1',
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one governed replacement for {old!r}, found {count}")
    text = text.replace(old, new, 1)

marker = 'for name in SOURCE_NAMES | set(SLOT_NAMES):\n'
material_normalization = '''def normalize_principled(material_name, base_color, metallic, roughness):
    material = bpy.data.materials[material_name]
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {material_name}")
    for link in list(links):
        if link.to_node == bsdf and link.to_socket.name in {"Base Color", "Metallic", "Roughness"}:
            links.remove(link)
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness


normalize_principled("M_M01_StormDrain_CastIron", (0.025, 0.03, 0.035), 0.82, 0.52)
normalize_principled("M_M01_StormDrain_DarkRecess", (0.004, 0.006, 0.008), 0.18, 0.76)
normalize_principled("M_M01_StormDrain_EdgeWear", (0.105, 0.115, 0.125), 0.72, 0.40)


'''
if text.count(marker) != 1:
    raise RuntimeError("Material-normalization insertion point changed")
text = text.replace(marker, material_normalization + marker, 1)

namespace = {"__name__": "__main__", "__file__": str(BASE)}
exec(compile(text, str(BASE), "exec"), namespace, namespace)
