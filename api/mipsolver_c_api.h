#ifndef MIPSOLVER_C_API_H
#define MIPSOLVER_C_API_H

#include <stdbool.h>

// Define platform-specific macros for exporting/importing symbols
// This is crucial for creating DLLs on Windows
#if defined(_WIN32)
    #ifdef MIPSOLVER_EXPORTS
        #define MIPSOLVER_API __declspec(dllexport)
    #else
        #define MIPSOLVER_API __declspec(dllimport)
    #endif
#else
    #define MIPSOLVER_API
#endif


#ifdef __cplusplus
extern "C" {
#endif

// Opaque pointers to hide C++ implementation details
typedef void* MIPSolver_ProblemHandle;
typedef void* MIPSolver_SolutionHandle;

// C-style enums that mirror the C++ enums
typedef enum {
    MIPSOLVER_VAR_CONTINUOUS = 0,
    MIPSOLVER_VAR_INTEGER = 1,
    MIPSOLVER_VAR_BINARY = 2
} MIPSolver_VariableType;

typedef enum {
    MIPSOLVER_OBJ_MAXIMIZE = 0,
    MIPSOLVER_OBJ_MINIMIZE = 1
} MIPSolver_ObjectiveType;

typedef enum {
    MIPSOLVER_STATUS_OPTIMAL = 2,
    MIPSOLVER_STATUS_INFEASIBLE = 1,
    // Add other statuses as needed
} MIPSolver_SolutionStatus;


// --- Problem Management Functions ---

/** @brief Creates a new optimization problem. */
MIPSOLVER_API MIPSolver_ProblemHandle MIPSolver_CreateProblem(const char* name, MIPSolver_ObjectiveType obj_type);

/** @brief Destroys a problem object and frees memory. */
MIPSOLVER_API void MIPSolver_DestroyProblem(MIPSolver_ProblemHandle handle);

/** @brief Adds a variable to the problem. Returns the variable's index. */
MIPSOLVER_API int MIPSolver_AddVariable(MIPSolver_ProblemHandle handle, const char* name, MIPSolver_VariableType type);

/** @brief Sets the bounds for a specific variable. */
MIPSOLVER_API void MIPSolver_SetVariableBounds(MIPSolver_ProblemHandle handle, int var_index, double lower, double upper);

/** @brief Sets the objective function coefficient for a variable. */
MIPSOLVER_API void MIPSolver_SetObjectiveCoefficient(MIPSolver_ProblemHandle handle, int var_index, double coeff);

/** @brief Adds a constraint to the problem. Returns the constraint's index. */
MIPSOLVER_API int MIPSolver_AddConstraint(MIPSolver_ProblemHandle handle, const char* name, int type, double rhs);

/** @brief Adds a variable with a coefficient to a specific constraint. */
MIPSOLVER_API void MIPSolver_AddConstraintCoefficient(MIPSolver_ProblemHandle handle, int constraint_index, int var_index, double coeff);


// --- Solving Functions ---

/** @brief Solves the problem using the Branch & Bound solver. */
MIPSOLVER_API MIPSolver_SolutionHandle MIPSolver_Solve(MIPSolver_ProblemHandle problem_handle);


// --- Solution Management Functions ---

/** @brief Destroys a solution object and frees memory. */
MIPSOLVER_API void MIPSolver_DestroySolution(MIPSolver_SolutionHandle handle);

/** @brief Gets the status of the solution (e.g., optimal, infeasible). */
MIPSOLVER_API MIPSolver_SolutionStatus MIPSolver_GetStatus(MIPSolver_SolutionHandle handle);

/** @brief Gets the objective value of the solution. */
MIPSOLVER_API double MIPSolver_GetObjectiveValue(MIPSolver_SolutionHandle handle);

/** @brief Gets the number of variables in the solution. */
MIPSOLVER_API int MIPSolver_GetSolutionNumVars(MIPSolver_SolutionHandle handle);

/** @brief Fills a user-provided array with the variable values from the solution. */
MIPSOLVER_API void MIPSolver_GetVariableValues(MIPSolver_SolutionHandle handle, double* values_array);


#ifdef __cplusplus
} // extern "C"
#endif

#endif // MIPSOLVER_C_API_H
