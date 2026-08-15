from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEGACY_PATH = PROJECT_ROOT / "Scripts" / "Workers" / "worker_core_yak52_airframe_refinement01.py"
ASSET_ID = "core-yak52-airframe-recovery01"


def load_frozen_worker() -> Any:
    specification = importlib.util.spec_from_file_location(
        "skyguard_frozen_yak52_airframe_refinement01", LEGACY_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not load frozen worker: {LEGACY_PATH}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def corrected_set_lighting(profile: str, key: Any, fill: Any, rim: Any, world: Any) -> None:
    settings = {
        "daylight": (4.0, 1750.0, 720.0, 850.0, (0.055, 0.075, 0.11)),
        "overcast": (2.0, 1050.0, 900.0, 500.0, (0.09, 0.10, 0.12)),
        "night": (0.7, 640.0, 280.0, 1050.0, (0.006, 0.012, 0.028)),
        "wet": (2.4, 1350.0, 620.0, 1100.0, (0.025, 0.04, 0.065)),
        "cockpit": (1.3, 800.0, 360.0, 700.0, (0.012, 0.022, 0.034)),
    }
    exposure, key_energy, fill_energy, rim_energy, color = settings[profile]
    key.data.energy = key_energy
    fill.data.energy = fill_energy
    rim.data.energy = rim_energy
    world.color = color
    key.data.color = (1.0, 0.82, 0.66) if profile in {"night", "cockpit"} else (1.0, 0.94, 0.84)
    rim.data.color = (0.20, 0.42, 1.0) if profile in {"night", "wet"} else (0.68, 0.80, 1.0)
    key["SKG_ExposureHint"] = exposure


def main() -> int:
    frozen = load_frozen_worker()
    frozen.ASSET_ID = ASSET_ID
    frozen.set_lighting = corrected_set_lighting
    return int(frozen.main())


if __name__ == "__main__":
    raise SystemExit(main())
