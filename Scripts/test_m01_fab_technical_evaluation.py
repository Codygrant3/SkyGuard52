"""Mutation tests for the M01 acquired-kit technical evaluation gate."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_m01_fab_staging_inventory as inventory_builder
import verify_m01_fab_quarantine_intake as intake_verifier
import verify_m01_fab_technical_evaluation as verifier


class FabTechnicalEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.record = json.loads(
            verifier.TEMPLATE_PATH.read_text(encoding="utf-8")
        )
        intake = self._ready_intake()
        intake_path = self.root / (
            verifier.EVIDENCE_PREFIX + "intake_record.json"
        )
        intake_path.parent.mkdir(parents=True, exist_ok=True)
        intake_path.write_text(
            json.dumps(intake, indent=2), encoding="utf-8"
        )
        self.record["intake_record"] = self._existing_evidence(intake_path)
        self.record["status"] = (
            "ACQUIRED_READY_FOR_MANUAL_QUARANTINE_IMPORT"
        )
        for index, slot_record in enumerate(self.record["slots"]):
            slot = slot_record["slot"]
            payload = self.root / inventory_builder.SLOT_ROOTS[slot]
            payload.mkdir(parents=True, exist_ok=True)
            (payload / f"asset_{index}.uasset").write_bytes(
                f"manual payload {slot}".encode("utf-8")
            )
            dependency = self._evidence(f"{slot}_dependencies.txt")
            slot_record["dependencies"]["evidence"] = dependency
            slot_record["dependencies"]["items"] = []
            self._refresh_inventory(slot_record)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _evidence(self, label: str) -> dict:
        path = self.root / (verifier.EVIDENCE_PREFIX + label)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"evidence for {label}\n".encode("utf-8"))
        return self._existing_evidence(path)

    def _existing_evidence(self, path: Path) -> dict:
        payload = path.read_bytes()
        return {
            "path": path.relative_to(self.root).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def _ready_intake(self) -> dict:
        intake = json.loads(
            intake_verifier.TEMPLATE_PATH.read_text(encoding="utf-8")
        )
        intake["status"] = (
            "EVIDENCE_COMPLETE_READY_FOR_MANUAL_QUARANTINE_INSPECTION"
        )
        for index, asset in enumerate(intake["assets"]):
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
            asset["storage"].update({
                "download_bytes": 1000 + index,
                "installed_bytes": 2000 + index,
            })
            asset["texture_inventory"].update({
                "total_textures": 2,
                "resolutions": [{
                    "width": 2048,
                    "height": 2048,
                    "count": 2,
                    "formats": ["PNG"],
                    "usage": ["BaseColor", "Normal"],
                }],
            })
            asset["dependencies"]["items"] = []
            asset["quarantine_disposition"] = (
                "APPROVED_FOR_MANUAL_QUARANTINE_INSPECTION"
            )
            asset["final_disposition"] = (
                "QUARANTINE_ONLY_NOT_RUNTIME_APPROVED"
            )
            prefix = f"intake_asset_{index}"
            asset["catalog"]["product_page_snapshot"] = self._evidence(
                prefix + "_product.txt"
            )
            asset["commerce"]["license_text_snapshot"] = self._evidence(
                prefix + "_license.txt"
            )
            asset["commerce"]["receipt_or_acquisition_record"] = (
                self._evidence(prefix + "_receipt.txt")
            )
            asset["compatibility"]["evidence"] = self._evidence(
                prefix + "_compatibility.txt"
            )
            asset["storage"]["download_package"] = self._evidence(
                prefix + "_download.txt"
            )
            asset["storage"]["installed_inventory_manifest"] = (
                self._evidence(prefix + "_installed.txt")
            )
            asset["texture_inventory"]["inventory_evidence"] = (
                self._evidence(prefix + "_textures.txt")
            )
            for feature in intake_verifier.FEATURES:
                asset["runtime_features"][feature]["evidence"] = (
                    self._evidence(prefix + f"_{feature}.txt")
                )
            asset["dependencies"]["inventory_evidence"] = self._evidence(
                prefix + "_dependencies.txt"
            )
            asset["immutable_artifacts"] = [
                self._evidence(prefix + "_immutable.txt")
            ]
        return intake

    def _refresh_inventory(self, slot_record: dict) -> None:
        slot = slot_record["slot"]
        manifest = inventory_builder.build_inventory(self.root, slot)
        path = self.root / inventory_builder.OUTPUTS[slot]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        slot_record["staging"]["inventory_manifest"] = (
            self._existing_evidence(path)
        )

    def _add_import_results(self, slot_record: dict) -> None:
        slot = slot_record["slot"]
        destination = verifier.DESTINATIONS[slot]
        token = verifier.NAME_TOKENS[slot]
        contract = slot_record["unreal_contract"]
        master = f"{destination}/M_{token}_Master"
        instance = f"{destination}/MI_{token}_Primary"
        texture = f"{destination}/T_{token}_BaseColor"
        contract["import_status"] = "QUARANTINE_IMPORTED"
        contract["asset_registry_evidence"] = self._evidence(
            f"{slot}_asset_registry.txt"
        )
        contract["meshes"] = [{
            "object_path": f"{destination}/SM_{token}_Hero",
            "triangle_count": 120000,
            "nanite_enabled": True,
            "lod_count": 1,
            "collision": "CUSTOM_UCX",
            "foreground": True,
            "material_slots": [instance],
        }]
        contract["materials"] = [
            {
                "object_path": master,
                "kind": "MASTER",
                "parent_material": None,
                "blend_mode": "OPAQUE",
                "shader_complexity": "MEDIUM",
                "texture_references": [texture],
            },
            {
                "object_path": instance,
                "kind": "INSTANCE",
                "parent_material": master,
                "blend_mode": "OPAQUE",
                "shader_complexity": "LOW",
                "texture_references": [texture],
            },
        ]

    def evaluate(self, record: dict | None = None) -> dict:
        return verifier.evaluate(record or self.record, self.root)

    def test_template_fails_closed(self) -> None:
        template = json.loads(
            verifier.TEMPLATE_PATH.read_text(encoding="utf-8")
        )
        result = verifier.evaluate(template)
        self.assertEqual(result["gate_status"], "FAIL_CLOSED")
        self.assertEqual(
            result["disposition"], "HOLD_NO_IMPORT_NO_PROMOTION"
        )

    def test_acquired_two_slot_record_reaches_only_manual_import(self) -> None:
        result = self.evaluate()
        self.assertEqual(result["gate_status"], "PASS")
        self.assertEqual(
            result["disposition"], "READY_FOR_MANUAL_QUARANTINE_IMPORT"
        )
        self.assertFalse(result["automatic_import_allowed"])
        self.assertFalse(result["runtime_promotion_allowed"])

    def test_complete_technical_results_reach_visual_review_only(self) -> None:
        record = copy.deepcopy(self.record)
        record["status"] = "TECHNICAL_EVALUATION_COMPLETE"
        for slot_record in record["slots"]:
            self._add_import_results(slot_record)
        result = self.evaluate(record)
        self.assertEqual(result["gate_status"], "PASS")
        self.assertEqual(result["disposition"], "READY_FOR_VISUAL_REVIEW")
        self.assertFalse(result["runtime_promotion_allowed"])

    def test_third_kit_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["slots"].append(copy.deepcopy(record["slots"][0]))
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_staging_mutation_breaks_tree_hash(self) -> None:
        record = copy.deepcopy(self.record)
        slot = record["slots"][0]["slot"]
        payload = self.root / inventory_builder.SLOT_ROOTS[slot]
        (payload / "late_mutation.uasset").write_bytes(b"changed")
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_executable_payload_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        slot_record = record["slots"][0]
        payload = self.root / inventory_builder.SLOT_ROOTS[slot_record["slot"]]
        (payload / "unexpected.dll").write_bytes(b"binary")
        self._refresh_inventory(slot_record)
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_dependency_outside_allowlist_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["slots"][0]["dependencies"]["items"] = [{
            "object_path": "/Game/UntrackedVendor/Material",
            "kind": "Material",
            "approved": True,
        }]
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_wrong_unreal_destination_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["slots"][0]["unreal_contract"]["destination_root"] = (
            "/Game/Skyguard/Production/City"
        )
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_imported_mesh_requires_nanite_or_authored_lods(self) -> None:
        record = copy.deepcopy(self.record)
        record["status"] = "TECHNICAL_EVALUATION_COMPLETE"
        for slot_record in record["slots"]:
            self._add_import_results(slot_record)
        mesh = record["slots"][0]["unreal_contract"]["meshes"][0]
        mesh["nanite_enabled"] = False
        mesh["lod_count"] = 1
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_foreground_complex_collision_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["status"] = "TECHNICAL_EVALUATION_COMPLETE"
        for slot_record in record["slots"]:
            self._add_import_results(slot_record)
        record["slots"][1]["unreal_contract"]["meshes"][0][
            "collision"
        ] = "COMPLEX_AS_SIMPLE"
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_material_naming_and_texture_containment_are_enforced(self) -> None:
        record = copy.deepcopy(self.record)
        record["status"] = "TECHNICAL_EVALUATION_COMPLETE"
        for slot_record in record["slots"]:
            self._add_import_results(slot_record)
        material = record["slots"][0]["unreal_contract"]["materials"][1]
        material["object_path"] = "/Game/Outside/BadMaterial"
        material["texture_references"] = ["/Game/Outside/BadTexture"]
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_unready_intake_cannot_unlock_technical_gate(self) -> None:
        record = copy.deepcopy(self.record)
        intake_path = self.root / record["intake_record"]["path"]
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
        intake["assets"][0]["commerce"]["license_tier"] = ""
        intake_path.write_text(json.dumps(intake), encoding="utf-8")
        record["intake_record"] = self._existing_evidence(intake_path)
        self.assertEqual(self.evaluate(record)["gate_status"], "FAIL_CLOSED")

    def test_schema_source_has_required_markers(self) -> None:
        self.assertEqual(verifier.validate_schema_source(), [])
        json.loads(verifier.SCHEMA_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
