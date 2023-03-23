import sys
sys.path.append(".")
from seaverify.prelude import *

@test
def assign(n: u64):
    n = 1
    seaverify_assert(n == 1)

@test
def assign(n: u64):
    n = 1
    seaverify_assert(n == 1)

@fail_test
def assign_2(n: u64):
    n = 1
    seaverify_assert(n == 2)

@fail_test
def assign_2(n: u64):
    n = 1
    seaverify_assert(n == 2)

@test
def assign_value(n: u64, m: u64):
    n = m
    seaverify_assert(n == m)

@fail_test
def assign_value_fail(n: u64, m: u64):
    n = m
    seaverify_assert(n == 1)

@test
def assign_value_min(n: u64, a: u64, b: u64):
    n = min(a, b)
    seaverify_assert(n == min(a, b))

@test
def assign_value_min(n: u64, a: u64, b: u64):
    n = min(a, b)
    seaverify_assert(n <= a)
    seaverify_assert(n <= b)

@test
def assign_value_min(n: u64, a: u64, b: u64):
    assert a <= b
    n = min(a, b)
    seaverify_assert(n == a)

assert all(verify_tests())