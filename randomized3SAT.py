import solver
import random

def schoningRandomized3SAT(constraints):
    """
    randomized algorithm for 3SAT
    Input:
        constraints: A 2D-array of constraints, each element is disjunction. i.e. [1, -2, 3] means 1 OR not 2 OR 3.

        example: [[1015, -1415, 1014], [1912, 1917]]
    """

    # pick a random assignment uniformly
    variables = set()
    for disjunction in constraints:
        for variable in disjunction:
            variables.add(abs(variable))
    randomBinarySequence = [random.randint(0, 1) for i in range(0, len(variables))]

    variablesList = list(variables)
    randomAssignment = set()
    for i in range(0, len(variables)):
        if randomBinarySequence[i]: 
            randomAssignment.add(variablesList[i])
    
    for i in range(0, 3 * len(variables)):
        satisfiable, clause = checkSatisfiability(randomAssignment, constraints)
        if satisfiable:
            difference = variables.difference(randomAssignment)
            falseVariables = set()
            for diff in difference:
                falseVariables.add(-1 * diff)
            return randomAssignment.union(falseVariables)
        else:
            flipVariable = clause[random.randint(0, len(clause) - 1)]
            if abs(flipVariable) in randomAssignment:
                randomAssignment.remove(abs(flipVariable))
            else:
                randomAssignment.add(abs(flipVariable))
    
    difference = variables.difference(randomAssignment)
    falseVariables = set()       
    for diff in difference:
        falseVariables.add(-1 * diff)
    return randomAssignment.union(falseVariables)

    
def checkSatisfiability(assignment, constraints):
    for clause in constraints:
        truthValue = False
        for var in clause:
            if abs(var) in assignment:
                if var >= 0:
                    truthValue = True
            else:
                if var < 0:
                    truthValue = True
        if not truthValue:
            return False, clause
    return True, constraints[-1]

def generateRandomConstraints(size):
    constraint = []
    for i in range(0, size):
        clause = []
        for i in range(0, random.randint(2, 3)):
            clause.append(random.randint(-1 * size, size))
        constraint.append(clause)
    return constraint

# for i in range(0, 10):
#     for i in {10, 20, 30, 40, 50}:
#         c1 = generateRandomConstraints(i)
#         print(checkSatisfiability(schoningRandomized3SAT(c1), c1))
