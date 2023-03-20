# The fizzbuzz of seahorse cookbook

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

class FizzBuzz(Account):
  fizz: bool
  buzz: bool
  n: u64

@instruction
def init(owner: Signer, fizzbuzz: Empty[FizzBuzz]):
  fizzbuzz.init(payer = owner, seeds = ['fizzbuzz', owner])

@instruction
@enforce(lambda before, after: after.fizzbuzz.n <= before.n)
def do_fizzbuzz(fizzbuzz: FizzBuzz, n: u64):
  fizzbuzz.fizz = n % 3 == 0
  fizzbuzz.buzz = n % 5 == 0
  if not fizzbuzz.fizz and not fizzbuzz.buzz:
    fizzbuzz.n = n
  else:
    fizzbuzz.n = 0

if __name__ == '__main__':
  add_invariant(lambda _: _.fizzbuzz.n == 0 or (not(_.fizzbuzz.fizz) and not(_.fizzbuzz.buzz)))
  add_invariant(lambda _: _.fizzbuzz.n >= 0)
  # add_invariant(lambda _: _.fizzbuzz.n <= 100)
  verify_contract()