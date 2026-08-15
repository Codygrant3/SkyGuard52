from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01_recovery02.py"
POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01_recovery02.py"


class Recovery02ContractTests(unittest.TestCase):
    def test_python_sources_parse(self) -> None:
        ast.parse(WORKER.read_text(encoding="utf-8"))
        ast.parse(POSTFLIGHT.read_text(encoding="utf-8"))

    def test_frozen_authorities_are_hash_bound(self) -> None:
        text = WORKER.read_text(encoding="utf-8")
        self.assertIn("94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866", text)
        self.assertIn("b49d338c68f7c32f229ac16ed0671d9844172c0ad0c0b705bd5a5953bd5d12d3", text)

    def test_required_refinements_exist(self) -> None:
        text = WORKER.read_text(encoding="utf-8")
        for token in ("refined_build_building", "refined_add_vehicle", "refined_add_tree", "refined_build_shore_and_street", "refined_configure_condition", "refined_render_checkpoints"):
            self.assertIn(token, text)

    def test_no_external_model_loading(self) -> None:
        text = WORKER.read_text(encoding="utf-8")
        for forbidden in ("bpy.ops.import", "requests.", "http://", "https://"):
            self.assertNotIn(forbidden, text)

    def test_manifest_binding_is_unique_and_ready(self) -> None:
        manifest = json.loads((ROOT / r"Production\production_manifest.json").read_text(encoding="utf-8"))
        assets = [a for a in manifest["assets"] if a.get("id") == "m01-environment-hero-streetshore-proof01-recovery02"]
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
