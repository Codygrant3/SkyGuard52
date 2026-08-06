import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"Scripts"))
import verify_phase2_yak52_r4_slice01_recovery03 as g
class T(unittest.TestCase):
 def test_gate(self):self.assertEqual([],g.run(ROOT)[1])
 def test_both_mappings(self):
  c=json.loads((ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY03_OUTPUT_CONTRACT.json").read_text())
  self.assertEqual("PLAIN_AXES",c["compatibility"]["datum"]["to"]);self.assertEqual("BLENDER_EEVEE",c["compatibility"]["render_engine"]["to"])
 def test_terminal_bound(self):
  c=json.loads((ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY03_OUTPUT_CONTRACT.json").read_text());self.assertFalse(c["terminal_recovery02"]["retry_allowed"])
if __name__=="__main__":unittest.main()
