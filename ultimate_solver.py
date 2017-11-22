import argparse
import random


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
    random.shuffle(wizards)

    return wizards


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


def write_output(input_filename, solution):
    split = input_filename.split('/')[-1].split('_')

    if len(split) == 3:
        output_filename = "output_{}_{}.out".format(split[1], split[2])
    elif len(split) == 2:
        output_filename = "output_{}.out".format(split[1])
    else:
        raise Exception("Input filename format is trash")

    with open(output_filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Constraint Solver.")
    parser.add_argument("input_file", type=str, help="___.in")
    parser.add_argument("debug", type=str, help="debug")
    args = parser.parse_args()

    if args.debug == "-d":
        DEBUG = True

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.input_file, solution)