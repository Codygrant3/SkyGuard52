from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "Scripts" / "blender_bld_m01_yak_prod_002.py"
VERIFIER_PATH = ROOT / "Scripts" / "verify_bld_m01_yak_prod_002.py"
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_002_CONTRACT.json"
)
SPEC = importlib.util.spec_from_file_location("yak002_verifier", VERIFIER_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class Yak002SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = VERIFIER.evaluate_source(cls.contract, GENERATOR, ROOT)

    def test_source_gate_passes_without_running_blender(self) -> None:
        self.assertEqual("PASS", self.report["gate"])
        self.assertEqual("NOT_RUN", self.report["artifact_gate"])

    def test_review_render_evidence_is_hash_bound(self) -> None:
        self.assertTrue(self.report["checks"]["three_review_renders"])
        self.assertTrue(self.report["checks"]["review_render_integrity"])
        self.assertTrue(self.report["checks"]["review_findings_present"])

    def test_001_and_l88_geometry_are_never_imported(self) -> None:
        self.assertTrue(self.report["checks"]["no_001_or_l88_geometry_import"])
        source = GENERATOR.read_text(encoding="utf-8-sig")
        for forbidden in (
            "bpy.ops.import_scene.gltf",
            "bpy.ops.wm.open_mainfile",
            "bpy.data.libraries.load",
            "base.create_aircraft",
            "base.create_fuselage",
        ):
            self.assertNotIn(forbidden, source)

    def test_yak_specific_refinement_parts_are_required(self) -> None:
        names = set(self.contract["required_mesh_objects"])
        for required in (
            "GEO_PROD002_CowlingShutters",
            "GEO_PROD002_Spinner",
            "GEO_PROD002_MainWheel_L",
            "GEO_PROD002_NoseWheel",
            "GEO_PROD002_WingRootFairing_L",
            "GEO_PROD002_VerticalStabilizer",
            "GEO_PROD002_CockpitSidewall_L",
            "GEO_PROD002_GaugeClusterRear",
        ):
            self.assertIn(required, names)

    def test_decal_material_ids_are_governed(self) -> None:
        ids = self.contract["material_id_contract"]
        self.assertEqual(100, ids["panel_line_decal"])
        self.assertEqual(101, ids["rivet_decal"])
        self.assertGreaterEqual(len(self.contract["decal_ready_objects"]), 8)

    def test_movable_parts_are_separate(self) -> None:
        parts = self.contract["movable_parts"]
        self.assertGreaterEqual(len(parts), 20)
        self.assertEqual("rudder_hinge", parts["GEO_PROD002_Rudder"])
        self.assertEqual(
            "canopy_slide_origin", parts["GEO_PROD002_CanopyRearSlidingGlass"]
        )

    def test_outputs_are_isolated_from_001(self) -> None:
        for path in self.contract["outputs"].values():
            self.assertIn("002", path)
            self.assertNotIn("Yak52_Production/", path)


class Yak002ArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        blend = self.root / "candidate002.blend"
        glb = self.root / "candidate002.glb"
        blend.write_bytes(b"blend002")
        glb.write_bytes(b"glb002")

        def bound(path: Path) -> dict:
            return {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        objects = []
        minimums = self.contract["minimum_mesh_vertices"]
        movable = self.contract["movable_parts"]
        decals = set(self.contract["decal_ready_objects"])
        for name in self.contract["required_mesh_objects"]:
            custom = {}
            if name in movable:
                custom = {
                    "SKG_Movable": True,
                    "SKG_PivotRole": movable[name],
                }
            slots = ["MAT002_YakPaint"]
            if name in decals:
                custom.update(
                    {
                        "SKG_DecalReady": True,
                        "SKG_MaterialID_PanelLine": 100,
                        "SKG_MaterialID_Rivet": 101,
                    }
                )
                slots.extend(["MAT002_PanelLine", "MAT002_Rivet"])
            objects.append(
                {
                    "name": name,
                    "type": "MESH",
                    "vertices": max(1200, minimums.get(name, 0)),
                    "polygons": 1000,
                    "uv_layers": ["UV0"],
                    "material_slots": slots,
                    "custom_properties": custom,
                    "location_m": copy.deepcopy(
                        self.contract["movable_pivot_positions_m"].get(
                            name, [0.0, 0.0, 0.0]
                        )
                    ),
                }
            )
        for name in (
            self.contract["required_socket_objects"]
            + self.contract["required_datum_objects"]
        ):
            objects.append({"name": name, "type": "EMPTY", "custom_properties": {}})
        self.manifest = {
            "schema": VERIFIER.ARTIFACT_SCHEMA,
            "build_id": VERIFIER.BUILD_ID,
            "blender_version": "5.2.0",
            "base_source_reference": {
                "sha256": self.contract["base_source_reference"]["sha256"],
                "use": "python_helpers_only_no_001_artifact_or_datablock_import",
            },
            "l88_reference": {
                "sha256": self.contract["l88_reference"]["sha256"],
                "use": "datum_reference_only_not_imported",
            },
            "outputs": {"blend": bound(blend), "glb": bound(glb)},
            "objects": objects,
            "measured_dimensions_m": copy.deepcopy(
                self.contract["reference_dimensions_m"]
            ),
            "validation": {
                "pass": True,
                "missing_meshes": [],
                "missing_sockets": [],
                "missing_datums": [],
                "uv_failures": [],
                "material_failures": [],
                "minimum_vertex_failures": [],
                "movable_failures": [],
                "pivot_position_failures": [],
                "decal_failures": [],
            },
            "forbidden_name_violations": [],
            "promotion": self.contract["promotion"],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evaluate(self, manifest: dict | None = None) -> dict:
        return VERIFIER.evaluate_artifacts(
            self.contract, manifest or self.manifest, self.root
        )

    def test_valid_synthetic_artifact_passes(self) -> None:
        self.assertEqual("PASS", self.evaluate()["gate"])

    def test_tampered_glb_fails(self) -> None:
        Path(self.manifest["outputs"]["glb"]["path"]).write_bytes(b"tampered")
        self.assertEqual("FAIL", self.evaluate()["gate"])

    def test_missing_gear_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["objects"] = [
            item
            for item in manifest["objects"]
            if item["name"] != "GEO_PROD002_MainWheel_L"
        ]
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_missing_movable_pivot_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        target = next(
            item
            for item in manifest["objects"]
            if item["name"] == "GEO_PROD002_Rudder"
        )
        target["custom_properties"].pop("SKG_PivotRole")
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["movable_parts"])

    def test_wrong_movable_origin_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        target = next(
            item
            for item in manifest["objects"]
            if item["name"] == "GEO_PROD002_CanopyRearSlidingGlass"
        )
        target["location_m"] = [0.0, 0.0, 0.0]
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["movable_pivot_positions"])

    def test_missing_decal_metadata_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        target = next(
            item
            for item in manifest["objects"]
            if item["name"] == "GEO_PROD002_FuselageShell"
        )
        target["custom_properties"].pop("SKG_MaterialID_Rivet")
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["decal_metadata"])

    def test_dimension_drift_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["measured_dimensions_m"]["overall_length"] = 8.4
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["dimension_results"]["overall_length"])

    def test_final_claim_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["promotion"] = "AAA_final"
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])


if __name__ == "__main__":
    unittest.main()
