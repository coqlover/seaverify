# Everything related to print/pretty-printing anything related to the solver

import z3
from seaverify.global_vars import solver, all_vars, begin_vars

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
