from collections import deque
from typing import Callable, List, Tuple


class CSP(object):
    
    def __init__(self, *args, **kwargs) -> None:
        self.variables = {}
        self.constraints = []
        self.unassigned_var = []
        self.var_constraints = {}
        self.assignments = {}
        self.assignments_number = 0

    def add_constraint(self, constraint_func: Callable, variables: List) -> None:
        """
        Adds a constraint to the CSP.
        """
        self.constraints.append((constraint_func, variables))
        for variable in variables:
            if variable not in self.var_constraints:
                self.var_constraints[variable] = []
            self.var_constraints[variable].append(constraint_func)

    def add_variable(self, variable: any, domain: List) -> None:
        """
        Adds a variable to the CSP with its domain.
        """
        self.variables[variable] = domain[:]
        self.unassigned_var.append(variable)
        self.assignments[variable] = None

    def assign(self, variable: any, value: any) -> None:
        """
        Assigns a value to a variable in the CSP.
        """
        self.assignments[variable] = value
        self.unassigned_var.remove(variable)
        self.assignments_number += 1

    def un_assign(self, removed_values_from_domain: List[Tuple[any, any]], variable: any) -> None:
        """
        Un-assign a variable and restores its domain values.
        """
        self.assignments[variable] = None
        self.unassigned_var.append(variable)
        for var, value in removed_values_from_domain:
            self.variables[var].append(value)

    def is_consistent(self, variable: any, value: any) -> bool:
        """
        Checks if assigning a value to a variable violates any constraints.
        """
        temp_assignment = self.assignments.copy()
        temp_assignment[variable] = value
        for constraint_func, vars_in_constraint in self.constraints:
            if variable in vars_in_constraint:
                values = [temp_assignment[var] for var in vars_in_constraint]
                if None not in values and not constraint_func(*values):
                    return False
        return True

    def is_complete(self) -> bool:
        """
        Checks if the CSP is complete, i.e., all variables have been assigned.
        """
        return len(self.unassigned_var) == 0

    def is_assigned(self, variable: any) -> bool:
        """
        Checks if a variable has been assigned a value.
        """
        return self.assignments[variable] is not None
