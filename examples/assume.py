# Example of an invariant preserved accros function calls

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

@instruction
@assume(lambda _: _.value == 10)
@enforce(lambda before, after: after.n == 10)
def with_assume(n: u64, value: u64):
  n = value

@instruction
@enforce(lambda before, after: after.n == 10)
def with_assert(n: u64, value: u64):
  assert value == 10
  n = value

if __name__ == '__main__':
  verify_contract()