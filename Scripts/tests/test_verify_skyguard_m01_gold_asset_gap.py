from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_m01_gold_asset_gap.py"
)
SPEC = importlib.util.spec_from_file_location("m01_gold_asset_gap", MODULE_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class M01GoldAssetGapVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        evidence_path = self.root / "evidence.bin"
        evidence_path.write_bytes(b"governed evidence")
        evidence = {
            "path": "evidence.bin",
            "bytes": evidence_path.stat().st_size,
            "sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
            "kind": "receipt",
            "claim": "Synthetic test evidence.",
        }
        gates = {name: False for name in VERIFIER.REQUIRED_QUALITY_GATES}
        families = []
        for family_id in sorted(VERIFIER.REQUIRED_FAMILY_IDS):
            families.append(
                {
                    "id": family_id,
                    "display_name": family_id,
                    "status": "blockout_proxy",
                    "evidence": ["test_evidence"],
                    "proxy_markers": ["synthetic blockout marker"],
                    "quality_gates": copy.deepcopy(gates),
                    "missing_requirements": ["final production acceptance"],
                    "next_action": "Replace the synthetic candidate.",
                }
            )
        self.manifest = {
            "schema": VERIFIER.SCHEMA,
            "audit_id": "test-audit",
            "required_asset_family_ids": sorted(VERIFIER.REQUIRED_FAMILY_IDS),
            "required_quality_gates": sorted(VERIFIER.REQUIRED_QUALITY_GATES),
            "evidence_catalog": {"test_evidence": evidence},
            "asset_families": families,
            "summary": {
                "required_family_count": len(VERIFIER.REQUIRED_FAMILY_IDS),
                "production_count": 0,
                "blockout_proxy_count": len(VERIFIER.REQUIRED_FAMILY_IDS),
                "missing_count": 0,
                "unverified_count": 0,
                "gold_slice_ready": False,
                "asset_gate": "PASS_WITH_GAPS",
            },
            "next_serialized_blender_build": {
                "build_id": "test-build",
                "closes_or_unblocks": ["yak52_exterior"],
                "required_outputs": ["source"],
                "acceptance_before_unreal_import": ["offline gate"],
            },
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evaluate(self, manifest: dict | None = None) -> dict:
        return VERIFIER.evaluate(manifest or self.manifest, self.root)

    def test_valid_gap_manifest_passes_integrity_but_not_asset_gate(self) -> None:
        report = self.evaluate()
        self.assertEqual("PASS", report["gate"])
        self.assertEqual("PASS_WITH_GAPS", report["asset_gate"])
        self.assertFalse(report["gold_slice_ready"])

    def test_invalid_status_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["asset_families"][0]["status"] = "candidate"
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_production_requires_every_quality_gate(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        family = manifest["asset_families"][0]
        family["status"] = "production"
        family["proxy_markers"] = []
        family["missing_requirements"] = []
        manifest["summary"]["production_count"] = 1
        manifest["summary"]["blockout_proxy_count"] -= 1
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_tampered_evidence_fails(self) -> None:
        (self.root / "evidence.bin").write_bytes(b"tampered")
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["all_evidence_integrity"])

    def test_missing_cannot_reference_existing_candidate_evidence(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        family = manifest["asset_families"][0]
        family["status"] = "missing"
        family["proxy_markers"] = []
        manifest["summary"]["missing_count"] = 1
        manifest["summary"]["blockout_proxy_count"] -= 1
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])

    def test_unverified_requires_no_proxy_marker(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["asset_families"][0]["status"] = "unverified"
        manifest["summary"]["unverified_count"] = 1
        manifest["summary"]["blockout_proxy_count"] -= 1
        self.assertEqual("FAIL", self.evaluate(manifest)["gate"])


class M01GoldAssetGapSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.manifest_path = (
            cls.root
            / "Docs"
            / "AAA_Review"
            / "M01_GOLD_ASSET_GAP_MANIFEST.json"
        )
        cls.manifest = json.loads(
            cls.manifest_path.read_text(encoding="utf-8-sig")
        )

    def test_real_manifest_has_no_false_production_claim(self) -> None:
        self.assertEqual(0, self.manifest["summary"]["production_count"])
        self.assertFalse(self.manifest["summary"]["gold_slice_ready"])

    def test_real_manifest_covers_governed_families_exactly(self) -> None:
        ids = {item["id"] for item in self.manifest["asset_families"]}
        self.assertEqual(VERIFIER.REQUIRED_FAMILY_IDS, ids)

    def test_next_build_is_upstream_yak_and_cockpit_source(self) -> None:
        build = self.manifest["next_serialized_blender_build"]
        self.assertIn("yak52_exterior", build["closes_or_unblocks"])
        self.assertIn("rear_cockpit", build["closes_or_unblocks"])
        self.assertIn("crew_arms_gloves", build["closes_or_unblocks"])


if __name__ == "__main__":
    unittest.main()
