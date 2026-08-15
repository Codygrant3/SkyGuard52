"""Bounded Recovery01 wrapper for the coastal facade bay Production01 worker.

The frozen Production01 worker rejected the accepted consolidated window frame
because its guard compared the installed wall-surround width (3.60 m) to the
inner sash envelope.  Frozen GLB accessor bounds prove the 3.60 m value.  This
wrapper changes only that exact guard and the fresh asset identity; all geometry,
materials, cameras, checkpoints, exports and evidence logic remain in the frozen
Production01 worker.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
FROZEN_WORKER = ROOT / "Scripts/Production/m01_coastal_facade_bay_production01/build_m01_coastal_facade_bay_production01.py"
RECOVERY_ASSET_ID = "m01-coastal-facade-bay-production01-recovery01"
RECOVERY_CLASSIFICATION = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_FACADE_BAY_PRODUCTION01_RECOVERY01_BLENDER_EXECUTION"


def load_frozen_worker():
    spec = importlib.util.spec_from_file_location("skyguard_coastal_facade_bay_production01_frozen", FROZEN_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load frozen worker: {FROZEN_WORKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


worker = load_frozen_worker()
original_require = worker.require


def recovery_require(condition: bool, message: str) -> None:
    if message == "Contract classification changed":
        values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
        original_require("--contract" in values, "Recovery01 contract argument missing")
        contract_path = Path(values[values.index("--contract") + 1])
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        original_require(contract.get("classification") == RECOVERY_CLASSIFICATION, "Recovery01 contract classification changed")
        return
    if message == "Accepted window width changed":
        frame = worker.bpy.data.objects.get(worker.WINDOW_OBJECTS[0])
        original_require(frame is not None, "Accepted consolidated frame missing during Recovery01 guard")
        minimum, maximum = worker.base.bounds([frame])
        measured_width = maximum.x - minimum.x
        original_require(3.55 <= measured_width <= 3.65, f"Accepted consolidated frame width outside frozen GLB authority: {measured_width}")
        return
    original_require(condition, message)


worker.require = recovery_require
worker.ASSET_ID = RECOVERY_ASSET_ID
worker.base.ASSET_ID = RECOVERY_ASSET_ID


if __name__ == "__main__":
    raise SystemExit(worker.main())
