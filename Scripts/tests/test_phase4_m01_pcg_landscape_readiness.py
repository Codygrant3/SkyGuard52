from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


GENERATOR = _load(
    "phase4_landscape_generator",
    ROOT / "Scripts/generate_skyguard_phase4_m01_landscape_source.py",
)
VERIFIER = _load(
    "phase4_pcg_landscape_verifier",
    ROOT / "Scripts/verify_skyguard_phase4_m01_pcg_landscape_readiness.py",
)


class LandscapeSourceGeneratorTests(unittest.TestCase):
    def test_governed_heightmap_is_deterministic(self) -> None:
        first = GENERATOR.generate_samples()
        second = GENERATOR.generate_samples()
        self.assertEqual(first, second)
        self.assertEqual(505 * 127, len(first))
        self.assertGreater(max(first), min(first))

    def test_binary_and_manifest_are_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "height.r16"
            manifest_path = root / "manifest.json"
            manifest = GENERATOR.write_source(output, manifest_path)
            self.assertEqual(505 * 127 * 2, output.stat().st_size)
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                manifest["sha256"],
            )
            self.assertFalse(manifest["serialized_landscape_created"])
            self.assertFalse(manifest["visible_quality_accepted"])

    def test_non_governed_dimensions_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GENERATOR.generate_samples(504, 127)


class PCGLandscapeReadinessVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_path = (
            ROOT
            / "Docs/AAA_Review"
            / "PHASE4_M01_PCG_LANDSCAPE_AUTHORING_CONTRACT.json"
        )
        cls.contract = json.loads(
            cls.contract_path.read_text(encoding="utf-8-sig")
        )

    def test_real_contract_is_integrity_green_but_not_promoted(self) -> None:
        report = VERIFIER.evaluate(ROOT, self.contract)
        self.assertEqual("PASS", report["gate"])
        self.assertIn(
            report["authoring_status"],
            {
                "READY_FOR_EDITOR_AUTHORING",
                "SERIALIZED_ASSETS_PRESENT_REQUIRES_EDITOR_GATE",
                "SERIALIZED_EDITOR_GATE_PASS",
            },
        )
        self.assertFalse(report["promotion"]["aaa_visual_acceptance"])
        self.assertFalse(
            report["promotion"]["production_vegetation_complete"]
        )

    def test_stage_reordering_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        stages = contract["graph_contract"]["required_stages_in_order"]
        stages[2], stages[3] = stages[3], stages[2]
        report = VERIFIER.evaluate(ROOT, contract)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["governed_stage_order"])

    def test_missing_route_difference_node_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["graph_contract"]["required_node_types"].remove(
            "UPCGDifferenceSettings"
        )
        report = VERIFIER.evaluate(ROOT, contract)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["governed_node_types"])

    def test_two_actor_data_nodes_are_required(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["graph_contract"]["required_node_type_counts"][
            "UPCGDataFromActorSettings"
        ] = 1
        report = VERIFIER.evaluate(ROOT, contract)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["governed_node_counts"])

    def test_licensed_slots_cannot_silently_enable_generation(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["graph_contract"]["spawn_limits"][
            "licensed_mesh_slots_must_be_nonempty_before_generation"
        ] = False
        report = VERIFIER.evaluate(ROOT, contract)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["licensed_slots_fail_closed"])


class PCGLandscapeSourceContractTests(unittest.TestCase):
    def test_director_owns_fail_closed_runtime_handoff(self) -> None:
        header = (
            ROOT
            / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h"
        ).read_text(encoding="utf-8-sig")
        cpp = (
            ROOT
            / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp"
        ).read_text(encoding="utf-8-sig")
        source = header + cpp
        for marker in (
            "InlandVegetationPCG",
            "ProductionLandscape",
            "AuthoredPCGGraph",
            "Skyguard.PCG.Inclusion",
            "Skyguard.PCG.Exclusion",
            "GenerateOnDemand",
            "bReadyForAuthoredPCGGeneration",
            "PCG_M01_InlandVegetation.PCG_M01_InlandVegetation",
            "bAuthoredPCGStructureReady",
            "bLicensedVegetationLibraryApproved",
            "bAllowAuthoredPCGGeneration",
        ):
            self.assertIn(marker, source)
        self.assertIn(
            "InlandVegetationPCG->bActivated =\n"
            "\t\t\tReadiness.bReadyForAuthoredPCGGeneration",
            cpp,
        )

    def test_build_declares_real_engine_modules(self) -> None:
        build = (ROOT / "Source/Skyguard52/Skyguard52.Build.cs").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('"Landscape"', build)
        self.assertIn('"PCG"', build)

    def test_editor_gate_is_validation_only(self) -> None:
        source = (
            ROOT
            / "Scripts/verify_skyguard_phase4_m01_pcg_landscape_assets.py"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("does_asset_exist", source)
        self.assertIn("load_level", source)
        self.assertNotIn("new_level(", source)
        self.assertNotIn("save_current_level", source)

    def test_builder_is_immutable_and_never_generates_pcg(self) -> None:
        source = (
            ROOT
            / "Scripts/build_skyguard_phase4_m01_pcg_landscape_v5.py"
        ).read_text(encoding="utf-8-sig")
        self.assertIn(
            "Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03",
            source,
        )
        self.assertIn("Immutable target already exists", source)
        self.assertIn("pcg_generation_invoked", source)
        self.assertIn('"licensed_vegetation_slots": []', source)
        self.assertNotIn(".generate_local(", source.lower())
        self.assertNotIn(".generate(", source.lower())

    def test_native_authoring_bridge_has_exact_safe_contract(self) -> None:
        header = (
            ROOT
            / "Source/Skyguard52/"
            "SkyguardMission01EnvironmentAuthoringLibrary.h"
        ).read_text(encoding="utf-8-sig")
        cpp = (
            ROOT
            / "Source/Skyguard52/"
            "SkyguardMission01EnvironmentAuthoringLibrary.cpp"
        ).read_text(encoding="utf-8-sig")
        source = header + cpp
        for marker in (
            "HeightmapWidth = 505",
            "HeightmapHeight = 127",
            "M01_P4_Landscape_Production",
            "FVector(0.f, 7000.f, -120.f)",
            "UPCGGetLandscapeSettings",
            "UPCGDataFromActorSettings",
            "UPCGSurfaceSamplerSettings",
            "UPCGDifferenceSettings",
            "UPCGDensityFilterSettings",
            "UPCGTransformPointsSettings",
            "UPCGStaticMeshSpawnerSettings",
            "WeightedSelector->MeshEntries.Reset()",
            "bLicensedVegetationLibraryApproved = false",
            "bAllowAuthoredPCGGeneration = false",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("GenerateLocal(", source)


if __name__ == "__main__":
    unittest.main()
