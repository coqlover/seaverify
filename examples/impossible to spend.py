# When you assume too strong proprieties, it becomes impossible to satisfy them
# Here is a demo

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

# The solver will warn you that it is impossible to satisfy the assumption
# This is obvious in this case, but sometimes it can be subtle why it's impossible to spend
# And when it's impossible to spend, every @enforce properties becomes true: no path of execution can invalidate them!
# So it's not good if by mistake you assume something that is impossible to satisfy
@instruction
@assume(lambda _: 1==2)
def impossible():
  1

# Whereas in this case, the solver will only warn you that the property 1==2 is false
@instruction
@enforce(lambda _: 1==2)
def possible():
  1

if __name__ == '__main__':
  verify_contract()