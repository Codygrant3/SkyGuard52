from __future__ import annotations

import ast
import hashlib
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
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_008_CONTRACT.json"
)
GENERATOR_PATH = (
    ROOT / "Scripts" / "blender_m01_hero_grouped_topology_bake_008.py"
)
VERIFIER_PATH = (
    ROOT
    / "Scripts"
    / "verify_skyguard_m01_hero_grouped_topology_bake_008.py"
)
SUPERVISOR_PATH = (
    ROOT / "Scripts" / "run_m01_hero_grouped_topology_bake_008.ps1"
)
ANALYZER_PATH = (
    ROOT / "Scripts" / "analyze_m01_grouped_topology_007_visual_failures.py"
)
CLASSIFICATION_PATH = (
    ROOT
    / "Saved"
    / "Reports"
    / "M01_HERO_GROUPED_TOPOLOGY_VISUAL_FAILURE_CLASSIFICATION_008.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


SPEC = importlib.util.spec_from_file_location(
    "grouped_topology_verifier_008",
    VERIFIER_PATH,
)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class GroupedTopologyBake008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.contract, cls.base_contract_path = VERIFIER.load_effective_contract(
            CONTRACT_PATH,
            ROOT,
        )
        cls.generator = GENERATOR_PATH.read_text(encoding="utf-8-sig")
        cls.verifier = VERIFIER_PATH.read_text(encoding="utf-8-sig")
        cls.supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
        cls.analyzer = ANALYZER_PATH.read_text(encoding="utf-8-sig")
        cls.classification = json.loads(
            CLASSIFICATION_PATH.read_text(encoding="utf-8-sig")
        )

    def test_01_source_gate_passes_every_check(self) -> None:
        report = VERIFIER.evaluate_source(
            self.contract,
            CONTRACT_PATH,
            GENERATOR_PATH,
            ROOT,
        )
        self.assertEqual(report["gate"], "PASS", report["errors"])
        self.assertTrue(all(report["checks"].values()))

    def test_02_build007_evidence_is_hash_bound_and_unchanged(self) -> None:
        corrective = self.contract["corrective_map_contract"]
        source_manifest = resolve(corrective["source_manifest"])
        source_receipt = resolve(corrective["source_review_receipt"])
        self.assertEqual(
            sha256(source_manifest),
            corrective["source_manifest_sha256"],
        )
        self.assertEqual(
            sha256(source_receipt),
            corrective["source_review_receipt_sha256"],
        )
        self.assertEqual(
            self.classification["manifest"]["sha256"],
            corrective["source_manifest_sha256"],
        )
        self.assertEqual(
            self.classification["direct_review_receipt"]["sha256"],
            corrective["source_review_receipt_sha256"],
        )

    def test_03_offline_analyzer_never_launches_dcc_or_engine(self) -> None:
        tree = ast.parse(self.analyzer, filename=str(ANALYZER_PATH))
        imported_modules = {
            node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertNotIn("bpy", imported_modules)
        self.assertNotIn("subprocess", imported_modules)
        self.assertNotIn("Start-Process", self.analyzer)
        self.assertNotIn("UnrealEditor", self.analyzer)
        self.assertEqual(self.classification["gate"], "PASS")
        self.assertEqual(
            self.classification["analysis_mode"],
            "offline_json_and_hash_only_no_blender_no_unreal",
        )
        self.assertTrue(all(self.classification["checks"].values()))

    def test_04_exact_six_rebake_and_eighteen_reuse_partition(self) -> None:
        corrective = self.contract["corrective_map_contract"]
        expected_rebakes = {
            "Pathfinder/PaintShell/Normal",
            "Pathfinder/PaintShell/AO",
            "Pathfinder/EdgeHardware/Normal",
            "Lighthouse/WhiteTower/Normal",
            "Lighthouse/WhiteTower/AO",
            "RadarPost/MastDrive/Normal",
        }
        rebakes = set(corrective["rebake_targets"])
        reused = {
            item["key"]
            for item in self.classification["reused_accepted_maps"]
        }
        all_maps = {
            f"{asset['id']}/{group['id']}/{map_type}"
            for asset in self.contract["assets"]
            for group in asset["groups"]
            for map_type in ("Normal", "AO")
        }
        self.assertEqual(rebakes, expected_rebakes)
        self.assertEqual(len(rebakes), 6)
        self.assertEqual(len(reused), 18)
        self.assertFalse(rebakes & reused)
        self.assertEqual(rebakes | reused, all_maps)

    def test_05_reused_maps_are_review_passes_with_hash_identity(self) -> None:
        receipt_path = resolve(
            self.contract["corrective_map_contract"]["source_review_receipt"]
        )
        receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        receipt_maps = {
            f"{item['asset']}/{item['group']}/{item['map_type']}": item
            for item in receipt["maps"]
        }
        for item in self.classification["reused_accepted_maps"]:
            source = Path(item["source_path"])
            self.assertEqual(receipt_maps[item["key"]]["result"], "PASS")
            self.assertEqual(sha256(source), item["sha256"])
            self.assertEqual(
                receipt_maps[item["key"]]["sha256"],
                item["sha256"],
            )

    def test_06_component_isolation_uses_bake_only_duplicates(self) -> None:
        for token in (
            "def connected_component_vertex_sets(",
            "def component_descriptors(",
            "def match_components(",
            "def component_explosion_offsets(",
            "def apply_component_explosion(",
            "def make_component_exploded_bake_set(",
            "def remove_bake_objects(",
        ):
            self.assertIn(token, self.generator)
        start = self.generator.index("def make_component_exploded_bake_set(")
        end = self.generator.index("\ndef remove_bake_objects(", start)
        implementation = self.generator[start:end]
        self.assertIn("duplicate_mesh(", implementation)
        self.assertIn("apply_component_explosion(item", implementation)
        self.assertIn(
            '"production_geometry_translated": False',
            self.generator,
        )

    def test_07_corrective_settings_are_tightly_bounded(self) -> None:
        classification_policies = self.classification["group_policies"]
        groups = {
            f"{asset['id']}/{group['id']}": group
            for asset in self.contract["assets"]
            for group in asset["groups"]
        }
        self.assertEqual(set(classification_policies), {
            "Pathfinder/PaintShell",
            "Pathfinder/EdgeHardware",
            "Lighthouse/WhiteTower",
            "RadarPost/MastDrive",
        })
        for key, policy in classification_policies.items():
            group = groups[key]
            self.assertEqual(
                group["bevel_width_m"],
                policy["bevel_width_m"],
            )
            self.assertEqual(
                group["cage_extrusion_m"],
                policy["cage_extrusion_m"],
            )
            self.assertEqual(
                group["max_ray_distance_m"],
                policy["max_ray_distance_m"],
            )
            self.assertLess(
                group["bevel_width_m"],
                group["cage_extrusion_m"],
            )
            self.assertLess(
                group["cage_extrusion_m"],
                group["max_ray_distance_m"],
            )
            self.assertEqual(policy["component_spacing_multiplier"], 3.0)

    def test_08_ao_policy_is_two_direct_and_ten_dedicated(self) -> None:
        repair = self.contract["topology_repair_contract"]
        policies = repair["group_policies"]
        direct = [
            key
            for key, item in policies.items()
            if item["ao_policy"] == "direct_low_self_occlusion"
        ]
        dedicated = [
            key
            for key, item in policies.items()
            if item["ao_policy"]
            == "selected_to_active_from_dedicated_bounded_ao_occluder"
        ]
        self.assertEqual(len(direct), repair["direct_low_ao_count"])
        self.assertEqual(len(direct), 2)
        self.assertEqual(len(dedicated), repair["dedicated_ao_occluder_count"])
        self.assertEqual(len(dedicated), 10)
        self.assertIn("Pathfinder/PaintShell", dedicated)
        self.assertIn("Lighthouse/WhiteTower", dedicated)

    def test_09_revision008_namespace_is_isolated(self) -> None:
        self.assertEqual(
            self.contract["build_id"],
            "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
        )
        self.assertTrue(
            all(
                "008" in value or "HeroGroupedTopology_008" in value
                for value in self.contract["outputs"].values()
            )
        )
        names = [
            group[key]
            for asset in self.contract["assets"]
            for group in asset["groups"]
            for key in (
                "low_object",
                "high_object",
                "cage_object",
                "texture_prefix",
            )
        ]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all("_008" in name for name in names))

    def test_10_generator_reuses_only_accepted_maps(self) -> None:
        self.assertIn("def reuse_accepted_map(", self.generator)
        self.assertIn("shutil.copy2(source_path, output)", self.generator)
        self.assertIn(
            'if copied["sha256"] != evidence["sha256"]',
            self.generator,
        )
        self.assertIn('"mode": "hash_verified_reuse"', self.generator)
        self.assertIn('"mode": "corrective_rebake"', self.generator)
        self.assertIn(
            'map_key not in corrective_inputs["rebake_targets"]',
            self.generator,
        )

    def test_11_supervisor_is_serialized_and_archives_inputs(self) -> None:
        for token in (
            "M01_HERO_GROUPED_TOPOLOGY_BAKE_008_CONTRACT.json",
            "blender_m01_hero_grouped_topology_bake_008.py",
            "verify_skyguard_m01_hero_grouped_topology_bake_008.py",
            "analyze_m01_grouped_topology_007_visual_failures.py",
            "attempt_correction_basis",
            "visual_failure_classification",
            "source_manifest",
            "source_review_receipt",
            'Get-Process -Name "blender"',
            "Refusing to overlap the exclusive heavy lane",
            "is immutable and already has canonical output(s)",
            "blender.stdout.log",
            "blender.stderr.log",
            "SHA256SUMS.json",
        ):
            self.assertIn(token, self.supervisor)

    def test_12_review_queue_requires_only_six_new_maps(self) -> None:
        self.assertIn("required_map_count = 6", self.supervisor)
        self.assertIn("inherited_pass_map_count = 18", self.supervisor)
        self.assertIn(
            "ACCEPTED_BY_HASH_VERIFIED_BUILD_007_REUSE",
            self.supervisor,
        )
        self.assertIn('direct_original_resolution_map_review = "NOT_REVIEWED"', self.supervisor)
        self.assertIn("promotion_authorized = $false", self.supervisor)
        self.assertIn("p3_4_closed = $false", self.supervisor)

    def test_13_python_sources_parse(self) -> None:
        ast.parse(self.generator, filename=str(GENERATOR_PATH))
        ast.parse(self.verifier, filename=str(VERIFIER_PATH))
        ast.parse(self.analyzer, filename=str(ANALYZER_PATH))

    def test_14_contract_and_classification_json_parse(self) -> None:
        self.assertEqual(
            sha256(CLASSIFICATION_PATH),
            self.overlay["visual_failure_classification_sha256"],
        )
        self.assertEqual(
            sha256(self.base_contract_path),
            self.overlay["extends_contract_sha256"],
        )
        self.assertEqual(self.classification["failed_map_count"], 6)
        self.assertEqual(self.classification["reused_accepted_map_count"], 18)

    def test_15_canonical_output_state_is_not_partial(self) -> None:
        output_paths = [
            resolve(value) for value in self.contract["outputs"].values()
        ]
        existing = [path for path in output_paths if path.exists()]
        self.assertIn(
            len(existing),
            {0, len(output_paths)},
            f"Partial Build 008 canonical output state: {existing}",
        )
        if existing:
            manifest = json.loads(
                resolve(self.contract["outputs"]["manifest"]).read_text(
                    encoding="utf-8-sig"
                )
            )
            self.assertEqual(
                manifest["build_id"],
                "BLD_M01_HERO_GROUPED_TOPOLOGY_008",
            )

    def test_16_readiness_remains_fail_closed_before_blender(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_manifest = Path(temp_dir) / "missing.json"
            report = VERIFIER.build_report(
                self.contract,
                CONTRACT_PATH,
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

    def test_17_reused_map_artifact_hash_uses_defined_helper(self) -> None:
        self.assertIn(
            "sha256_file(source_path)",
            self.verifier,
        )
        self.assertNotIn(
            "sha256(source_path)",
            self.verifier,
        )


if __name__ == "__main__":
    unittest.main()
