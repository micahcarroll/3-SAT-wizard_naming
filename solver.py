# This Python file uses the following encoding: utf-8
import argparse
import random
import pycosat
import randomized3SAT
from itertools import combinations
import numpy as np

DEBUG = True

"""
======================================================================
  Complete the following function.
======================================================================
"""

def generate_3_term_clauses(wizards):
    # Possible combinations: 12 + 13 + 23  |  12 + 13 + ¬23  |  12 + ¬13 + ¬23 | ¬12 + 13 + 23  |  ¬12 + ¬13 + 23  |  ¬12 + ¬13 + ¬23
    # Invalid combinations: 12 + ¬13 + 23  |  ¬12 + 13 + ¬23
    # This logic could be made nicer
    clauses_with_3_terms = []
    for i in wizards:
        for j in wizards:
            for k in wizards:
                if  i < j < k:
                    variables = [Variable(i, j), Variable(i, k), Variable(j, k)]
                    truth_values = np.array([False, True, False])
                    clauses_with_3_terms += [Clause(variables, truth_values), Clause(variables, ~truth_values)]
    
    return clauses_with_3_terms

def naive_order_wizards(variables, wizards):
    # Searches for ordering of wizards that satisfies the Variables and their states
    solution = []
    for wizard in wizards:
        target_index = 0
        for i in range(len(solution)):
            ith_solution_wizard = solution[i]
            
            if variables.should_be_before(ith_solution_wizard, wizard):
                if DEBUG:
                    print(wizard + " is larger than " + ith_solution_wizard + " at index " + str(i))
                target_index = i + 1

        if DEBUG:
            print("Inserting " + wizard + " at index " + str(target_index))
        solution.insert(target_index, wizard)
        if DEBUG:
            print(solution)
        # if check_for_non_valid_constraint(solution, constraints) is not None:
        #     pass
    return solution

def check_for_non_valid_constraint(ordering, constraints):
    node_map = {k: v for v, k in enumerate(ordering)}
    errors = []
    count = 0

    for constraint in constraints:
        a = constraint[0]
        b = constraint[1]
        m = constraint[2]
        if not (a in node_map and b in node_map and m in node_map):
            continue

        wiz_a = node_map[a]
        wiz_b = node_map[b]
        wiz_mid = node_map[m]

        if (wiz_a < wiz_mid < wiz_b) or (wiz_b < wiz_mid < wiz_a):
            #print("{} was found between {} and {}".format(
            #    constraint[2], constraint[0], constraint[1]))
            errors.append((wiz_a, wiz_b, wiz_mid))
            count += 1

    if errors and DEBUG:
        print(str(count) + " Errors found!")
        return errors
    else:
        return None

def solve(num_wizards, num_constraints, wizards, constraints, sat2=False):
    """
    Write your algorithm here.
    Input:
        num_wizards: Number of wizards
        num_constraints: Number of constraints
        wizards: An array of wizard names, in no particular order
        constraints: A 2D-array of constraints, 
                     where constraints[0] may take the form ['A', 'B', 'C']

    Output:
        An array of wizard names in the ordering your algorithm returns
    """
    random.shuffle(wizards)

    variables = Variables()

    constraint_clauses = [clause for constraint in constraints for clause in Constraint(constraint).get_clauses()]
    clauses_with_3_terms = generate_3_term_clauses(wizards)

    sat3 = SAT3(constraint_clauses + clauses_with_3_terms)

    sat3.solve_with_pycosat(variables)

    result = naive_order_wizards(variables, wizards)

    # var = Variables(sat_solution, wiz)
    # var2 = Variables(sat_solution2, wiz)
    # search = OrderWizards(var, wiz)
    # search2 = OrderWizards(var2, wiz)
    # result = wiz.decode_multiple(search2.naive_search(constraints))
    # if DEBUG:
    #     print(result)
    errors = check_for_non_valid_constraint(result, constraints)
    if errors is None and DEBUG:
        print("CHECK PASSED!")
    if errors:
        print("An error was found")

    return result

class Variables(object):

    def __init__(self):
        wizard_combinations = list((combinations(wizards, 2))) # do we even have to create them all at the beginning?
        self.variables = [Variable(wiz1, wiz2) for wiz1, wiz2 in wizard_combinations]
        self.variables_set = {var.combination: var for var in self.variables} # to be able to access specific variables fast
        self.encoder, self.decoder = self.generate_encoding()

    def generate_encoding(self):
        encoder = {}
        decoder = {}
        for i in range(len(self.variables)):
            # Each encoded combination will be in sorted order
            # Encoding starts at 1 to prevent problems with pycosat
            encoder[self.variables[i]] = i + 1
            decoder[i + 1] = self.variables[i]
        return encoder, decoder

    def should_be_before(self, wizard1, wizard2):
        combination = tuple(sorted([wizard1, wizard2]))
        target_variable = self.variables_set[combination]

        if target_variable.before == wizard1 and target_variable.state:
            return True
        elif target_variable.before == wizard2 and not target_variable.state:
            return True
        else:
            return False
        

class Variable(object):
    def __init__(self, name1, name2, state=0):
        # equvalent to creating a variable 'name 1 is before name 2'
        self.combination = tuple(sorted([name1, name2]))
        self.before = self.combination[0]
        self.after = self.combination[1]
        self.state = state
    
    def __hash__(self):
        return hash(self.combination)

    def __eq__(self, other):
        if type(other) == type(self):
            return (self.combination) == (other.combination)
        elif type(other) == bool:
            return bool(self) == other
        else:
            return super() == other

    def __ne__(self, other):
        return not(self == other)

    def __nonzero__(self):#missleading
        return self.state

    def __repr__(self):
        return "{} is before {}".format(self.before, self.after)

    def switch(self):
        self.state = 1 - self.state

    def encode(self, encoder):
        return encoder[self]

class Constraint(object):
    def __init__(self, constraint):
        self.middle_wizard = constraint[-1]
        self.side_wizards = constraint[:2]

    def get_clauses(self):
        """
        For each constraint "m not btw a and b" return a constraint
        of the form (a < m or b > m) and (b < m or a > m).
        """
        a = self.side_wizards[0]
        b = self.side_wizards[1]
        m = self.middle_wizard

        # Simplify by noting that each 2 clauses created this way are opposite
        left_sides = np.array([a, m, b, m])
        right_sides = np.array([m, b, m, a])
        truth_values = left_sides < right_sides

        variables = [Variable(wiz1, wiz2) for wiz1, wiz2 in zip(left_sides, right_sides)]

        return Clause(variables[:2], truth_values[:2]), Clause(variables[2:], truth_values[2:])

class Clause(object):
    def __init__(self, variables, truth_values):
        self.variables = variables
        self.truth_values = truth_values

    def __repr__(self):
        return " OR ".join(
            [str(tupl) for tupl in zip(self.truth_values, [repr(var) for var in self.variables])]
        )

    def satisfied(self):
        return any(np.array(self.variables) == np.array(self.truth_values))

class SAT3(object):
    def __init__(self, clauses):
        self.clauses = clauses
    
    def solve_with_pycosat(self, variables):
        pycosat_clauses = self.convert_to_pycosat(variables.encoder)
        pycosat_solution = pycosat.solve(pycosat_clauses)
        self.set_variables_from_pycosat(pycosat_solution, variables.decoder)

    def convert_to_pycosat(self, encoder):
        pycosat_instance = []
        for clause in self.clauses:
            pycosat_clause = []
            for item in zip(clause.variables, clause.truth_values):
                truth_value = item[1]
                encoded_variable = encoder[item[0]]
                if not truth_value:
                    encoded_variable *= -1
                pycosat_clause.append(encoded_variable)
            pycosat_instance.append(pycosat_clause)
        return pycosat_instance
        
    def set_variables_from_pycosat(self, pycosat_solution, decoder):
        print(pycosat_solution)
        for var in pycosat_solution:
            if var < 0:
                decoder[-var].state=0
            else:
                decoder[var].state=1

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        num_constraints = int(f.readline())
        constraints = []
        wizards = set()
        for _ in range(num_constraints):
            c = f.readline().split()
            constraints.append(c)
            for w in c:
                wizards.add(w)

    wizards = list(wizards)
    return num_wizards, num_constraints, wizards, constraints


def write_output(filename, solution):
    with open(filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Constraint Solver.")
    parser.add_argument("input_file", type=str, help="___.in")
    parser.add_argument("output_file", type=str, help="___.out")
    parser.add_argument("debug", type=str, help="debug")
    args = parser.parse_args()

    if args.debug == "-d":
        DEBUG = True

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)