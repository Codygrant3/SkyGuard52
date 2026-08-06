from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"Scripts"))
import verify_phase2_yak52_r4_slice01_recovery02_readiness as gate

class Recovery02Tests(unittest.TestCase):
    def setUp(self):self.c=json.loads((ROOT/gate.CONTRACT_REL).read_text(encoding="utf-8-sig"))
    def has(self,errors,text):self.assertTrue(any(text in e for e in errors),errors)
    def test_01_canonical_contract(self):self.assertEqual([],gate.validate_data(self.c))
    def test_02_full_offline_gate(self):self.assertEqual([],gate.run(ROOT)[1])
    def test_03_supported_enum(self):
        self.assertIn("PLAIN_AXES",gate.SUPPORTED);self.assertNotIn("CROSS",gate.SUPPORTED)
    def test_04_enum_mutation_fails(self):
        c=copy.deepcopy(self.c);c["compatibility_contract"]["replacement_enum"]="CROSS"
        self.has(gate.validate_data(c),"replacement enum must be PLAIN_AXES")
    def test_05_recovery01_retry_fails(self):
        c=copy.deepcopy(self.c);c["recovery_evidence"]["recovery01_retry_allowed"]=True
        self.has(gate.validate_data(c),"Recovery01 terminal boundary mismatch")
    def test_06_output_alias_drift_fails(self):
        c=copy.deepcopy(self.c);c["outputs"]["blend"]="bad.blend"
        self.has(gate.validate_data(c),"output alias mismatch")
    def test_07_missing_contract_path_fails(self):
        c=copy.deepcopy(self.c);del c["outputs"]["comparison_directory"]
        self.has(gate.validate_data(c),"contract path missing: outputs.comparison_directory")
    def test_08_claim_fails(self):
        c=copy.deepcopy(self.c);c["claims"]["silhouette_locked"]=True
        self.has(gate.validate_data(c),"claim must remain false")
    def test_09_script_hash_fails(self):
        c=copy.deepcopy(self.c);c["authoring_script"]["sha256"]="0"*64
        self.has(gate.validate_files(ROOT,c),"authoring script drift")
    def test_10_wrapper_hash_fails(self):
        c=copy.deepcopy(self.c);c["launch_contract"]["wrapper_sha256"]="0"*64
        self.has(gate.validate_files(ROOT,c),"wrapper drift")
    def test_11_terminal_receipt_bound(self):
        self.assertEqual("80720a9f9cc5a43f775cc08d09379d35d75fa94c46c127aebeae6c9f55404d57",self.c["recovery_evidence"]["receipt_sha256"])
    def test_12_frozen_access_paths(self):
        source=(ROOT/gate.FROZEN_REL).read_text(encoding="utf-8")
        self.assertEqual(gate.EXPECTED_PATHS,gate.extract_paths(source))
if __name__=="__main__":unittest.main()
