# Seaverify

Seaverify is a tool for verifying properties of SeaHorse programs. It requires the user to specify some properties, and it automatically verifies them with Z3.

It is a work in progress, and doesn't model correctly the semantic of Solana, so please don't use it in production.

## Example

Assuming you have a program like this:

```python
@instruction
def increment(n: u64):
    n += 1
```

You can annotate it with some properties. For instance, that n increases.

```python
@instruction
@enforce(lambda before, after: after.n > before.n)
def increment(n: u64):
    n += 1
```

Or write a test for it:

```python
@test
def test_increment(n: u64):
    old_n = n
    increment(n = n)
    increment(n = n)
    seaverify_assert(n == old_n + 2)
```

Then, seaverify will verify this property for every possible value of n. It cannot miss a testcase (assuming my library doesn't have a bug) like a fuzzer can.

[Run the file `hello_world.py` to see the result!](https://github.com/coqlover/seaverify/blob/main/examples/hello_world.py)

---

Even if you stack a lot of properties, seaverify will verify them very quickly.  
[For instance, for `add_liquidity` of the file `see_amm.py`](https://github.com/coqlover/seaverify/blob/main/examples/see_amm.py#L110:L132)  
These are simple properties, but I guess useful ones, and it takes 1sec to verify them all.
```python
@instruction
# Money is conserved
@enforce(lambda before, after: before.pool_token_vault_a.amount() + before.token_amount_a == after.pool_token_vault_a.amount())
@enforce(lambda before, after: before.pool_token_vault_b.amount() + before.token_amount_b == after.pool_token_vault_b.amount())
# Pool token vault goes up only
@enforce(lambda before, after: before.pool_token_vault_a.amount() <= after.pool_token_vault_a.amount())
@enforce(lambda before, after: before.pool_token_vault_b.amount() <= after.pool_token_vault_b.amount())
# User token account goes down only
@enforce(lambda before, after: before.user_token_account_a.amount() >= after.user_token_account_a.amount())
@enforce(lambda before, after: before.user_token_account_b.amount() >= after.user_token_account_b.amount())
# Balances after are positive
@enforce(lambda before, after: after.pool_token_vault_a.amount() >= 0)
@enforce(lambda before, after: after.pool_token_vault_b.amount() >= 0)
@enforce(lambda before, after: after.user_token_account_a.amount() >= 0)
@enforce(lambda before, after: after.user_token_account_b.amount() >= 0)
# User lp token account goes up only
@enforce(lambda before, after: before.user_lp_token_account.amount() <= after.user_lp_token_account.amount())
# LP token mint goes up only
@enforce(lambda before, after: before.lp_token_mint.supply() <= after.lp_token_mint.supply())
def add_liquidity(
```

When one/some properties are violated, seaverify will tell you which one and give you values of variable that violate this properties:  
(Lot of variable are printed, emphasis here on this readme is mine, the real output is somewhat hard to navigate for now)

```python
Start state:
...
+ Symbolic pool_token_vault_a :
+ + _amount?2 : 0
...
End state:
...
+ Symbolic pool_token_vault_a :
+ + _amount?6 : 3
...
Verification of add_liquidity failed; Here are your properties:
✅ lambda _: True
✅ lambda before, after: before.pool_token_vault_a.amount() + before.token_amount_a == after.pool_token_vault_a.amount()
✅ lambda before, after: before.pool_token_vault_b.amount() + before.token_amount_b == after.pool_token_vault_b.amount()
✅ lambda before, after: before.pool_token_vault_a.amount() <= after.pool_token_vault_a.amount()
✅ lambda before, after: before.pool_token_vault_b.amount() <= after.pool_token_vault_b.amount()
✅ lambda before, after: before.user_token_account_a.amount() >= after.user_token_account_a.amount()
✅ lambda before, after: before.user_token_account_b.amount() >= after.user_token_account_b.amount()
❌ lambda before, after: after.pool_token_vault_a.amount() == 0
✅ lambda before, after: after.pool_token_vault_b.amount() >= 0
✅ lambda before, after: after.user_token_account_a.amount() >= 0
✅ lambda before, after: after.user_token_account_b.amount() >= 0
✅ lambda before, after: before.user_lp_token_account.amount() <= after.user_lp_token_account.amount()
✅ lambda before, after: before.lp_token_mint.supply() <= after.lp_token_mint.supply()
```

[Check out the file `see_amm.py` for more](https://github.com/coqlover/seaverify/blob/main/examples/see_amm.py)  

---

Even "non-trivial" are easy to write for you and easy to verify for the solver.  
For instance for a tictactoe game, it's instant to verify the fact that there can only be one winner at the same time.

To do so, we ask the solver to prove that "There is no winner" implies "There can't be 2winners". Here is the property:

```python
not first_win(moves=before.moves) and not second_win(moves=before.moves)
=> not (first_win(moves=after.moves) and second_win(moves=after.moves))
```

And the solver proves that property instantly. [Check out the file tictactoe.py for more](https://github.com/coqlover/seaverify/blob/main/examples/tictactoe.py).  

## Installation

+ Clone this repository: `git clone github.com/coqlover/seaverify`
+ Install python-z3: `pip3 install z3-solver`

## Usage

To just try it, run any file of the folder examples. For instance: `python3 examples/calculator.py`

To add seaverify to your project, I haven't tested yet, but here are the steps:

+ Clone this repository in your project: `git clone https://github.com/coqlover/seaverify`
+ Replace the seahorse prelude by mine: `from seahorse.prelude import *` by `from seaverify.prelude import *`
+ Add `verify_contract() if __name__ == "__main__" else None` at the end of your file
+ Run `python3 your_file.py` to verify properties
+ Run `python3 seaverify/build.py` instead of `seahorse build` to build your program (haven't tested that yet)

## Features

+ **Verification of properties about function**.  
For instance, `@enforce(lambda before, after: after.n == before.n + 1)` will prove that the function increments n. You can also `@assume` something, eg `n>0`, if you know that this function CAN'T be called with `n==0`.  
Check the file `examples/calculator.py` for an example.
+ **Verification of invariants**.  
For instance, `@invariant(lambda state: state.n > 0)` will prove that after every `@instruction` call, `n` is always stricly positive. The way to prove that, is to ask the solver to prove, for every function, that if n was stricly positive before the function, then it'll be after.  
Check the file `examples/invariant.py` for an example.  
(When I wrote that I think I misunderstood how programs works in Solana, so this may not be very useful). 
+ **Symbolic testing**.  
Create test functions, the solver will try every possible value and you will be confident your test suite cannot forget an edge case value like a fuzzer can.  
Check the file `examples/hello world.py` and `examples/calculator.py` for an example. 

## Non-features

This tool only supports u64, so right now values can't be negative.

Same for everything specific to solana, I need to dive deep into anchor and the sealevel to make sure the way my library model the behavior of solana objects is correct.

So there is absolutely no guarantee that seaverify model correctly the semantic of solana. Do not use it in production.

Same for function calls. I'm not sure yet if I copy arguments, or pass reference to it. For now it's a reference if you give a variable, and a copy if you do a function call. I'm not sure what to do, it'll probably change in the future.

## How it works

The code is compiled to Z3 expression.

Then we ask Z3 some questions, it depends on what we want to do.

Also, unlike other verification tools, the analysis is done directly on the source code, and not on the compiled bytecode.

### Assertion of properties

For instance, if your code is:

```python
@assume(A1)
@assume(A2)
@enforce(B1)
@enforce(B2)
def f(args)
    C
```

Then Z3 is asked to find value of args such that:

```python
A1(args) and A2(args) and B(args) and ((not C1(args)) or (not C2(args)))
```

If it succeeds, it returns a counterexample that violate for instance C1, otherwise it returns `unsat` and the property is verified for all inputs!

### Symbolic testing

For instance, if your code is:

```python
@test
def f(args)
    A1
    seaverify_assert_eq(B1)
    A2
    seaverify_assert_eq(B2)
```

Then Z3 is asked to find value of args such that:

```python
A1(args) and A2(args) and ((not B1(args)) or (not B2(args)))
```

If it succeeds, it returns a counterexample that violate the assertion, otherwise it returns `unsat` and your test is valid for all inputs!