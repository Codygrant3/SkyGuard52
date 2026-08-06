from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import audit_skyguard_phase4_m01_landscape_attempt07_recovery04 as audit


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY04_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Recovery04OfflineAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )

    def test_recovery03_evidence_inventory_is_exact(self):
        immutable = self.contract["immutable_recovery03"]
        root = ROOT / immutable["root"]
        self.assertEqual(8, len(immutable["files"]))
        self.assertEqual(8, immutable["total_file_count"])
        observed_total = 0
        for item in immutable["files"].values():
            path = root / item["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(item["bytes"], path.stat().st_size)
            self.assertEqual(item["sha256"], sha256_file(path))
            observed_total += path.stat().st_size
        self.assertEqual(immutable["total_bytes"], observed_total)

    def test_recovery03_failed_only_old_palette_matcher(self):
        root, receipt, _ = audit.verify_recovery03(self.contract)
        self.assertTrue(root.is_dir())
        failed = [
            name
            for name, passed in receipt["checks"].items()
            if not passed
        ]
        self.assertEqual(["all_16_component_ids_visible"], failed)
        self.assertEqual(
            0, receipt["component_palette"]["matching_id_count"]
        )
        self.assertTrue(
            receipt["checks"][
                "all_three_phases_reached_stable_compilation_readiness"
            ]
        )

    def test_direct_linear_rgb8_audit_proves_all_components(self):
        root, receipt, _ = audit.verify_recovery03(self.contract)
        analysis = audit.analyze_component_png(
            root
            / self.contract["offline_palette_audit"][
                "component_capture_file"
            ],
            self.contract,
            receipt,
        )
        self.assertEqual(17, analysis["unique_rgb8_color_count"])
        self.assertEqual(16, analysis["component_id_count"])
        self.assertEqual(72022, analysis["nonblack_pixel_count"])
        self.assertTrue(analysis["linear_rgb8_direct_match"])
        self.assertFalse(analysis["srgb_decode_applied"])
        self.assertTrue(
            analysis["all_components_single_four_connected_regions"]
        )
        self.assertTrue(analysis["horizontal_order_valid"])
        self.assertTrue(analysis["vertical_pairing_valid"])
        self.assertLessEqual(
            analysis["maximum_to_minimum_area_ratio"], 1.02
        )

    def test_expected_palette_is_black_plus_sixteen_unique_colors(self):
        palette = audit.expected_palette()
        self.assertEqual(16, len(palette))
        self.assertEqual(16, len(set(palette.values())))
        self.assertNotIn((0, 0, 0), set(palette.values()))
        self.assertEqual((28, 85, 64), palette[0])
        self.assertEqual((227, 170, 115), palette[15])

    def test_tooling_is_offline_only(self):
        implementation = self.contract["implementation_files"]
        auditor = (
            ROOT / implementation["offline_auditor"]["file"]
        ).read_text(encoding="utf-8-sig")
        launcher = (
            ROOT / implementation["offline_launcher"]["file"]
        ).read_text(encoding="utf-8-sig")
        combined = auditor + "\n" + launcher
        for forbidden in (
            "UnrealEditor.exe",
            "Build.bat",
            "dotnet.exe",
            "ShaderCompileWorker",
            "blender.exe",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertIn(
            "--authorize-single-recovery04-offline-audit", combined
        )
        for field in (
            "unreal_launched",
            "native_build_launched",
            "recapture_performed",
            "full_capture_invoked",
            "profile_invoked",
            "promotion_allowed",
        ):
            self.assertIn(field, auditor)

    def test_implementation_hashes_and_syntax(self):
        for item in self.contract["implementation_files"].values():
            path = ROOT / item["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(item["bytes"], path.stat().st_size)
            self.assertEqual(item["sha256"], sha256_file(path))
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8-sig"))

    def test_recovery04_namespace_has_not_been_created(self):
        root = (
            ROOT / self.contract["offline_audit_execution"]["root"]
        )
        self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
