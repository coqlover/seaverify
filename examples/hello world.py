# Simplest example

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

@instruction
@enforce(lambda before, after: after.n == before.n + 1)
def increment(n: u64):
    n += 1

if __name__ == '__main__':
   verify_contract()