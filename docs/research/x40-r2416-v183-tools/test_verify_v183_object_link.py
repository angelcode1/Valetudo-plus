import unittest
import verify_v183_object_link as v
class CompactVerification(unittest.TestCase):
 def test_sha_format(self):
  for h in v.SHA.values():self.assertEqual(len(h),64)
 def test_checked_object_field_stores(self):
  self.assertEqual(v.WORDS['node_laser_transfer.so'][0x1306e4],0xf909c274)
  self.assertEqual(v.WORDS['node_laser_transfer.so'][0x3ac948],0xf904d2b3)
 def test_bl_decode_positive(self):
  self.assertEqual(v.branch_target(0x94000002,0x1000),0x1008)
 def test_bl_decode_negative(self):
  self.assertEqual(v.branch_target(0x97ffffff,0x1000),0xffc)
 def test_bl_reject_noncall(self):
  with self.assertRaises(v.Refusal):v.branch_target(0x14000002,0x1000)
if __name__=='__main__':unittest.main()
