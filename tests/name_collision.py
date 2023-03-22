# Simplest example
# Increment a variable by 1 and by any amount

import sys
sys.path.append(".")
from seaverify.prelude import *

@test
def correct(n: u64):
    n = 1
    seaverify_assert(n == 1)

@test
def correct(n: u64):
    n = 1
    seaverify_assert(n == 2)

@test
def correct(n: u64):
    n = 1
    seaverify_assert(n == 3)

@test
def correct(n: u64):
    n = 5
    seaverify_assert(n == 5)

@test
def correct(n: u64):
    n = 6
    seaverify_assert(n == 6)

@fail_test
def fail(n: u64):
    n = 1
    seaverify_assert(n == 2)

@fail_test
def fail(n: u64):
    n = 1
    seaverify_assert(n == 1)

@fail_test
def fail(n: u64):
    n = 2
    seaverify_assert(n == 2)

@fail_test
def fail(n: u64):
    n = 3
    seaverify_assert(n == 4)

assert verify_tests() == [True, False, False, True, True, True, False, False, True]

# ====================
# Results of tests:
# ✅ correct
# ❌ correct
# ❌ correct
# ✅ correct
# ✅ correct
# ✅ fail
# ❌ fail
# ❌ fail
# ✅ fail