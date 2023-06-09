# Translation of ast python object to z3 expression
# Doc of ast python: https://docs.python.org/3/library/ast.html
# (Copilot got the doc first try lmao)

from seaverify.global_vars import all_instructions, all_vars, begin_vars, global_counter, symbolic_objects, current_before_name, current_after_name, solver, every_assert_statement
from seaverify.object import hardcoded_base_objects, make_int, HardcodedMapping
from seaverify.operator import operator_to_z3
import seahorse
import z3
import ast
import inspect
import textwrap

def lambda_to_z3(lam, init_args, only_after=False):
    # Retrieve the name of the arguments of the lambda
    lambda_args = lam.body[0].value.args.args
    global current_before_name
    global current_after_name
    current_before_name = lambda_args[0].arg
    current_after_name = lambda_args[1].arg if len(lambda_args) > 1 else None
    if only_after and current_after_name is None:
        current_before_name, current_after_name = current_after_name, current_before_name
    # Get the body of the lambda
    function = lam
    try:
        function = function.body[0]
    except:
        pass
    # todo rewrite the whole function
    class Arg:
        def __init__(self, arg) -> None:
            self.arg = arg
    args = [Arg(i) for i in begin_vars] # todo
    all_vars.clear()
    for i in range(len(args)):
        all_vars[args[i].arg] = init_args[i]
    return stmt_to_z3(function)

def add_args_to_solver(function, init_args):
    all_vars.clear()
    begin_vars.clear()
    function = ast.parse(inspect.getsource(function))
    function = function.body[0]
    args = function.args.args
    from copy import deepcopy
    for i in range(len(args)):
        all_vars[args[i].arg] = init_args[i]
        begin_vars[args[i].arg] = deepcopy(init_args[i])

def create_z3_expr(function):
    function = function.body[0]
    return stmt_to_z3(function.body)

def stmt_to_z3(node, current_condition=z3.BoolVal(True)):
    # print("stmt_to_z3", node, type(node))
    aux_expr_to_z3 = lambda node: expr_to_z3(node, current_condition) # same but propagate current_condition
    if type(node) == list:
        if len(node) == 0:
            return None
        for i in range(len(node)-1):
            stmt_to_z3(node[i], current_condition)
        return stmt_to_z3(node[-1], current_condition)
    if isinstance(node, ast.If):
        condition = aux_expr_to_z3(node.test)
        body = stmt_to_z3(node.body, z3.And(current_condition, condition))
        orelse = stmt_to_z3(node.orelse, z3.And(current_condition, z3.Not(condition)))
        if body is None:
            body = z3.BoolVal(True)
        if orelse is None:
            orelse = z3.BoolVal(True)
        return z3.simplify(z3.If(z3.And(current_condition, condition), body, orelse))
    elif isinstance(node, ast.Return):
        return aux_expr_to_z3(node.value)
    elif isinstance(node, ast.AugAssign):
        target = node.target
        assert isinstance(target, ast.Name) or isinstance(target, ast.Attribute), "Only single variable assigment is supported for now"
        target_name = target.id if isinstance(target, ast.Name) else target.attr
        value = aux_expr_to_z3(node.value)
        aug_value = operator_to_z3(node.op, [get_z3_object(target), value])
        get_z3_object(target, current_condition, target_name, aug_value)
        return None
    elif isinstance(node, ast.Assign):
        assert len(node.targets) == 1, "Please split your multiple assigment expr into single assigments expression"
        target = node.targets[0]
        # Array
        if isinstance(target, ast.Subscript):
            target_name = target.value.id
            target_index = aux_expr_to_z3(target.slice)
            #new_value = z3.Store(get_z3_object(target.value), target_index, aux_expr_to_z3(node.value))
            obj = get_z3_object(target.value)
            value = aux_expr_to_z3(node.value)
            obj[target_index] = z3.simplify(z3.If(current_condition, value, obj[target_index]))
            #new_value = z3.Store(get_z3_object(target.value)._list, target_index, aux_expr_to_z3(node.value))
            #get_z3_object(target.value, current_condition, target_name, new_value)
        else:
            assert isinstance(target, ast.Name) or isinstance(target, ast.Attribute), "Only single variable assigment is supported for now"
            target_name = target.id if isinstance(target, ast.Name) else target.attr
            new_value = aux_expr_to_z3(node.value)
            if type(new_value) == list:
                new_value = list_to_z3(new_value)
            get_z3_object(target, current_condition, target_name, new_value)
        return None
    elif isinstance(node, ast.Expr):
        return aux_expr_to_z3(node.value)
    elif isinstance(node, ast.Assert):
        solver.add(z3.simplify(z3.Implies(current_condition, aux_expr_to_z3(node.test))))
        return None
    else:
        raise Exception("Todo in stmt_to_z3 -> node type: " + str(type(node)))

def expr_to_z3(node, current_condition=z3.BoolVal(True)):
    #print("expr_to_z3", node, type(node))
    aux_expr_to_z3 = lambda node: expr_to_z3(node, current_condition) # same but propagate current_condition
    if isinstance(node, ast.Constant):
        return constant_to_z3(type(node.value), node.value)
    elif isinstance(node, ast.Compare):
        assert len(node.ops) == 1
        assert len(node.comparators) == 1
        left = aux_expr_to_z3(node.left)
        right = aux_expr_to_z3(node.comparators[0])
        return operator_to_z3(node.ops[0], [left, right])
    elif isinstance(node, ast.BoolOp):
        values = [aux_expr_to_z3(n) for n in node.values]
        return operator_to_z3(node.op, values)
    elif isinstance(node, ast.BinOp):
        left, right = aux_expr_to_z3(node.left), aux_expr_to_z3(node.right)
        return operator_to_z3(node.op, [left, right])
    elif isinstance(node, ast.UnaryOp):
        return operator_to_z3(node.op, [aux_expr_to_z3(node.operand)])
    elif isinstance(node, ast.Name):
        return all_vars[node.id]
    elif isinstance(node, ast.Attribute):
        return get_z3_object(node)
    elif isinstance(node, ast.Lambda):
        return aux_expr_to_z3(node.body)
    elif isinstance(node, ast.List):
        all_values = [aux_expr_to_z3(n) for n in node.elts]
        return all_values
    elif isinstance(node, ast.Subscript):
        value = aux_expr_to_z3(node.value)
        index = node.slice.value if isinstance(node.slice, ast.Constant) else aux_expr_to_z3(node.slice)
        # todo only aux_expr_to_z3(node.slice)
        #value.__getitem__(value, index)
        return value[index] if isinstance(value, list) else value[index]
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id == "print":
                print("LOG:", [aux_expr_to_z3(n) for n in node.args])
                return None
            if node.func.id == "min" or node.func.id == "max":
                assert len(node.args) == 2, "We support only when min and max take exactly two arguments"
                left = aux_expr_to_z3(node.args[0])
                right = aux_expr_to_z3(node.args[1])
                if node.func.id == "min":
                    return z3.If(left < right, left, right)
                else:
                    return z3.If(left > right, left, right)
            if node.func.id == "seaverify_assert":
                assert len(node.args) == 1, "seaverify_assert takes only one argument"
                b = aux_expr_to_z3(node.args[0])
                every_assert_statement.append(z3.simplify(z3.Implies(current_condition, b)))
                return None
            if node.func.id == "seaverify_implies":
                assert len(node.args) == 2, "seaverify_implies takes two arguments"
                a = aux_expr_to_z3(node.args[0])
                b = aux_expr_to_z3(node.args[1])
                return z3.simplify(z3.Implies(current_condition, z3.Implies(a, b)))
            if node.func.id == "z3_map_assign":
                assert len(node.args) == 3
                f = get_z3_object(node.args[0])
                index = aux_expr_to_z3(node.args[1])
                value = aux_expr_to_z3(node.args[2])
                name = f.name() if f is not None else "map"
                new_f = hardcoded_base_objects[HardcodedMapping](global_counter.create(name))
                idx = z3.Const(global_counter.create("idx_"+name), index.sort())
                solver.add(z3.ForAll(idx, z3.Implies(idx != index, new_f(idx) == f(idx))))
                solver.add(new_f(index) == value)
                return new_f
            if node.func.id == "z3_map_lookup":
                assert len(node.args) == 2
                f = get_z3_object(node.args[0])
                index = aux_expr_to_z3(node.args[1])
                answer = z3.Const(global_counter.create(f.name()+"["+str(index)+"]"), f.range())
                solver.add(answer == f(index))
                return answer
            # Otherwise, it's a function call
            # Push every arguments in all_vars, execute the function, and clean all_vars
            # Todo refactor below
            possible_candidates = [f for f in all_instructions if f.__name__ == node.func.id]
            assert len(possible_candidates) > 0, "No function named "+node.func.id+" found"
            assert len(possible_candidates) == 1, "Multiple functions named "+node.func.id+" found"
            f = possible_candidates[0]
            old_vars = {}
            for k, v in all_vars.items():
                old_vars[k] = v
            assert len(node.args) == 0, "Only keyword arguments are supported"
            new_all_vars = {}
            for kw in node.keywords:
                new_all_vars[kw.arg] = aux_expr_to_z3(kw.value)
            all_vars.clear()
            for k, v in new_all_vars.items():
                all_vars[k] = v
            # Execute the function
            import seaverify
            answer = seaverify.decorators.transform_f_to_z3(f)
            # Clean all_vars
            new_all_vars.clear()
            for k, v in old_vars.items():
                new_all_vars[k] = v
            for kw in node.keywords:
                if isinstance(kw.value, ast.Name):
                    new_all_vars[kw.value.id] = all_vars[kw.arg]
            all_vars.clear()
            for k, v in new_all_vars.items():
                all_vars[k] = v
            return answer
        elif isinstance(node.func, ast.Attribute):
            # This is an object calling one of its method with kwargs
            obj = get_z3_object(node.func.value)
            method_name = node.func.attr
            kwargs = {kw.arg: aux_expr_to_z3(kw.value) for kw in node.keywords}
            # at the end of the call we want to execute getattr(obj, method_name)(obj, **kwargs)
            # add self, kwargs to all_vars
            old_vars = {}
            for k, v in all_vars.items():
                old_vars[k] = v
            for k, v in kwargs.items():
                all_vars[k] = v
            all_vars["self"] = obj
            # execute the method
            f = getattr(obj, method_name)
            f = inspect.getsource(f.__code__)
            f = "\n".join(f.split("\n")[1:])
            f = textwrap.dedent(f)
            function = ast.parse(f)
            answer = stmt_to_z3(function.body, current_condition)
            all_vars.clear()
            for k, v in old_vars.items():
                all_vars[k] = v
            return answer
        else:
            assert False, "Other function calls not supported yet"
    else:
        raise Exception("Todo in expr_to_z3 -> node type: " + str(type(node)))

# todo generalize to create default value of sort
# todo forbid negative index
# todo rewrite
def list_to_z3(values):
    if not type(values) == list:
        return values
    from seaverify.prelude import Z3List
    return Z3List(values, len(values))
    assert len(values) >= 1, "Creation of empty array not yet supported due to lackness of type"
    array_sort = z3.IntSort() # todo generalize
    answer = z3.Array(global_counter.create("array"), z3.IntSort(), array_sort)
    for i, v in enumerate(values):
        solver.add(z3.Select(answer, i) == v)
    # Defa
    idx = z3.Int(global_counter.create("array_index"))
    default_value = -1
    if hasattr(values[0], "sort") and values[0].sort() == z3.StringSort():
        default_value = z3.String(global_counter.create("default_string"))
    solver.add(z3.simplify(z3.ForAll(idx, z3.Implies(idx >= len(values), z3.Select(answer, idx) == default_value))))
    solver.add(z3.simplify(z3.ForAll(idx, z3.Implies(idx < 0, z3.Select(answer, idx) == default_value))))
    return answer

def get_z3_object(node, current_condition=None, new_name=None, new_value=None):
    is_assigment = (current_condition is not None) and (new_name is not None) and (new_value is not None)
    # Node can either be a simple variable, in that case we return from the args of the function
    # Or, it can be nested get_attributes call of an object (aka variable.name.blabla)
    # In that case, we unroll the chain of call to get variable, get it from the arg, and roll it back
    # while node is an attribute, unroll it to the the very first variable
    current_node = node
    parent_node = None
    chain = []
    while isinstance(current_node, ast.Attribute):
        chain.append(current_node)
        parent_node = current_node
        current_node = current_node.value
    first_elem = chain[0] if chain else None
    # Now, we pick from the function argument
    # if current_node is before/after, then we want parent_node
    # todo refactor this shit too
    is_in_lambda = (current_node.id == current_before_name) or (current_node.id == current_after_name)
    name_in_allvars = parent_node.attr if is_in_lambda else current_node.id
    if is_assigment and not new_name in all_vars:
        all_vars[new_name] = None
    #assert name_in_allvars in all_vars, "Variable " + name_in_allvars + " not found"
    if is_in_lambda:
        chain = chain[:-1]
    returned_value = None
    if current_node.id == current_before_name:
        returned_value = begin_vars[name_in_allvars]
    else: #current_node.value.id == current_after_name:
        returned_value = all_vars[name_in_allvars]
    # Roll it back
    second_to_last_elem = None
    for elem in reversed(chain):
        second_to_last_elem = returned_value
        returned_value = getattr(returned_value, elem.attr)
    # Add the new var to the solver
    if is_assigment:
        new_var = None
        is_object = not hasattr(new_value, "sort") #isinstance(new_value, z3.z3.DatatypeRef)
        if is_object:
            # if new_value is a Funcdecl of z3
            if hasattr(new_value, "range"):
                new_var = z3.Function(global_counter.create(new_name), z3.StringSort(), z3.IntSort()) # todo generalize
                idx = z3.Const(global_counter.create("idx"+new_name), z3.StringSort())
                returned_value = new_var if returned_value is None else returned_value
                solver.add(z3.simplify(z3.If(current_condition,
                                 z3.ForAll(idx, new_var(idx) == new_value(idx)), 
                                 z3.ForAll(idx, new_var(idx) == returned_value(idx)))))
            else:
                assert False, "Assigment of object not supported yet"
                #new_var = object_to_z3(new_value, new_name, True)
                new_var = new_value # the line above and the for loop deep-copies the object, here we just do a shallow copy ?
                all_vars[new_name] = new_var
                # for each attribute, add a new variable to the solver
                # for k, v in new_value.__dict__.items():
                #     if not callable(v):
                #         get_z3_object(ast.Attribute(ast.Name(new_name, ast.Load()), k, ast.Load()),
                #                       current_condition, global_counter.create(new_name + "." + k), v)
        else:
            new_var_sort = returned_value.sort() if returned_value is not None else new_value.sort()
            new_var = z3.Const(global_counter.create(new_name), new_var_sort)
        if chain:
            setattr(second_to_last_elem, first_elem.attr, new_var)
        else:
            all_vars[name_in_allvars] = new_var
        if not is_object:
            returned_value = new_var if returned_value is None else returned_value
            solver.add(z3.simplify(z3.If(current_condition, new_var == new_value, new_var == returned_value)))
    return returned_value

def constant_to_z3(object_type, value=None, name=None):
    #print("constant_to_z3", object_type, value)
    if object_type == int:
        name = "CONST"+str(value) if value is not None else None
        name = global_counter.create("const_int") if name is None else name
        answer = make_int(name)
        solver.add(answer == value) if value is not None else None
        return answer
    elif object_type == bool:
        name = "CONST"+str(value) if value is not None else None
        name = global_counter.create("const_bool") if name is None else name
        answer = z3.Bool(name)
        if value is not None:
            solver.add(answer == value)
        return answer
    elif object_type == type or object_type == str: #todo
        name = "const_string" if name is None else name
        return z3.String(global_counter.create(name))
    else:
        if value is not None:
            return z3.String(global_counter.create(name))
        return object_to_z3(object_type, name)
    raise Exception("Todo in constant_to_z3 -> type&value: " + str(object_type) + " " + str(value))

# From a class, create the exact same class but with symbolic attributes
def object_to_z3(cls, name, is_copy=False):
    # If the class is a generic type, eg List[T] or Empty[T]
    if hasattr(cls, "__origin__"):
        # If the class is an Empty[T], return T
        if cls.__origin__ == seahorse.prelude.Empty:
            return object_to_z3(cls.__args__[0], name, is_copy)
        # List, create a z3 array
        if cls.__origin__ == list:
            from seaverify.prelude import Z3List
            return Z3List(z3.Array(global_counter.create(name), z3.IntSort(),
                                   #z3.IntSort()), 0)
                                   object_to_z3(cls.__args__[0], "").sort()), z3.Int(global_counter.create(name + ".length")))
    # If the object is something we hardcode by something special, we just return it
    if cls in hardcoded_base_objects:
        return hardcoded_base_objects[cls](global_counter.create(name))
    # If the class already exists, we just return it - not sure yet todo
    if hasattr(cls, "__name__") and cls.__name__ in symbolic_objects:
        pass #return symbolic_objects[cls.__name__]
    # Create a new class with the same name
    new_obj = type("Symbolic " + name, (object,), {})()
    # Transfer each annotation into an attribute
    if hasattr(cls, "__annotations__"):
        for name in cls.__annotations__:
            object_type = cls.__annotations__[name]
            new_attribute = constant_to_z3(object_type, None, name)
            setattr(new_obj, name, new_attribute)
    if is_copy:
        for name in cls.__dict__.keys():
            if not callable(getattr(cls, name)):
                setattr(new_obj, name, None)
    # Transfer each function into a function for the new class
    for name in dir(cls):
        if name.startswith("__") and name not in ["__getitem__", "__setitem__", "__str__", "__repr__"]:
            continue
        #if name in ["__class__", "__dict__", "__doc__", "__module__", "__weakref__"]:
        #    continue
        attr = getattr(cls, name)
        if callable(attr):
            setattr(new_obj, name, attr)
    # Add an "init" function that takes any number of arguments and returns self (todo initialize the fields)
    def init(self, *args, **kwargs):
        return self
    setattr(new_obj, "init", init)
    return new_obj