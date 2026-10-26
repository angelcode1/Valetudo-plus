import os,unittest
from pathlib import Path
import v193_repo_check as v
class StaticTests(unittest.TestCase):
 def test_reference_counts(self):
  self.assertEqual([len(row[1]) for row in v.KEYS.values()],[2,6])
 def test_adrp_known_next_key(self):
  self.assertEqual(v.adrp_add(0xb00028c1,0x91342021,0xaeee4c),0x1007d08)
 def test_adrp_known_original_key(self):
  self.assertEqual(v.adrp_add(0xb00028a1,0x91338021,0xaf231c),0x1007ce0)
 def test_adrp_invalid_pair(self):
  self.assertIsNone(v.adrp_add(0,0,0xaeee4c))
 def test_bl_math_site(self):
  self.assertEqual(v.bl_target(0x97e5743f,0xaf24e4),0x44f5e0)
 @unittest.skipUnless(os.environ.get("X40_R2416_V193_ROUTE_ELF"),"private source ELF not supplied")
 def test_original(self):
  data=Path(os.environ["X40_R2416_V193_ROUTE_ELF"]).read_bytes()
  self.assertFalse(v.verify(data)["newCleaningTaskOrAutonomousRecleanProven"])
if __name__=="__main__":unittest.main()
