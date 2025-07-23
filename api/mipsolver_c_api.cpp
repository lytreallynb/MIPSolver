#include "mipsolver_c_api.h"
#include "../src/core.h"
#include "../src/solution.h"
#include "../src/branch_bound_solver.h"

// Helper macros to safely cast opaque pointers back to C++ pointers
#define GET_PROBLEM(handle) static_cast<MIPSolver::Problem*>(handle)
#define GET_SOLUTION(handle) static_cast<MIPSolver::Solution*>(handle)

extern "C" {

// --- Problem Management ---

MIPSOLVER_API MIPSolver_ProblemHandle MIPSolver_CreateProblem(const char* name, MIPSolver_ObjectiveType obj_type) {
    auto cpp_obj_type = (obj_type == MIPSOLVER_OBJ_MAXIMIZE) ? MIPSolver::ObjectiveType::MAXIMIZE : MIPSolver::ObjectiveType::MINIMIZE;
    // Allocate the C++ object on the heap and return its pointer as a handle
    return new MIPSolver::Problem(name, cpp_obj_type);
}

MIPSOLVER_API void MIPSolver_DestroyProblem(MIPSolver_ProblemHandle handle) {
    if (handle) {
        delete GET_PROBLEM(handle);
    }
}

MIPSOLVER_API int MIPSolver_AddVariable(MIPSolver_ProblemHandle handle, const char* name, MIPSolver_VariableType type) {
    if (!handle) return -1;
    auto cpp_var_type = MIPSolver::VariableType::CONTINUOUS;
    if (type == MIPSOLVER_VAR_INTEGER) cpp_var_type = MIPSolver::VariableType::INTEGER;
    if (type == MIPSOLVER_VAR_BINARY) cpp_var_type = MIPSolver::VariableType::BINARY;
    
    return GET_PROBLEM(handle)->addVariable(name, cpp_var_type);
}

MIPSOLVER_API void MIPSolver_SetVariableBounds(MIPSolver_ProblemHandle handle, int var_index, double lower, double upper) {
    if (!handle) return;
    GET_PROBLEM(handle)->getVariable(var_index).setBounds(lower, upper);
}

MIPSOLVER_API void MIPSolver_SetObjectiveCoefficient(MIPSolver_ProblemHandle handle, int var_index, double coeff) {
    if (!handle) return;
    GET_PROBLEM(handle)->setObjectiveCoefficient(var_index, coeff);
}

MIPSOLVER_API int MIPSolver_AddConstraint(MIPSolver_ProblemHandle handle, const char* name, int type, double rhs) {
    if (!handle) return -1;
    // Note: C++ enum mapping would be needed here for constraint type
    return GET_PROBLEM(handle)->addConstraint(name, static_cast<MIPSolver::ConstraintType>(type), rhs);
}

MIPSOLVER_API void MIPSolver_AddConstraintCoefficient(MIPSolver_ProblemHandle handle, int constraint_index, int var_index, double coeff) {
    if (!handle) return;
    GET_PROBLEM(handle)->getConstraint(constraint_index).addVariable(var_index, coeff);
}


// --- Solving ---

MIPSOLVER_API MIPSolver_SolutionHandle MIPSolver_Solve(MIPSolver_ProblemHandle problem_handle) {
    if (!problem_handle) return nullptr;

    MIPSolver::BranchBoundSolver solver;
    solver.setVerbose(false); // Keep it quiet for library use
    MIPSolver::Problem* problem = GET_PROBLEM(problem_handle);

    // The solve method returns a Solution object by value.
    // We must allocate a new one on the heap to return its handle.
    MIPSolver::Solution* solution = new MIPSolver::Solution(solver.solve(*problem));
    return solution;
}


// --- Solution Management ---

MIPSOLVER_API void MIPSolver_DestroySolution(MIPSolver_SolutionHandle handle) {
    if (handle) {
        delete GET_SOLUTION(handle);
    }
}

MIPSOLVER_API MIPSolver_SolutionStatus MIPSolver_GetStatus(MIPSolver_SolutionHandle handle) {
    if (!handle) return MIPSOLVER_STATUS_INFEASIBLE;
    // Note: C++ enum mapping would be needed here
    return static_cast<MIPSolver_SolutionStatus>(GET_SOLUTION(handle)->getStatus());
}

MIPSOLVER_API double MIPSolver_GetObjectiveValue(MIPSolver_SolutionHandle handle) {
    if (!handle) return 0.0;
    return GET_SOLUTION(handle)->getObjectiveValue();
}

MIPSOLVER_API int MIPSolver_GetSolutionNumVars(MIPSolver_SolutionHandle handle) {
    if (!handle) return 0;
    return GET_SOLUTION(handle)->getValues().size();
}

MIPSOLVER_API void MIPSolver_GetVariableValues(MIPSolver_SolutionHandle handle, double* values_array) {
    if (!handle || !values_array) return;
    const auto& values = GET_SOLUTION(handle)->getValues();
    for (size_t i = 0; i < values.size(); ++i) {
        values_array[i] = values[i];
    }
}

} // extern "C"
