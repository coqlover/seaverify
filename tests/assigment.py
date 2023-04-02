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

@test
def in_if_branch(n: u64):
    n = 0
    if False:
        n = 1
    seaverify_assert(n == 0)

@test
def in_if_branch(n: u64):
    n = 0
    if True:
        n = 1
    seaverify_assert(n == 1)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    seaverify_assert(n == 1)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if n == 1:
        n = 2
    seaverify_assert(n == 2)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if n == 7:
        n = 2
    seaverify_assert(n == 1)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if n == 1:
        n = 2
    if n == 1:
        n = 3
    seaverify_assert(n == 2)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if False:
        n = 2
    if n == 1:
        n = 3
    seaverify_assert(n == 3)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if True:
        n = 2
    if n == 1:
        n = 3
    seaverify_assert(n == 2)

@test
def in_if_branch(n: u64):
    n = 0
    if n == 0:
        n = 1
    if False:
        n = 2
    if n == 2:
        n = 3
    seaverify_assert(n == 1)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    seaverify_assert(l[0] == 1)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if False:
        l[0] = 2
    seaverify_assert(l[0] == 1)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if True:
        l[0] = 2
    seaverify_assert(l[0] == 2)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if False:
        l[0] = 3
    if False:
        l[0] = 2
    seaverify_assert(l[0] == 1)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if False:
        l[0] = 3
    if True:
        l[0] = 2
    seaverify_assert(l[0] == 2)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if True:
        l[0] = 3
    if False:
        l[0] = 2
    seaverify_assert(l[0] == 3)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if True:
        l[0] = 3
    if True:
        l[0] = 2
    seaverify_assert(l[0] == 2)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if True:
        l[0] = 3
    if l[0] == 3:
        l[0] = 2
    seaverify_assert(l[0] == 2)

@test
def assign_array(l: List[u64]):
    l[0] = 1
    if True:
        l[0] = 3
    if l[0] == 1:
        l[0] = 2
    seaverify_assert(l[0] == 3)

assert all(verify_tests())