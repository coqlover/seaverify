import sys
sys.path.append(".")
from seaverify.prelude import *

@test
def implies_u64(n: u64):
    m = n
    seaverify_assert(seaverify_implies(n == 1, m == 1))

@test
def implies_u64(n: u64):
    m = n
    seaverify_assert((not (m == 1)) or (n == 1))

@fail_test
def implies_u64(n: u64):
    m = n
    seaverify_assert(n == 1)

@fail_test
def implies_u64(n: u64):
    m = n
    seaverify_assert(m == 1)

@fail_test
def implies_u64(n: u64):
    m = n
    seaverify_assert((m == 1) and (n == 1))

@fail_test
def implies_u64(n: u64):
    m = n
    seaverify_assert((not (m == 1)) and (not (n == 1)))

@test
def implies_bool(n: u64, m: u64):
    a = n == 1
    b = m == 1
    assert (seaverify_implies(a, b))
    seaverify_assert((not a) or b)

@test
def implies_bool(n: u64, m: u64):
    a = n == 1
    b = m == 1
    assert ((not a) or b)
    seaverify_assert(seaverify_implies(a, b))

@test
def implies_bool(n: u64, m: u64, o: u64):
    a = n == 1
    b = m == 1
    c = o == 1
    assert (c == seaverify_implies(a, b))
    seaverify_assert(c == ((not a) or b))

@test
def implies_bool(n: u64, m: u64):
    a = n == 1
    b = m == 1
    seaverify_assert(((not a) or b) == seaverify_implies(a, b))

assert all(verify_tests())