from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from Scripts import blender_pre_render_quality_gate as subject


class FakeObject:
    type = "MESH"

    def __init__(self, name: str, role: str, vertices: int, polygons: int, uvs: int) -> None:
        self.name = name
        self._role = role
        self.data = SimpleNamespace(
            vertices=[None] * vertices,
            polygons=[None] * polygons,
            uv_layers=[None] * uvs,
        )
        self.material_slots = [SimpleNamespace(material=SimpleNamespace(name="MAT_Primary"))]

    def get(self, key: str):
        return self._role if key == "SKG_Role" else None


CONFIG = {
    "excluded_roles": ["measurement_authority"],
    "primary_roles": ["primary_airframe"],
    "minimum_total_renderable_vertices": 100,
    "minimum_primary_vertices": 100,
    "minimum_material_count": 1,
}


class PreRenderQualityGateTests(unittest.TestCase):
    def test_measurement_mesh_is_excluded(self) -> None:
        report = subject.inspect_objects(
            [
                FakeObject("GEO_Primary", "primary_airframe", 150, 50, 1),
                FakeObject("GEO_Measure", "measurement_authority", 4, 0, 0),
            ],
            CONFIG,
        )
        self.assertTrue(report["pass"])

    def test_enforce_writes_failure_receipt_before_raising(self) -> None:
        collection = SimpleNamespace(
            all_objects=[FakeObject("GEO_Primary", "primary_airframe", 20, 5, 0)]
        )
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "pre_render_quality.json"
            with self.assertRaises(subject.PreRenderGateError):
                subject.enforce(collection, CONFIG, receipt)
            self.assertTrue(receipt.is_file())


if __name__ == "__main__":
    unittest.main()
