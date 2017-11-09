import argparse
import random

def write_output(filename, num_wizards, num_constraints):
    order = generate_wizard_names(num_wizards)

    with open(filename, "w") as f:
        solution = generate_wizard_names(num_wizards)
        
        f.write(str(num_wizards) + "\n")
        for wizard in solution:
            f.write("{0} ".format(wizard))
        f.write("\n" + str(num_constraints) + "\n")

        constraints = generate_constraints(solution, num_constraints, num_wizards)
        for constraint in constraints:
            # randomize order when writing out
            for wizard in constraint:
                f.write("{0} ".format(wizard))
            f.write("\n")

def generate_constraints(wizards, num_constraints, num_wizards):
    constraints = set()
    max_constraints = calc_max_constraints(num_wizards)
    print(max_constraints)
    count = 0

    for i in range(num_constraints):

        while True:
            if len(constraints) == max_constraints:
                return constraints

            constraint = generate_constraint(wizards, num_constraints, num_wizards)

            if constraint not in constraints:
                print(constraint)
                constraints.add(constraint)
                count += 1
                break

    return constraints

def calc_max_constraints(num_wizards):
    n = num_wizards 
    return (2 * (n - 2) + 3 * pow(n - 2, 2) + pow(n - 2, 3)) / 3

def generate_constraint(wizards, num_constraints, num_wizards):
    endpoints = random.sample(range(num_wizards), 2)
    upper = max(endpoints)
    lower = min(endpoints)

    outside_interval = list(range(0, lower)) + list(range(upper + 1, num_wizards))
    
    if outside_interval == []:
        return generate_constraint(wizards, num_constraints, num_wizards)
    
    non_middle = random.sample(outside_interval, 1)[0]
    return (wizards[lower], wizards[upper], wizards[non_middle])

def generate_wizard_names(num_wizards):
    names = ['Emily', 'Andrew', 'Noah', 'Isaiah', 'Eliana', 'Benjamin', 'Adalyn', 'Matthew', 'Adeline', 'Caden', 'Sophia', 'Levi', 'Zoe', 'Landon', 'Mackenzie', 'Jayden', 'Arianna', 'Nicholas', 'Leah', 'Ella', 'Avery', 'Kaylee', 'Caleb', 'Christian', 'Jacob', 'Nora', 'Muhammad', 'Connor', 'Victoria', 'Sebastian', 'Aria', 'Charlotte', 'Emma', 'Ava', 'Lillian', 'Grayson', 'Julian', 'Layla', 'Brayden', 'Ellie', 'Hannah', 'Mila', 'Abigail', 'Madison', 'Camilla', 'Hailey', 'Brooklyn', 'Logan', 'Liam', 'Peyton', 'Anna', 'Elena', 'Alexander', 'Mia', 'Ryan', 'Elijah', 'Chloe', 'Aiden', 'Amelia', 'Dylan', 'Isaac', 'David', 'Henry', 'Jack', 'Cameron', 'Maria', 'Lily', 'Harper', 'Luke', 'Jayce', 'Addison', 'Evelyn', 'Wyatt', 'Grace', 'Gabriel', 'Aubrey', 'Scarlett', 'Aaliyah', 'Jackson', 'Owen', 'Eli', 'John', 'Madelyn', 'Riley', 'Daniel', 'Mason', 'Kenneth', 'Lincoln', 'Lucas', 'Oliver', 'Natalie', 'William', 'James', 'Elizabeth', 'Carter', 'Sarah', 'Isabella', 'Olivia', 'Nathan', 'Ethan']
    return random.sample(names, num_wizards)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("num_wizards", type=int, help = "___.in")
    parser.add_argument("num_constraints", type=int, help = "___.out")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args() 
    write_output(args.output_file, args.num_wizards, args.num_constraints)