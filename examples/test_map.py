# Some example with map. Not sure to which solana object it'll correspond

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

@instruction
@enforce(lambda before, after: after.token.balance(user=before.alice) == before.token.balance(user=before.alice) - 10)
@enforce(lambda before, after: after.token.balance(user=before.bob) == before.token.balance(user=before.bob) + 10)
@assume(lambda _: _.alice.key() != _.bob.key())
def test_simple_transfer_1(alice: Signer, bob: Signer, token: TokenMap):
  token.transfer(authority=alice, to=bob, amount=10)

@instruction
@enforce(lambda before, after: after.token.balance(user=before.alice) == before.token.balance(user=before.alice) - 10)
@enforce(lambda before, after: after.token.balance(user=before.bob) == before.token.balance(user=before.bob) + 10)
@assume(lambda _: _.alice.key() != _.bob.key())
def test_simple_transfer_2(alice: Signer, bob: Signer, token: TokenMap):
  token.transfer(authority=alice, to=bob, amount=6)
  token.transfer(authority=alice, to=bob, amount=3)
  token.transfer(authority=alice, to=bob, amount=1)

@instruction
@enforce(lambda before, after: after.token.balance(user=before.alice) == before.token.balance(user=before.alice) - before.amount)
@enforce(lambda before, after: after.token.balance(user=before.bob) == before.token.balance(user=before.bob) + before.amount)
@assume(lambda _: _.alice.key() != _.bob.key())
def test_simple_transfer_3(alice: Signer, bob: Signer, token: TokenMap, amount: i64):
  token.transfer(authority=alice, to=bob, amount=amount)

@instruction
@enforce(lambda before, after: after.token.balance(user=before.alice) == before.token.balance(user=before.alice) - before.amount)
@enforce(lambda before, after: after.token.balance(user=before.bob) == before.token.balance(user=before.bob) + before.amount)
@assume(lambda _: _.alice.key() != _.bob.key())
def test_simple_transfer_4(alice: Signer, bob: Signer, token: TokenMap, amount: i64, amount1: i64, amount2: i64):
  assert amount == amount1 + amount2
  token.transfer(authority=alice, to=bob, amount=amount1)
  token.transfer(authority=alice, to=bob, amount=amount2)

@instruction
@enforce(lambda before, after: after.token.balance(user=before.alice) == 0)
@assume(lambda _: _.alice.key() != _.bob.key())
def test_simple_transfer_5(alice: Signer, bob: Signer, token: TokenMap):
  token.transfer(authority=alice, to=bob, amount=token.balance(user=alice))

if __name__ == '__main__':
  verify_contract()