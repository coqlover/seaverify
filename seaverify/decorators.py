from seaverify.object import *
from seaverify.toz3 import create_z3_expr, all_vars, begin_vars, global_counter, lambda_to_z3, add_args_to_solver, object_to_z3
from seaverify.prelude import solver, all_instructions, reset_solver
import ast
import functools
import inspect
import z3

# ================
# Helper functions
# ================

def print_z3_var(var, model, s="+"):
  if var is None:
    return
  # if var is a z3 ast, print it
  if isinstance(var, z3.AstRef):
    value = model[var]
    if value is not None:
      print(s, var, ":", value)
  else:
    print(s, var.__class__.__name__, ":")
    # Loop over all attributes of var and print them
    for k in var.__dict__:
      try:
        if not callable(var.__dict__[k]):
          print_z3_var(var.__dict__[k], model, s+" +")
      except:
        pass
    #print("No relevant value (?) for ", var)

def print_solution(func, simplified=False):
  if not simplified:
    print("---------------------------------")
    print("Constraints:")
    print(solver.assertions())
    print("---------------------------------")
  model = solver.model()
  if not simplified:
    print("All variables:")
    print(model)
  print("---------------------------------")
  print("Start state:")
  for x in begin_vars:
    print_z3_var(begin_vars[x], model)
  print("---------------------------------")
  print("End state:")
  for x in all_vars:
    print_z3_var(all_vars[x], model)
  print("---------------------------------")
  return
  print("Values of arguments at the end of the function:")
  for a in args:
    # If a is an object, loop over attributes and print them all
    # todo
    if isinstance(a, Account):
      for k in a.__dict__:
        try:
          print("Value of", k, ":", solver.model()[a.__dict__[k]])
        except:
          print("Can't print attribute of", k)
    else:
      try:
        print("Value of", a, ":", solver.model()[a])
      except:
        print("Can't print value of", a)
  print("---------------------------------")

# ====================
# Functions decorators
# ====================

list_assume = {}

def assume(lam):
  def decorator(func):
    add_assume(func, lam)
    return func
  return decorator

def add_assume(func, lam):
  if not func in list_assume:
    list_assume[func] = set()
  list_assume[func].add(lam)

list_enforce = {}

def enforce(lam):
  def decorator(func):
    add_enforce(func, lam)
    return func
  return decorator

def add_enforce(func, lam):
  if not func in list_enforce:
    list_enforce[func] = []
  list_enforce[func].append(lam)

# Both assume and enforce
def invariant(lam):
  def decorator(func):
    add_assume(func, lam)
    add_enforce(func, lam)
    return func
  return decorator

list_test = []

def test(lam):
  list_test.append(lam)
  def decorator(func):
    return func
  return decorator


# ================
# Class decorators
# ================


# =================
# Regular functions
# =================

# todo
def create_symbolic_object(obj, name):
  return object_to_z3(obj, name)

def get_lambda_source(lam):
  if type(lam) == str:
    return lam
  s = inspect.getsource(lam)
  s = s[s.find("lam"):]
  s = s[:s.find("\n")-1]
  return s

def add_lam_to_solver(lam, args, only_after=False):
  s = get_lambda_source(lam)
  #try:
  expr = lambda_to_z3(ast.parse(s), args, only_after)
  #except:
    # Todo the parsing can fail with this error not raised!!!!!
  #  print("Error in parsing", s)
  #  print("For now keep your lambda in a single line ahah")
  #  raise Exception("Error in parsing, no \\n allowed in lambda")
  return expr

def create_symbolic_arguments(f):
  global_counter.reset()
  param_list = inspect.signature(f).parameters
  args = []
  # Todo double check the non-taken branch because it was generated by copilot
  for param in param_list:
    elem = param_list[param]
    if elem.default == inspect.Parameter.empty:
      # If the argument is not optional, we create a new symbolic variable
      args.append(create_symbolic_object(elem.annotation, param))
    else:
      # If the argument is optional, we create a new symbolic variable
      # and we add a constraint that it is equal to the default value
      args.append(create_symbolic_object(elem.annotation, param))
      solver.add(args[-1] == elem.default)
  return args

def transform_f_to_z3(f):
  return create_z3_expr(ast.parse(inspect.getsource(f)))

def verify_invariant(lam, invariants):
  print("Verifying invariant:", inspect.getsource(lam), end="")
  invariant_is_correct = True
  for f in all_instructions:
    #if not "calculator" in f.__name__:
    #   continue
    reset_solver()
    # First, transform the argument of the function into z3 variables
    args = create_symbolic_arguments(f)
    add_args_to_solver(f, args)
    # Assert the invariant we want to prove
    solver.add(add_lam_to_solver(lam, args))
    # Assume the already proven invariants
    for inv in invariants:
      solver.add(add_lam_to_solver(inv, args))
    # Assume the properties written in "assume"
    if f in list_assume:
      for inv in list_assume[f]:
        solver.add(add_lam_to_solver(inv, args))
    # Now we execute the function
    transform_f_to_z3(f)
    # Fetch last value of variables
    end_args = []
    for x in all_vars:
      end_args.append(all_vars[x])
    after = z3.BoolVal(False)
    every_after = []
    # Now we check it's SAT, because maybe the user wrote assumptions that makes the whole thing always UNSAT
    # aka it's never possible to execute the function with the given assumptions
    res = solver.check()
    if res == z3.unsat:
      print("Assumptions of " + f.__name__ + " are too strong: it's never possible to execute successfully the function with the given assumptions")
      print(solver)
      assert False, "Assumptions are too strong, check model above"
    # Assume the properties written in "enforce"
    if f in list_enforce:
      for inv in list_enforce[f]:
        after = z3.Or(after, z3.Not(add_lam_to_solver(inv, end_args, True)))
        every_after.append(inv)
    # Assert the opposite of the invariant we want to prove
    after = z3.Or(after, z3.Not(add_lam_to_solver(lam, end_args, True)))
    every_after.append(lam)
    solver.add(after)
    # Solve, and print
    res = solver.check()
    print(solver)
    print(solver.assertions())
    if res == z3.sat:
      invariant_is_correct = False
      print_solution(f)
      print("Verification of " + f.__name__ + " failed; Here are your properties:")
      for every in reversed(every_after):
        solver.push()
        solver.add(add_lam_to_solver(every, end_args, True))
        res = solver.check()
        if res == z3.unsat:
          print("❌", get_lambda_source(every))
          solver.pop()
        else:
          print("✅", get_lambda_source(every))
    assert invariant_is_correct, "Invariant is not correct, please check printed message above"

all_invariants = []
def add_invariant(lam):
   all_invariants.append(lam)

def verify_contract():
  print("Verification on these functions of the contract:", [f.__name__ for f in all_instructions])
  all_invariants.insert(0, lambda _: True)
  for i in range(len(all_invariants)):
    verify_invariant(all_invariants[i], all_invariants[:i])
  print("Done verifying the contract")

global every_assert_statement
every_assert_statement = []

def single_verify_test(f):
  #print("Verifying test:", inspect.getsource(f), end="")
  reset_solver()
  # First, transform the argument of the function into z3 variables
  args = create_symbolic_arguments(f)
  add_args_to_solver(f, args)
  # Now we execute the function
  import seaverify.decorators
  seaverify.decorators.every_assert_statement = []
  transform_f_to_z3(f)
  solver.add(z3.Or([z3.Not(x) for x in seaverify.decorators.every_assert_statement]))
  res = solver.check()
  if res == z3.sat:
    print("❌❌❌❌❌❌")
    print(f.__name__, "is not correct")
    print_solution(f, True)
    print("❌❌❌❌❌❌")
    return False
  return True

def verify_tests():
  print("Verification of tests")
  results = []
  for test in list_test:
    results.append(single_verify_test(test))
  print("--------------------")
  print("Results of tests:")
  for i in range(len(results)):
    test = list_test[i]
    answer = results[i]
    s = "✅" if answer else "❌"
    print(s, test.__name__)