# Import the module we built
import mipsolver

def main():
    """
    Demonstrates how to use the Python API for the MIPSolver.
    """
    print("--- Testing MIPSolver Python API ---")

    # 1. Create a problem
    # We use the high-level Python classes we defined in the bindings
    problem = mipsolver.Problem("MyPythonProblem", mipsolver.ObjectiveType.MAXIMIZE)

    # 2. Add variables
    x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
    x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
    
    # Bounds are often implicitly handled for BINARY, but can be set explicitly
    problem.set_variable_bounds(x0, 0, 1)
    problem.set_variable_bounds(x1, 0, 1)

    # 3. Set objective: Maximize 5*x0 + 8*x1
    problem.set_objective_coefficient(x0, 5.0)
    problem.set_objective_coefficient(x1, 8.0)

    # 4. Add constraint: 2*x0 + 4*x1 <= 10
    # --- CORRECTED LINE: Use the proper enum instead of an integer ---
    c0 = problem.add_constraint("c0", mipsolver.ConstraintType.LESS_EQUAL, 10.0)
    
    problem.add_constraint_coefficient(c0, x0, 2.0)
    problem.add_constraint_coefficient(c0, x1, 4.0)

    # 5. Create a solver and solve the problem
    solver = mipsolver.Solver()
    solution = solver.solve(problem)

    # 6. Process the solution
    if solution:
        print(f"Solution Status: {solution.get_status()}")
        print(f"Objective Value: {solution.get_objective_value()}")
        
        values = solution.get_values()
        for i, val in enumerate(values):
            print(f"Variable x{i} = {val}")
    else:
        print("Solver did not find a solution.")

if __name__ == "__main__":
    main()

