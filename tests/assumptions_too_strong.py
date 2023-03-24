# Verify the solver notifies us when assumptions are too strong
# Todo, same for @test

import sys
sys.path.append(".")
from seaverify.prelude import *

@instruction
def double_assigment(n: i64):
  assert n==1
  assert n==2

success = True
try:
   verify_contract()
   success = False
except:
   pass
assert success