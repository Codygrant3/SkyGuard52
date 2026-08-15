from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "Scripts" / "Workers" / "worker_core_yak52_airframe_refinement01_recovery01.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("airframe_recovery01", WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery01 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LightData:
    def __init__(self):
        self.energy = 0.0
        self.color = (0.0, 0.0, 0.0)


class LightObject:
    def __init__(self):
        self.data = LightData()
        self.properties = {}

    def __setitem__(self, key, value):
        self.properties[key] = value


class World:
    color = (0.0, 0.0, 0.0)


class Recovery01ContractTests(unittest.TestCase):
    def test_all_profiles_write_energy_to_light_data(self):
        module = load_wrapper()
        expected = {
            "daylight": (1750.0, 720.0, 850.0),
            "overcast": (1050.0, 900.0, 500.0),
            "night": (640.0, 280.0, 1050.0),
            "wet": (1350.0, 620.0, 1100.0),
            "cockpit": (800.0, 360.0, 700.0),
        }
        for profile, energies in expected.items():
            key, fill, rim, world = LightObject(), LightObject(), LightObject(), World()
            module.corrected_set_lighting(profile, key, fill, rim, world)
            self.assertEqual((key.data.energy, fill.data.energy, rim.data.energy), energies)
            self.assertIn("SKG_ExposureHint", key.properties)

    def test_wrapper_preserves_frozen_worker(self):
        module = load_wrapper()
        self.assertEqual(module.ASSET_ID, "core-yak52-airframe-recovery01")
        self.assertTrue(module.LEGACY_PATH.is_file())
        self.assertEqual(
            module.LEGACY_PATH.stat().st_size,
            21715,
        )

    def test_source_contains_no_object_energy_write(self):
        source = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("key.data.energy = key_energy", source)
        self.assertIn("fill.data.energy = fill_energy", source)
        self.assertIn("rim.data.energy = rim_energy", source)
        self.assertNotIn("exposure, key.energy", source)


if __name__ == "__main__":
    unittest.main()
