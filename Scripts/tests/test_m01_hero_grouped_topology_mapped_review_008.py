from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = (
    ROOT
    / "Scripts"
    / "blender_m01_hero_grouped_topology_mapped_review_008.py"
)
MANIFEST = (
    ROOT
    / "Saved"
    / "Reports"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_MANIFEST_008.json"
)
ATTEMPT = (
    ROOT
    / "Saved"
    / "BuildAttempts"
    / "M01_HERO_GROUPED_TOPOLOGY_008"
    / "attempt_20260802T161843676Z"
)
DIRECT_RECEIPT = ATTEMPT / "direct_original_resolution_map_review_receipt.json"
OUTPUT_ROOT = ATTEMPT / "mapped_mesh_review_attempt_02"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MappedMeshReview008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SCRIPT.read_text(encoding="utf-8-sig")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        cls.receipt = json.loads(
            DIRECT_RECEIPT.read_text(encoding="utf-8-sig")
        )

    def test_01_script_parses(self) -> None:
        ast.parse(self.source, filename=str(SCRIPT))

    def test_02_direct_map_gate_is_green(self) -> None:
        self.assertEqual(self.receipt["overall_gate"], "PASS")
        self.assertEqual(self.receipt["reviewed_corrective_map_count"], 6)
        self.assertEqual(self.receipt["pass_count"], 6)
        self.assertEqual(self.receipt["fail_count"], 0)
        self.assertTrue(self.receipt["mapped_mesh_review_authorized"])
        self.assertFalse(self.receipt["unreal_import_authorized"])

    def test_03_master_and_manifest_are_hash_verified(self) -> None:
        self.assertEqual(
            self.manifest["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
        )
        master = Path(self.manifest["outputs"]["master_blend"]["path"])
        self.assertTrue(master.is_file())
        self.assertEqual(
            sha256(master),
            self.manifest["outputs"]["master_blend"]["sha256"],
        )
        self.assertEqual(
            sha256(MANIFEST),
            "57bc413b867090d798ed8ec1fb8d39d5955fffcb2901bd9355fbfe0e49b3a102",
        )

    def test_04_all_twenty_four_maps_are_hash_verified(self) -> None:
        maps = [
            item
            for asset in self.manifest["assets"]
            for group in asset["groups"]
            for item in group["maps"]
        ]
        self.assertEqual(len(maps), 24)
        for item in maps:
            path = Path(item["path"])
            self.assertTrue(path.is_file())
            self.assertEqual(sha256(path), item["sha256"])

    def test_05_script_has_no_bake_save_or_unreal_operation(self) -> None:
        for forbidden in (
            "bpy.ops.object.bake",
            "bpy.ops.wm.save_as_mainfile",
            "bpy.ops.wm.save_mainfile",
            "UnrealEditor",
            "subprocess",
        ):
            self.assertNotIn(forbidden, self.source)
        self.assertIn('"canonical_map_write_count": 0', self.source)
        self.assertIn('"bake_operation_count": 0', self.source)
        self.assertIn('"master_save_count": 0', self.source)

    def test_06_exact_three_assets_three_views(self) -> None:
        self.assertIn(
            'REQUIRED_ASSETS = {"Pathfinder", "Lighthouse", "RadarPost"}',
            self.source,
        )
        self.assertIn('"three_quarter"', self.source)
        self.assertIn('"grazing_port"', self.source)
        self.assertIn('"grazing_starboard"', self.source)
        self.assertIn('"preview_count": len(preview_records)', self.source)

    def test_07_material_uses_governed_normal_and_ao_maps(self) -> None:
        self.assertIn('normal_image.colorspace_settings.name = "Non-Color"', self.source)
        self.assertIn('ao_image.colorspace_settings.name = "Non-Color"', self.source)
        self.assertIn('nodes.new("ShaderNodeNormalMap")', self.source)
        self.assertIn('multiply.blend_type = "MULTIPLY"', self.source)
        self.assertIn("verify_map_evidence(group)", self.source)

    def test_08_output_is_attempt_local_and_prelaunch_absent(self) -> None:
        self.assertFalse(OUTPUT_ROOT.exists())
        self.assertIn(
            "output_root = attempt / args.review_attempt",
            self.source,
        )
        self.assertIn(
            "Mapped-review output already exists; refusing overwrite",
            self.source,
        )

    def test_09_blender52_uses_supported_eevee_enum(self) -> None:
        self.assertIn(
            'scene.render.engine = "BLENDER_EEVEE"',
            self.source,
        )
        self.assertNotIn("BLENDER_EEVEE_NEXT", self.source)
        self.assertIn(
            'default="mapped_mesh_review_attempt_02"',
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
