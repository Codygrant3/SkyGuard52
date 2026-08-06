import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts"))
import verify_phase2_yak52_r4_slice01_recovery05 as gate


class Recovery05ReadinessTests(unittest.TestCase):
    def test_gate_passes(self) -> None:
        self.assertEqual([], gate.run(ROOT))

    def test_failed_recovery04_is_bound_and_nonretryable(self) -> None:
        contract = json.loads((ROOT / gate.CONTRACT).read_text())
        terminal = contract["terminal_recovery04"]
        self.assertFalse(terminal["retry_allowed"])
        self.assertEqual(
            "0088485c6aa6e3b75d08defe55b69ecb3b32e42f4e7f221a5919b2cdc782622e",
            terminal["receipt_sha256"],
        )

    def test_new_output_namespace(self) -> None:
        contract = json.loads((ROOT / gate.CONTRACT).read_text())
        for value in contract["outputs"].values():
            self.assertIn("RECOVERY05", value.upper())

    def test_glb_extension_fix_is_scoped(self) -> None:
        contract = json.loads((ROOT / gate.CONTRACT).read_text())
        fix = contract["compatibility"]["glb_temp_extension"]
        self.assertEqual(".glb.tmp.glb", fix["observed"])
        self.assertEqual(".glb.tmp", fix["required"])


if __name__ == "__main__":
    unittest.main()
