# Simplest example
# Increment a variable by 1 and by any amount

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS')

# Increment by 1 a variable
@instruction
@enforce(lambda before, after: after.n == before.n + 1)
def increment_1(n: u64):
    n += 1

@test
def test_increment_1(n: u64):
    old_n = n
    increment_1(n = n)
    seaverify_assert(n == old_n + 1)

# Increment by any amount a variable
@instruction
@enforce(lambda before, after: after.n == before.n + before.value)
@enforce(lambda before, after: after.value == before.value)
def increment_value(n: u64, value: u64):
    n += value

@test
def test_increment_value(n: u64, value1: u64, value2: u64):
    old_n = n
    increment_value(n = n, value = value1)
    seaverify_assert(n == old_n + value1)
    increment_value(n = n, value = value2)
    seaverify_assert(n == old_n + value1 + value2)

if __name__ == '__main__':
   verify_contract()
   verify_tests()