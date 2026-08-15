from __future__ import annotations

import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py"
POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OfflineContractTests(unittest.TestCase):
    def test_worker_source_compiles(self) -> None:
        compile(WORKER.read_text(encoding="utf-8"), str(WORKER), "exec")

    def test_worker_has_fresh_geometry_and_pbr_contract(self) -> None:
        source = WORKER.read_text(encoding="utf-8")
        self.assertIn('"fresh_geometry": True', source)
        self.assertIn('"recovery10_mesh_reuse": False', source)
        self.assertIn('"external_model_use": False', source)
        self.assertEqual(source.count("bpy.ops.export_scene.gltf"), 1)
        self.assertEqual(source.count("bpy.ops.wm.save_as_mainfile"), 1)
        self.assertGreaterEqual(source.count("make_pbr_material("), 7)

    def test_postflight_source_compiles(self) -> None:
        compile(POSTFLIGHT.read_text(encoding="utf-8"), str(POSTFLIGHT), "exec")

    def test_glb_parser_accepts_minimal_glb2(self) -> None:
        module = load_module(POSTFLIGHT, "skyguard_proof_postflight_glb_test")
        document = json.dumps({"asset": {"version": "2.0"}, "nodes": []}, separators=(",", ":")).encode("utf-8")
        document += b" " * ((4 - len(document) % 4) % 4)
        payload = struct.pack("<I", len(document)) + struct.pack("<I", 0x4E4F534A) + document
        glb = b"glTF" + struct.pack("<II", 2, 12 + len(payload)) + payload
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.glb"
            path.write_bytes(glb)
            parsed = module.parse_glb(path)
        self.assertEqual(parsed["asset"]["version"], "2.0")

    def test_image_metrics_detect_nonblack_detail(self) -> None:
        module = load_module(POSTFLIGHT, "skyguard_proof_postflight_image_test")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.png"
            image = Image.new("RGB", (64, 64), (150, 170, 190))
            for x in range(0, 64, 4):
                for y in range(64):
                    image.putpixel((x, y), (25, 35, 45))
            image.save(path)
            metrics = module.image_metrics(path)
        self.assertEqual((metrics["width"], metrics["height"]), (64, 64))
        self.assertGreater(metrics["mean_luma_linear"], 0.05)
        self.assertGreater(metrics["edge_fraction_0_035"], 0.05)


if __name__ == "__main__":
    unittest.main()
