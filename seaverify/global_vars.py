# This file is the creation of every global variable
# Sometimes it involes writting some code, but the code isn't used elsewhere

# In a test function, every seaverify_assert function call will append to this variable
every_assert_statement = []

# In a test function, every print function call will append to this variable
every_print_statement = []

# We use a single z3 solver everywhere
import z3
solver = z3.Solver()

# Todo comment
all_vars = {}
begin_vars = {}

# When an @enforce(lambda before, after: ...) is used
# current_before_name and current_after_name are set to the name of the before and after variables
# This is because I don't handle gracefully the names and so on. Todo refactor it
current_before_name = None
current_after_name = None

# Every @instruction function is appended to this list
# It is used when veryfing an invariant for instance, it loops over that list
all_instructions = []

# todo
symbolic_objects = {}

# Used to create fresh variables in the z3 solver
class __GlobalCounter:
    def __init__(self) -> None:
        self.counter = {}
    def create(self, s):
        if not s in self.counter:
            self.counter[s] = -1
        self.counter[s] += 1
        return s + "?" + str(self.counter[s])
    def reset(self):
        self.counter = {}
global_counter = __GlobalCounter()