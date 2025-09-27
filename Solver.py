from collections import deque
from typing import Callable, List, Tuple, Any
from CSP import CSP


class Solver(object):

    def __init__(self, csp: CSP, domain_heuristics: bool = False, variable_heuristics: bool = False, MAC: bool = False) -> None:
    
        self.domain_heuristic = domain_heuristics
        self.variable_heuristic = variable_heuristics
        self.MAC = MAC
        self.csp = csp
        self.board_size = int(len(self.csp.variables) ** 0.5)

    def backtrack_solver(self) -> None | dict:
        """
        Backtracking algorithm to solve the constraint satisfaction problem (CSP).
        """
        if self.csp.is_complete():
            # Convert string keys like "1,2" to tuples (1, 2)
            return {tuple(map(int, key.split(","))): value for key, value in self.csp.assignments.items()}

        variable = self.select_unassigned_variable()
        domain = self.ordered_domain_value(variable)

        for value in domain:
            if self.csp.is_consistent(variable, value):
                self.csp.assign(variable, value)
                removed_values = self.apply_MAC() if self.MAC else []

                result = self.backtrack_solver()
                if result:
                    return result

                self.csp.un_assign(removed_values, variable)

        return None


    def select_unassigned_variable(self) -> any:
        """
        Selects an unassigned variable using the MRV heuristic or random selection.
        """
        if self.variable_heuristic:
            return self.MRV(self.csp.unassigned_var)
        return self.csp.unassigned_var[0]

    def ordered_domain_value(self, variable: str) -> List[Any]:
        """
        Returns a list of domain values for the given variable in a specific order.
        """
        if self.domain_heuristic:
            return self.LCV(variable)
        return self.csp.variables[variable]

    def apply_MAC(self) -> List[Any]:
        """
        Applies the Maintaining Arc Consistency (MAC) algorithm to the CSP.
        """
        removed_values = []
        queue = deque(self.csp.constraints)

        while queue:
            constraint_func, vars_in_constraint = queue.popleft()
            for x in vars_in_constraint:
                for y in vars_in_constraint:
                    if x != y:
                        removed = self.binary_arc_reduce(x, y, constraint_func)
                        if removed:
                            removed_values.extend(removed)
                            queue.append((constraint_func, vars_in_constraint))

        return removed_values

    def multi_arc_reduce(self, constraint_func: callable, variables: List[Any]) -> List[Tuple[Any, Any]]:
        """
        Reduces the domains of variables based on the specified constraint.
        """
        removed_values = []
        for var in variables:
            for value in self.csp.variables[var]:
                temp_assignment = self.csp.assignments.copy()
                temp_assignment[var] = value
                if not constraint_func(*[temp_assignment[v] for v in variables]):
                    removed_values.append((var, value))
                    self.csp.variables[var].remove(value)

        return removed_values

    def binary_arc_reduce(self, x: Any, y: Any, constraint_func: callable) -> List[Any] | None:
        """
        Reduce the domain of variable x based on the constraints between x and y.
        """
        removed_values = []
        for value_x in self.csp.variables[x]:
            if not any(constraint_func(value_x, value_y) for value_y in self.csp.variables[y]):
                removed_values.append(value_x)

        for value in removed_values:
            self.csp.variables[x].remove(value)

        return removed_values if removed_values else None

    def MRV(self, variables) -> Any:
        """
        Selects the variable with the Minimum Remaining Values (MRV) heuristic.
        """
        return min(variables, key=lambda var: len(self.csp.variables[var]))

    def LCV(self, variable: Any) -> List[Any]:
        """
        Orders the values of a variable based on the Least Constraining Value (LCV) heuristic.
        """
        def count_constraints(value):
            count = 0
            temp_assignment = self.csp.assignments.copy()
            temp_assignment[variable] = value
            for constraint_func, vars_in_constraint in self.csp.constraints:
                if variable in vars_in_constraint:
                    if not constraint_func(*[temp_assignment.get(v, None) for v in vars_in_constraint]):
                        count += 1
            return count

        return sorted(self.csp.variables[variable], key=count_constraints)
