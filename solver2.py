# This Python file uses the following encoding: utf-8
import argparse
import random
from itertools import combinations, permutations
import numpy as np
import SAT3

global DEBUG
DEBUG = False

"""
======================================================================
  Complete the following function.
======================================================================
"""

def generate_3_term_clauses(wizards, variables):
    # Possible combinations: 12 + 13 + 23  |  12 + 13 + ¬23  |  12 + ¬13 + ¬23 | ¬12 + 13 + 23  |  ¬12 + ¬13 + 23  |  ¬12 + ¬13 + ¬23
    # Invalid combinations: 12 + ¬13 + 23  |  ¬12 + 13 + ¬23
    clauses_with_3_terms = []
    for i, j, k in permutations(wizards, 3):
        if  i < j < k:
            constraint_3 = [variables.get((i, j)), variables.get((i, k)), variables.get((j, k))]
            truth_values = np.array([False, True, False])
            clauses_with_3_terms += [Clause(constraint_3, truth_values), Clause(constraint_3, ~truth_values)]
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
    return solution

def check_for_non_valid_constraint(ordering, constraints):
    node_map = {k: v for v, k in enumerate(ordering)}
    errors = []
    count = 0

    for constraint in constraints:
        a, b, m = constraint
        if not (a in node_map and b in node_map and m in node_map):
            continue
        
        wiz_a, wiz_b, wiz_mid = node_map[a], node_map[b], node_map[m]
        if (wiz_a < wiz_mid < wiz_b) or (wiz_b < wiz_mid < wiz_a):
            print("{} was found between {} and {}".format(constraint[2], constraint[0], constraint[1]))
            errors.append((wiz_a, wiz_b, wiz_mid))
            count += 1

    if errors:
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
    clauses_with_3_terms = generate_3_term_clauses(wizards, variables)

    all_clauses = constraint_clauses + clauses_with_3_terms
    SAT3.PycosatSolver(all_clauses, variables).solve()
    #SAT3.LocalSearch(all_clauses, variables).solve()
    result = naive_order_wizards(variables, wizards)

    errors = check_for_non_valid_constraint(result, constraints) # We should delete this once we trust the smart version below
    errors_smart = all([clause.satisfied for clause in all_clauses])
    print("Errors were found") if errors else print("Constraints Satisfied!")
    print("Errors were found") if errors_smart else print("Constraints Satisfied!")

    return result

class Variables(object):
    def __init__(self):
        wizard_combinations = list((combinations(wizards, 2)))
        self.variables = [Variable(wiz1, wiz2) for wiz1, wiz2 in wizard_combinations]
        self.dict = {var.combination: var for var in self.variables} # to be able to access specific variables fast
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

    def get(self, combination):
        # Get a specific variable corresponding to a combination of wizards
        return self.dict[combination]

    def should_be_before(self, wizard1, wizard2):
        combination = tuple(sorted([wizard1, wizard2]))
        target_variable = self.get(combination)
        if (target_variable.before == wizard1 and target_variable.state) or (target_variable.before == wizard2 and not target_variable.state):
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
        a , b = self.side_wizards
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

    @property
    def satisfied(self):
        return any(np.array(self.variables) == np.array(self.truth_values))

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
    parser.add_argument("-d", action='store_true', help="debug")
    args = parser.parse_args()

    if args.d: DEBUG = True

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)