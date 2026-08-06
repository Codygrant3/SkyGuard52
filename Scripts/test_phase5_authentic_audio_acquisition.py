"""Mutation tests for the authentic-audio acquisition/import boundary."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_authentic_audio_acquisition.py"
SPEC = importlib.util.spec_from_file_location("authentic_audio_gate", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class AuthenticAudioAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(VERIFIER.SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(
            VERIFIER.MANIFEST_PATH.read_text(encoding="utf-8")
        )

    def validate(self, manifest):
        return VERIFIER.validate(self.schema, manifest)[0]

    def make_importable_shell(self, category="EngineIdle"):
        manifest = copy.deepcopy(self.manifest)
        entry = next(
            item for item in manifest["entries"] if item["category_id"] == category
        )
        entry["acquisition_state"] = "APPROVED_FOR_GOVERNED_IMPORT"
        return manifest, entry

    def test_empty_manifest_is_structurally_valid_and_blocked(self):
        errors, importable = VERIFIER.validate(self.schema, self.manifest)
        self.assertEqual([], errors)
        self.assertEqual(0, importable)

    def test_importable_rejects_missing_license_evidence(self):
        manifest, _ = self.make_importable_shell()
        errors = self.validate(manifest)
        self.assertTrue(any("license" in error for error in errors))

    def test_importable_rejects_missing_source_hash(self):
        manifest, entry = self.make_importable_shell()
        entry["source"]["original_filename"] = "source.wav"
        entry["source"]["original_sha256"] = "not-a-hash"
        errors = self.validate(manifest)
        self.assertTrue(any("source SHA-256" in error for error in errors))

    def test_importable_rejects_raw_redistribution_risk(self):
        manifest, entry = self.make_importable_shell()
        entry["distribution_risk"]["standalone_redistribution_allowed"] = True
        errors = self.validate(manifest)
        self.assertTrue(any("standalone redistribution" in error for error in errors))

    def test_importable_rejects_unverified_recorder_metadata(self):
        manifest, entry = self.make_importable_shell()
        entry["semantic"]["metadata_verified"] = False
        errors = self.validate(manifest)
        self.assertTrue(any("metadata is not verified" in error for error in errors))

    def test_open_canopy_requires_specific_evidence(self):
        manifest, entry = self.make_importable_shell("OpenCockpitWind")
        entry["semantic"]["open_canopy_claim"] = True
        entry["semantic"]["recorded_subject"] = "generic aircraft"
        entry["semantic"]["listener_perspective"] = "Exterior"
        errors = self.validate(manifest)
        self.assertTrue(any("canopy opening fraction" in error for error in errors))
        self.assertTrue(any("documented airspeed" in error for error in errors))
        self.assertTrue(any("not RearCockpit" in error for error in errors))
        self.assertTrue(any("not verified Yak-52" in error for error in errors))

    def test_missing_state_cannot_smuggle_source_evidence(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["entries"][0]["source"]["original_sha256"] = "a" * 64
        errors = self.validate(manifest)
        self.assertTrue(any("empty-state source is not empty" in error for error in errors))

    def test_all_twenty_five_bank_bindings_are_governed_once(self):
        bindings = [
            binding
            for entry in self.manifest["entries"]
            for binding in entry["bank_bindings"]
        ]
        expected = set().union(*VERIFIER.EXPECTED_BINDINGS.values())
        self.assertEqual(25, len(bindings))
        self.assertEqual(25, len(set(bindings)))
        self.assertEqual(expected, set(bindings))

    def test_importable_rejects_lossy_or_unmetered_derivative(self):
        manifest, entry = self.make_importable_shell()
        entry["derivative"].update(
            {
                "filename": "preview.mp3",
                "sample_rate_hz": 44100,
                "bit_depth": 16,
                "channels": 6,
                "true_peak_dbtp": -0.1,
                "clipped_sample_count": 12,
            }
        )
        errors = self.validate(manifest)
        self.assertTrue(any("must be a WAV" in error for error in errors))
        self.assertTrue(any("must be 48000" in error for error in errors))
        self.assertTrue(any("bit depth must be 24" in error for error in errors))
        self.assertTrue(any("mono or stereo" in error for error in errors))
        self.assertTrue(any("exceeds -3 dBTP" in error for error in errors))
        self.assertTrue(any("clipped samples" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
