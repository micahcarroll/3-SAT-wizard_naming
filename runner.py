import solver
import code_generator
import time

def run(num_wizards, num_constraints):
    solution = code_generator.generate_wizard_names(num_wizards)
    constraints = code_generator.generate_constraints(solution, num_constraints, num_wizards)

    startTime = time.time()
    r, e = solver.solve(num_wizards, num_constraints, solution, constraints)
    elapsedTime = time.time() - startTime
    if e is None:
        e_len = 0
    else:
        e_len = len(e)
    return elapsedTime, e_len