from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY03_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Recovery03OfflineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )

    def test_recovery02_inventory_and_compile_failure_are_immutable(self):
        item = self.contract["immutable_recovery02_failure"]
        root = ROOT / item["root"]
        self.assertEqual(3, len(item["files"]))
        for evidence in item["files"].values():
            path = root / evidence["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(evidence["bytes"], path.stat().st_size)
            self.assertEqual(evidence["sha256"], sha256_file(path))
        manifest = json.loads(
            (root / "run_manifest.json").read_text(encoding="utf-8-sig")
        )
        self.assertEqual("FAILED", manifest["terminal_state"])
        self.assertEqual(1, len(manifest["stages"]))
        self.assertEqual(6, manifest["stages"][0]["exit_code"])
        self.assertFalse(manifest["author_stage_invoked"])
        self.assertFalse(manifest["full_capture_invoked"])
        self.assertFalse(manifest["profile_invoked"])
        self.assertFalse((root / "tiny_proof_receipt.json").exists())
        log = (
            root
            / "logs/build_recovery02_deferred_material_bridge.stdout.log"
        ).read_text(encoding="utf-8-sig", errors="replace")
        for message in item["compiler_errors_required"]:
            self.assertIn(message, log)

    def test_recovery03_is_compile_activation_blocked(self):
        prerequisite = self.contract["full_module_compile_prerequisite"]
        authorization = self.contract["execution_authorization"]
        self.assertEqual(
            "REQUIRED_AND_CURRENTLY_UNSATISFIED",
            prerequisite["state"],
        )
        self.assertEqual(
            "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE",
            prerequisite["required_gate"],
        )
        self.assertFalse(prerequisite["build_or_activation_creation_allowed_by_recovery03"])
        self.assertEqual(
            "BLOCKED_PREREQUISITE_FULL_MODULE_COMPILE_PROOF_REQUIRED",
            authorization["current_state"],
        )
        self.assertFalse(authorization["native_build_allowed"])
        self.assertFalse(authorization["tiny_live_proof_allowed"])

    def test_wrapper_inherits_frozen_deferred_proof_in_new_namespace(self):
        implementation = self.contract["implementation_files"]
        frozen = ROOT / implementation["frozen_recovery02_tiny_proof"]["file"]
        wrapper = ROOT / implementation["recovery03_tiny_proof"]["file"]
        self.assertEqual(
            "5635d15262db7e7f597f62e2f8466a640bccde61088acc2a232842a713a31ffc",
            sha256_file(frozen),
        )
        text = wrapper.read_text(encoding="utf-8-sig")
        self.assertIn(
            "prove_skyguard_phase4_m01_landscape_attempt07_recovery02_tiny_live",
            text,
        )
        self.assertIn("SkyguardAttempt07Recovery03ProofRoot", text)
        self.assertIn(
            "SkyguardRecovery03CompileActivationSha256", text
        )
        self.assertEqual(
            "Saved/Profiling/Phase4/M01_LandscapeVisible_Attempt07/"
            "tiny_proof_01/recovery_03",
            self.contract["tiny_live_proof"]["execution_root"],
        )

    def test_supervisor_and_launcher_are_proof_only(self):
        implementation = self.contract["implementation_files"]
        supervisor = (
            ROOT / implementation["recovery03_supervisor"]["file"]
        ).read_text(encoding="utf-8-sig")
        launcher = (
            ROOT / implementation["recovery03_launcher"]["file"]
        ).read_text(encoding="utf-8-sig")
        combined = supervisor + "\n" + launcher
        for forbidden in (
            "Build.bat",
            "dotnet.exe",
            "build_recovery03",
            "author_recovery03",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertIn('"proof_only": True', supervisor)
        self.assertIn('"build_stage_allowed": False', supervisor)
        self.assertIn('"author_stage_allowed": False', supervisor)
        self.assertIn("UnrealEditor.exe", supervisor)
        self.assertIn("source_inventory", supervisor)
        self.assertIn("compiled_module_sha256", supervisor)

    def test_implementation_hashes_and_python_syntax(self):
        for item in self.contract["implementation_files"].values():
            path = ROOT / item["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(item["sha256"], sha256_file(path))
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8-sig"))

    def test_recovery03_has_not_run(self):
        execution_root = (
            ROOT / self.contract["tiny_live_proof"]["execution_root"]
        )
        self.assertFalse(execution_root.exists())


if __name__ == "__main__":
    unittest.main()
