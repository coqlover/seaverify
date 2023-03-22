# Simplest example
# Increment a variable by 1 and by any amount

import sys
sys.path.append(".")
from seaverify.prelude import *

@instruction
def increment_1(n: u64):
    n += 1

@instruction
def increment_value(n: u64, value: u64):
    n += value

#######
# Tests
#######

@test
def test_increment_value_1(n: u64, value1: u64, value2: u64):
    old_n = n
    increment_value(n = n, value = value1)
    seaverify_assert(n == old_n + value1)
    increment_value(n = n, value = value2)
    seaverify_assert(n == old_n + value1 + value2)

@test
def test_increment_value_2(n: u64, value1: u64):
    old_n = n
    increment_value(n = n, value = value1)
    seaverify_assert(n >= old_n)

# Todo fix it
assert(all(verify_tests()))