import sys
sys.path.append(".")
from seaverify.prelude import *

# Write a lot of simple mathematical tests to test every operators

@test
def add(n: u64):
    old_n = n
    n = n + 1
    seaverify_assert(n == old_n + 1)

@test
def add(n: u64, m: u64):
    old_n = n
    n = n + m
    seaverify_assert(n == old_n + m)

@test
def add(n: u64, m: u64):
    old_n = n
    n = n + m
    seaverify_assert(n >= old_n)

@test
def add(n: u64, m: u64):
    n = n + m
    seaverify_assert(n >= m)

@fail_test
def add(n: u64, m: u64):
    n = n + m
    seaverify_assert(n > m)

@fail_test
def add(n: u64, m: u64):
    n = n + m
    seaverify_assert(n < m)

@fail_test
def add(n: u64):
    n += 1
    seaverify_assert(n == 5)

@fail_test
def add(n: u64):
    old_n = n
    n += 1
    seaverify_assert(old_n == n)

@test
def mul(n: u64):
    old_n = n
    n = n * 2
    seaverify_assert(n == old_n + old_n)

#@test
def mul(n: u64, m: u64):
    old_n = n
    n = n * m
    seaverify_assert(n == old_n * m)

#@test
def mul(n: u64, m: u64):
    old_n = n
    n = n * m
    if m != 0:
        seaverify_assert(n >= old_n)
    else:
        seaverify_assert(n == 0)

# Split the above test into 2
#@test
def mul(n: u64, m: u64):
    assert m != 0
    old_n = n
    n = n * m
    seaverify_assert(n >= old_n)

#@test
def mul(n: u64, m: u64):
    assert m == 0
    n = n * m
    seaverify_assert(n == 0)

#@test
def mul(n: u64, m: u64):
    assert m > 1
    old_n = n
    n = n * m
    seaverify_assert(n > old_n)

@fail_test
def mul(n: u64):
    old_n = n
    n = n * 2
    seaverify_assert(n == old_n)

@fail_test
def mul(n: u64):
    old_n = n
    n = n * 5
    seaverify_assert(n == old_n + 10)

@test
def sub(n: u64):
    old_n = n
    n = n - 1
    seaverify_assert(n < old_n)

@test
def sub(n: u64):
    old_n = n
    n = n - 1
    seaverify_assert(old_n > 0)

@test
def sub(n: u64, m: u64):
    old_n = n
    n = n - m
    seaverify_assert(n <= old_n)
    seaverify_assert(n == old_n - m)

@test
def sub(n: u64):
    n = n - n
    seaverify_assert(n == 0)

@fail_test
def sub(n: u64):
    n = n - n
    seaverify_assert(n == 1)

@fail_test
def sub(n: u64):
    old_n = n
    n -= 10
    seaverify_assert(n >= old_n)

assert(all(verify_tests()))