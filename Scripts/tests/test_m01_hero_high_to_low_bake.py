from __future__ import annotations

import copy
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
    / "M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json"
)
GENERATOR_PATH = ROOT / "Scripts" / "blender_m01_hero_high_to_low_bake.py"
VERIFIER_PATH = (
    ROOT / "Scripts" / "verify_skyguard_m01_hero_high_to_low_bake.py"
)
SPEC = importlib.util.spec_from_file_location("m01_hilo_verifier", VERIFIER_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


def bound(path: Path) -> dict:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


class M01HighToLowSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        cls.report = VERIFIER.evaluate_source(
            cls.contract,
            GENERATOR_PATH,
            ROOT,
        )

    def test_source_gate_passes_without_running_blender(self) -> None:
        self.assertEqual("PASS", self.report["gate"], self.report["errors"])

    def test_three_distinct_asset_specific_detail_builders_exist(self) -> None:
        self.assertTrue(self.report["checks"]["asset_specific_detail_builders"])
        self.assertTrue(self.report["checks"]["asset_scope"])

    def test_selected_to_active_and_explicit_cages_are_required(self) -> None:
        checks = self.report["checks"]
        self.assertTrue(checks["bake_contract_shape"])
        self.assertTrue(checks["generator_selected_to_active"])
        self.assertTrue(checks["generator_cage_enabled"])
        self.assertTrue(checks["generator_named_cage"])
        self.assertTrue(checks["generator_explicit_cage_geometry"])
        generator = GENERATOR_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("bake.cage_object = cage", generator)
        self.assertNotIn("bake.cage_object = cage.name", generator)
        self.assertIn("bpy.ops.object.bake(type=map_type.upper())", generator)

    def test_generator_creates_separate_mesh_datablocks(self) -> None:
        self.assertTrue(
            self.report["checks"]["generator_separate_mesh_copy"]
        )
        source = GENERATOR_PATH.read_text(encoding="utf-8-sig")
        self.assertNotIn(
            "same_mesh_tangent_space_with_authored_shader_bump",
            source,
        )

    def test_contract_does_not_claim_p3_4_complete(self) -> None:
        self.assertIn("candidate_requires", self.contract["promotion"])
        self.assertGreaterEqual(len(self.contract["non_claims"]), 4)


class M01HighToLowArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        source = self.root / "source.blend"
        master = self.root / "master.blend"
        low_glb = self.root / "low.glb"
        source.write_bytes(b"source")
        master.write_bytes(b"master")
        low_glb.write_bytes(b"low glb")
        self.contract["source_blend"] = str(source)
        self.manifest = {
            "schema": VERIFIER.MANIFEST_SCHEMA,
            "build_id": VERIFIER.BUILD_ID,
            "source": bound(source),
            "bake_contract": copy.deepcopy(
                self.contract["bake_contract"]
            ),
            "outputs": {
                "master_blend": bound(master),
                "low_glb": bound(low_glb),
            },
            "assets": [],
            "validation": {"pass": True, "failures": []},
            "promotion": VERIFIER.PROMOTION,
        }
        map_hashes = []
        for index, spec in enumerate(self.contract["assets"]):
            low_vertices = 1000
            high_vertices = int(
                low_vertices
                * float(spec["minimum_high_to_low_vertex_ratio"])
            ) + 50
            maps = []
            for map_spec in self.contract["bake_contract"]["maps"]:
                path = (
                    self.root
                    / f"{index}_{map_spec['type'].lower()}.png"
                )
                path.write_bytes(
                    f"{spec['id']}:{map_spec['type']}".encode("ascii")
                )
                record = {
                    **bound(path),
                    "type": map_spec["type"],
                    "width": self.contract["bake_contract"]["resolution"],
                    "height": self.contract["bake_contract"]["resolution"],
                    "channels": 3,
                    "color_space": map_spec["color_space"],
                    "varied_rgb_channels": max(
                        2, map_spec["minimum_varied_rgb_channels"]
                    ),
                    "projection": {
                        "selected_to_active": True,
                        "cage_object": spec["cage_object"],
                        "cage_extrusion_m": spec["cage_extrusion_m"],
                        "max_ray_distance_m": spec["max_ray_distance_m"],
                    },
                }
                maps.append(record)
                map_hashes.append(record["sha256"])
            self.manifest["assets"].append(
                {
                    "id": spec["id"],
                    "source_object": spec["source_object"],
                    "low": {
                        "object": spec["low_object"],
                        "mesh_datablock": spec["low_object"] + "_Mesh",
                        "vertices": low_vertices,
                        "triangles": 1500,
                        "dimensions_m": [5.0, 4.0, 3.0],
                        "uv_layers": [
                            self.contract["bake_contract"]["uv_layer"]
                        ],
                    },
                    "high": {
                        "object": spec["high_object"],
                        "mesh_datablock": spec["high_object"] + "_Mesh",
                        "vertices": high_vertices,
                        "triangles": 5000,
                        "dimensions_m": [5.02, 4.02, 3.02],
                        "uv_layers": [],
                    },
                    "cage": {
                        "object": spec["cage_object"],
                        "mesh_datablock": spec["cage_object"] + "_Mesh",
                        "vertices": low_vertices,
                        "triangles": 1500,
                        "dimensions_m": [5.04, 4.04, 3.04],
                        "uv_layers": [],
                    },
                    "high_to_low_vertex_ratio": round(
                        high_vertices / low_vertices, 6
                    ),
                    "high_to_low_bounds_delta_m": 0.02,
                    "detail_groups": copy.deepcopy(
                        spec["required_detail_groups"]
                    ),
                    "maps": maps,
                }
            )
        canonical_hashes = [
            map_record["sha256"]
            for asset in sorted(
                self.manifest["assets"],
                key=lambda item: item["id"],
            )
            for map_record in sorted(
                asset["maps"],
                key=lambda item: item["type"],
            )
        ]
        self.manifest["package_fingerprint_sha256"] = hashlib.sha256(
            "\n".join(canonical_hashes).encode("ascii")
        ).hexdigest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evaluate(self, manifest: dict | None = None) -> dict:
        return VERIFIER.evaluate_artifacts(
            self.contract,
            manifest or self.manifest,
            self.root,
        )

    def test_valid_synthetic_artifact_passes(self) -> None:
        report = self.evaluate()
        self.assertEqual("PASS", report["gate"], report["errors"])

    def test_same_mesh_datablock_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        asset = manifest["assets"][0]
        asset["high"]["mesh_datablock"] = asset["low"]["mesh_datablock"]
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_missing_explicit_cage_projection_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["assets"][0]["maps"][0]["projection"][
            "cage_object"
        ] = ""
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_insufficient_high_density_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        asset = manifest["assets"][0]
        asset["high"]["vertices"] = asset["low"]["vertices"]
        asset["high_to_low_vertex_ratio"] = 1.0
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_tampered_map_fails(self) -> None:
        path = Path(self.manifest["assets"][0]["maps"][0]["path"])
        path.write_bytes(b"tampered")
        self.assertEqual("FAIL", self.evaluate()["gate"])

    def test_fingerprint_order_is_asset_and_map_stable(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["assets"].reverse()
        self.assertEqual("PASS", self.evaluate(manifest)["gate"])
        manifest["assets"][0]["maps"].reverse()
        self.assertEqual("PASS", self.evaluate(manifest)["gate"])

    def test_false_final_promotion_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["promotion"] = "AAA_final"
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])


if __name__ == "__main__":
    unittest.main()
