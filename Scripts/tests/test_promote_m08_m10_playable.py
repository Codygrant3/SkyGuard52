from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "promote_m08_m10_playable.py"
SPEC = importlib.util.spec_from_file_location("m08_m10_promotion", MODULE_PATH)
PROMOTION = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(PROMOTION)


class M08M10PromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc)
        self.maps = [
            f"/Game/Skyguard/Maps/Campaign_v1/Lvl_M{index:02d}_Mission_Playable_v1"
            for index in range(1, 8)
        ] + [
            PROMOTION.PROMOTIONS[f"M{index:02d}"]["assembly"]
            for index in range(8, 11)
        ]
        self.write_config(self.maps)
        self.write_matrix(self.maps)
        for package in self.maps[:7]:
            self.write_umap(package, f"{package}\n".encode())
        for mission_id, spec in PROMOTION.PROMOTIONS.items():
            self.write_valid_evidence(mission_id, spec["expected"])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_config(self, maps: list[str]) -> None:
        path = self.root / PROMOTION.DEFAULT_GAME_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "[/Script/UnrealEd.ProjectPackagingSettings]",
            "bCookAll=False",
        ]
        lines.extend(f'+MapsToCook=(FilePath="{package}")' for package in maps)
        lines.append('+DirectoriesToAlwaysCook=(Path="/Game/Skyguard/Data/Campaign_v1")')
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_matrix(self, maps: list[str]) -> None:
        path = self.root / PROMOTION.MATRIX_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "skyguard.phase8.mission-soak-matrix.v1",
            "required_mission_count": 10,
            "missions": [
                {
                    "id": f"M{index:02d}",
                    "name": f"Mission {index:02d}",
                    "map": package,
                    "status": (
                        "PROXY_ASSEMBLY_CANDIDATE"
                        if index >= 8
                        else "PLAYABLE_INTEGRATION_CANDIDATE"
                    ),
                    "soak_seconds": 300,
                }
                for index, package in enumerate(maps, 1)
            ],
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_umap(self, package: str, payload: bytes) -> Path:
        path = PROMOTION.package_to_umap(self.root, package)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return path

    def write_valid_evidence(self, mission_id: str, expected: str) -> None:
        umap = self.write_umap(expected, f"{mission_id} playable\n".encode())
        reports = self.root / "Saved/Reports"
        reports.mkdir(parents=True, exist_ok=True)
        build = reports / f"{mission_id}_PLAYABLE_INTEGRATION_BUILD.json"
        build.write_text(json.dumps({
            "gate": "PASS",
            "target_map": expected,
            "source_preserved": True,
            "package_sha256": hashlib.sha256(umap.read_bytes()).hexdigest(),
        }), encoding="utf-8")
        attempt = (
            self.root / "Saved/Reports" / f"{mission_id}_Playable"
            / "attempt_20260802T110000000Z"
        )
        attempt.mkdir(parents=True)
        receipt = reports / f"{mission_id}_PLAYABLE_INTEGRATION_GATE_LATEST.json"
        receipt.write_text(json.dumps({
            "gate": "PASS",
            "attempt": str(attempt),
            "automation": {"success": 4, "failure": 0, "missing": []},
            "persistence_audit": {"gate": "PASS"},
        }), encoding="utf-8")
        base = self.now.timestamp() - 7200
        os.utime(umap, (base, base))
        os.utime(build, (base + 10, base + 10))
        os.utime(receipt, (base + 20, base + 20))

    def plan(self):
        return PROMOTION.plan_promotion(self.root, now=self.now)

    def test_clean_dry_run_passes_and_preserves_exact_order(self) -> None:
        report, config_after, matrix_after = self.plan()
        self.assertEqual("PASS", report["gate"])
        self.assertFalse(report["mutation_performed"])
        self.assertEqual(
            PROMOTION.MISSION_ORDER,
            [PROMOTION.mission_id_from_map(path) for path in report["proposed_map_order"]],
        )
        for mission_id, spec in PROMOTION.PROMOTIONS.items():
            self.assertIn(spec["expected"], config_after)
            mission = next(
                item for item in json.loads(matrix_after)["missions"]
                if item["id"] == mission_id
            )
            self.assertEqual(spec["expected"], mission["map"])
            self.assertEqual("PLAYABLE_INTEGRATION_CANDIDATE", mission["status"])

    def test_dry_run_never_mutates_files(self) -> None:
        config = self.root / PROMOTION.DEFAULT_GAME_REL
        matrix = self.root / PROMOTION.MATRIX_REL
        before = (config.read_bytes(), matrix.read_bytes())
        self.plan()
        self.assertEqual(before, (config.read_bytes(), matrix.read_bytes()))

    def test_missing_receipt_fails_closed(self) -> None:
        (self.root / "Saved/Reports/M09_PLAYABLE_INTEGRATION_GATE_LATEST.json").unlink()
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])

    def test_failing_receipt_fails_closed(self) -> None:
        path = self.root / "Saved/Reports/M10_PLAYABLE_INTEGRATION_GATE_LATEST.json"
        payload = json.loads(path.read_text())
        payload["gate"] = "FAIL"
        path.write_text(json.dumps(payload))
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])

    def test_stale_receipt_fails_closed(self) -> None:
        path = self.root / "Saved/Reports/M08_PLAYABLE_INTEGRATION_GATE_LATEST.json"
        payload = json.loads(path.read_text())
        stale_attempt = (
            self.root / "Saved/Reports/M08_Playable"
            / "attempt_20260720T110000000Z"
        )
        stale_attempt.mkdir(parents=True)
        payload["attempt"] = str(stale_attempt)
        path.write_text(json.dumps(payload))
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])

    def test_wrong_expected_target_fails_closed(self) -> None:
        path = self.root / "Saved/Reports/M09_PLAYABLE_INTEGRATION_BUILD.json"
        payload = json.loads(path.read_text())
        payload["target_map"] = PROMOTION.PROMOTIONS["M09"]["assembly"]
        path.write_text(json.dumps(payload))
        receipt = self.root / "Saved/Reports/M09_PLAYABLE_INTEGRATION_GATE_LATEST.json"
        os.utime(receipt, None)
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])

    def test_missing_playable_umap_fails_closed(self) -> None:
        PROMOTION.package_to_umap(
            self.root, PROMOTION.PROMOTIONS["M10"]["expected"]
        ).unlink()
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])

    def test_apply_creates_backups_writes_atomically_and_runs_verifier(self) -> None:
        report, config_after, matrix_after = self.plan()
        calls = []

        def verifier(root, config, matrix, output):
            calls.append((root, config, matrix, output))
            return {"gate": "PASS", "checks": {"exact_order": True}}

        result = PROMOTION.apply_promotion(
            self.root,
            report,
            config_after,
            matrix_after,
            verifier_runner=verifier,
            now=self.now,
        )
        self.assertTrue(result["mutation_performed"])
        self.assertEqual(1, len(calls))
        backup = Path(result["backup_directory"])
        self.assertTrue((backup / "DefaultGame.ini").is_file())
        self.assertTrue((backup / "PHASE8_MISSION_SOAK_MATRIX.json").is_file())
        self.assertTrue((backup / "manifest.json").is_file())
        self.assertIn(
            PROMOTION.PROMOTIONS["M08"]["expected"],
            (self.root / PROMOTION.DEFAULT_GAME_REL).read_text(),
        )

    def test_failed_post_write_verifier_rolls_back_both_files(self) -> None:
        report, config_after, matrix_after = self.plan()
        config = self.root / PROMOTION.DEFAULT_GAME_REL
        matrix = self.root / PROMOTION.MATRIX_REL
        before = (config.read_bytes(), matrix.read_bytes())

        def verifier(root, config, matrix, output):
            raise RuntimeError("synthetic cook-contract failure")

        with self.assertRaises(RuntimeError):
            PROMOTION.apply_promotion(
                self.root,
                report,
                config_after,
                matrix_after,
                verifier_runner=verifier,
                now=self.now,
            )
        self.assertEqual(before, (config.read_bytes(), matrix.read_bytes()))

    def test_reordered_matrix_fails_closed(self) -> None:
        path = self.root / PROMOTION.MATRIX_REL
        payload = json.loads(path.read_text())
        payload["missions"][0], payload["missions"][1] = (
            payload["missions"][1],
            payload["missions"][0],
        )
        path.write_text(json.dumps(payload))
        self.assertEqual("FAIL_CLOSED", self.plan()[0]["gate"])


if __name__ == "__main__":
    unittest.main()
