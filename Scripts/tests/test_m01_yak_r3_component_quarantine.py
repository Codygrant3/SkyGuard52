import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "audit_m01_yak_r3_component_import_source.py"
)
SPEC = importlib.util.spec_from_file_location("r3_audit", MODULE_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(AUDIT)


class R3ComponentQuarantineTests(unittest.TestCase):
    def test_bound_source_audit_passes(self):
        report = AUDIT.audit_source()
        self.assertEqual(report["gate"], "PASS_COMPONENT_IMPORT_SOURCE_AUDIT")
        self.assertFalse(report["promotion_allowed"])

    def test_contract_is_quarantine_only(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        self.assertIn("/Quarantine/", contract["unreal"]["destination"])
        self.assertFalse(contract["unreal"]["promotion_allowed"])
        self.assertFalse(contract["unreal"]["runtime_map_change_allowed"])
        self.assertFalse(contract["unreal"]["config_change_allowed"])

    def test_exactly_ten_component_meshes(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        self.assertEqual(len(contract["component_meshes"]), 10)
        self.assertEqual(len(contract["support_materials"]), 5)
        self.assertEqual(contract["support_textures"], [])

    def test_l88_gameplay_bundles_are_retained(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        self.assertEqual(
            set(contract["retained_l88_bundles"]),
            {
                "Aircraft_RearCockpit",
                "Crew_Pilot",
                "Crew_RearGunner_FirstPerson",
                "Crew_RearGunner_ThirdPerson",
                "Weapon_Rifle",
                "Weapon_Igla",
            },
        )

    def test_whole_aircraft_classes_are_forbidden(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        self.assertIn("World", contract["forbidden_import_classes"])
        self.assertIn("Blueprint", contract["forbidden_import_classes"])
        self.assertIn("SkeletalMesh", contract["forbidden_import_classes"])

    def test_camera_is_explicit_reference_only(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        self.assertFalse(contract["camera_reference"]["glb_node_expected"])

    def test_incomplete_evaluation_is_not_promotable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "skyguard.m01.yak-r3-component-evaluation.v1",
                        "components": [],
                        "global_evidence": {},
                    }
                ),
                encoding="utf-8",
            )
            report = AUDIT.verify_evaluation(path)
        self.assertEqual(report["gate"], "NOT_PROMOTABLE")
        self.assertTrue(report["errors"])

    def test_complete_evaluation_still_requires_manual_review(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        evidence_path = AUDIT.CONTRACT_PATH
        evidence = {
            "path": str(evidence_path.relative_to(AUDIT.ROOT)).replace("\\", "/"),
            "bytes": evidence_path.stat().st_size,
            "sha256": AUDIT.sha256(evidence_path),
        }
        component = {
            field: [evidence]
            for field in contract["promotion_requirements"]["per_component"]
        }
        components = [
            {"ledger_identity": identity, **component}
            for identity in contract["component_meshes"]
        ]
        global_evidence = {
            field: [evidence]
            for field in contract["promotion_requirements"]["global"]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.json"
            path.write_text(
                json.dumps(
                    {
                        "components": components,
                        "global_evidence": global_evidence,
                    }
                ),
                encoding="utf-8",
            )
            report = AUDIT.verify_evaluation(path)
        self.assertEqual(report["gate"], "READY_FOR_MANUAL_PROMOTION_REVIEW")
        self.assertFalse(report["automatic_promotion"])

    def test_builder_only_resumes_exact_failed_attempt(self):
        text = (
            MODULE_PATH.parents[0]
            / "build_m01_yak_r3_component_quarantine.py"
        ).read_text(encoding="utf-8")
        self.assertIn("validate_resume_assets", text)
        self.assertIn(
            "non-empty quarantine is not the exact recoverable failed attempt",
            text,
        )
        self.assertIn("replace_existing = False", text)

    def test_reference_evidence_avoids_abstract_data_asset_classes(self):
        contract = AUDIT.load_json(AUDIT.CONTRACT_PATH)
        text = (
            MODULE_PATH.parents[0]
            / "build_m01_yak_r3_component_quarantine.py"
        ).read_text(encoding="utf-8")
        verifier = (
            MODULE_PATH.parents[0]
            / "verify_m01_yak_r3_component_quarantine.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            contract["unreal"]["reference_storage"], "metadata_on_each_component"
        )
        self.assertNotIn("DataAssetFactory", text)
        self.assertNotIn("unreal.DataAsset", text)
        self.assertNotIn("unreal.PrimaryDataAsset", text)
        self.assertIn("Skyguard.PivotReferenceJson", text)
        self.assertIn("Skyguard.SafetyCameraReferenceJson", text)
        self.assertIn("Skyguard.PivotReferenceJson", verifier)
        self.assertIn("Skyguard.SafetyCameraReferenceJson", verifier)

    def test_gate_does_not_build_or_launch_blender(self):
        text = (
            MODULE_PATH.parents[0]
            / "run_m01_yak_r3_component_quarantine_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Build.bat", text)
        self.assertNotIn("Start-Process -FilePath $BuildTool", text)
        self.assertNotIn("Start-Process -FilePath $Blender", text)
        self.assertNotIn("-ExecCmds=Automation", text)

    def test_gate_normalizes_empty_error_marker_pipeline_to_an_array(self):
        text = (
            MODULE_PATH.parents[0]
            / "run_m01_yak_r3_component_quarantine_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"\$Markers\s*=\s*@\(\s*@\(", re.MULTILINE))
        self.assertIn("$Markers.Count", text)
        self.assertIn("success_marker_present", text)


if __name__ == "__main__":
    unittest.main()
