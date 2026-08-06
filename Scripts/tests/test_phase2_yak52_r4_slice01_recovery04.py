import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"Scripts"))
import verify_phase2_yak52_r4_slice01_recovery04 as g
class T(unittest.TestCase):
 def test_gate(self):self.assertEqual([],g.run(ROOT)[1])
 def test_three_migrations(self):
  c=json.loads((ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY04_OUTPUT_CONTRACT.json").read_text());x=c["compatibility"]
  self.assertEqual("PLAIN_AXES",x["datum"]["to"]);self.assertEqual("BLENDER_EEVEE",x["render_engine"]["to"]);self.assertEqual("scene.world is None",x["world"]["precondition"])
 def test_terminal_bound(self):
  c=json.loads((ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY04_OUTPUT_CONTRACT.json").read_text());self.assertFalse(c["terminal_recovery03"]["retry_allowed"])
 def test_checksum_contract(self):
  c=json.loads((ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY04_OUTPUT_CONTRACT.json").read_text());self.assertIn("WriteAllLines",c["launch_wrapper"]["checksum_format"])
if __name__=="__main__":unittest.main()
