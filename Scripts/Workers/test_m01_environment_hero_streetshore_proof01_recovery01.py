from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py"
WRAPPER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01_recovery01.py"
POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01_recovery01.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Recovery01ContractTests(unittest.TestCase):
    def test_frozen_worker_hash(self) -> None:
        self.assertEqual(sha256(ORIGINAL), "94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866")

    def test_wrapper_declares_three_bounded_replacements(self) -> None:
        text = WRAPPER.read_text(encoding="utf-8")
        self.assertEqual(text.count("BLENDER_EEVEE_NEXT"), 1)
        self.assertEqual(text.count('BLENDER_EEVEE"'), 1)
        self.assertIn("RECOVERY_ASSET_ID", text)
        self.assertIn("RECOVERY_GATE_ID", text)

    def test_transformed_source_compiles(self) -> None:
        text = ORIGINAL.read_text(encoding="utf-8")
        replacements = (
            ('ASSET_ID = "m01-environment-hero-streetshore-proof01"', 'ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery01"'),
            ('GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01"', 'GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01_RECOVERY01"'),
            ('scene.render.engine = "BLENDER_EEVEE_NEXT"', 'scene.render.engine = "BLENDER_EEVEE"'),
        )
        for old, new in replacements:
            self.assertEqual(text.count(old), 1)
            text = text.replace(old, new, 1)
        compile(text, "recovery01", "exec")

    def test_postflight_is_identity_only_binding(self) -> None:
        text = POSTFLIGHT.read_text(encoding="utf-8")
        self.assertIn("EXPECTED_SOURCE_SHA256", text)
        self.assertIn("ORIGINAL_ID", text)
        self.assertIn("RECOVERY_ID", text)

    def test_manifest_has_one_ready_recovery_asset(self) -> None:
        manifest = json.loads((ROOT / r"Production\production_manifest.json").read_text(encoding="utf-8"))
        assets = [a for a in manifest["assets"] if a.get("id") == "m01-environment-hero-streetshore-proof01-recovery01"]
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
