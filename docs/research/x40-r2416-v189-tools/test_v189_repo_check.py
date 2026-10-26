"""Tests for the additional repository-side v189 compact ELF checker (offline)."""
import os,unittest
from pathlib import Path
import v189_repo_check as v
class StaticChecks(unittest.TestCase):
 def test_expected_counts(self):
  self.assertEqual([len(v.PLTS[k][2]) for k in ('end','complete','update_vector','update_noargs')],[2,3,1,0])
 def test_sha_format(self):self.assertEqual(len(v.SHA),64)
 def test_end_instruction_word(self):self.assertEqual(v.WORDS[0xad9fc4],0x35ff1dc0)
 def test_signed_branch(self):self.assertEqual(v.sign((1<<19)-1,19),-1)
 def test_direct_call_positive(self):self.assertEqual(v.bl(0x94000002,0x1000),0x1008)
 def test_direct_call_rejects_plain_b(self):
  with self.assertRaises(v.Refusal):v.bl(0x14000002,0x1000)
 @unittest.skipUnless(os.environ.get('X40_R2416_V189_ROUTE_ELF'),'private ELF not supplied')
 def test_original_elf(self):
  data=Path(os.environ['X40_R2416_V189_ROUTE_ELF']).read_bytes()
  self.assertFalse(v.verify(data)['runtimeRecleanProven'])
 @unittest.skipUnless(os.environ.get('X40_R2416_V189_ROUTE_ELF'),'private ELF not supplied')
 def test_original_hash_rejection(self):
  data=bytearray(Path(os.environ['X40_R2416_V189_ROUTE_ELF']).read_bytes());data[130]^=1
  with self.assertRaises(v.Refusal):v.verify(bytes(data))
if __name__=='__main__':unittest.main()
