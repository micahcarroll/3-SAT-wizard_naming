import argparse
import random
import pycosat

"""
======================================================================
  Complete the following function.
======================================================================
"""

# The current problem is that the SAT solver sucks, it returns conflicting requirements -> 
# massive.in
# eli < c < an < eli
# 24 < 18 < 14 < 24
# the problem is that this is 3SAT not 2SAT, so we have to encode that there can't be loops in ordering
# ab + bc => ¬ ca
# possible combinations:
# 12 + 13 + 23
# 12 + 13 + ¬23
# 12 + ¬13 + ¬23 
# ¬12 + 13 + 23
# ¬12 + ¬13 + 23
# ¬12 + ¬13 + ¬23

class Wiz(object):
    # Wizard Manager

    def __init__(self, wizards):
        self.list = wizards
        self.wizard_encoder, self.wizard_decoder = self.create_encoder_decoder(wizards)
        self.encoded_list = self.encode_wizards(wizards)

    def create_encoder_decoder(self, wizards):
        # The encoder starts at 10
        encoder = {}
        decoder = {}
        for i in range(len(self.list)):
            ith_wizard = self.list[i]
            encoding_index = i + 10
            encoder[ith_wizard] = encoding_index
            decoder[encoding_index] = ith_wizard
        
        return encoder, decoder

    def encode_wizards(self, wizard_list):
        return [self.encode_wizard(w) for w in wizard_list]

    def decode_wizards(self, wizard_list):
        return [self.decode_wizard(w) for w in wizard_list]

    def encode_wizard(self, name):
        return self.wizard_encoder[name]

    def decode_wizard(self, number):
        return self.wizard_decoder[number]

class Constraint(object):
    """docstring for Constraint"""
    def __init__(self, constraint, wiz):
        self.wiz = wiz
        self.list = constraint
        self.encoded = wiz.encode_wizards(constraint)

    def convert_to_sat(self):
        """
        for each constraint "m not btw a and b" return a constraint 
        of the form (a < m or b > m) and (b < m or a > m)

        input constraints will be of the form ["a", "b", "m"]
        note that this is equivalent to [1, 2, 3]
        output constraints should be of the form [[13, -23], [23, -13]]
        """
        sat_constraint = []
        a, b, m = self.list
        first, second, middle = self.encoded
     
        # write a < m
        if first < middle:
            str_encoded = str(first) + str(middle)
            sat_constraint.append(int(str_encoded))
        else:
            str_encoded = str(middle) + str(first)
            sat_constraint.append(-int(str_encoded))
        
        # write b > m
        if middle < second:
            str_encoded = str(middle) + str(second)
            sat_constraint.append(int(str_encoded))
        else:
            str_encoded = str(second) + str(middle)
            sat_constraint.append(-int(str_encoded))

        # AND the reverse
        reverse_constraint = [-x for x in sat_constraint]

        return [sat_constraint, reverse_constraint]

class Variables(object):
    def __init__(self, sat_solution, wiz):
        self.list = [var for var in sat_solution if (len(self.clean(var)) == 4 
                     and self.first_half(var) < self.second_half(var)
                     and self.first_half(var) in wiz.wizard_decoder
                     and self.second_half(var) in wiz.wizard_decoder)]
        self.wiz = wiz

    def clean(self, var):
        s = str(var)
        if s[0] == '-':
            return s[1:]
        return s

    def first_half(self, var):
        v = self.clean(var)
        if len(v) != 4:
            print("ERROR")
        return int(str(v)[:2])

    def second_half(self, var):
        v = self.clean(var)
        if len(v) != 4:
            print("ERROR")
        return int(str(v)[2:])

    def both_sides(self, var):
        return self.first_half(var), self.second_half(var)

    def involving_enc(self, x):
        # Returns a list of all variables involving a
        lst = []
        for item in self.list:
            a = self.first_half(item)
            b = self.second_half(item)
            
            if (a == x or b == x) and (a < b):
                lst.append(item)
        return lst

    def between(self, x, y):
        if x < y:
            code = int(str(x) + str(y))
        else:
            code = int(str(y) + str(x))

        if code in self.list:
            return code
        elif -code in self.list:
            return -code
        else:
            return None

    def between_decoded(self, x, y):
        result = self.between(x, y)
        v = str(result)
        s = " smaller "
        if str(v[0]) == '-':
            s = " larger "
        
        first = self.wiz.decode_wizard(self.first_half(result))
        second = self.wiz.decode_wizard(self.second_half(result))
        print(first + " is" + s + "than " + second)
        return [first, s, second]

    def smaller_than_enc(self, a, b):
        # i.e. "before"
        if a < b:
            if int(str(a) + str(b)) in self.list:
                return True
        else:
            if -int(str(b) + str(a)) in self.list:
                return True
        return False

    def larger_than_enc(self, a, b):
        return not self.smaller_than_enc(a, b)

    def smaller_than_name(self, name_1, name_2):
        a = self.wiz.encode_wizard(name_1)
        b = self.wiz.encode_wizard(name_2)
        return self.smaller_than_enc(a, b)

    def larger_than_name(self, name_1, name_2):
        return not self.smaller_than_name(name_1, name_2)

    def is_negative(self, constraint):
        return str(constraint)[0] == '-'

    # def check_solution_on_constraints(self, solution):
    #     encoded_sol = self.wiz.encode_wizards(solution)
        
    #     for constraint in self.list:
    #         first = self.first_half(constraint)
    #         second = self.second_half(constraint)

    #         if not self.is_negative(constraint):
    #             if not encoded_sol.index(first) < encoded_sol.index(second):
    #                 print(self.wiz.decode_wizard(first) + " was found after " +
    #                 self.wiz.decode_wizard(second))
    #         else:
    #             if not encoded_sol.index(first) > encoded_sol.index(second):
    #                 print(self.wiz.decode_wizard(first) + " was found after " +
    #                 self.wiz.decode_wizard(second))


class Search(object):
    # Searches for ordering that satisfies Variables
    def __init__(self, var, wiz):
        self.var = var
        self.wiz = wiz

    def naive_search(self, constraints):
        solution = []

        for wizard in self.wiz.encoded_list:
            target_index = 0

            for i in range(len(solution)):
                ith_solution_wizard = solution[i]

                if self.var.larger_than_enc(wizard, ith_solution_wizard):
                    print(self.wiz.decode_wizard(wizard) + " is larger than " + self.wiz.decode_wizard(ith_solution_wizard) + " at index " + str(i))
                    target_index = i + 1

            print("Inserting " + self.wiz.decode_wizard(wizard) + " at index " + str(target_index))
            
            solution.insert(target_index, wizard)

            print(self.wiz.decode_wizards(solution))

            if check_for_non_valid_constraint(self.wiz.decode_wizards(solution), constraints) is not None:
                pass
        
        return solution

def solve(num_wizards, num_constraints, wizards, constraints):
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
    #random.shuffle(wizards)
    wiz = Wiz(wizards)
    sat_constraints = convert(wiz, constraints)

    sat_solution = pycosat.solve(sat_constraints)
    var = Variables(sat_solution, wiz)
    search = Search(var, wiz)
    result = wiz.decode_wizards(search.naive_search(constraints))
    print(result)

    if check_for_non_valid_constraint(result, constraints) is None:
        print("CHECK PASSED!")

    return result


def convert(wiz, constraints):
    new_constraints = []

    for constraint in constraints:
        if constraint == []:
            return

        constraint = Constraint(constraint, wiz)
        double_constraint = constraint.convert_to_sat()
        c = double_constraint[0]
        r = double_constraint[1]
        if c not in new_constraints:
            new_constraints.append(c) #make into a set
        if r not in new_constraints:
            new_constraints.append(r)

    return new_constraints


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
            print("{} was found between {} and {}".format(constraint[2], constraint[0], constraint[1]))
            errors.append((wiz_a, wiz_b, wiz_mid))
            count += 1
    
    if errors:
        print(str(count) + " ERRORS found!")
        return errors
    else:
        return None


"""
======================================================================
   No need to change any code below this line
======================================================================
"""

def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        SOL = f.readline().split()
        num_constraints = int(f.readline())
        constraints = []
        wizards = set()
        for _ in range(num_constraints):
            c = f.readline().split()
            constraints.append(c)
            for w in c:
                wizards.add(w)
                
    wizards = list(wizards)
    return num_wizards, num_constraints, wizards, constraints, SOL

def write_output(filename, solution):
    with open(filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("input_file", type=str, help = "___.in")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args()

    num_wizards, num_constraints, wizards, constraints, SOL = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)
