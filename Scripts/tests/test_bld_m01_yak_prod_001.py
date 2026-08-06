from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = ROOT / "Scripts" / "verify_bld_m01_yak_prod_001.py"
GENERATOR_PATH = ROOT / "Scripts" / "blender_bld_m01_yak_prod_001.py"
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_001_CONTRACT.json"
)
SPEC = importlib.util.spec_from_file_location("bld_m01_yak_verifier", VERIFIER_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class BldM01YakSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = VERIFIER.evaluate_source(cls.contract, GENERATOR_PATH)

    def test_source_contract_passes_without_running_blender(self) -> None:
        self.assertEqual("PASS", self.report["gate"])
        self.assertEqual("NOT_RUN", self.report["artifact_gate"])

    def test_generator_never_imports_or_links_l88_geometry(self) -> None:
        self.assertTrue(self.report["checks"]["no_external_geometry_import"])
        source = GENERATOR_PATH.read_text(encoding="utf-8-sig")
        self.assertNotIn("bpy.ops.import_scene.gltf", source)
        self.assertNotIn("bpy.data.libraries.load", source)

    def test_governed_real_world_dimensions(self) -> None:
        dimensions = self.contract["reference_dimensions_m"]
        self.assertAlmostEqual(7.745, dimensions["overall_length"], places=3)
        self.assertAlmostEqual(9.3, dimensions["wingspan"], places=3)
        self.assertAlmostEqual(2.7, dimensions["overall_height"], places=3)
        self.assertAlmostEqual(2.4, dimensions["propeller_diameter"], places=3)

    def test_required_groups_are_separate_objects(self) -> None:
        names = set(self.contract["required_mesh_objects"])
        for required in {
            "GEO_PROD_Fuselage",
            "GEO_PROD_Wing_L",
            "GEO_PROD_Flap_L",
            "GEO_PROD_Aileron_L",
            "GEO_PROD_PropBlade_A",
            "GEO_PROD_CanopyRearSlidingGlass",
            "GEO_PROD_CockpitTubRear",
        }:
            self.assertIn(required, names)

    def test_blockout_names_are_forbidden(self) -> None:
        forbidden = set(self.contract["forbidden_name_tokens"])
        self.assertIn("blockout", forbidden)
        self.assertIn("proxy", forbidden)
        self.assertIn("cube", forbidden)


class BldM01YakArtifactVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        blend = self.root / "master.blend"
        glb = self.root / "candidate.glb"
        blend.write_bytes(b"blend")
        glb.write_bytes(b"glb")

        def bound(path: Path) -> dict:
            return {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        objects = []
        minimums = self.contract["minimum_mesh_vertices"]
        for name in self.contract["required_mesh_objects"]:
            objects.append(
                {
                    "name": name,
                    "type": "MESH",
                    "vertices": max(1000, minimums.get(name, 0)),
                    "polygons": 1000,
                    "uv_layers": ["UV0"],
                    "material_slots": ["MAT_YakPaint"],
                }
            )
        for name in self.contract["required_socket_objects"]:
            objects.append({"name": name, "type": "EMPTY"})
        for name in self.contract["required_datum_objects"]:
            objects.append({"name": name, "type": "EMPTY"})
        self.manifest = {
            "schema": VERIFIER.ARTIFACT_SCHEMA,
            "build_id": VERIFIER.BUILD_ID,
            "blender_version": "5.2.0",
            "measured_dimensions_m": copy.deepcopy(
                self.contract["reference_dimensions_m"]
            ),
            "l88_reference": {
                "sha256": self.contract["l88_reference"]["sha256"],
                "use": "datum_reference_only_not_imported",
            },
            "outputs": {"blend": bound(blend), "glb": bound(glb)},
            "objects": objects,
            "validation": {
                "pass": True,
                "missing_meshes": [],
                "missing_sockets": [],
                "missing_datums": [],
                "uv_failures": [],
                "material_failures": [],
                "minimum_vertex_failures": [],
            },
            "forbidden_name_violations": [],
            "promotion": self.contract["promotion"],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evaluate(self, manifest: dict | None = None) -> dict:
        return VERIFIER.evaluate_artifacts(
            self.contract, manifest if manifest is not None else self.manifest
        )

    def test_valid_synthetic_artifact_manifest_passes(self) -> None:
        self.assertEqual("PASS", self.evaluate()["gate"])

    def test_tampered_glb_fails(self) -> None:
        Path(self.manifest["outputs"]["glb"]["path"]).write_bytes(b"tampered")
        self.assertEqual("FAIL", self.evaluate()["gate"])

    def test_blockout_name_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["objects"][0]["name"] = "GEO_blockout_Fuselage"
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["blockout_name_rejection"])

    def test_missing_uv_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["objects"][0]["uv_layers"] = []
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_dimension_drift_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["measured_dimensions_m"]["wingspan"] = 8.2
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["dimension_results"]["wingspan"])

    def test_production_final_claim_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["promotion"] = "production_final"
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])


if __name__ == "__main__":
    unittest.main()
