from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
SDK_PATH = TEST_DIR.parent / "skyguard_blender_worker_sdk.py"
if not SDK_PATH.is_file():
    SDK_PATH = TEST_DIR / "skyguard_blender_worker_sdk.py"
SPEC = importlib.util.spec_from_file_location("skyguard_blender_worker_sdk", SDK_PATH)
assert SPEC and SPEC.loader
SDK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SDK)


class BlenderWorkerSdkTests(unittest.TestCase):
    def test_parse_worker_args(self) -> None:
        args = SDK.parse_worker_args(
            ["blender", "--background", "--", "--output", "C:\\tmp\\out", "--asset-id", "asset"]
        )
        self.assertEqual(args.output, "C:\\tmp\\out")
        self.assertEqual(args.asset_id, "asset")

    def test_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.bin"
            path.write_bytes(b"skyguard")
            self.assertEqual(
                SDK.sha256(path),
                "b9c8934f436ed52282dc31928efd349e7f1327b1822c7094035c6c34b86bb8ea",
            )

    def test_socket_prefix_rejected_before_bpy_access(self) -> None:
        with self.assertRaises(SDK.WorkerError):
            SDK.create_socket("Origin", (0.0, 0.0, 0.0), None)

    def test_blender_only_api_is_lazy(self) -> None:
        with self.assertRaises(SDK.WorkerError):
            SDK.blender_module()


if __name__ == "__main__":
    unittest.main()
