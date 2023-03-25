# Properties about an imaginary AMM (a simple one, just x*y==k)

import sys
sys.path.append(".")
from seaverify.prelude import *

##############
# Helper funcs
##############

@instruction
def get_price(a: u64, b: u64):
    assert a > 0
    assert b > 0
    return a//b

@instruction
def is_round_price(a: u64, b: u64):
    return get_price(a=a, b=b) * b == a

@instruction
def execute_swap(a: u64, b: u64, delta_a: u64, delta_b: u64, inverse: bool):
    # Todo refactor current condition to that it's applied everywhere
    # Here the arithmetic constraints inside the if branch are asked no matter current_condition
    product = a * b
    if inverse == 0:
        a += delta_a
        b -= delta_b
    else:
        a -= delta_a
        b += delta_b
    assert a * b == product

#######
# Tests
#######

# Verify that when we do a swap, token_a goes up and token_b goes down
@test
def quantity_is_consistent(a: u64, b: u64, delta_a: u64, delta_b: u64):
    start_a = a
    start_b = b
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=0)
    seaverify_assert(a >= start_a)
    seaverify_assert(b <= start_b)

@fail_test
def quantity_is_consistent(a: u64, b: u64, delta_a: u64, delta_b: u64):
    start_a = a
    start_b = b
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=1)
    seaverify_assert(a >= start_a)
    seaverify_assert(b <= start_b)

# When we do a swap the only ammount that makes the product stays constant
# is indeed the formula every AMM uses
@test
def swap(a: u64, b: u64, delta_a: u64, delta_b: u64):
    start_a = a
    start_b = b
    assert a*b > 0
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=0)
    seaverify_assert(delta_b == (start_b*delta_a) // (start_a+delta_a))

@test
def price_goes_up_when_we_make_a_swap(a: u64, b: u64, delta_a: u64, delta_b: u64, inverse: u64):
    start_a = a
    start_b = b
    assert a*b > 0
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=inverse)
    if inverse==0:
        seaverify_assert(get_price(a=a, b=b) >= get_price(a=start_a, b=start_b))
    else:
        seaverify_assert(get_price(a=a, b=b) <= get_price(a=start_a, b=start_b))

@test
def when_price_went_up_tokena_went_up(a: u64, b: u64, product: u64, delta_a: u64, delta_b: u64, inverse: u64):
    start_a = a
    start_b = b
    assert a*b > 0
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=inverse)
    if get_price(a=a, b=b) > get_price(a=start_a, b=start_b):
        seaverify_assert(a > start_a)
        seaverify_assert(b < start_b)
    if get_price(a=a, b=b) < get_price(a=start_a, b=start_b):
        seaverify_assert(a < start_a)
        seaverify_assert(b > start_b)

@test
def price_stays_the_same_when_we_add_liquidity(start_a: u64, start_b: u64, product: u64, delta_a: u64, delta_b: u64):
    assert start_a * start_b == product
    assert product > 0
    a = start_a + delta_a
    b = start_b + delta_b
    assert a * b == product
    seaverify_assert(get_price(a=a, b=b) == get_price(a=start_a, b=start_b))

@test
def add_liquidity(start_a: u64, start_b: u64, product: u64, delta_a: u64, delta_b: u64):
    assert start_a * start_b == product
    assert product > 0
    a = start_a + delta_a
    b = start_b + delta_b
    assert a * b == product
    seaverify_assert(get_price(a=a, b=b) == get_price(a=start_a, b=start_b))

# Proof:
# start_a = a*start_b + rest_a
# delta_a = a'*delta_b + rest_a'
# get_price(start_a, start_b) = start_a // start_b = (a*start_b + rest_a) // start_b = a + rest_a // start_b = a
# both price are equal => a = a'
# get_price(start_a + delta_a, start_b + delta_b) =
# (a*start_b + rest_a + a*delta_b + rest_a') // (start_b + delta_b) =
# (a*start_b + a*delta_b + rest_a + rest_a') // (start_b + delta_b) =
# [(a*start_b + a*delta_b) // (start_b + delta_b)] + [(rest_a + rest_a') // (start_b + delta_b)] =
# a + (rest_a + rest_a') // (start_b + delta_b) =
# a because rest_a < start_b and rest_a' < delta_b => rest_a + rest_a' < start_b + delta_b so the // is 0
@test
def add_liquidity(start_a: u64, start_b: u64, delta_a: u64, delta_b: u64):
    assert get_price(a=start_a, b=start_b) == get_price(a=delta_a, b=delta_b)
    a = start_a + delta_a
    b = start_b + delta_b
    seaverify_assert(get_price(a=a, b=b) == get_price(a=start_a, b=start_b))

# But the opposite can fail
#(rest_a - rest_a') can be of either sign
@fail_test
def remove_liquidity(start_a: u64, start_b: u64, delta_a: u64, delta_b: u64):
    assert get_price(a=start_a, b=start_b) == get_price(a=delta_a, b=delta_b)
    a = start_a - delta_a
    b = start_b - delta_b
    seaverify_assert(get_price(a=a, b=b) == get_price(a=start_a, b=start_b))

@test
def remove_liquidity(start_a: u64, start_b: u64, delta_a: u64, delta_b: u64):
    assert get_price(a=start_a, b=start_b) == get_price(a=delta_a, b=delta_b)
    rest_a = start_a % start_b
    rest_a_prime = delta_a % delta_b
    assert rest_a - rest_a_prime <= 0
    a = start_a - delta_a
    b = start_b - delta_b
    seaverify_assert(get_price(a=a, b=b) == get_price(a=start_a, b=start_b))

@test
def swap_then_inverse(a: u64, b: u64, delta_a: u64, delta_b: u64):
    start_a = a
    start_b = b
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=0)
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=1)
    seaverify_assert(a == start_a)
    seaverify_assert(b == start_b)

@test
def price_cant_become_zero(a: u64, b: u64, delta_a: u64, delta_b: u64, inverse: u64):
    assert get_price(a=a, b=b) > 0
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=inverse)
    assert is_round_price(a=a, b=b)
    seaverify_assert(get_price(a=a, b=b) > 0)

@test
def pool_cant_be_drained(a: u64, b: u64, delta_a: u64, delta_b: u64, inverse: u64):
    assert a*b > 0
    execute_swap(a=a, b=b, delta_a=delta_a, delta_b=delta_b, inverse=inverse)
    seaverify_assert(a > 0)
    seaverify_assert(b > 0)

assert(all(verify_tests()))