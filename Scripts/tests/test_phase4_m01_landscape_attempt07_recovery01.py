from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
UE_ROOT = Path(r"D:\UE_5.8")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY01_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class Attempt07Recovery01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )

    def test_failed_attempt07_is_exhaustively_hash_bound(self) -> None:
        failed = self.contract["immutable_failed_attempt07"]
        root = ROOT / failed["root"]
        files = sorted(path for path in root.rglob("*") if path.is_file())
        self.assertEqual(len(files), len(failed["files"]))
        expected = {
            item["file"]: item for item in failed["files"].values()
        }
        for path in files:
            relative = path.relative_to(root).as_posix()
            self.assertIn(relative, expected)
            self.assertEqual(path.stat().st_size, expected[relative]["bytes"])
            self.assertEqual(
                sha256_file(path), expected[relative]["sha256"]
            )
        manifest = json.loads(
            (root / "run_manifest.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(manifest["terminal_state"], "FAILED")
        self.assertEqual(len(manifest["stages"]), 1)
        self.assertFalse(manifest["full_capture_invoked"])
        self.assertFalse(manifest["profile_invoked"])

    def test_ue58_has_no_landscape_material_usage_flag(self) -> None:
        evidence = self.contract["ue58_source_evidence"]
        interface = (
            UE_ROOT / evidence["material_interface_header"]["file"]
        )
        self.assertEqual(
            sha256_file(interface),
            evidence["material_interface_header"]["sha256"],
        )
        source = interface.read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertNotIn("MATUSAGE_Landscape", source)
        self.assertFalse(
            evidence["material_interface_header"][
                "matusage_landscape_present"
            ]
        )

    def test_implementation_is_hash_bound_and_python_parses(self) -> None:
        for item in self.contract["implementation_files"].values():
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(sha256_file(path), item["sha256"], path)
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"))

    def test_recovery_contains_no_invalid_landscape_usage_path(self) -> None:
        names = (
            "native_header",
            "native_implementation",
            "diagnostic_builder",
            "recovery01_author",
            "recovery01_tiny_proof",
        )
        source = "\n".join(
            (ROOT / self.contract["implementation_files"][name]["file"])
            .read_text(encoding="utf-8")
            for name in names
        )
        self.assertNotIn("MATUSAGE_Landscape", source)
        self.assertNotIn("used_with_landscape", source)

    def test_native_bridge_finishes_and_validates_resources(self) -> None:
        source = (
            ROOT
            / self.contract["implementation_files"][
                "native_implementation"
            ]["file"]
        ).read_text(encoding="utf-8")
        for token in (
            "FAssetCompilingManager::Get().FinishAllCompilation()",
            "GShaderCompilingManager->FinishAllCompilation()",
            "Resource->FinishCompilation()",
            "Resource->IsCompilationFinished()",
            "Resource->GetGameThreadShaderMap()",
            "ShaderMap->IsValidForRendering()",
            "Result.ValidShaderMapResourceCount == 16",
        ):
            self.assertIn(token, source)
        section = source.split(
            "SetTransientLandscapeDiagnosticMaterialSynchronized(", 1
        )[1]
        self.assertLess(
            section.index(
                "Landscape->UpdateAllComponentMaterialInstances(true)"
            ),
            section.index(
                "FinishLandscapeMaterialCompilation(Landscape, Material)"
            ),
        )
        self.assertLess(
            section.index(
                "FinishLandscapeMaterialCompilation(Landscape, Material)"
            ),
            section.index("Component->RecreateRenderState_Concurrent()"),
        )

    def test_camera_transform_is_applied_before_proxy_configuration(self) -> None:
        helper = (
            ROOT
            / self.contract["implementation_files"][
                "attempt07_proof_helpers"
            ]["file"]
        ).read_text(encoding="utf-8")
        capture = helper.split("def capture_one(", 1)[1].split(
            "\ndef coverage_analysis", 1
        )[0]
        configure = capture.index(
            "configure_landscape_scene_capture_diagnostic"
        )
        self.assertLess(capture.index("capture.set_actor_location"), configure)
        self.assertLess(capture.index("capture.set_actor_rotation"), configure)

    def test_recovery_is_absent_and_execution_remains_unauthorized(self) -> None:
        outputs = self.contract["new_immutable_outputs"]
        for name in ("coverage_material", "component_id_material"):
            self.assertFalse((ROOT / outputs[name]["file"]).exists())
        self.assertFalse(
            (
                ROOT / self.contract["tiny_live_proof"]["execution_root"]
            ).exists()
        )
        authorization = self.contract["execution_authorization"]
        for field in (
            "unreal_launch_allowed",
            "native_build_allowed",
            "author_new_diagnostic_assets_allowed",
            "tiny_live_proof_allowed",
            "full_capture_allowed",
            "profile_allowed",
            "automatic_retry_allowed",
            "network_allowed",
            "promotion_allowed",
        ):
            self.assertFalse(authorization[field], field)

    def test_supervisor_has_only_bounded_future_stages(self) -> None:
        source = (
            ROOT
            / self.contract["implementation_files"][
                "recovery01_supervisor"
            ]["file"]
        ).read_text(encoding="utf-8")
        build = source.index('"build_native_landscape_usage_bridge"')
        author = source.index('"author_recovery01_diagnostic_materials"')
        proof = source.index('"recovery01_tiny_live_proof_d3d12_sm6"')
        self.assertLess(build, author)
        self.assertLess(author, proof)
        self.assertNotIn("capture_skyguard_phase4", source)
        self.assertNotIn("ProfileWarmupSeconds", source)


if __name__ == "__main__":
    unittest.main()
