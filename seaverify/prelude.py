# Override some part of the seahorse prelude to add feature
# Ideally, can't break anything

from seaverify.global_vars import symbolic_objects, all_instructions
from seahorse.prelude import *
from seaverify.object import HardcodedMapping
# Function we don't use but expose the end user to (non exhaustive list)
from seaverify.decorators import assume, invariant, test, fail_test, enforce, add_invariant, verify_contract, verify_tests

# ==================
# Hardcoded function
# ==================

def z3_map_lookup(map: HardcodedMapping, key: str):
    """Return the value associated with key in map"""

def z3_map_assign(map: HardcodedMapping, key: str, value: int):
    """Return a new map with key associated with value"""

def seaverify_assert(value: Any) -> None:
    """Assert that value is true."""

def seaverify_implies(A: Any, B: Any) -> None:
    """Create the statement A => B."""

# ==========
# Rust types
# ==========


# ============
# Solana types
# Todo write them correctly
# ============

# should have bump but I have a name collision thing problem. Todo
class Pool:
    authority: str
    token_mint_a: str
    token_mint_b: str
    token_vault_a: str
    token_vault_b: str
    lp_token_mint: str
    def init(self, payer=None, seeds=None):
        return self

class TokenOwner:
    _map: HardcodedMapping
    def transfer(self, authority=None, to=None, amount=None):
        assert amount >= 0
        assert authority._owner == self
        assert to._owner == self
        authority_amount = z3_map_lookup(self._map, authority.key())
        to_amount = z3_map_lookup(self._map, to.key())
        self._map = z3_map_assign(self._map, authority.key(), authority_amount - amount)
        self._map = z3_map_assign(self._map, to.key(), to_amount + amount)
    def balance(self, user=None):
        return z3_map_lookup(self._map, user.key())

class TokenAccount(AccountWithKey):
    _amount: u64
    _key: str
    #_mint: str
    # _owner: TokenOwner
    def transfer(self, authority=None, to=None, amount=None, signer=None):
        #assert self._mint == to._mint
        self._amount -= amount
        to._amount += amount
        #self._owner.transfer(authority = self, to = to, amount = amount)
    def amount(self):
        return self._amount #return self._owner.balance(user = self)
    def key(self):
        return self._key
    def init(self, payer=None, authority=None, mint=None, seeds=None):
        self._amount = 0
        #self._authority = authority
        #self._mint = mint
        return self

class TokenMap(AccountWithKey):
    _amount: u64
    _key: str
    _map: HardcodedMapping
    def transfer(self, authority=None, to=None, amount=None, signer=None):
        assert amount >= 0
        authority_amount = z3_map_lookup(self._map, authority.key())
        to_amount = z3_map_lookup(self._map, to.key())
        self._map = z3_map_assign(self._map, authority.key(), authority_amount - amount)
        self._map = z3_map_assign(self._map, to.key(), to_amount + amount)
    def balance(self, user=None):
        return z3_map_lookup(self._map, user.key())
    def amount(self):
        return self._amount
    def key(self):
        return self._key
    def init(self, payer=None, authority=None, mint=None, seeds=None):
        return self

class TokenMint(AccountWithKey):
    decimals: u8
    _supply: u64
    _key: str
    def mint(self, authority=None, to=None, amount=None):
        self._supply += amount
        to._amount += amount
    def burn(self, authority=None, holder=None, amount=None):
        self._supply -= amount
        holder._amount -= amount
    def supply(self):
        return self._supply
    def key(self):
        return self._key

class Signer:
    _key: str
    def key(self):
        return self._key

class PubkeyClass:
    def find_program_address(self, a, b):
        return ["ok"]

# Currently not used
symbolic_objects.update({
    "TokenAccount": TokenAccount,
    "TokenMint": TokenMint,
    "Signer": Signer,
    "PubkeyClass": PubkeyClass
})

# ================
# Helper functions
# ================


def instruction(function: Callable[..., None]) -> Callable[..., None]:
    """Decorator to turn a function into a program instruction."""
    all_instructions.append(function)
    return function

def dataclass(function: Callable[..., None]) -> Callable[..., None]:
    """Decorator to create an automatic default class constructor."""