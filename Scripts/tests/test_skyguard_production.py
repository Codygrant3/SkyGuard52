from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
CONTROLLER = TEST_DIR.parent / "skyguard_production.py"
if not CONTROLLER.is_file():
    CONTROLLER = TEST_DIR / "skyguard_production.py"
SPEC = importlib.util.spec_from_file_location("skyguard_production", CONTROLLER)
assert SPEC and SPEC.loader
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class ProductionPipelineTests(unittest.TestCase):
    def test_sha256_and_atomic_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("skyguard", encoding="utf-8")
            self.assertEqual(
                PIPELINE.sha256(source),
                "b9c8934f436ed52282dc31928efd349e7f1327b1822c7094035c6c34b86bb8ea",
            )
            target = root / "receipt.json"
            PIPELINE.atomic_write_json(target, {"ok": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

    def test_transitions_reject_skipping_review(self) -> None:
        asset = {"id": "test", "status": "ready"}
        with self.assertRaises(PIPELINE.PipelineError):
            PIPELINE.transition(asset, "accepted", "not allowed")
        PIPELINE.transition(asset, "running", "launch")
        PIPELINE.transition(asset, "awaiting_review", "complete")
        PIPELINE.transition(asset, "accepted", "reviewed")
        self.assertEqual(asset["status"], "accepted")

    def test_output_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.blend").write_bytes(b"blend")
            (root / "asset.glb").write_bytes(b"glb")
            for index in range(3):
                (root / f"render_{index}.png").write_bytes(b"png")
            passed, errors = PIPELINE.output_checks(root, {"minimum_renders": 3})
            self.assertTrue(passed, errors)

    def test_duplicate_ids_fail_manifest(self) -> None:
        manifest = {
            "schema": "skyguard.production-manifest.v1",
            "project": {"root": str(PIPELINE.ROOT)},
            "policies": {"accepted_states": ["queued"]},
            "toolchain": {},
            "assets": [
                {"id": "same", "status": "queued", "priority": 1},
                {"id": "same", "status": "queued", "priority": 2},
            ],
        }
        errors = PIPELINE.validate_manifest(manifest, check_files=False)
        self.assertTrue(any("Duplicate asset ids" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
