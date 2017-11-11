import argparse
import random
import math
from instance_validator import processInput

BABY_NAMES = ['Emily', 'Andrew', 'Noah', 'Isaiah', 'Eliana', 'Benjamin', 'Adalyn', 'Matthew', 'Adeline', 'Caden', 'Sophia', 'Levi', 'Zoe', 'Landon', 'Mackenzie', 'Jayden', 'Arianna', 'Nicholas', 'Leah', 'Ella', 'Avery', 'Kaylee', 'Caleb', 'Christian', 'Jacob', 'Nora', 'Muhammad', 'Connor', 'Victoria', 'Sebastian', 'Aria', 'Charlotte', 'Emma', 'Ava', 'Lillian', 'Grayson', 'Julian', 'Layla', 'Brayden', 'Ellie', 'Hannah', 'Mila', 'Abigail', 'Madison', 'Camilla', 'Hailey', 'Brooklyn', 'Logan', 'Liam', 'Peyton', 'Anna', 'Elena', 'Alexander', 'Mia', 'Ryan', 'Elijah', 'Chloe', 'Aiden', 'Amelia', 'Dylan', 'Isaac', 'David', 'Henry', 'Jack', 'Cameron', 'Maria', 'Lily', 'Harper', 'Luke', 'Jayce', 'Addison', 'Evelyn', 'Wyatt', 'Grace', 'Gabriel', 'Aubrey', 'Scarlett', 'Aaliyah', 'Jackson', 'Owen', 'Eli', 'John', 'Madelyn', 'Riley', 'Daniel', 'Mason', 'Kenneth', 'Lincoln', 'Lucas', 'Oliver', 'Natalie', 'William', 'James', 'Elizabeth', 'Carter', 'Sarah', 'Isabella', 'Olivia', 'Nathan', 'Ethan', 'Orkun', 'Micah']

def generate_wizard_names(num_wizards):
    return random.sample(BABY_NAMES, num_wizards)

def get_max_constraints(num_wizards):
    return (2 * (num_wizards - 2) + 3 * pow(num_wizards - 2, 2) + pow(num_wizards - 2, 3)) / 3

def generate_constraint(wizards, num_constraints):
    endpoints = random.sample(range(len(wizards)), 2)
    upper = max(endpoints)
    lower = min(endpoints)
    outside_interval = list(range(0, lower)) + list(range(upper + 1, len(wizards)))
    if outside_interval == []:
        return generate_constraint(wizards, num_constraints)
    non_middle = random.sample(outside_interval, 1)[0]
    return (wizards[lower], wizards[upper], wizards[non_middle])

def generate_constraints(wizards, num_constraints):
    constraints = []
    max_constraints = min(num_constraints, get_max_constraints(len(wizards)))
    while True:
        if len(constraints) == max_constraints:
            return constraints
        constraint = generate_constraint(wizards, num_constraints)
        if constraint not in constraints:
            constraints.append(constraint)

def generate_interleaved_constraints(wizards, num_constraints):
    # abc, cde, edf, fgh 
    constraints = []
    for i in range(0, 2 * num_constraints, 2):
        constraint = [wizards[(i - 1) % len(wizards)], wizards[i % len(wizards)], wizards[(i + 1) % len(wizards)]]
        constraints.append(constraint)
    return constraints

def generate_chain_constraints(wizards, num_constraints):
    # wizards: list of wizard names
    # num_constraints: ignored value
    # RETURNS: constraints of the form abc, def, ghi, adg
    constraints = []
    triplet_count = int(math.ceil(len(wizards) / 3.0))
    chain_count = int(math.ceil((triplet_count - 1) / 2.0))
    print("Creating {} triplets and {} chain constraints.".format(triplet_count, chain_count))
    triplet_start = 0
    while triplet_start + 2 < len(wizards):
        constraints.append([wizards[triplet_start], wizards[(triplet_start+1)%len(wizards)], wizards[(triplet_start+2)%len(wizards)]])
        triplet_start += 3
    missing_wizards = len(wizards) - triplet_start - 1
    if missing_wizards == 1:
        constraints.append([wizards[0], wizards[1], wizards[-1]])
    elif missing_wizards == 2:
        constraints.append([wizards[0], wizards[-2], wizards[-1]])
    chain_start = 0
    while chain_start + 6 < len(wizards):
        constraints.append([wizards[chain_start], wizards[(chain_start+3)%len(wizards)], wizards[(chain_start+6)%len(wizards)]])
        chain_start += 9
    print("Created a total of {} constraints.".format(len(constraints)))
    other_constraints = generate_constraints(wizards, num_constraints - len(constraints))
    print("Created random {} constraints to add on top.".format(len(other_constraints)))
    return constraints + other_constraints

def write_output(filename, num_wizards, num_constraints):
    wizards = generate_wizard_names(num_wizards)
    # constraints = generate_constraints(wizards, num_constraints)
    # constraints = generate_interleaved_constraints(wizards, num_constraints)
    constraints = generate_chain_constraints(wizards, num_constraints)
    random.shuffle(constraints)
    with open(filename, "w") as f:
        f.write(str(len(wizards)) + "\n")
        for wizard in wizards:
            f.write("{0} ".format(wizard))
        f.write("\n" + str(len(constraints)) + "\n")
        for constraint in constraints:
            for wizard in constraint:
                f.write("{0} ".format(wizard))
            f.write("\n")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("num_wizards", type=int, help = "___.in")
    parser.add_argument("num_constraints", type=int, help = "___.out")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args()
    write_output(args.output_file, args.num_wizards, args.num_constraints)
    print("Checking if generated file is valid: " + processInput(args.output_file, args.num_wizards))