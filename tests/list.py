import sys
sys.path.append(".")
from seaverify.prelude import *

@test
def assign_elt(l: List[u64]):
    l[0] = 4
    seaverify_assert(l[0] == 4)

@test
def assign_elt(l: List[u64], i: u64):
    l[i] = 4
    seaverify_assert(l[i] == 4)

@test
def assign_elt(l: List[u64], i: u64, j: u64):
    l[i] = j
    seaverify_assert(l[i] == j)

@test
def eq(l: List[u64]):
    seaverify_assert(l == l)

@test
def eq(l: List[u64], i: u64):
    seaverify_assert(l[i] == l[i])

@fail_test
def test_size(l: List[u64]):
    seaverify_assert(l.size >= 3)

@test
def test_size(l: List[u64]):
    l[0] = 4
    seaverify_assert(l.size >= 1)

@fail_test
def test_size(l: List[u64]):
    l[0] = 4
    seaverify_assert(l.size >= 2)

@test
def test_size(l: List[u64]):
    seaverify_assert(l.size >= 0)

@test
def test_size(l: List[u64], i: u64):
    l[i] = 4
    seaverify_assert(l.size >= i)

@test
def test_size(l: List[u64], i: u64):
    l[i] = 4
    seaverify_assert(l.size >= i)

@test
def test_size(l: List[u64], i: u64):
    l[i] = 4
    seaverify_assert(l.size >= i+1)

@fail_test
def test_size(l: List[u64], i: u64):
    l[i] = 4
    seaverify_assert(l.size >= i+2)

@fail_test
def test_size(l: List[u64], k: List[u64]):
    seaverify_assert(l.size >= k.size)

@fail_test
def test_size(l: List[u64], k: List[u64]):
    seaverify_assert(l[0] == k[0])

@fail_test
def test_eq(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 4
    seaverify_assert(l == k)

@fail_test
def test_eq(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 4
    assert l.size == 1
    seaverify_assert(l == k)

@fail_test
def create_list(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 2
    assert l.size == 1
    assert k.size == 1
    seaverify_assert(l == k)

@test
def create_list(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 4
    assert l.size == 1
    assert k.size == 1
    seaverify_assert(l == k)

@fail_test
def create_list(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 4
    assert l.size == 2
    assert k.size == 2
    seaverify_assert(l == k)

@test
def test_eq(l: List[u64], k: List[u64]):
    seaverify_assert(l != k)

@test
def test_eq(l: List[u64], k: List[u64]):
    l[0] = 4
    k[0] = 4
    seaverify_assert(l != k)

@fail_test
def test_eq(l: List[u64], k: List[u64]):
    seaverify_assert(l == k)

@test
def transivity(l: List[u64], k: List[u64], o: List[u64]):
    assert l == k
    assert k == o
    seaverify_assert(l == o)

@fail_test
def transitivity(l: List[u64], k: List[u64], o: List[u64]):
    assert l == k
    seaverify_assert(l == o)

@test
def create_list(l: List[u64]):
    l[0] = 1
    l[1] = 2
    l[2] = 3
    assert l.size == 3
    seaverify_assert(l[0] == 1)
    seaverify_assert(l[1] == 2)
    seaverify_assert(l[2] == 3)
    seaverify_assert(l.size == 3)

@test
def test_unreachable(l: List[u64]):
    assert l.size == 1
    l[4] = 2
    seaverify_assert(False)

@fail_test
def test_unreachable(l: List[u64]):
    assert l.size == 1
    seaverify_assert(False)

assert all(verify_tests())