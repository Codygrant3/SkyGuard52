from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(r"D:\Skyguard52")
DOC_ROOT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08"


class ToolchainWave08Contracts(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((DOC_ROOT / name).read_text(encoding="utf-8"))

    def test_lanes_use_unique_fresh_roots(self) -> None:
        contracts = [
            self.load("character_prototype_contract.json"),
            self.load("audio_prototype_contract.json"),
            self.load("environment_prototype_contract.json"),
        ]
        self.assertEqual(3, len({item["target_root"] for item in contracts}))
        self.assertEqual(3, len({item["attempt_root"] for item in contracts}))
        for item in contracts:
            self.assertFalse(pathlib.Path(item["target_root"]).exists())
            self.assertFalse(pathlib.Path(item["attempt_root"]).exists())

    def test_only_environment_copies_content(self) -> None:
        character = self.load("character_prototype_contract.json")
        audio = self.load("audio_prototype_contract.json")
        environment = self.load("environment_prototype_contract.json")
        self.assertFalse(character["copy_content"])
        self.assertFalse(audio["copy_content"])
        self.assertTrue(environment["copy_content"])
        self.assertTrue(character["drop_runtime_modules"])
        self.assertTrue(audio["drop_runtime_modules"])
        self.assertFalse(environment["drop_runtime_modules"])
        self.assertFalse(character["copy_source"])
        self.assertFalse(audio["copy_plugins"])
        self.assertTrue(environment["copy_source"])
        self.assertTrue(environment["copy_plugins"])
        self.assertTrue(environment["copy_binaries"])

    def test_canonical_plugin_states_are_not_authorized_for_mutation(self) -> None:
        for name in (
            "character_prototype_contract.json",
            "audio_prototype_contract.json",
            "environment_prototype_contract.json",
        ):
            contract = self.load(name)
            prohibitions = " ".join(contract["prohibitions"]).lower()
            self.assertIn("canonical", prohibitions)

    def test_no_external_or_generated_geometry(self) -> None:
        character = self.load("character_prototype_contract.json")
        joined = " ".join(character["prohibitions"]).lower()
        self.assertIn("no external models", joined)
        self.assertIn("no generated geometry", joined)

    def test_environment_map_has_distinct_future_package(self) -> None:
        environment = self.load("environment_prototype_contract.json")
        self.assertNotEqual(environment["source_map_asset"], environment["future_clone_asset"])
        self.assertTrue(environment["future_clone_asset"].startswith("/Game/ToolchainWave08/"))


if __name__ == "__main__":
    unittest.main()
