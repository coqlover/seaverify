import sys
sys.path.append(".")
from seaverify.prelude import *

# todo it timesout
#@test
def mul(n: u64, m: u64):
    old_n = n
    new_n = n * m
    seaverify_assert(new_n == old_n * m)

assert(all(verify_tests()))