from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "Scripts" / "verify_bld_m01_yak_uplift_003_r2.py"
SPEC = importlib.util.spec_from_file_location("uplift003_r2_verifier", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Uplift003R2VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._copy_source_tree()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _copy(self, relative: str) -> None:
        source = REPO_ROOT / relative
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    def _copy_source_tree(self) -> None:
        for relative in (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json",
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json",
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_SOURCE_AUDIT.json",
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json",
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json",
            "Docs/AAA_Review/BLD_M01_YAK_PROD_002_VISUAL_REVIEW.md",
            "Saved/Reports/L88_RUNTIME_ASSEMBLY_CONTRACT.json",
            "Saved/BuildAttempts/BLD_M01_YAK_UPLIFT_003/attempt_01/stderr.log",
            "Scripts/blender_l88_yak52_blockout.py",
            "Scripts/blender_bld_m01_yak_prod_002.py",
            "Scripts/blender_bld_m01_yak_uplift_003.py",
            "Scripts/blender_bld_m01_yak_uplift_003_r2.py",
            "Content/Skyguard/Meshes/Source/L88/YAK52_L88_MASTER_BLOCKOUT.blend",
            "Content/Skyguard/Meshes/Source/L88/yak52_l88_silhouette_blockout.glb",
            "Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_Beauty_FINAL.png",
            "Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_SideOrtho_FINAL.png",
            "Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_TopOrtho_FINAL.png",
            "Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_RearCockpitHero_FINAL.png",
            "Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_RearGunnerADS_FINAL.png",
        ):
            self._copy(relative)

    def _json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8-sig"))

    def _write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _refresh_contract_record(self, key: str, relative: str) -> None:
        contract_path = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        contract = self._json(contract_path)
        path = self.root / relative
        contract["immutable_sources"][key]["bytes"] = path.stat().st_size
        contract["immutable_sources"][key]["sha256"] = digest(path)
        self._write_json(contract_path, contract)

    def _refresh_overlay_record(self, key: str, relative: str) -> None:
        overlay_path = (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        overlay = self._json(overlay_path)
        path = self.root / relative
        overlay[key]["bytes"] = path.stat().st_size
        overlay[key]["sha256"] = digest(path)
        self._write_json(overlay_path, overlay)
        self._refresh_contract_record("r2_component_ledger", overlay_path)

    def _make_artifacts(self) -> dict:
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        overlay = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        base = self._json(overlay["base_ledger"]["path"])
        runtime = self._json("Saved/Reports/L88_RUNTIME_ASSEMBLY_CONTRACT.json")
        resolved = verifier.resolve_ledger(overlay, base, runtime)
        output_records = {}
        for key, payload in (
            ("blend", b"synthetic-r2-blend"),
            ("glb", b"synthetic-r2-glb"),
        ):
            path = self.root / contract["outputs"][key]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            output_records[key] = {
                "path": contract["outputs"][key],
                "bytes": len(payload),
                "sha256": digest(path),
            }
        comparisons = []
        for index, slot in enumerate(contract["matched_comparison_slots"]):
            path = self.root / slot["candidate"]
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"synthetic-r2-comparison-{index}".encode()
            path.write_bytes(payload)
            comparisons.append(
                {
                    "slot": slot["slot"],
                    "baseline": slot["baseline"],
                    "candidate": {
                        "path": slot["candidate"],
                        "bytes": len(payload),
                        "sha256": digest(path),
                    },
                }
            )
        records = []
        for item in resolved:
            if item["classification"] == "source_absent_hold":
                continue
            records.append(
                {
                    "name": item["name"],
                    "type": "MESH",
                    "uplift_class": item["classification"],
                    "promotion_allowed": False,
                    "inherited_from": "L88",
                    "governance_role": None,
                    "donor_source": None,
                }
            )
        for name in contract["required_donor_objects"]:
            records.append(
                {
                    "name": name,
                    "type": "MESH" if name.startswith("GEO_") else "EMPTY",
                    "uplift_class": "donor_from_002",
                    "promotion_allowed": False,
                    "inherited_from": None,
                    "governance_role": None,
                    "donor_source": "BLD-M01-YAK-PROD-002 Python construction",
                }
            )
        for name, spec in contract["required_safety_and_clearance_volumes"].items():
            records.append(
                {
                    "name": name,
                    "type": "EMPTY",
                    "uplift_class": None,
                    "promotion_allowed": False,
                    "inherited_from": None,
                    "governance_role": spec["role"],
                    "donor_source": None,
                }
            )
        records.append(
            {
                "name": contract["first_stage_camera"]["name"],
                "type": "CAMERA",
                "uplift_class": None,
                "promotion_allowed": False,
                "inherited_from": None,
                "governance_role": None,
                "donor_source": None,
            }
        )
        exceptions = [
            {
                "governed_name": name,
                "classification": "source_absent_hold",
                "required_as_object": False,
                "synthesized": False,
                "actual_source_name_observed": overlay["actual_source_observations"][name],
                "actual_source_object_present": True,
                "promotion_allowed": False,
            }
            for name in overlay["classification_overrides"]
        ]
        counts = Counter(item["classification"] for item in resolved)
        manifest = {
            "schema": "skyguard.bld-m01-yak-uplift-003-r2.artifact-manifest.v1",
            "build_id": verifier.BUILD_ID,
            "status": "provisional_uplift_candidate_not_accepted_not_final_not_aaa",
            "promotion_allowed": False,
            "stage_order": verifier.EXPECTED_STAGE_ORDER,
            "component_accounting": {
                "governed_total": 240,
                "exact_object_required": 232,
                "source_absent_hold": 8,
                "equation_valid": True,
            },
            "resolved_component_ledger": resolved,
            "classification_counts": dict(sorted(counts.items())),
            "source_absent_hold_records": exceptions,
            "object_records": records,
            "matched_comparisons": comparisons,
            "outputs": output_records,
            "original_l88_unchanged": True,
            "claims": {
                "final": False,
                "aaa": False,
                "unreal_accepted": False,
                "matched_visual_review_accepted": False,
            },
        }
        self._write_json(contract["outputs"]["manifest"], manifest)
        return manifest

    def test_source_gate_reconciles_232_plus_8_to_240(self) -> None:
        result = verifier.verify(self.root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["governed_component_count"], 240)
        self.assertEqual(result["exact_object_requirement_count"], 232)
        self.assertEqual(result["source_absent_hold_count"], 8)

    def test_exception_count_drift_is_rejected(self) -> None:
        relative = (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        overlay = self._json(relative)
        overlay["classification_overrides"].pop("GEO_CanopySeal_0_76_R")
        self._write_json(relative, overlay)
        self._refresh_contract_record("r2_component_ledger", relative)
        with self.assertRaisesRegex(verifier.ValidationError, "eight R2 exceptions"):
            verifier.verify(self.root)

    def test_exception_synthesis_permission_is_rejected(self) -> None:
        relative = (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        overlay = self._json(relative)
        overlay["source_absent_hold_policy"]["synthesis_allowed"] = True
        self._write_json(relative, overlay)
        self._refresh_contract_record("r2_component_ledger", relative)
        with self.assertRaisesRegex(verifier.ValidationError, "policy is unsafe"):
            verifier.verify(self.root)

    def test_actual_dotted_name_observation_drift_is_rejected(self) -> None:
        relative = (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        overlay = self._json(relative)
        overlay["actual_source_observations"]["GEO_CanopySeal_0_76_R"] = (
            "GEO_CanopySeal_WRONG"
        )
        self._write_json(relative, overlay)
        self._refresh_contract_record("r2_component_ledger", relative)
        with self.assertRaisesRegex(verifier.ValidationError, "dotted source names"):
            verifier.verify(self.root)

    def test_stage_order_drift_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        contract = self._json(relative)
        contract["required_stage_order"][0:2] = reversed(
            contract["required_stage_order"][0:2]
        )
        self._write_json(relative, contract)
        with self.assertRaisesRegex(verifier.ValidationError, "stage order"):
            verifier.verify(self.root)

    def test_r1_output_overlap_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        contract = self._json(relative)
        contract["outputs"]["blend"] = (
            "Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003/"
            "BLD_M01_YAK_UPLIFT_003_MASTER.blend"
        )
        self._write_json(relative, contract)
        with self.assertRaisesRegex(verifier.ValidationError, "not isolated|overlaps R1"):
            verifier.verify(self.root)

    def test_tampered_actual_source_inventory_is_rejected(self) -> None:
        relative = (
            "Content/Skyguard/Meshes/Source/L88/yak52_l88_silhouette_blockout.glb"
        )
        path = self.root / relative
        path.write_bytes(path.read_bytes() + b"tamper")
        with self.assertRaisesRegex(verifier.ValidationError, "byte count mismatch"):
            verifier.verify(self.root)

    def test_complete_synthetic_artifact_gate_passes(self) -> None:
        self._make_artifacts()
        result = verifier.verify(self.root, artifacts=True)
        self.assertEqual(result["mode"], "artifacts")

    def test_synthesized_absent_governed_object_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        overlay = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
        )
        name = next(iter(overlay["classification_overrides"]))
        manifest["object_records"].append(
            {
                "name": name,
                "type": "MESH",
                "uplift_class": "source_absent_hold",
                "promotion_allowed": False,
                "inherited_from": "L88",
            }
        )
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "synthesized as object"):
            verifier.verify(self.root, artifacts=True)

    def test_missing_exception_record_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        manifest["source_absent_hold_records"].pop()
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "count is not eight"):
            verifier.verify(self.root, artifacts=True)

    def test_final_claim_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        manifest["claims"]["aaa"] = True
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "acceptance/final/AAA"):
            verifier.verify(self.root, artifacts=True)

    def test_missing_matched_candidate_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        candidate = self.root / manifest["matched_comparisons"][0]["candidate"]["path"]
        candidate.unlink()
        with self.assertRaisesRegex(verifier.ValidationError, "candidate missing"):
            verifier.verify(self.root, artifacts=True)

    def test_missing_rear_gunner_camera_record_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        camera_name = contract["first_stage_camera"]["name"]
        manifest["object_records"] = [
            row for row in manifest["object_records"] if row["name"] != camera_name
        ]
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "rear-gunner camera"):
            verifier.verify(self.root, artifacts=True)

    def test_tampered_r2_glb_is_rejected(self) -> None:
        self._make_artifacts()
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
        )
        (self.root / contract["outputs"]["glb"]).write_bytes(b"tampered")
        with self.assertRaisesRegex(verifier.ValidationError, "artifact glb byte count"):
            verifier.verify(self.root, artifacts=True)


if __name__ == "__main__":
    unittest.main()
