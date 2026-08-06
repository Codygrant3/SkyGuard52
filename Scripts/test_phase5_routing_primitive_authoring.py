#!/usr/bin/env python3

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "AAA_Review"
SCRIPTS = ROOT / "Scripts"


class Phase5RoutingPrimitiveAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.specs = json.loads(
            (
                DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
            ).read_text(encoding="utf-8")
        )
        self.briefs = json.loads(
            (
                DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
            ).read_text(encoding="utf-8")
        )

    def test_exact_named_primitive_coverage(self):
        attenuation = {item["name"] for item in self.specs["attenuation"]}
        concurrency = {item["name"] for item in self.specs["concurrency"]}
        self.assertEqual(
            {item["attenuation_contract"] for item in self.briefs["categories"]},
            attenuation,
        )
        self.assertEqual(
            {item["concurrency_contract"] for item in self.briefs["categories"]},
            concurrency,
        )
        self.assertEqual(15, len(attenuation))
        self.assertEqual(14, len(concurrency))

    def test_builder_preserves_missing_source_truth_boundary(self):
        source = (
            SCRIPTS / "build_skyguard_phase5_routing_primitives.py"
        ).read_text(encoding="utf-8")
        self.assertIn("MISSING_SOURCE", source)
        self.assertIn("explicit_missing_source_count", source)
        self.assertNotIn("AudioImport", source)
        self.assertNotIn("download", source.lower())

    def test_fresh_audit_rejects_metasound_filename_shells(self):
        source = (
            SCRIPTS / "verify_skyguard_phase5_routing_primitives.py"
        ).read_text(encoding="utf-8")
        self.assertIn("unverified empty MetaSound shells were created", source)
        self.assertIn("bank_routing_binding_count", source)
        self.assertIn("explicit_missing_source_count", source)

    def test_builder_and_audit_are_attempt_scoped(self):
        for name in (
            "build_skyguard_phase5_routing_primitives.py",
            "verify_skyguard_phase5_routing_primitives.py",
        ):
            source = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertIn("SKYGUARD_PHASE5_PRIMITIVES_ATTEMPT_DIR", source)


if __name__ == "__main__":
    unittest.main()
