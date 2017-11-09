import argparse
import random
import pycosat

"""
======================================================================
  Complete the following function.
======================================================================
"""

class Wiz(object):
    # Wizard Manager

    def __init__(self, wizards):
        self.list = wizards
        self.wizard_encoder = {k: n + 1 for n, k in enumerate(wizards)}
        self.wizard_decoder = {n + 1: k for n, k in enumerate(wizards)}

    def encode_wizard(self, name):
        return self.wizard_encoder[name]

    def decode_wizard(self, number):
        return self.wizard_decoder[number]

def solve(num_wizards, num_constraints, wizards, constraints):
    """
    Write your algorithm here.
    Input:
        num_wizards: Number of wizards
        num_constraints: Number of constraints
        wizards: An array of wizard names, in no particular order
        constraints: A 2D-array of constraints, 
                     where constraints[0] may take the form ['A', 'B', 'C']i

    Output:
        An array of wizard names in the ordering your algorithm returns
    """
    wiz = Wiz(wizards)
    sat_constraints = convert(wiz, constraints)

    return pycosat.solve(sat_constraints)



def convert(wiz, constraints):
    
    new_constraints = []

    for constraint in constraints:
        """
        for each constraint "m not btw a and b" return a constraint 
        of the form (a < m or b > m) and (b < m or a > m)

        input constraints will be of the form ["a", "b", "m"]
        note that this is equivalent to [1, 2, 3]
        output constraints should be of the form [[13, -23], [23, -13]]
        """
        if constraint == []:
            break

        encoded_constraint = []
        a = constraint[0]
        b = constraint[1]
        m = constraint[2]
        first = wiz.encode_wizard(a)
        second = wiz.encode_wizard(b)
        middle = wiz.encode_wizard(m)

        printer = ""

        # write a < m
        if first < middle:
            str_encoded = str(first) + str(second)
            encoded_constraint.append(int(str_encoded))
            
        else:
            str_encoded = str(second) + str(first)
            encoded_constraint.append(-int(str_encoded))
        
        # write b > m
        if middle < second:
            str_encoded = str(middle) + str(second)
            encoded_constraint.append(int(str_encoded))
        else:
            str_encoded = str(second) + str(middle)
            encoded_constraint.append(-int(str_encoded))


        #print("( " + a + " < " + b + " or " + b + " > " + m + ") AND (" + b + " < " + m + " or " + a + " > " + m + ")")
        
        reverse_constraint = [-x for x in encoded_constraint]
        
        
        c = encoded_constraint
        r = reverse_constraint

        new_constraints.append(encoded_constraint) #make into a set
        new_constraints.append(reverse_constraint)

    return new_constraints


def check_for_non_valid_constraint(num_wizards, ordering, constraints):
    node_map = {k: v for v, k in enumerate(ordering)}

    for constraint in constraints:
        wiz_a = node_map[constraint[0]]
        wiz_b = node_map[constraint[1]]
        wiz_mid = node_map[constraint[2]]

        if (wiz_a < wiz_mid < wiz_b) or (wiz_b < wiz_mid < wiz_a):
            print("{} was found between {} and {}".format(constraint[2], constraint[0], constraint[1]))
            return (wiz_a, wiz_b, wiz_mid)
            

    return None

class Constraint(object):
    """docstring for Constraint"""
    def __init__(self, constraint):
        self.x1 = constraint[0]
        self.x2 = constraint[1]
        self.c = constraint[2]

    def two_sides(self, switched):
        if not switched:
            return [[self.x1, self.c], 
                    [self.x2, self.c]]
        else:
            return [[self.c, self.x1], 
                    [self.c, self.x2]]

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        f.readline()
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

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("input_file", type=str, help = "___.in")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args()

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)
