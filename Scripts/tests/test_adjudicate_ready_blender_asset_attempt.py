from __future__ import annotations

import json
from pathlib import Path
import struct
import tempfile
import unittest

from Scripts import adjudicate_ready_blender_asset_attempt as subject
from Scripts import adjudicate_ready_blender_asset_attempt_v2 as subject_v2


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_png_header(path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height))


def write_glb(path: Path, nodes: list[str], meshes: int = 1, skins: int = 0, animations: int = 0) -> None:
    payload = {
        "asset": {"version": "2.0"},
        "nodes": [{"name": name} for name in nodes],
        "meshes": [{} for _ in range(meshes)],
        "skins": [{} for _ in range(skins)],
        "animations": [{} for _ in range(animations)],
    }
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    padded = encoded + b" " * ((4 - len(encoded) % 4) % 4)
    total = 12 + 8 + len(padded)
    path.write_bytes(struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<II", len(padded), 0x4E4F534A) + padded)


class ReadyBlenderPostflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.original_attempts_root = subject.ATTEMPTS_ROOT
        subject.ATTEMPTS_ROOT = self.root / "Attempts"
        self.addCleanup(setattr, subject, "ATTEMPTS_ROOT", self.original_attempts_root)

    def build_yak_fixture(self) -> tuple[Path, dict[str, object]]:
        contracts = subject.load_json(subject.CONTRACT_PATH)["contracts"]
        contract = contracts["core-yak52-airframe"]
        attempt = subject.ATTEMPTS_ROOT / "core-yak52-airframe" / "attempt_fixture"
        output = attempt / "output"
        output.mkdir(parents=True)
        (output / contract["blend"]).write_bytes(b"BLENDER_FIXTURE")
        write_glb(output / contract["glb"], contract["required_glb_nodes"], meshes=1)
        for index in range(11):
            write_png_header(output / "renders" / f"view_{index:02d}.png", 2560, 1440)
        write_json(
            output / "dimension_receipt.json",
            {"schema": contract["required_json"]["dimension_receipt.json"], "global_envelope_pass": True},
        )
        write_json(
            output / "source_parity_receipt.json",
            {"schema": contract["required_json"]["source_parity_receipt.json"], "unchanged": True},
        )
        write_json(
            output / "topology_material_receipt.json",
            {"schema": contract["required_json"]["topology_material_receipt.json"]},
        )
        write_json(
            output / "artifact_receipt.json",
            {
                "schema": contract["required_json"]["artifact_receipt.json"],
                "render_count": 11,
                "render_dimensions": [2560, 1440],
                "unreal_import_authorized": False,
            },
        )
        write_json(
            attempt / "terminal.json",
            {
                "asset_id": "core-yak52-airframe",
                "launch_count": 1,
                "retry_count": 0,
                "timeout": False,
                "status": "awaiting_review",
                "exit_code": 0,
                "exit_code_type": "int",
                "artifact_inventory": subject.inventory(output),
            },
        )
        return attempt, contract

    def test_current_shahed_failed_lane_preserves_recovery02_contract(self) -> None:
        contract = subject.load_json(subject.CONTRACT_PATH)["contracts"]["core-shahed136"]
        manifest = subject.load_json(subject.MANIFEST_PATH)
        asset = next(item for item in manifest["assets"] if item["id"] == "core-shahed136")
        self.assertEqual(asset["status"], "failed")
        self.assertEqual(
            contract["worker_script"],
            r"Scripts\Workers\worker_core_shahed136_refinement01_recovery02.py",
        )
        self.assertGreaterEqual(len(contract["authorities"]), 3)
        for authority in contract["authorities"]:
            subject.verify_authority(authority)
        self.assertEqual(
            asset["worker"]["postflight"]["script"],
            subject_v2.SCRIPT_RELATIVE,
        )
        self.assertEqual(
            contract["quality_gate"]["profile"],
            "hero_airframe_proxy_rejection_v1",
        )

    def test_v2_accepts_standing_authority_mode_separation(self) -> None:
        source = "\n".join(
            (
                "param([switch]$ExecuteOnce, [switch]$OfflineContractTest)",
                "$StandingAuthority = 'standing_heavy_process_authorization.json'",
                "$authority.execution_policy.per_run_user_authorization_required",
                "$authority.execution_policy.one_heavy_process_at_a_time",
                "$authority.execution_policy.automatic_retry_count",
                "$authority.execution_policy.failed_namespace_reuse",
            )
        )
        self.assertTrue(subject_v2._has_governed_mode_separation(source))

    def test_v2_rejects_unguarded_execute_once(self) -> None:
        self.assertFalse(
            subject_v2._has_governed_mode_separation(
                "param([switch]$ExecuteOnce, [switch]$OfflineContractTest)"
            )
        )

    def test_complete_fixture_passes(self) -> None:
        attempt, contract = self.build_yak_fixture()
        report = subject.validate_attempt("core-yak52-airframe", attempt, contract)
        self.assertEqual(report["output_file_count"], 17)
        self.assertEqual(report["required_glb_nodes_verified"], len(contract["required_glb_nodes"]))
        self.assertTrue(report["inventory_parity"])

    def test_wrong_png_dimensions_are_rejected(self) -> None:
        attempt, contract = self.build_yak_fixture()
        write_png_header(attempt / "output" / "renders" / "view_00.png", 1280, 720)
        with self.assertRaisesRegex(subject.AdjudicationError, "PNG dimensions mismatch"):
            subject.validate_attempt("core-yak52-airframe", attempt, contract)

    def test_glb_socket_loss_is_rejected(self) -> None:
        attempt, contract = self.build_yak_fixture()
        write_glb(attempt / "output" / contract["glb"], contract["required_glb_nodes"][:-1], meshes=1)
        with self.assertRaisesRegex(subject.AdjudicationError, "missing required nodes"):
            subject.validate_attempt("core-yak52-airframe", attempt, contract)

    def test_output_tamper_after_terminal_is_rejected(self) -> None:
        attempt, contract = self.build_yak_fixture()
        (attempt / "output" / "SKG_Yak52_Airframe_Refinement01.blend").write_bytes(b"CHANGED")
        with self.assertRaisesRegex(subject.AdjudicationError, "inventory differs"):
            subject.validate_attempt("core-yak52-airframe", attempt, contract)

    def test_receipt_false_value_is_rejected(self) -> None:
        attempt, contract = self.build_yak_fixture()
        write_json(
            attempt / "output" / "dimension_receipt.json",
            {"schema": contract["required_json"]["dimension_receipt.json"], "global_envelope_pass": False},
        )
        with self.assertRaisesRegex(subject.AdjudicationError, "Receipt check failed"):
            subject.validate_attempt("core-yak52-airframe", attempt, contract)

    def test_attempt_must_be_in_governed_asset_namespace(self) -> None:
        attempt, contract = self.build_yak_fixture()
        wrong = self.root / "wrong" / attempt.name
        wrong.parent.mkdir(parents=True)
        attempt.rename(wrong)
        with self.assertRaisesRegex(subject.AdjudicationError, "outside the governed asset namespace"):
            subject.validate_attempt("core-yak52-airframe", wrong, contract)


if __name__ == "__main__":
    unittest.main()
