"""Blender 5.2 API-bound Recovery02 for Production Reset01 Checkpoint01."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py"
PROBE = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json"
EXPECTED_SOURCE = "fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891"
EXPECTED_PROBE = "c017409181b17a9f27fc909445d458ada586d096f0ab66a40fe4fe2b3d37f53e"


def main() -> None:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE:
        raise RuntimeError("Frozen generator hash mismatch")
    probe_raw = PROBE.read_bytes()
    if hashlib.sha256(probe_raw).hexdigest() != EXPECTED_PROBE:
        raise RuntimeError("Blender 5.2 API probe hash mismatch")
    probe = json.loads(probe_raw)
    sky = probe["sky_texture"]
    if "MULTIPLE_SCATTERING" not in sky["sky_type_enum"] or "aerosol_density" not in sky["properties"]:
        raise RuntimeError("Required Blender 5.2 sky capabilities were not proved")
    if "BLENDER_EEVEE" not in probe["render_engines"]:
        raise RuntimeError("Required Blender 5.2 render engine was not proved")
    required_gltf = {"filepath", "export_format", "use_selection", "export_yup", "export_extras", "export_materials"}
    if not required_gltf.issubset(set(probe["gltf_export_properties"])):
        raise RuntimeError("Required GLB exporter properties were not proved")

    source = raw.decode("utf-8")
    substitutions = [
        ('VisibleEnvironmentProductionReset01_Checkpoint01"', 'VisibleEnvironmentProductionReset01_Checkpoint01_Recovery02"'),
        ('M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01.blend', 'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY02.blend'),
        ('sky.sky_type = "NISHITA"', 'sky.sky_type = "MULTIPLE_SCATTERING"'),
        ('sky.dust_density = 1.2', 'sky.aerosol_density = 1.2'),
    ]
    for old, new in substitutions:
        if source.count(old) != 1:
            raise RuntimeError(f"Expected exactly one source binding for {old!r}")
        source = source.replace(old, new)
    code = compile(source, str(SOURCE) + "::Recovery02", "exec")
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    exec(code, namespace, namespace)


if __name__ == "__main__":
    main()
