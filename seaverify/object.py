import seahorse.prelude
import z3

# todo check which one to use
# make_int = lambda name: z3.Int(name)
# make_int = lambda name: z3.FreshInt(name)
# make_int = lambda name: z3.BitVec(name, 34)
# make_int = lambda name: z3.BitVec(name, 35) # timeout - not anymore
#make_int = lambda name: z3.BitVec(name, 64)
make_int = lambda name: z3.Int(name)

class HardcodedMapping:
  pass

hardcoded_generic_objects = {
#  List: lambda name, type: z3.Array(name, z3.IntSort(), type)
}

hardcoded_base_objects = {
  seahorse.prelude.u64: make_int,
  seahorse.prelude.Pubkey: lambda name: z3.String(name),
  HardcodedMapping: lambda name: z3.Function(name, z3.StringSort(), z3.IntSort()), # todo generalize the intsort with above
}