from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path


WORKER = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\build_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01.py"
)


def main() -> int:
    spec = importlib.util.spec_from_file_location("skyguard_r07_smoke_worker", WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery07 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source, receipt = module.load_recovery07_source()
    namespace = {"__name__": "skyguard_r07_smoke_embedded", "__file__": str(WORKER), "__package__": None}
    exec(compile(source, str(WORKER), "exec"), namespace)
    reset_scene = namespace["reset_scene"]
    build_materials = namespace["build_materials"]
    collection = namespace["collection"]
    add_box = namespace["add_box"]
    reset_scene()
    materials = build_materials()
    target = collection("R07_FAST_BOX_SMOKE")
    start = time.perf_counter()
    count = 1000
    for index in range(count):
        width = (1.25, 1.55, 1.85, 2.15)[index % 4]
        add_box(
            f"SMOKE_{index:04d}",
            ((index % 40) * 2.5, (index // 40) * 2.0, 1.0),
            (width, 0.14, 1.72),
            materials[("metal", "concrete", "glass", "plaster_fde")[index % 4]],
            target,
            0.018,
        )
    elapsed = time.perf_counter() - start
    result = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery07.fast-box-smoke.v1",
        "classification": "PASS" if elapsed <= 30.0 else "FAIL",
        "object_count": count,
        "cached_mesh_count": len(namespace["_FAST_BOX_MESH_CACHE"]),
        "elapsed_seconds": elapsed,
        "unresolved_named_calls": receipt["generated_call_graph"]["unresolved_named_calls"],
    }
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["classification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
