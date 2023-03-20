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
@enforce(lambda before, after: after.n == before.n + 1)
def increment(n: u64):
    n += 1
```

Then, seaverify will verify this property for every possible value of n. It cannot miss a testcase (assuming my library doesn't have a bug) like a fuzzer can.

Run the program `hello world.py` to see the result!

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

## Usage

To try it, you probably need Z3, and then clone this repo and execute any file of the folder example: `python3 examples/calculator.py`

To add seaverify to your project, here are the steps:

+ Clone this repository in your project: `git clone https://github.com/coqlover/seaverify`
+ Replace the seahorse prelude by mine: `from seahorse.prelude import *` by `from seaverify.prelude import *`
+ Add `verify_contract() if __name__ == "__main__" else None` at the end of your file
+ Run `python3 your_file.py` to verify properties
+ Run `python3 seaverify/build.py` instead of `seahorse build` to build your program (haven't tested that yet)

## Features

+ Verification of properties on before/after values of arguments of the functions of your program: `@enforce(lambda before, after: after.n == before.n + 1)` -> here `before.n` is the value of n before the function is called, and `after.n` is the value of n after the function is called. Check the file `examples/calculator.py` for an example.
+ Assumptions of properties on before values of arguments of the functions of your program: `@assume(lambda before: before.n >= 0)` -> here `before.n` is the value of n before the function is called, and this property is assumed to be true. This is useful if you know it's true, but don't spend compute time to assert it. Check the file `examples/assume.py` for an example.
+ Verification of invariants on the state of your program: `@invariant(lambda state: state.n >= 0)` -> here `state.n` is the value of n at every function call. It verifies, for every instruction of your program, that if the invariant is true before a function call, it will be true after the function call. I think I misunderstood how programs works in Solana, so this may not be very useful. Check the file `examples/invariant.py` for an example.

## Non-features

I only support i64 and u64, and everything is considered a u64, so can't be negative.

Same for everything specific to solana, I need to dive deep into anchor and the sealevel to make sure the way my library model the behavior of solana objects is correct.

So there is absolutely no guarantee that seaverify model correctly the semantic of solana. Do not use it in production.

## How it works

Code written in the decorators are compiled to Z3 expression, as well as the code of the function. Then, the Z3 solver is used to verify that the function satisfies the property.

Unlike other verification tools, the analysis is done directly on the source code, and not on the compiled bytecode.

For instance, your code is:

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
