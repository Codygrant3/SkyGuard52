from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from verify_environment_visual_remediation01_offline import load_json, require, sha256


class OfflineHelpersTest(unittest.TestCase):
    def test_sha256_is_lowercase_and_stable(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.bin"
            path.write_bytes(b"skyguard")
            self.assertEqual(sha256(path), "b9c8934f436ed52282dc31928efd349e7f1327b1822c7094035c6c34b86bb8ea")

    def test_load_json_accepts_object(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            path.write_text('{"passed": true}\n', encoding="utf-8")
            self.assertEqual(load_json(path), {"passed": True})

    def test_load_json_rejects_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_json(path)

    def test_require_rejects_false(self) -> None:
        with self.assertRaises(AssertionError):
            require(False, "bounded failure")

    def test_require_accepts_true(self) -> None:
        require(True, "unused")


if __name__ == "__main__":
    unittest.main()
