# The calculator of the seahorse cookbook

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

class Calculator(Account):
  owner: Pubkey
  display: i64

#@instruction
@enforce(lambda before, after: after.calculator.owner == before.owner.key())
def init_calculator(owner: Signer, calculator: Empty[Calculator]):
  calculator = calculator.init(payer = owner, seeds = ['Calculator', owner])
  calculator.owner = owner.key()

@instruction
@enforce(lambda before, after: after.calculator.display == 0)
@enforce(lambda before, after: before.calculator.owner == before.owner.key())
def reset_calculator(owner: Signer, calculator: Calculator):
  print(owner.key(), 'is resetting a calculator', calculator.key())
  assert owner.key() == calculator.owner, 'This is not your calculator!'
  calculator.display = 0

@instruction
@enforce(lambda before, after: not(before.op > 3) or (after.calculator.display == before.calculator.display))
@enforce(lambda before, after: before.op == after.op)
def do_operation(owner: Signer, calculator: Calculator, op: i64, num: i64):
  assert owner.key() == calculator.owner, 'This is not your calculator!'
  if op == 0:
    calculator.display += num
  elif op == 1:
    calculator.display -= num
  elif op == 2:
    calculator.display *= num
  elif op == 3:
    calculator.display //= num

@instruction
@enforce(lambda before, after: before.calculator.display + before.num == after.calculator.display)
def add_to_calculator(owner: Signer, calculator: Calculator, num: i64):
  assert owner.key() == calculator.owner, 'This is not your calculator!'
  calculator.display += num

@instruction
def modify_owner(owner: Signer, calculator: Calculator, new_owner: Pubkey):
  assert owner.key() == calculator.owner, 'This is not your calculator!'
  calculator.owner = new_owner


#######
# Tests
#######

@test
def test_assigment(calculator: Calculator, value: i64):
  calculator.display = 1
  calculator.display += value
  seaverify_assert(calculator.display == 1+value)

# Todo split multiple assert statements into multiple tests to make it easier to debug with a counterexample
# Here for instance, if the middle assert fails, we don't have much info
@test
def test_assigment_2(calculator: Calculator, value: i64):
  calculator.display = 0
  seaverify_assert(calculator.display == 0)
  calculator.display = 1
  seaverify_assert(calculator.display == 1)
  calculator.display = 2
  seaverify_assert(calculator.display == 2)

@test
def test_reset(owner2: Signer, calculator: Calculator):
  reset_calculator(owner=owner2, calculator=calculator)
  assert calculator.display == 0
  seaverify_assert(calculator.display == 0)

@test
def test_modify_owner(owner: Signer, owner2: Signer, calculator: Calculator):
  assert owner.key() == calculator.owner
  seaverify_assert(calculator.owner == owner.key())
  modify_owner(owner=owner, calculator=calculator, new_owner=owner2.key())
  seaverify_assert(calculator.owner == owner2.key())

@test
def test_add_to_calculator(owner: Signer, calculator: Calculator, value: i64):
  old_value = calculator.display
  do_operation(owner=owner, calculator=calculator, op=0, num=value)
  seaverify_assert(calculator.display == old_value + value)

if __name__ == '__main__':
  # The above invariant will fail due to modify_owner. Try to uncomment it!
  # add_invariant(lambda _: _.calculator.owner == _.owner.key())
  # Will fail too
  # add_invariant(lambda _: _.calculator.display == 0)
  # Not this one because I for now only incorrectly support unsigned integers
  add_invariant(lambda _: _.calculator.display >= 0)
  # Will fail too
  # add_invariant(lambda _: _.calculator.display >= 1)
  verify_contract()
  verify_tests()