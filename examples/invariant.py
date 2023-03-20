# Example of an invariant preserved accros function calls

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

class Object(Account):
  value: i64

# Set the value to 10
@instruction
@enforce(lambda before, after: after.object.value == 10)
def reset_value(object: Object):
  object.value = 10

# Decrease the value if certain conditions are met
@instruction
@enforce(lambda before, after: after.object.value == before.object.value - 1)
def decrease_value_1(object: Object):
  assert object.value > 10, "Only possible when above 10"
  object.value -= 1

# Decrease the value if certain conditions are met
@instruction
@enforce(lambda before, after: after.object.value <= before.object.value)
def decrease_value_2(object: Object):
  if object.value > 100:
    object.value //= 10

# Increase the value by whatever you want
@instruction
@enforce(lambda before, after: after.object.value > before.object.value)
def add_value(object: Object, value: i64):
  assert value > 0, "What you try to do is useless"
  object.value += value

# At all time, the value is at least 10
if __name__ == '__main__':
  add_invariant(lambda _: _.object.value >= 10)
  verify_contract()