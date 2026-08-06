from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_m01_third_party_final_use_receipt import (  # noqa: E402
    READY_DISPOSITION,
    READY_STATUS,
    REQUIRED_POLICY,
    REQUIRED_ASSERTIONS,
    SCHEMA,
    validate_record,
)


class FinalUseReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def artifact(self, relative: str, payload: bytes | None = None) -> dict:
        data = payload if payload is not None else relative.encode("utf-8")
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {
            "path": relative.replace("\\", "/"),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    def valid_asset(self, suffix: str = "001") -> dict:
        evidence_prefix = f"Saved/Evidence/{suffix}"
        return {
            "asset_record_id": f"M01-FAB-{suffix}",
            "provider": "FAB",
            "source_identity": {
                "product_or_asset_id": f"product-{suffix}",
                "asset_name": "Licensed Coastal Support Kit",
                "creator_or_publisher": "Example Publisher",
                "source_url": "https://example.invalid/fab/product",
                "version": "5.8-r1",
            },
            "license": {
                "license_name": "Fab Standard License",
                "license_tier": "Recorded tier",
                "acquired_at": "2026-08-04T12:00:00+00:00",
                "cooked_windows_redistribution_covered": True,
                "license_snapshot": self.artifact(
                    f"{evidence_prefix}/license.txt"
                ),
                "acquisition_record": self.artifact(
                    f"{evidence_prefix}/acquisition.json"
                ),
            },
            "source_inventory": self.artifact(
                f"{evidence_prefix}/source_inventory.json"
            ),
            "project_assets": [
                {
                    "game_package_path":
                        f"/Game/Skyguard/Environment/M01/SM_Coast_{suffix}",
                    "asset_class": "StaticMesh",
                    "project_file": self.artifact(
                        f"Content/Skyguard/Environment/M01/SM_Coast_{suffix}.uasset"
                    ),
                }
            ],
            "mission_uses": [
                {
                    "mission_id": "M01",
                    "map_path": "/Game/Skyguard/Maps/M01_CoastalIntercept",
                    "purpose": "Mid-distance coastal support art",
                    "visibility_zone": "MID",
                }
            ],
            "modifications": ["Material instances recalibrated for Skyguard."],
            "dependencies": {
                "items": [],
                "evidence": self.artifact(
                    f"{evidence_prefix}/dependencies.json"
                ),
            },
            "acceptance": {
                "intake_record": self.artifact(
                    f"{evidence_prefix}/intake.json"
                ),
                "technical_evaluation": self.artifact(
                    f"{evidence_prefix}/technical.json"
                ),
                "visual_acceptance": self.artifact(
                    f"{evidence_prefix}/visual.json"
                ),
                "performance_acceptance": self.artifact(
                    f"{evidence_prefix}/performance.json"
                ),
            },
            "release": {
                "shipping_notice_required": False,
                "shipping_notice": None,
                "ship_original_source_files": False,
                "redistribution_constraints": [
                    "Redistribute only as cooked game content."
                ],
            },
            "final_disposition": "ACCEPTED_FOR_M01_FINAL_CANDIDATE",
        }

    def valid_record(self) -> dict:
        return {
            "schema": SCHEMA,
            "receipt_id": "M01-THIRD-PARTY-FINAL-USE-TEST",
            "status": READY_STATUS,
            "project_root": str(self.root),
            "candidate": {
                "candidate_id": "M01-RC-TEST",
                "package_or_build_artifact": self.artifact(
                    "Saved/Releases/M01/test-package.zip"
                ),
            },
            "policy": dict(REQUIRED_POLICY),
            "assets": [self.valid_asset()],
            "final_assertions": {
                field: True for field in REQUIRED_ASSERTIONS
            },
            "final_disposition": READY_DISPOSITION,
        }

    def codes(self, record: dict) -> set[str]:
        return {
            item["code"]
            for item in validate_record(record, self.root)
        }

    def test_valid_record_passes(self) -> None:
        self.assertEqual(validate_record(self.valid_record(), self.root), [])

    def test_template_state_fails_closed(self) -> None:
        record = self.valid_record()
        record["status"] = "EVIDENCE_INCOMPLETE_FAIL_CLOSED"
        record["assets"] = []
        record["final_disposition"] = "HOLD_NO_RUNTIME_PROMOTION"
        for field in record["final_assertions"]:
            record["final_assertions"][field] = False
        codes = self.codes(record)
        self.assertIn("NOT_READY", codes)
        self.assertIn("NO_FINAL_USE_ASSETS", codes)
        self.assertIn("ASSERTION_NOT_PROVEN", codes)

    def test_project_file_hash_mismatch_fails(self) -> None:
        record = self.valid_record()
        record["assets"][0]["project_assets"][0]["project_file"][
            "sha256"
        ] = "0" * 64
        self.assertIn("SHA256_MISMATCH", self.codes(record))

    def test_quarantine_reference_fails(self) -> None:
        record = self.valid_record()
        record["assets"][0]["project_assets"][0][
            "game_package_path"
        ] = "/Game/Skyguard/Quarantine/M01/City/SM_Test"
        self.assertIn("QUARANTINE_REFERENCE_FORBIDDEN", self.codes(record))

    def test_missing_mission_use_fails(self) -> None:
        record = self.valid_record()
        record["assets"][0]["mission_uses"][0]["mission_id"] = "M02"
        self.assertIn("M01_USE_NOT_PROVEN", self.codes(record))

    def test_missing_visual_acceptance_fails(self) -> None:
        record = self.valid_record()
        record["assets"][0]["acceptance"]["visual_acceptance"] = {
            "path": "",
            "bytes": 0,
            "sha256": "",
        }
        self.assertIn("INVALID_EVIDENCE_PATH", self.codes(record))

    def test_duplicate_asset_id_fails(self) -> None:
        record = self.valid_record()
        duplicate = deepcopy(record["assets"][0])
        record["assets"].append(duplicate)
        self.assertIn("DUPLICATE_ASSET_RECORD_ID", self.codes(record))

    def test_invalid_acquisition_timestamp_fails(self) -> None:
        record = self.valid_record()
        record["assets"][0]["license"]["acquired_at"] = "2026-08-04"
        self.assertIn("INVALID_ACQUISITION_TIMESTAMP", self.codes(record))

    def test_runtime_promotion_policy_cannot_be_preapproved(self) -> None:
        record = self.valid_record()
        record["policy"]["runtime_promotion_allowed"] = True
        self.assertIn("INVALID_POLICY_VALUE", self.codes(record))


if __name__ == "__main__":
    unittest.main()
