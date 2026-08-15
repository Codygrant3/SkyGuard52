from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from Scripts import blender_hero_quality_gate as subject


class HeroQualityGateTests(unittest.TestCase):
    def _fixture(self, root: Path, *, vertices: int, luminance: int) -> tuple[Path, dict]:
        output = root / "attempt_fixture" / "output"
        renders = output / "renders"
        renders.mkdir(parents=True)
        (output / "topology.json").write_text(
            json.dumps(
                {
                    "objects": [
                        {
                            "name": "GEO_Primary",
                            "type": "MESH",
                            "role": "primary_airframe",
                            "polygons": 10,
                            "vertices": vertices,
                            "uv_layers": 1,
                            "materials": ["MAT_Primary"],
                        },
                        {
                            "name": "GEO_Measurement",
                            "type": "MESH",
                            "role": "measurement_authority",
                            "polygons": 0,
                            "vertices": 4,
                            "uv_layers": 0,
                            "materials": [],
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        Image.new("RGB", (16, 16), (luminance, luminance, luminance)).save(
            renders / "review.png"
        )
        contract = {
            "quality_gate": {
                "profile": "fixture",
                "topology": {
                    "receipt": "topology.json",
                    "excluded_roles": ["measurement_authority"],
                    "primary_roles": ["primary_airframe"],
                    "minimum_total_renderable_vertices": 100,
                    "minimum_primary_vertices": 100,
                    "minimum_material_count": 1,
                },
                "image_rules": [
                    {
                        "glob": "renders/*.png",
                        "dark_threshold": 0.02,
                        "bright_threshold": 0.95,
                        "minimum_mean_luminance": 0.03,
                        "maximum_mean_luminance": 0.85,
                        "maximum_dark_pixel_fraction": 0.97,
                        "maximum_bright_pixel_fraction": 0.20,
                    }
                ],
            }
        }
        return output.parent, contract

    def test_passes_and_excludes_nonrendering_measurement_mesh(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt, contract = self._fixture(Path(directory), vertices=150, luminance=128)
            report = subject.evaluate(attempt, contract)
            self.assertTrue(report["pass"])
            self.assertEqual(report["topology"]["missing_uvs"], [])

    def test_accumulates_sparse_geometry_and_black_frame_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt, contract = self._fixture(Path(directory), vertices=20, luminance=0)
            report = subject.evaluate(attempt, contract)
            self.assertFalse(report["pass"])
            self.assertGreaterEqual(len(report["errors"]), 3)

    def test_rejects_washed_out_frame(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt, contract = self._fixture(Path(directory), vertices=150, luminance=255)
            report = subject.evaluate(attempt, contract)
            self.assertFalse(report["pass"])
            self.assertGreater(report["images"][0]["mean_luminance"], 0.85)
            self.assertGreater(report["images"][0]["bright_pixel_fraction"], 0.20)
            self.assertIn("clipped", report["errors"][0])

    def test_region_gate_catches_black_pane_hidden_by_bright_frame(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt, contract = self._fixture(Path(directory), vertices=150, luminance=128)
            image = Image.new("RGB", (16, 16), (255, 255, 255))
            image.paste((0, 0, 0), (0, 0, 8, 16))
            image.save(attempt / "output" / "renders" / "review.png")
            contract["quality_gate"]["image_rules"] = [
                {
                    "glob": "renders/review.png",
                    "roi_normalized": [0.0, 0.0, 0.5, 1.0],
                    "dark_threshold": 0.02,
                    "minimum_mean_luminance": 0.10,
                    "maximum_mean_luminance": 0.90,
                    "maximum_dark_pixel_fraction": 0.50,
                    "maximum_bright_pixel_fraction": 0.50,
                }
            ]
            report = subject.evaluate(attempt, contract)
            self.assertFalse(report["pass"])
            self.assertEqual(report["images"][0]["roi_pixels"], [0, 0, 8, 16])
            self.assertEqual(report["images"][0]["width"], 8)
            self.assertGreater(report["images"][0]["dark_pixel_fraction"], 0.99)

    def test_region_gate_rejects_flat_midgray_pane_without_interior_variation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt, contract = self._fixture(Path(directory), vertices=150, luminance=128)
            contract["quality_gate"]["image_rules"][0].update(
                {
                    "roi_normalized": [0.25, 0.25, 0.75, 0.75],
                    "minimum_luminance_stddev": 0.05,
                }
            )
            report = subject.evaluate(attempt, contract)
            self.assertFalse(report["pass"])
            self.assertAlmostEqual(report["images"][0]["luminance_stddev"], 0.0)


if __name__ == "__main__":
    unittest.main()
