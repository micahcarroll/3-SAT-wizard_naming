import solver
import code_generator
import time

def run(num_wizards, num_constraints, sat2=False):
    solution = code_generator.generate_wizard_names(num_wizards)
    constraints = code_generator.generate_constraints(solution, num_constraints)

    startTime = time.time()
    r, e = solver.solve(num_wizards, num_constraints, solution, constraints, sat2)
    elapsedTime = time.time() - startTime
    if e is None:
        e_len = 0
    else:
        e_len = len(e)
    return elapsedTime, e_len

def run_chain(num_wizards, num_constraints, sat2=False):
    solution = code_generator.generate_wizard_names(num_wizards)
    constraints = code_generator.generate_chain_constraints(solution, num_constraints)

    startTime = time.time()
    r, e = solver.solve(num_wizards, num_constraints, solution, constraints)
    elapsedTime = time.time() - startTime
    if e is None:
        e_len = 0
    else:
        e_len = len(e)
    return elapsedTime, e_len