import pycosat

class SAT3(object):
    def __init__(self, clauses, variables):
        self.clauses = clauses
        self.variables = variables

class LocalSearch(SAT3):
    def solve(self, depth=1000):
        for i in range(depth):
            self.switch_one()
        
    def switch_one(self):
        for clause in self.clauses: 
            if not clause.satisfied:
                best_change = 0
                best_variable = None
                for var in clause.variables:
                    change = self.try_switch(var)
                    print(change)
                    if change > best_change:
                        best_change = change
                        best_variable = var

                if best_variable:
                    print("Switching {} with {} change".format(best_variable, best_change))
                    best_variable.switch()
                    break

    def try_switch(self, variable):
        current = self.num_satisfied()
        variable.switch()
        with_switch = self.num_satisfied()
        variable.switch()
        return with_switch - current

    def num_satisfied(self):
        return sum([clause.satisfied for clause in self.clauses])

class PycosatSolver(SAT3):

    def solve(self):
        pycosat_clauses = self.convert_to_pycosat(self.variables.encoder)
        pycosat_solution = pycosat.solve(pycosat_clauses)
        self.set_variables_from_pycosat(pycosat_solution, self.variables.decoder)

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
        for var in pycosat_solution:
            if var < 0:
                decoder[-var].state = 0
            else:
                decoder[var].state = 1