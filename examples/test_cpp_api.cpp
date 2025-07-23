#include <iostream>
#include <vector>
#include "mipsolver_c_api.h"

int main() {
    std::cout << "--- Testing MIPSolver C++ API ---" << std::endl;

    // 1. Create a problem
    MIPSolver_ProblemHandle problem = MIPSolver_CreateProblem("MyTestProblem", MIPSOLVER_OBJ_MAXIMIZE);
    if (!problem) {
        std::cerr << "Failed to create problem." << std::endl;
        return 1;
    }

    // 2. Add variables: x0 (binary), x1 (binary)
    int x0 = MIPSolver_AddVariable(problem, "x0", MIPSOLVER_VAR_BINARY);
    MIPSolver_SetVariableBounds(problem, x0, 0, 1);

    int x1 = MIPSolver_AddVariable(problem, "x1", MIPSOLVER_VAR_BINARY);
    MIPSolver_SetVariableBounds(problem, x1, 0, 1);

    // 3. Set objective: Maximize 5*x0 + 8*x1
    MIPSolver_SetObjectiveCoefficient(problem, x0, 5.0);
    MIPSolver_SetObjectiveCoefficient(problem, x1, 8.0);

    // 4. Add constraint: 2*x0 + 4*x1 <= 10
    int c0 = MIPSolver_AddConstraint(problem, "c0", 0 /*LESS_EQUAL*/, 10.0);
    MIPSolver_AddConstraintCoefficient(problem, c0, x0, 2.0);
    MIPSolver_AddConstraintCoefficient(problem, c0, x1, 4.0);

    // 5. Solve the problem
    MIPSolver_SolutionHandle solution = MIPSolver_Solve(problem);

    // 6. Process the solution
    if (solution) {
        std::cout << "Solution Status: " << MIPSolver_GetStatus(solution) << " (2 is Optimal)" << std::endl;
        std::cout << "Objective Value: " << MIPSolver_GetObjectiveValue(solution) << std::endl;

        int num_vars = MIPSolver_GetSolutionNumVars(solution);
        std::vector<double> values(num_vars);
        MIPSolver_GetVariableValues(solution, values.data());

        for (int i = 0; i < num_vars; ++i) {
            std::cout << "Variable " << i << " = " << values[i] << std::endl;
        }

        // 7. Clean up solution
        MIPSolver_DestroySolution(solution);
    } else {
        std::cerr << "Solver failed to return a solution." << std::endl;
    }

    // 8. Clean up problem
    MIPSolver_DestroyProblem(problem);

    return 0;
}
