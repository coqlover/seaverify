# Trying to prove math properties with z3

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

#@instruction
@enforce(lambda before, after: after.n == 1)
def assigment(n: i64):
  n = 1

#@instruction
@enforce(lambda before, after: after.n % 2 == 0)
def to_even(n: i64):
  if n%2 == 1:
    n -= 1

# Need answer as argument because it's not supported yet to access created variables
# Takes some time to verify, but it works
#@instruction
@assume(lambda _: _.n > 0)
@assume(lambda _: _.n <= 10000000000)
@enforce(lambda before, after: before.n == after.n)
@enforce(lambda before, after: (10 ** after.answer >= before.n) and (10 ** (after.answer + 1) < before.n))
def log10(n: i64, answer: i64):
  if n == 1:
    answer = 0
  elif n <= 10:
    answer = 1
  elif n <= 100:
    answer = 2
  elif n <= 1000:
    answer = 3
  elif n <= 10000:
    answer = 4
  elif n <= 100000:
    answer = 5
  elif n <= 1000000:
    answer = 6
  elif n <= 10000000:
    answer = 7
  elif n <= 100000000:
    answer = 8
  elif n <= 1000000000:
    answer = 9
  elif n <= 10000000000:
    answer = 10

# In a AMM, when one token goes up, the other goes down
#@instruction
@assume(lambda _: _.a > 0)
@assume(lambda _: _.b > 0)
@enforce(lambda before, after: before.bb < before.b)
def constant_product(a: i64, b: i64, constant: i64, aa: i64, bb: i64):
  assert a*b == constant
  assert aa*bb == constant
  assert aa > a

# Can this exists?
# Takes forever to figure out it's impossible to find an sqrt_n_plus_one
#@instruction
@assume(lambda _: _.n > 1)
def sqrt_plus_one(n: i64, sqrt_n: i64, sqrt_n_plus_one: i64):
  assert sqrt_n*sqrt_n == n
  assert sqrt_n_plus_one*sqrt_n_plus_one == n+1

# Same (I thought it'd work lmao) todo make it possible to guide the solver
#@instruction
@assume(lambda _: _.n > 1)
@enforce(lambda before, after: after.sqrt_n_plus_one >= after.sqrt_n + 1)
@enforce(lambda before, after: after.sqrt_n_plus_one*after.sqrt_n_plus_one >= after.sqrt_n*after.sqrt_n + 2*after.sqrt_n + 1)
@enforce(lambda before, after: after.sqrt_n > 1)
@enforce(lambda before, after: after.sqrt_n_plus_one*after.sqrt_n_plus_one >= after.sqrt_n*after.sqrt_n + 2)
@enforce(lambda before, after: after.sqrt_n_plus_one*after.sqrt_n_plus_one > after.n+1)
def sqrt_plus_one_guided(n: i64, sqrt_n: i64, sqrt_n_plus_one: i64, help1: i64, help2: i64):
  assert sqrt_n*sqrt_n == n
  assert sqrt_n_plus_one*sqrt_n_plus_one == n+1

if __name__ == '__main__':
  verify_contract()