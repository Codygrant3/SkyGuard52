from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "Docs/AAA_Review"


def load(name: str) -> dict:
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class R6OfflineGateTests(unittest.TestCase):
    def test_all_design_json_is_valid(self) -> None:
        names = [
            "PHASE2_YAK52_R6_SLICE01_CONTRACT.json",
            "PHASE2_YAK52_R6_SLICE01_DIMENSION_LEDGER.json",
            "PHASE2_YAK52_R6_SLICE01_FUSELAGE_STATIONS.json",
            "PHASE2_YAK52_R6_SLICE01_COWLING_RADIAL_LEDGER.json",
            "PHASE2_YAK52_R6_SLICE01_WING_ROOT_LEDGER.json",
            "PHASE2_YAK52_R6_SLICE01_CANOPY_KINEMATICS.json",
            "PHASE2_YAK52_R6_SLICE01_GUNNER_SIGHTLINE.json",
            "PHASE2_YAK52_R6_SLICE01_MATERIAL_SURFACE_SPEC.json",
            "PHASE2_YAK52_R6_SLICE01_TOPOLOGY_STRATEGY.json",
            "PHASE2_YAK52_R6_SLICE01_OBJECT_HIERARCHY.json",
            "PHASE2_YAK52_R6_SLICE01_CAMERAS.json",
            "PHASE2_YAK52_R6_SLICE01_ACCEPTANCE_RUBRIC.json",
            "PHASE2_YAK52_R6_SLICE01_NAMESPACE.json",
        ]
        for name in names:
            self.assertIsInstance(load(name), dict, name)

    def test_governed_dimensions_and_inference_labels(self) -> None:
        ledger = load("PHASE2_YAK52_R6_SLICE01_DIMENSION_LEDGER.json")
        values = {entry["id"]: entry for entry in ledger["measurements"]}
        self.assertEqual(values["overall_length"]["target"], 7.745)
        self.assertEqual(values["overall_length"]["tolerance"], 0.04)
        self.assertEqual(values["wingspan"]["target"], 9.3)
        self.assertEqual(values["wingspan"]["tolerance"], 0.04)
        allowed = {
            "GOVERNED_PRIOR_DIMENSION",
            "PHOTO_DERIVED_INFERENCE",
            "MECHANISM_INFERENCE",
            "UNVERIFIED_INFERENCE",
            "ERGONOMIC_INFERENCE",
        }
        self.assertTrue(all(entry["status"] in allowed for entry in values.values()))
        self.assertFalse(
            ledger["policy"]["inferred_values_may_drive_final_silhouette_acceptance"]
        )

    def test_station_loft_reaches_exact_length_datums(self) -> None:
        stations = load("PHASE2_YAK52_R6_SLICE01_FUSELAGE_STATIONS.json")[
            "stations"
        ]
        self.assertGreaterEqual(len(stations), 12)
        self.assertAlmostEqual(stations[-1]["x"] - stations[0]["x"], 7.745, places=6)
        self.assertTrue(all(stations[i]["x"] < stations[i + 1]["x"] for i in range(len(stations) - 1)))

    def test_camera_visibility_math_and_proof_fields(self) -> None:
        manifest = load("PHASE2_YAK52_R6_SLICE01_CAMERAS.json")
        self.assertGreaterEqual(len(manifest["cameras"]), 10)
        ids = {camera["id"] for camera in manifest["cameras"]}
        self.assertEqual(len(ids), len(manifest["cameras"]))
        aspect = 16.0 / 9.0
        for camera in manifest["cameras"]:
            self.assertTrue(camera["proves"], camera["id"])
            if camera["id"] == "R6_CAM_REAR_GUNNER_EYE":
                continue
            low, high = camera["screen_fraction"]
            if camera["projection"] == "PERSPECTIVE":
                distance = math.dist(camera["location"], camera["subject_center"])
                fraction = (
                    2.0
                    * camera["lens_mm"]
                    * camera["subject_radius_m"]
                    / (distance * manifest["render"]["sensor_width_mm"])
                )
            elif "horizontal_subject_extent_m" in camera:
                fraction = camera["horizontal_subject_extent_m"] / (
                    camera["ortho_scale_m"] * aspect
                )
            else:
                fraction = (
                    camera["vertical_subject_extent_m"] / camera["ortho_scale_m"]
                )
            self.assertGreaterEqual(fraction, low, camera["id"])
            self.assertLessEqual(fraction, high, camera["id"])

    def test_gunner_and_canopy_contracts_are_bounded(self) -> None:
        gunner = load("PHASE2_YAK52_R6_SLICE01_GUNNER_SIGHTLINE.json")
        canopy = load("PHASE2_YAK52_R6_SLICE01_CANOPY_KINEMATICS.json")
        self.assertEqual(
            gunner["offline_camera_ray_tests"]["required_sample_count"], 81
        )
        self.assertGreaterEqual(
            gunner["offline_camera_ray_tests"]["required_unobstructed_samples"], 77
        )
        self.assertGreaterEqual(
            canopy["rear_canopy"]["minimum_clear_opening_length_m"], 0.72
        )
        self.assertGreaterEqual(
            canopy["rear_canopy"]["minimum_clear_opening_width_m"], 0.78
        )

    def test_r6_paths_are_reserved_and_absent(self) -> None:
        namespace = load("PHASE2_YAK52_R6_SLICE01_NAMESPACE.json")
        for key in ("blender_directory", "blend", "glb", "manifest", "renders", "attempt_root"):
            self.assertFalse((ROOT / namespace[key]).exists(), key)
        self.assertFalse(namespace["unreal_import_authorized"])

    def test_immutable_inputs_and_user_references_match(self) -> None:
        expected = {
            ROOT / "Scripts/blender_phase2_yak52_r5_slice01.py":
                "446b4e8d71457b2f9bac3798c22b82fec212e89161ec30c7d2d800683fdfa1f2",
            ROOT / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R4/Slice01_Recovery05/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY05_MASTER.blend":
                "a7694e012e1dbdef06c432919f2a93d62ec3845c888506fe7019ef81aeb2f30e",
            Path(r"C:\Users\chris\AppData\Local\Temp\codex-clipboard-04e14908-5ac0-4988-9eec-9d32e74a2ee0.png"):
                "390162ac3d3c73c0567bcf822de2363908b27de9ea79b7796c6bcca143c41f5d",
            Path(r"C:\Users\chris\AppData\Local\Temp\codex-clipboard-47bf0604-6525-4282-9149-45cffde4f397.png"):
                "ab80a7d0c7327f4b27c22df7d0c9fb881aeef836b0f7a2a98fb51a201a8b46fd",
            Path(r"C:\Users\chris\AppData\Local\Temp\codex-clipboard-84f46082-7b3b-4a5c-b86b-9cb4c43d8a56.png"):
                "717a6724360032e296b5a91ca1928aa4d67148a9187cc86fca046a88afbb908c",
            Path(r"C:\Users\chris\AppData\Local\Temp\codex-clipboard-1c5365d0-9eff-481d-81ad-4b1edc038620.png"):
                "23a63dfff5cad7b052321fdf341d845d777b55bae913b6f116f6af9541ddb366",
        }
        for path, digest in expected.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(sha256(path), digest, path)

    def test_readiness_must_remain_reference_blocked(self) -> None:
        contract = load("PHASE2_YAK52_R6_SLICE01_CONTRACT.json")
        rubric = load("PHASE2_YAK52_R6_SLICE01_ACCEPTANCE_RUBRIC.json")
        self.assertFalse(contract["execution_policy"]["this_contract_authorizes_blender"])
        self.assertFalse(contract["claims"]["reference_locked"])
        reference_gate = next(gate for gate in rubric["gates"] if gate["id"] == "references")
        self.assertTrue(reference_gate["current"].startswith("FAIL_"))


if __name__ == "__main__":
    unittest.main()

