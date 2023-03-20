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

@test
def test_assigment(calculator: Calculator):
  assert calculator.display == 0
  calculator.display = 1
  seaverify_assert_eq(calculator.display, 1, 'The calculator should be 1')

@test
def test_reset(calculator: Calculator):
  #reset_calculator(calculator)
  assert calculator.display == 0
  seaverify_assert_eq(calculator.display, 0, 'The calculator should be 1')

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