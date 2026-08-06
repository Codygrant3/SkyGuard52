from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_acceptance_008.py"
BUILDER_PATH = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_candidate_008.py"
VERIFIER_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_candidate_008.py"
RUNNER_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_acceptance_008.ps1"
MAPPED_CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_views_008.py"
MAPPED_RUNNER_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_view_capture_008.ps1"
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_CONTRACT.json"

SPEC = importlib.util.spec_from_file_location("grouped008_unreal_audit", AUDIT_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(AUDIT)


class GroupedTopologyUnrealAcceptance008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8-sig")
        cls.verifier = VERIFIER_PATH.read_text(encoding="utf-8-sig")
        cls.runner = RUNNER_PATH.read_text(encoding="utf-8-sig")

    def test_01_offline_readiness_passes(self):
        report = AUDIT.audit_source(write_report=False)
        self.assertEqual(
            report["gate"],
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_AUTHORIZATION",
            [item for item in report["checks"] if not item["passed"]],
        )
        self.assertFalse(report["unreal_launched"])
        self.assertFalse(report["promotion_allowed"])

    def test_02_candidate_namespace_isolated_and_non_overwriting(self):
        unreal = self.contract["unreal"]
        self.assertIn("/Candidates/", unreal["candidate_root"])
        self.assertTrue(unreal["must_start_empty"])
        self.assertFalse(unreal["replace_existing"])
        self.assertFalse(unreal["runtime_map_change_allowed"])
        self.assertFalse(unreal["config_change_allowed"])
        self.assertIn("replace_existing = False", self.builder)
        self.assertNotIn("replace_existing = True", self.builder)
        self.assertIn("candidate root is non-empty", self.builder)

    def test_03_exact_mesh_map_and_material_contract(self):
        self.assertEqual(self.contract["mesh_policy"]["expected_mesh_count"], 12)
        self.assertEqual(len(self.contract["mesh_targets"]), 12)
        self.assertIn("len(map_records) == 24", AUDIT_PATH.read_text(encoding="utf-8-sig"))
        self.assertIn("one_candidate_material_per_group", json.dumps(self.contract))

    def test_04_texture_interpretation_is_explicit(self):
        policy = self.contract["texture_policy"]
        self.assertFalse(policy["normal"]["srgb"])
        self.assertEqual(policy["normal"]["compression"], "TC_NORMALMAP")
        self.assertTrue(policy["normal"]["flip_green_channel"])
        self.assertEqual(policy["ao"]["compression"], "TC_MASKS")
        for token in ("TC_NORMALMAP", "TC_MASKS", "flip_green_channel"):
            self.assertIn(token, self.builder)
            self.assertIn(token, self.verifier)

    def test_05_normal_and_ao_are_material_bound(self):
        self.assertIn("MP_NORMAL", self.builder)
        self.assertIn("MP_AMBIENT_OCCLUSION", self.builder)
        self.assertIn('mesh.set_material(index, material)', self.builder)
        self.assertIn("material_bindings", self.verifier)

    def test_06_scale_collision_and_nanite_are_gated(self):
        self.assertEqual(
            self.contract["mesh_policy"]["scale"]["maximum_dimension_relative_error"],
            0.02,
        )
        self.assertEqual(
            self.contract["mesh_policy"]["nanite"]["enabled_groups"],
            ["RadarPost/DishFeed"],
        )
        self.assertEqual(len(self.contract["mesh_policy"]["collision"]), 12)
        for token in ("add_simple_collisions", "nanite_settings", "maximum_dimension_relative_error"):
            self.assertIn(token, self.builder + self.verifier)

    def test_07_fresh_process_and_mapped_view_remain_required(self):
        acceptance = self.contract["acceptance"]
        self.assertTrue(acceptance["fresh_process_persistence_required"])
        self.assertTrue(acceptance["comparison_requires_original_resolution"])
        self.assertFalse(acceptance["promotion_allowed_on_pass"])
        self.assertIn("fresh_persistence", self.runner)
        self.assertIn("AWAITING_MAPPED_VIEW_REVIEW", self.runner)

    def test_08_rollback_is_candidate_only_and_non_destructive(self):
        rollback = self.contract["rollback"]
        self.assertEqual(rollback["scope"], "candidate_root_only")
        self.assertFalse(rollback["automatic_delete_on_failure"])
        self.assertFalse(rollback["runtime_asset_deletion_allowed"])
        self.assertNotIn("/Game/Skyguard/Maps", self.builder + self.verifier + self.runner)

    def test_09_supervisor_is_serialized_and_never_builds_or_launches_blender(self):
        self.assertIn("WaitForExit", self.runner)
        self.assertIn("ACTIVE_TIMEOUT_WAIT_NEVER_DUPLICATE", self.runner)
        self.assertIn("ShaderCompileWorker.exe", self.runner)
        self.assertIn("blender.exe", self.runner)
        self.assertNotIn("Build.bat", self.runner)
        self.assertNotIn("Start-Process -FilePath $Blender", self.runner)
        self.assertNotIn("-ExecCmds=Automation", self.runner)

    def test_10_python_sources_parse_without_importing_unreal(self):
        ast.parse(BUILDER_PATH.read_text(encoding="utf-8-sig"), filename=str(BUILDER_PATH))
        ast.parse(VERIFIER_PATH.read_text(encoding="utf-8-sig"), filename=str(VERIFIER_PATH))
        ast.parse(AUDIT_PATH.read_text(encoding="utf-8-sig"), filename=str(AUDIT_PATH))

    def test_11_offline_auditor_cannot_launch_heavy_tools(self):
        text = AUDIT_PATH.read_text(encoding="utf-8-sig")
        tree = ast.parse(text, filename=str(AUDIT_PATH))
        imports = {
            node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertNotIn("subprocess", imports)
        self.assertNotIn("bpy", imports)
        self.assertNotIn("unreal", imports)

    def test_12_promotion_and_p3_4_remain_false(self):
        for text in (self.builder, self.verifier, self.runner):
            self.assertIn("promotion_allowed", text)
            self.assertIn("p3_4_closed", text)
        self.assertFalse(self.contract["unreal"]["automatic_promotion"])

    def test_13_collision_has_commandlet_safe_fallback(self):
        self.assertIn("if subsystem is not None:", self.builder)
        self.assertIn('getattr(unreal, "EditorStaticMeshLibrary", None)', self.builder)
        self.assertIn("legacy.remove_collisions(mesh)", self.builder)
        self.assertIn("add_collision = legacy.add_simple_collisions", self.builder)
        self.assertIn("no commandlet-safe static-mesh collision API", self.builder)

    def test_14_none_collision_is_force_cleared_and_asserted(self):
        self.assertIn("def force_clear_simple_collision(mesh)", self.builder)
        self.assertIn('aggregate.set_editor_property(field, [])', self.builder)
        self.assertIn("primitive_count = simple_collision_count(mesh)", self.builder)
        self.assertIn("NONE collision policy retained simple primitives", self.builder)

    def test_15_verifier_normalizes_object_paths_to_package_paths(self):
        self.assertIn("def package_path(path:", self.verifier)
        self.assertIn('path.rsplit(".", 1)[0]', self.verifier)
        self.assertIn("package_path(material_path(mesh, index))", self.verifier)
        self.assertIn('expected_material = package_path(record["material"])', self.verifier)

    def test_16_positive_collision_count_is_fresh_process_authority(self):
        self.assertIn(
            "only NONE is synchronous",
            self.builder,
        )
        self.assertIn("legacy facade can return -1", self.builder)
        self.assertIn("return int(result)", self.builder)
        self.assertNotIn("int(result) < 0 or primitive_count <= 0", self.builder)
        self.assertNotIn("if int(result) < 0:", self.builder)

    def test_17_mapped_capture_is_exactly_nine_original_resolution_views(self):
        capture = MAPPED_CAPTURE_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("RESOLUTION = (2048, 2048)", capture)
        self.assertIn(
            'VIEWS = ("three_quarter", "grazing_port", "grazing_starboard")',
            capture,
        )
        self.assertIn("if len(records) != 9:", capture)
        self.assertIn("unreal.SceneCapture2D", capture)
        self.assertIn("export_render_target", capture)

    def test_18_mapped_capture_is_read_only_and_hash_bound(self):
        capture = MAPPED_CAPTURE_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("EXPECTED_PERSISTENCE_SHA256", capture)
        self.assertIn("candidate package hashes changed", capture)
        self.assertIn('"world_saved": False', capture)
        self.assertIn('"package_save_invoked": False', capture)
        self.assertNotIn("save_current_level", capture)
        self.assertNotIn("save_directory", capture)

    def test_19_mapped_capture_requires_real_gpu_and_bound_blender_previews(self):
        capture = MAPPED_CAPTURE_PATH.read_text(encoding="utf-8-sig")
        runner = MAPPED_RUNNER_PATH.read_text(encoding="utf-8-sig")
        self.assertIn('EXPECTED_RHI = "D3D12|SM6"', capture)
        self.assertIn("mapped_mesh_review_attempt_02", capture)
        self.assertIn("blender_reference_sha256", capture)
        self.assertIn('"-d3d12"', runner)
        self.assertIn('"-sm6"', runner)
        self.assertNotIn("-NullRHI", runner)


if __name__ == "__main__":
    unittest.main()
