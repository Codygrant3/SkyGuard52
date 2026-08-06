from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
DIAGNOSIS_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_DIAGNOSIS.json"
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
BUILDER_PATH = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_exposure.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("attempt03_audit", AUDIT_PATH)
SELECTOR = load_module("attempt03_selector", SELECTOR_PATH)


class GroupedTopologyUnrealMappedAttempt03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.diagnosis = json.loads(DIAGNOSIS_PATH.read_text(encoding="utf-8-sig"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8-sig")
        cls.capture = CAPTURE_PATH.read_text(encoding="utf-8-sig")
        cls.selector = SELECTOR_PATH.read_text(encoding="utf-8-sig")

    def test_01_offline_readiness_passes(self):
        report = AUDIT.audit(write_report=False)
        self.assertEqual(
            report["gate"],
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_ATTEMPT03_AUTHORIZATION",
            report["failures"],
        )
        self.assertFalse(report["unreal_launched"])
        self.assertFalse(report["blender_launched"])
        self.assertEqual(report["content_packages_created_or_modified"], 0)

    def test_02_diagnosis_numerically_distinguishes_dark_and_clipped(self):
        attempts = {
            item["attempt_id"]: item
            for item in self.diagnosis["exposure_diagnosis"]["attempts"]
        }
        self.assertLess(
            attempts["mapped_view_capture_01"]["mean_active_p50"],
            25.0,
        )
        self.assertGreater(
            attempts["mapped_view_capture_02"]["mean_active_clipped_fraction"],
            0.25,
        )

    def test_03_exact_glb_derived_transform_set(self):
        actors = self.contract["assembly"]["actors"]
        self.assertEqual(len(actors), 12)
        by_key = {item["key"]: item for item in actors}
        self.assertEqual(
            by_key["Lighthouse/WhiteTower"]["relative_location_cm"],
            [0.0, 0.0, 1000.0],
        )
        self.assertEqual(
            by_key["Lighthouse/LanternGlass"]["relative_location_cm"],
            [0.0, 0.0, 2170.000076],
        )
        self.assertEqual(
            by_key["RadarPost/BlastDoor"]["relative_location_cm"],
            [-509.000015, 0.0, 154.999995],
        )
        self.assertEqual(
            by_key["RadarPost/DishFeed"]["relative_location_cm"],
            [-76.012039, 0.0, 1700.0],
        )

    def test_04_builder_creates_only_new_review_map(self):
        self.assertIn("new_level(review_map)", self.builder)
        self.assertIn("save_current_level", self.builder)
        for forbidden in (
            "import_asset_tasks",
            "rename_asset",
            "delete_asset",
            "save_loaded_asset",
            "set_material",
            'set_editor_property("nanite_settings"',
        ):
            self.assertNotIn(forbidden, self.builder)
        self.assertIn("attempt03_new_package_count", self.builder)

    def test_05_single_process_sweep_is_exactly_63(self):
        sweep = self.contract["exposure_sweep"]
        self.assertTrue(sweep["single_unreal_process"])
        self.assertEqual(sweep["pilot_capture_count"], 63)
        self.assertEqual(
            len(sweep["manual_exposure_bias_candidates_ev"])
            * len(sweep["families"])
            * len(sweep["views_per_family"]),
            63,
        )
        self.assertIn("AEM_MANUAL", self.capture)
        self.assertIn("post_process_settings", self.capture)
        self.assertNotIn("save_current_level", self.capture)

    def test_06_selector_requires_one_global_ev_to_pass_all_nine(self):
        self.assertIn("all_nine_hard_bounds_passed", self.selector)
        self.assertIn("len(records) != 9", self.selector)
        self.assertIn("shutil.copyfile", self.selector)
        self.assertTrue(
            self.contract["exposure_sweep"]["one_global_bias_for_all_views"]
        )

    def test_07_selector_hard_bounds_reject_clipping(self):
        policy = self.contract["exposure_sweep"]["selector"]
        good = {
            "active_clipped_fraction": 0.005,
            "active_p50": 120.0,
            "active_p95": 220.0,
            "active_dynamic_range": 120.0,
        }
        clipped = dict(good, active_clipped_fraction=0.35)
        passed, failures, _penalty = SELECTOR.metric_result(good, policy)
        self.assertTrue(passed)
        self.assertEqual(failures, [])
        passed, failures, _penalty = SELECTOR.metric_result(clipped, policy)
        self.assertFalse(passed)
        self.assertIn("active_clipped_fraction", failures)

    def test_08_attempt03_does_not_authorize_promotion(self):
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertFalse(
            self.contract["acceptance"]["promotion_allowed_on_pass"]
        )
        self.assertFalse(
            self.contract["acceptance"]["p3_4_closed_on_pass"]
        )

    def test_09_python_sources_parse(self):
        for path in (AUDIT_PATH, BUILDER_PATH, CAPTURE_PATH, SELECTOR_PATH):
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))

    def test_10_offline_scripts_cannot_launch_heavy_tools(self):
        for path in (AUDIT_PATH, SELECTOR_PATH):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            imports = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            } | {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            self.assertNotIn("subprocess", imports)
            self.assertNotIn("unreal", imports)
            self.assertNotIn("bpy", imports)


if __name__ == "__main__":
    unittest.main()
