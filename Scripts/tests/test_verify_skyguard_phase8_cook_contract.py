from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase8_cook_contract.py"
)
SPEC = importlib.util.spec_from_file_location("cook_contract", MODULE_PATH)
COOK_CONTRACT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(COOK_CONTRACT)


class CookContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.default_game = self.root / "Config" / "DefaultGame.ini"
        self.matrix = self.root / "matrix.json"
        self.maps = [
            f"/Game/Skyguard/Maps/Lvl_M{index:02d}_Mission_{index:02d}"
            for index in range(1, 11)
        ]
        self.default_game.parent.mkdir(parents=True)
        self.write_matrix(self.maps)
        self.write_config(self.maps)
        for package_path in self.maps:
            source = COOK_CONTRACT.source_umap(self.root, package_path)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(b"umap")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_matrix(self, maps: list[str]) -> None:
        payload = {
            "required_mission_count": 10,
            "missions": [
                {"id": f"M{index:02d}", "map": package_path}
                for index, package_path in enumerate(maps, 1)
            ],
        }
        self.matrix.write_text(json.dumps(payload), encoding="utf-8")

    def write_config(self, maps: list[str]) -> None:
        lines = ["[/Script/UnrealEd.ProjectPackagingSettings]"]
        lines.extend(f'+MapsToCook=(FilePath="{path}")' for path in maps)
        self.default_game.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_clean_preflight_passes(self) -> None:
        report = COOK_CONTRACT.evaluate_preflight(
            self.root, self.default_game, self.matrix
        )
        self.assertEqual("PASS", report["gate"])

    def test_missing_config_path_fails(self) -> None:
        self.write_config(self.maps[:-1])
        report = COOK_CONTRACT.evaluate_preflight(
            self.root, self.default_game, self.matrix
        )
        self.assertEqual("FAIL", report["gate"])
        self.assertEqual([self.maps[-1]], report["missing_from_config"])

    def test_duplicate_config_path_fails(self) -> None:
        self.write_config(self.maps[:-1] + [self.maps[0]])
        report = COOK_CONTRACT.evaluate_preflight(
            self.root, self.default_game, self.matrix
        )
        self.assertEqual("FAIL", report["gate"])
        self.assertEqual([self.maps[0]], report["duplicate_config_paths"])

    def test_stale_config_path_fails(self) -> None:
        stale = "/Game/Skyguard/Maps/Lvl_M10_Stale"
        self.write_config(self.maps[:-1] + [stale])
        report = COOK_CONTRACT.evaluate_preflight(
            self.root, self.default_game, self.matrix
        )
        self.assertEqual("FAIL", report["gate"])
        self.assertEqual([stale], report["stale_config_paths"])

    def test_packaged_map_set_requires_exact_registry_and_container_maps(self) -> None:
        archive = self.root / "archive"
        utoc = archive / "Skyguard52-Windows.utoc"
        utoc.parent.mkdir(parents=True)
        utoc.write_bytes(
            b"\x00".join(f"{Path(path).name}.umap".encode() for path in self.maps)
        )
        registry = self.root / "DevelopmentAssetRegistry.bin"
        registry.write_bytes(b"\x00".join(path.encode() for path in self.maps))
        clean = COOK_CONTRACT.evaluate_packaged_maps(
            self.maps, archive, registry
        )
        self.assertEqual("PASS", clean["gate"])

        utoc.write_bytes(
            utoc.read_bytes()
            + b"\x00Lvl_M10_Stale.umap"
        )
        stale = COOK_CONTRACT.evaluate_packaged_maps(
            self.maps, archive, registry
        )
        self.assertEqual("FAIL", stale["gate"])
        self.assertEqual(["Lvl_M10_Stale.umap"], stale["stale_container_maps"])


if __name__ == "__main__":
    unittest.main()
