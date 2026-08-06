"""Mutation tests for the fail-closed M01 Fab/Quixel intake gate."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_m01_fab_quarantine_intake as verifier


class FabQuarantineGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.record = verifier.load_json(verifier.TEMPLATE_PATH)
        self.record["status"] = "EVIDENCE_COMPLETE_READY_FOR_MANUAL_QUARANTINE_INSPECTION"
        for index, asset in enumerate(self.record["assets"]):
            asset["commerce"].update({
                "paid_free_status": "FREE",
                "price_paid": 0,
                "currency": "USD",
                "acquired_at": "2026-08-02T12:00:00Z",
                "license_tier": "Fab Standard Personal",
            })
            asset["compatibility"].update({
                "supported_unreal_versions": ["5.8"],
                "target_engine_supported": True,
                "platform_restrictions": [],
                "cooked_windows_redistribution_covered": True,
            })
            asset["storage"].update({"download_bytes": 1000 + index, "installed_bytes": 2000 + index})
            asset["texture_inventory"].update({
                "total_textures": 2,
                "resolutions": [{
                    "width": 2048,
                    "height": 2048,
                    "count": 2,
                    "formats": ["PNG"],
                    "usage": ["BaseColor", "Normal"]
                }],
            })
            asset["dependencies"]["items"] = []
            asset["quarantine_disposition"] = "APPROVED_FOR_MANUAL_QUARANTINE_INSPECTION"
            asset["final_disposition"] = "QUARANTINE_ONLY_NOT_RUNTIME_APPROVED"
            self._fill_asset_evidence(asset, index)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _evidence(self, label: str) -> dict:
        relative = f"{verifier.EVIDENCE_PREFIX}{label}.txt"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = f"immutable evidence for {label}\n".encode()
        path.write_bytes(payload)
        return {
            "path": relative,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def _fill_asset_evidence(self, asset: dict, index: int) -> None:
        prefix = f"asset{index}"
        asset["catalog"]["product_page_snapshot"] = self._evidence(prefix + "_product")
        asset["commerce"]["license_text_snapshot"] = self._evidence(prefix + "_license")
        asset["commerce"]["receipt_or_acquisition_record"] = self._evidence(prefix + "_receipt")
        asset["compatibility"]["evidence"] = self._evidence(prefix + "_compatibility")
        asset["storage"]["download_package"] = self._evidence(prefix + "_download")
        asset["storage"]["installed_inventory_manifest"] = self._evidence(prefix + "_installed")
        asset["texture_inventory"]["inventory_evidence"] = self._evidence(prefix + "_textures")
        for feature in verifier.FEATURES:
            asset["runtime_features"][feature]["evidence"] = self._evidence(prefix + "_" + feature)
        asset["dependencies"]["inventory_evidence"] = self._evidence(prefix + "_dependencies")
        asset["immutable_artifacts"] = [self._evidence(prefix + "_immutable")]

    def evaluate(self, record: dict | None = None) -> dict:
        return verifier.evaluate(record or self.record, self.root)

    def test_template_fails_closed(self) -> None:
        template = verifier.load_json(verifier.TEMPLATE_PATH)
        result = verifier.evaluate(template)
        self.assertEqual(result["gate_status"], "FAIL_CLOSED")
        self.assertEqual(result["disposition"], "HOLD_NO_PURCHASE_NO_IMPORT")

    def test_complete_two_slot_record_passes_only_to_manual_quarantine(self) -> None:
        result = self.evaluate()
        self.assertEqual(result["gate_status"], "PASS")
        self.assertEqual(result["disposition"], "READY_FOR_MANUAL_QUARANTINE_INSPECTION")
        self.assertFalse(result["automatic_purchase_allowed"])
        self.assertFalse(result["automatic_import_allowed"])
        self.assertFalse(result["runtime_promotion_allowed"])

    def test_third_asset_fails_cardinality(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"].append(copy.deepcopy(record["assets"][0]))
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_two_city_kits_fail_slot_cardinality(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][1]["slot"] = "CITY_KIT"
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_content_presence_cannot_satisfy_evidence(self) -> None:
        record = copy.deepcopy(self.record)
        evidence = record["assets"][0]["catalog"]["product_page_snapshot"]
        evidence["path"] = "Content/AlreadyThere.uasset"
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_unsafe_automatic_import_policy_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["policy"]["automatic_import_allowed"] = True
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_missing_license_and_receipt_fail(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][0]["commerce"]["license_tier"] = ""
        record["assets"][0]["commerce"]["receipt_or_acquisition_record"] = {}
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_hash_mismatch_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][0]["immutable_artifacts"][0]["sha256"] = "0" * 64
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_target_engine_must_be_confirmed(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][1]["compatibility"]["target_engine_supported"] = False
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_texture_inventory_count_must_reconcile(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][1]["texture_inventory"]["total_textures"] = 99
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_ready_status_cannot_hide_hold_disposition(self) -> None:
        record = copy.deepcopy(self.record)
        record["assets"][0]["quarantine_disposition"] = "HOLD_EVIDENCE_INCOMPLETE"
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_complete_rejection_is_valid_but_never_import_ready(self) -> None:
        record = copy.deepcopy(self.record)
        record["status"] = "EVIDENCE_COMPLETE_REJECTED"
        for asset in record["assets"]:
            asset["quarantine_disposition"] = "REJECTED_BEFORE_IMPORT"
            asset["final_disposition"] = "REJECTED"
        result = self.evaluate(record)
        self.assertEqual(result["gate_status"], "PASS")
        self.assertEqual(result["disposition"], "VALIDATED_REJECTION")

    def test_schema_source_has_required_markers(self) -> None:
        self.assertEqual(verifier.validate_schema_source(), [])
        json.loads(verifier.SCHEMA_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
