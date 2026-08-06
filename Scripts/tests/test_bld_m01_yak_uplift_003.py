from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "Scripts" / "verify_bld_m01_yak_uplift_003.py"
SPEC = importlib.util.spec_from_file_location("uplift003_verifier", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Uplift003VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._copy_governed_source_tree()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _copy(self, relative: str) -> None:
        source = REPO_ROOT / relative
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    def _copy_governed_source_tree(self) -> None:
        for relative in (
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json",
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json",
            "Docs/AAA_Review/BLD_M01_YAK_PROD_002_VISUAL_REVIEW.md",
            "Saved/Reports/L88_RUNTIME_ASSEMBLY_CONTRACT.json",
            "Scripts/blender_bld_m01_yak_prod_002.py",
            "Scripts/blender_bld_m01_yak_uplift_003.py",
            "Content/Skyguard/Meshes/Source/L88/YAK52_L88_MASTER_BLOCKOUT.blend",
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
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _make_artifacts(self) -> dict:
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        ledger = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
        )
        runtime = self._json("Saved/Reports/L88_RUNTIME_ASSEMBLY_CONTRACT.json")
        resolved = verifier.resolve_component_ledger(ledger, runtime)

        output_records = {}
        for key, payload in (("blend", b"synthetic-uplift-blend"), ("glb", b"synthetic-uplift-glb")):
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
            payload = f"synthetic-comparison-{index}".encode()
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

        object_records = [
            {
                "name": item["name"],
                "type": "MESH",
                "uplift_class": item["classification"],
                "promotion_allowed": False,
                "inherited_from": "L88",
                "governance_role": None,
                "donor_source": None,
            }
            for item in resolved
        ]
        for name in contract["required_donor_objects"]:
            object_records.append(
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
            object_records.append(
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
        object_records.append(
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
        manifest = {
            "schema": "skyguard.bld-m01-yak-uplift-003.artifact-manifest.v1",
            "build_id": verifier.BUILD_ID,
            "status": "provisional_uplift_candidate_not_accepted_not_final_not_aaa",
            "promotion_allowed": False,
            "stage_order": verifier.EXPECTED_STAGE_ORDER,
            "outputs": output_records,
            "resolved_component_ledger": resolved,
            "classification_counts": dict(
                sorted(Counter(item["classification"] for item in resolved).items())
            ),
            "object_records": object_records,
            "matched_comparisons": comparisons,
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

    def test_source_contract_and_full_240_part_ledger_pass(self) -> None:
        result = verifier.verify(self.root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["component_count"], 240)
        self.assertEqual(set(result["classification_counts"]), verifier.ALLOWED_CLASSIFICATIONS)

    def test_unknown_component_override_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
        ledger = self._json(relative)
        ledger["component_overrides"]["GEO_NOT_IN_L88"] = "hold"
        self._write_json(relative, ledger)
        with self.assertRaisesRegex(verifier.ValidationError, "Unknown component overrides"):
            verifier.verify(self.root)

    def test_unknown_bundle_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
        ledger = self._json(relative)
        ledger["bundle_defaults"].pop("Weapon_Rifle")
        self._write_json(relative, ledger)
        with self.assertRaisesRegex(verifier.ValidationError, "Unknown bundle"):
            verifier.verify(self.root)

    def test_silent_promotion_policy_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
        ledger = self._json(relative)
        ledger["classification_policy"]["hold"]["promotion_allowed"] = True
        self._write_json(relative, ledger)
        with self.assertRaisesRegex(verifier.ValidationError, "silently promote"):
            verifier.verify(self.root)

    def test_incorrect_stage_order_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        contract = self._json(relative)
        contract["required_stage_order"][0:2] = reversed(
            contract["required_stage_order"][0:2]
        )
        self._write_json(relative, contract)
        with self.assertRaisesRegex(verifier.ValidationError, "stage order"):
            verifier.verify(self.root)

    def test_missing_camera_clearance_volume_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        contract = self._json(relative)
        contract["required_safety_and_clearance_volumes"].pop(
            "VOL_UPLIFT003_CameraClearance"
        )
        self._write_json(relative, contract)
        with self.assertRaisesRegex(verifier.ValidationError, "volumes drifted"):
            verifier.verify(self.root)

    def test_donor_component_without_replacement_mapping_is_rejected(self) -> None:
        relative = "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
        ledger = self._json(relative)
        ledger["donor_replacement_map"].pop("GEO_PropHub")
        self._write_json(relative, ledger)
        with self.assertRaisesRegex(verifier.ValidationError, "lack replacement mapping"):
            verifier.verify(self.root)

    def test_complete_synthetic_artifact_gate_passes(self) -> None:
        self._make_artifacts()
        result = verifier.verify(self.root, artifacts=True)
        self.assertEqual(result["mode"], "artifacts")
        self.assertEqual(result["matched_comparison_slots"], 5)

    def test_missing_matched_candidate_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        candidate_path = self.root / manifest["matched_comparisons"][2]["candidate"]["path"]
        candidate_path.unlink()
        with self.assertRaisesRegex(verifier.ValidationError, "candidate missing"):
            verifier.verify(self.root, artifacts=True)

    def test_tampered_glb_is_rejected(self) -> None:
        self._make_artifacts()
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        (self.root / contract["outputs"]["glb"]).write_bytes(b"tampered")
        with self.assertRaisesRegex(verifier.ValidationError, "artifact glb byte count mismatch"):
            verifier.verify(self.root, artifacts=True)

    def test_tampered_immutable_l88_source_is_rejected(self) -> None:
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        path = self.root / contract["immutable_sources"]["l88_blend"]["path"]
        path.write_bytes(path.read_bytes() + b"tamper")
        with self.assertRaisesRegex(verifier.ValidationError, "l88_blend byte count mismatch"):
            verifier.verify(self.root)

    def test_artifact_silent_promotion_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        manifest["object_records"][0]["promotion_allowed"] = True
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "Silent promotion detected"):
            verifier.verify(self.root, artifacts=True)

    def test_artifact_final_claim_is_rejected(self) -> None:
        manifest = self._make_artifacts()
        manifest["claims"]["final"] = True
        contract = self._json(
            "Docs/AAA_Review/BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
        )
        self._write_json(contract["outputs"]["manifest"], manifest)
        with self.assertRaisesRegex(verifier.ValidationError, "claims acceptance"):
            verifier.verify(self.root, artifacts=True)


if __name__ == "__main__":
    unittest.main()
