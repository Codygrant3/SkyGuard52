from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_003_CONTRACT.json"
)
GENERATOR_PATH = (
    ROOT / "Scripts" / "blender_m01_hero_grouped_topology_bake.py"
)
VERIFIER_PATH = (
    ROOT
    / "Scripts"
    / "verify_skyguard_m01_hero_grouped_topology_bake.py"
)
SUPERVISOR_PATH = (
    ROOT
    / "Scripts"
    / "run_m01_hero_grouped_topology_bake_003.ps1"
)
CONTRACT_004_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_004_CONTRACT.json"
)
CONTRACT_005_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_005_CONTRACT.json"
)
CONTRACT_006_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_006_CONTRACT.json"
)
CONTRACT_007_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_007_CONTRACT.json"
)
CLASSIFIER_PATH = (
    ROOT / "Scripts" / "analyze_m01_grouped_topology_006.py"
)
CLASSIFICATION_PATH = (
    ROOT
    / "Saved"
    / "Reports"
    / "M01_HERO_GROUPED_TOPOLOGY_CLASSIFICATION_007.json"
)

SPEC = importlib.util.spec_from_file_location(
    "grouped_topology_verifier",
    VERIFIER_PATH,
)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class GroupedTopologyBakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        cls.contract, _ = VERIFIER.load_effective_contract(
            CONTRACT_007_PATH,
            ROOT,
        )
        cls.generator = GENERATOR_PATH.read_text(encoding="utf-8-sig")
        cls.supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")

    def test_source_gate_passes(self) -> None:
        report = VERIFIER.evaluate_source(
            self.contract,
            CONTRACT_007_PATH,
            GENERATOR_PATH,
            ROOT,
        )
        self.assertEqual(report["gate"], "PASS", report["errors"])
        self.assertTrue(all(report["checks"].values()))

    def test_004_overlay_remains_hash_bound_failed_evidence(self) -> None:
        contract, base_path = VERIFIER.load_effective_contract(
            CONTRACT_004_PATH,
            ROOT,
        )
        self.assertEqual(
            contract["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_004",
        )
        self.assertEqual(base_path, CONTRACT_PATH)

    def test_005_overlay_is_hash_bound_and_source_ready(self) -> None:
        contract, base_path = VERIFIER.load_effective_contract(
            CONTRACT_005_PATH,
            ROOT,
        )
        self.assertEqual(
            contract["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_005",
        )
        self.assertEqual(base_path, CONTRACT_PATH)
        report = VERIFIER.evaluate_source(
            contract,
            CONTRACT_005_PATH,
            GENERATOR_PATH,
            ROOT,
        )
        self.assertEqual(report["gate"], "PASS", report["errors"])

    def test_006_overlay_is_hash_bound_and_source_ready(self) -> None:
        contract, base_path = VERIFIER.load_effective_contract(
            CONTRACT_006_PATH,
            ROOT,
        )
        self.assertEqual(
            contract["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_006",
        )
        self.assertEqual(base_path, CONTRACT_PATH)
        report = VERIFIER.evaluate_source(
            contract,
            CONTRACT_006_PATH,
            GENERATOR_PATH,
            ROOT,
        )
        self.assertEqual(report["gate"], "PASS", report["errors"])

    def test_007_overlay_is_hash_bound_and_source_ready(self) -> None:
        contract, base_path = VERIFIER.load_effective_contract(
            CONTRACT_007_PATH,
            ROOT,
        )
        self.assertEqual(
            contract["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
        )
        self.assertEqual(base_path, CONTRACT_PATH)
        report = VERIFIER.evaluate_source(
            contract,
            CONTRACT_007_PATH,
            GENERATOR_PATH,
            ROOT,
        )
        self.assertEqual(report["gate"], "PASS", report["errors"])

    def test_rejected_candidates_are_preserved(self) -> None:
        self.assertEqual(
            self.contract["supersedes_candidates"],
            [
                "BLD_M01_HERO_HILO_001",
                "BLD_M01_HERO_HILO_002",
                "BLD_M01_HERO_GROUPED_TOPOLOGY_003",
                "BLD_M01_HERO_GROUPED_TOPOLOGY_004",
                "BLD_M01_HERO_GROUPED_TOPOLOGY_005",
                "BLD_M01_HERO_GROUPED_TOPOLOGY_006",
            ],
        )
        self.assertIn(
            "006_FAILURE_REVIEW",
            self.contract["attempt_correction_basis"],
        )
        self.assertTrue(
            all(
                "007" in value
                or "HeroGroupedTopology_007" in value
                for value in self.contract["outputs"].values()
            )
        )

    def test_twelve_semantic_groups_are_governed(self) -> None:
        groups = [
            group
            for asset in self.contract["assets"]
            for group in asset["groups"]
        ]
        self.assertEqual(len(groups), 12)
        self.assertEqual(
            [len(asset["groups"]) for asset in self.contract["assets"]],
            [4, 4, 4],
        )

    def test_source_material_partition_is_exact_and_disjoint(self) -> None:
        for asset in self.contract["assets"]:
            memberships = [
                material
                for group in asset["groups"]
                for material in group["materials"]
            ]
            self.assertEqual(
                set(memberships),
                set(asset["required_source_materials"]),
            )
            self.assertEqual(len(memberships), len(set(memberships)))

    def test_group_object_names_are_globally_unique(self) -> None:
        names = [
            group[key]
            for asset in self.contract["assets"]
            for group in asset["groups"]
            for key in ("low_object", "high_object", "cage_object")
        ]
        self.assertEqual(len(names), 36)
        self.assertEqual(len(names), len(set(names)))

    def test_group_projection_is_tightly_bounded(self) -> None:
        for asset in self.contract["assets"]:
            for group in asset["groups"]:
                self.assertGreater(group["cage_extrusion_m"], 0.0)
                self.assertGreater(
                    group["max_ray_distance_m"],
                    group["cage_extrusion_m"],
                )
                self.assertLessEqual(group["max_ray_distance_m"], 0.04)
                self.assertLess(
                    group["bevel_width_m"],
                    group["cage_extrusion_m"],
                )

    def test_uv_policy_repacks_connected_charts_and_authors_seams(self) -> None:
        uv = self.contract["topology_contract"]["uv_authoring"]
        self.assertTrue(uv["smart_project_forbidden"])
        self.assertNotIn("bpy.ops.uv.smart_project", self.generator)
        self.assertNotIn("bpy.ops.uv.unwrap(", self.generator)
        self.assertIn("def mark_uv_chart_seams(", self.generator)
        self.assertIn('obj.data.uv_layers.get("UV_M01_AAA_0")', self.generator)
        self.assertIn("bpy.ops.uv.average_islands_scale()", self.generator)
        self.assertIn("bpy.ops.uv.pack_islands(", self.generator)

    def test_smoothing_and_cage_are_authored_per_group(self) -> None:
        self.assertIn("def author_smoothing(", self.generator)
        self.assertIn("def make_normal_offset_cage(", self.generator)
        self.assertIn("def ensure_high_density(", self.generator)
        self.assertIn("edge.smooth = not sharp", self.generator)
        self.assertIn("vertex.co += normal.normalized() * extrusion", self.generator)

    def test_partition_face_normals_are_recalculated_before_bake(self) -> None:
        normals = self.contract["topology_contract"][
            "face_normal_authoring"
        ]
        self.assertEqual(
            normals["method"],
            "bmesh_recalc_face_normals_per_partition",
        )
        self.assertTrue(
            normals["low_after_topology_repair_before_smoothing"]
        )
        self.assertTrue(normals["high_after_bevel_or_subdivision"])
        self.assertFalse(normals["zero_normal_faces_allowed"])
        self.assertIn(
            "def author_consistent_face_normals(",
            self.generator,
        )
        self.assertLess(
            self.generator.index(
                "low_face_orientation = author_consistent_face_normals(low)"
            ),
            self.generator.index("smoothing = author_smoothing("),
        )

    def test_offline_classifier_is_hash_bound_and_never_launches_dcc(self) -> None:
        classifier = CLASSIFIER_PATH.read_text(encoding="utf-8-sig")
        classification = json.loads(
            CLASSIFICATION_PATH.read_text(encoding="utf-8-sig")
        )
        self.assertNotIn("import bpy", classifier)
        self.assertNotIn("subprocess", classifier)
        self.assertEqual(classification["gate"], "PASS")
        self.assertEqual(classification["group_count"], 12)
        self.assertEqual(
            classification["analysis_mode"],
            "offline_glb_only_no_blender_no_unreal",
        )
        self.assertEqual(
            classification["summary"]["degenerate_groups"],
            1,
        )
        self.assertEqual(
            classification["summary"]["nonmanifold_groups"],
            1,
        )
        self.assertEqual(
            classification["summary"]["ao_failed_groups"],
            7,
        )
        self.assertEqual(
            classification["summary"]["dedicated_ao_occluder_groups"],
            9,
        )

    def test_build007_repairs_and_ao_policies_are_explicit(self) -> None:
        repair = self.contract["topology_repair_contract"]
        policies = repair["group_policies"]
        self.assertEqual(len(policies), 12)
        self.assertTrue(
            policies["Pathfinder/AccessPanels"]["remove_zero_area_faces"]
        )
        self.assertTrue(
            policies["Pathfinder/PaintShell"]["split_nonmanifold_edges"]
        )
        self.assertEqual(
            sum(
                item["ao_policy"] == "direct_low_self_occlusion"
                for item in policies.values()
            ),
            3,
        )
        self.assertEqual(
            sum(
                item["ao_policy"]
                == "selected_to_active_from_dedicated_bounded_ao_occluder"
                for item in policies.values()
            ),
            9,
        )
        self.assertIn("def repair_partition_topology(", self.generator)
        self.assertIn("def isolate_render_meshes(", self.generator)
        self.assertIn(
            'obj.hide_render = obj.name not in visible',
            self.generator,
        )

    def test_bakes_are_selected_to_active_and_group_isolated(self) -> None:
        bake = self.contract["bake_contract"]
        self.assertTrue(bake["selected_to_active"])
        self.assertTrue(bake["group_isolation_required"])
        self.assertTrue(bake["explicit_cage_required"])
        self.assertIn("bake.use_selected_to_active = True", self.generator)
        self.assertIn("bake.cage_object = cage", self.generator)
        self.assertIn("select_only([high, low], low)", self.generator)
        self.assertIn('if map_type == "AO":', self.generator)
        self.assertIn("bake.use_selected_to_active = False", self.generator)
        self.assertIn("select_only([low], low)", self.generator)

    def test_neutral_background_is_preserved(self) -> None:
        self.assertTrue(
            self.contract["bake_contract"]["preserve_neutral_background"]
        )
        self.assertIn(
            "scene.render.bake.use_clear = False",
            self.generator,
        )
        maps = {
            item["type"]: item
            for item in self.contract["bake_contract"]["maps"]
        }
        self.assertEqual(maps["Normal"]["neutral_background"], [0.5, 0.5, 1.0])
        self.assertEqual(maps["AO"]["neutral_background"], [1.0, 1.0, 1.0])

    def test_twenty_four_map_contract_is_enforced(self) -> None:
        self.assertIn("if len(all_map_hashes) != 24:", self.generator)
        self.assertIn("if len(all_low_objects) != 12:", self.generator)
        self.assertIn(
            '"twenty_four_maps"',
            VERIFIER_PATH.read_text(encoding="utf-8-sig"),
        )

    def test_readiness_is_fail_closed_before_blender(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_manifest = Path(temp_dir) / "missing.json"
            report = VERIFIER.build_report(
                self.contract,
                CONTRACT_007_PATH,
                GENERATOR_PATH,
                missing_manifest,
                ROOT,
            )
        self.assertEqual(report["gate"], "PASS_WITH_GAPS")
        self.assertEqual(
            report["terminal_state"],
            "GROUPED_SOURCE_READY_BLENDER_NOT_RUN",
        )
        self.assertFalse(report["p3_4_closed"])
        self.assertEqual(
            report["direct_original_resolution_map_review"],
            "NOT_RUN",
        )

    def test_supervisor_refuses_overlap_and_overwrite(self) -> None:
        self.assertIn(
            'Get-Process -Name "blender"',
            self.supervisor,
        )
        self.assertIn(
            "is immutable and already has canonical output(s)",
            self.supervisor,
        )
        self.assertIn(
            "Refusing to overlap the exclusive heavy lane",
            self.supervisor,
        )
        self.assertIn(
            "emitted a Python traceback despite Blender exit 0",
            self.supervisor,
        )

    def test_supervisor_persists_attempt_specific_evidence(self) -> None:
        for token in (
            "blender.stdout.log",
            "blender.stderr.log",
            "blender.pid",
            "source_verification.json",
            "artifact_verification.json",
            "SHA256SUMS.json",
            "supervisor_summary.json",
            "direct_map_review_queue.json",
        ):
            self.assertIn(token, self.supervisor)
        self.assertIn(
            "$contractData.classification_report",
            self.supervisor,
        )

    def test_no_promotion_before_direct_map_review(self) -> None:
        self.assertIn(
            "requires_direct_original_resolution_map_review",
            self.contract["promotion"],
        )
        self.assertIn(
            'direct_original_resolution_map_review = "NOT_REVIEWED"',
            self.supervisor,
        )
        self.assertIn(
            "promotion_authorized = $false",
            self.supervisor,
        )
        self.assertIn("p3_4_closed = $false", self.supervisor)


if __name__ == "__main__":
    unittest.main()
