"""Blender 5.2 compatibility wrapper for the frozen source evaluator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


FROZEN = Path(r"D:\Skyguard52\Scripts\Production\m01_lighthouse_source_evaluation01\evaluate_m01_lighthouse_sources.py")
spec = importlib.util.spec_from_file_location("skyguard_lighthouse_eval01_frozen", FROZEN)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load frozen evaluator: {FROZEN}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def make_material_compat(name: str, color: tuple[float, float, float, float], metallic: float, roughness: float):
    material = module.bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    module.require(principled is not None, "Principled BSDF unavailable")
    principled.inputs["Base Color"].default_value = color
    metallic_socket = principled.inputs.get("Metallic") or principled.inputs.get("Metallic IOR Level")
    module.require(metallic_socket is not None, "Blender 5.2 metallic input unavailable")
    metallic_socket.default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return material


module.make_material = make_material_compat

if __name__ == "__main__":
    raise SystemExit(module.main())
