# Takes some op(*args), adds constraints to the solver, and returns
# eg, a/b adds b!=0 to the solver, and returns the result "a/b"

from seaverify.global_vars import solver
import seaverify
import ast
import z3

# Todo all these operators are in the wrong order?
comparaison_operator_bitvec = {
    ast.Lt: z3.ULT,
    ast.LtE: z3.ULE,
    ast.Gt: z3.UGT,
    ast.GtE: z3.UGE,
    ast.Eq: lambda a,b : a==b,
    ast.NotEq: lambda a,b : a!=b,
}

comparaison_operator_default = {
    ast.Lt: lambda a,b : a<b,
    ast.LtE: lambda a,b : a<=b,
    ast.Gt: lambda a,b : a>b,
    ast.GtE: lambda a,b : a>=b,
    ast.Eq: lambda a,b : a==b,
    ast.NotEq: lambda a,b : a!=b,
}

comparaison_constraints_int = lambda a, b: solver.add(a >= 0, a <= 2**64, b >= 0, b <= 2**64)

arithmetic_operator_bitvec = {
    ast.Add: lambda a,b : a+b,
    ast.Sub: lambda a,b : a-b,
    ast.Mult: lambda a,b : a*b,
    ast.Div: z3.UDiv, #todo
    ast.FloorDiv: z3.UDiv, #todo
    ast.Pow: lambda a,b : a**b, #todo because it fails right now
    ast.Mod: z3.URem, #todo
}

arithmetic_operator_default = {
    ast.Add: lambda a,b : a+b,
    ast.Sub: lambda a,b : a-b,
    ast.Mult: lambda a,b : a*b,
    ast.Div: lambda a,b : a/b, #todo
    ast.FloorDiv: lambda a,b : a/b, #todo
    ast.Pow: lambda a,b : a**b, #todo
    ast.Mod: lambda a,b : a%b, #todo
}

arithmetic_constraints_bitvec = {
    ast.Add: lambda a,b : solver.add(z3.BVAddNoOverflow(a, b, False), z3.BVAddNoUnderflow(a, b)),
    ast.Sub: lambda a,b : solver.add(z3.BVSubNoOverflow(a, b), z3.BVSubNoUnderflow(a, b, False)),
    ast.Mult: lambda a,b : solver.add(z3.BVMulNoOverflow(a, b, False), z3.BVMulNoUnderflow(a, b)),
    ast.Div: lambda a,b : solver.add(b != 0), # todo
    ast.FloorDiv: lambda a,b : solver.add(b != 0), # todo
    ast.Pow: lambda a,b : solver.add(b != 0), # todo
    ast.Mod: lambda a,b : solver.add(b != 0), # todo
}

arithmetic_constraints_int = {
    ast.Add: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.Sub: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.Mult: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.Div: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.FloorDiv: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.Pow: lambda ans : solver.add(ans >= 0, ans <= 2**64),
    ast.Mod: lambda _ : None
}

logical_operator_default = {
    ast.And: z3.And,
    ast.Or: z3.Or,
    ast.Not: z3.Not,
}

def operator_to_z3(op, args):
    is_bitvec = isinstance(args[0], z3.BitVecRef)
    is_int = args[0].sort() == z3.IntSort() if hasattr(args[0], "sort") else False
    is_bool = args[0].sort() == z3.BoolSort() if hasattr(args[0], "sort") else False
    is_function = isinstance(args[0], z3.FuncDeclRef)
    is_str = args[0].sort() == z3.StringSort() if hasattr(args[0], "sort") else False
    from seaverify.prelude import Z3List
    is_array = type(args[0]) == Z3List or type(args[0]) == list
    is_python_object = not is_bitvec and not is_int and not is_bool and not is_function and not is_str and not is_array
    # Comparaison
    if type(op) in comparaison_operator_bitvec:
        assert len(args) == 2, "Comparaison with more than 2 args: " + str(args)
        if is_bitvec:
            return comparaison_operator_bitvec[type(op)](*args)
        if is_int:
            comparaison_constraints_int(*args)
            return comparaison_operator_default[type(op)](*args)
        if (type(op) == ast.Eq or type(op) == ast.NotEq) and (is_function or is_array or is_python_object):
            if is_function:
                idx = z3.Const("idx", z3.StringSort())
                return z3.ForAll(idx, args[0](idx) == args[1](idx)) if type(op) == ast.Eq else z3.Exists(idx, args[0](idx) != args[1](idx))
            if is_array:
                idx = z3.Const("idx", z3.IntSort())
                cond = z3.simplify(z3.And(idx >= 0, idx < args[0].size, idx < args[1].size))
                left = seaverify.toz3.list_to_z3(args[0])
                right = seaverify.toz3.list_to_z3(args[1])
                #assert args[0].range() == args[1].range(), "Arrays of different types: " + str(args)
                if type(op) == ast.Eq:
                    return z3.And(left.size == right.size, z3.ForAll(idx, z3.Implies(cond, left[idx] == right[idx])))
                if type(op) == ast.NotEq:
                    return z3.Or(left.size != right.size, z3.Exists(idx, z3.Implies(cond, left[idx] != right[idx])))
                else:
                    assert False, "Unreachable"
                #return z3.ForAll(idx, left[idx] == right[idx]) if type(op) == ast.Eq else z3.Exists(idx, left[idx] != right[idx])
            if is_python_object:
                # Loop over all the attributes
                every_eq = []
                for attr in dir(args[0]):
                    if attr.startswith("__"):
                        continue
                    if attr == "_repr_html_":
                        continue
                    if hasattr(args[0], attr):
                        if not hasattr(args[1], attr):
                            return z3.BoolVal(False)
                        every_eq.append(operator_to_z3(op, [getattr(args[0], attr), getattr(args[1], attr)]))
                if len(every_eq) == 0:
                    return z3.BoolVal(True) if type(op) == ast.Eq else z3.BoolVal(False)
                return z3.And(*every_eq) if type(op) == ast.Eq else z3.Or(*every_eq)
        else:
            return comparaison_operator_default[type(op)](*args)
    # Arithmetic
    elif type(op) in arithmetic_operator_default:
        assert len(args) == 2, "Not supported yet, arithmetic with more than 2 args: " + str(args)
        if is_bitvec:
            a, b = args
            arithmetic_constraints_bitvec[type(op)](a, b)
            return arithmetic_operator_bitvec[type(op)](a, b)
        if is_int:
            answer = arithmetic_operator_default[type(op)](*args)
            comparaison_constraints_int(*args)
            arithmetic_constraints_int[type(op)](answer)
            return answer
        assert False, "Not supported yet, arithmetic with non bitvec or int: " + str(args)
    # Logical
    elif type(op) in logical_operator_default:
        return logical_operator_default[type(op)](*args)
    else:
        raise Exception("Todo in operator_to_z3 -> op type: " + str(type(op)))
