#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Needed for automatic conversion of std::vector, etc.
#include "../src/core.h"
#include "../src/solution.h"
#include "../src/branch_bound_solver.h"

namespace py = pybind11;

// PYBIND11_MODULE defines the entry point for the Python extension module
PYBIND11_MODULE(mipsolver, m) {
    m.doc() = "Python bindings for the MIPSolver C++ library";

    // --- Bind Enums ---
    py::enum_<MIPSolver::VariableType>(m, "VariableType")
        .value("CONTINUOUS", MIPSolver::VariableType::CONTINUOUS)
        .value("INTEGER", MIPSolver::VariableType::INTEGER)
        .value("BINARY", MIPSolver::VariableType::BINARY)
        .export_values();

    py::enum_<MIPSolver::ObjectiveType>(m, "ObjectiveType")
        .value("MAXIMIZE", MIPSolver::ObjectiveType::MAXIMIZE)
        .value("MINIMIZE", MIPSolver::ObjectiveType::MINIMIZE)
        .export_values();
    
    py::enum_<MIPSolver::ConstraintType>(m, "ConstraintType")
        .value("LESS_EQUAL", MIPSolver::ConstraintType::LESS_EQUAL)
        .value("GREATER_EQUAL", MIPSolver::ConstraintType::GREATER_EQUAL)
        .value("EQUAL", MIPSolver::ConstraintType::EQUAL)
        .export_values();

    py::enum_<MIPSolver::Solution::Status>(m, "SolutionStatus")
        .value("OPTIMAL", MIPSolver::Solution::Status::OPTIMAL)
        .value("INFEASIBLE", MIPSolver::Solution::Status::INFEASIBLE)
        // ... add other statuses
        .export_values();


    // --- Bind Classes ---
    
    // Bind the Solution class first as it's used by the Solver
    py::class_<MIPSolver::Solution>(m, "Solution")
        .def("get_status", &MIPSolver::Solution::getStatus)
        .def("get_objective_value", &MIPSolver::Solution::getObjectiveValue)
        .def("get_values", &MIPSolver::Solution::getValues, "Returns the solution values as a list of floats.")
        .def("__repr__", [](const MIPSolver::Solution &s) {
            return "<mipsolver.Solution objective=" + std::to_string(s.getObjectiveValue()) + ">";
        });


    // Bind the Problem class
    py::class_<MIPSolver::Problem>(m, "Problem")
        .def(py::init<const std::string&, MIPSolver::ObjectiveType>(), py::arg("name"), py::arg("objective_type"))
        .def("add_variable", &MIPSolver::Problem::addVariable, py::arg("name"), py::arg("type") = MIPSolver::VariableType::CONTINUOUS)
        .def("set_objective_coefficient", &MIPSolver::Problem::setObjectiveCoefficient, py::arg("var_index"), py::arg("coeff"))
        .def("add_constraint", &MIPSolver::Problem::addConstraint, py::arg("name"), py::arg("type"), py::arg("rhs"))
        .def("add_constraint_coefficient", [](MIPSolver::Problem &p, int c_idx, int v_idx, double coeff) {
            p.getConstraint(c_idx).addVariable(v_idx, coeff);
        }, py::arg("constraint_index"), py::arg("var_index"), py::arg("coeff"))
        .def("set_variable_bounds", [](MIPSolver::Problem &p, int v_idx, double lower, double upper) {
            p.getVariable(v_idx).setBounds(lower, upper);
        }, py::arg("var_index"), py::arg("lower"), py::arg("upper"));

    // Bind the Solver class
    py::class_<MIPSolver::BranchBoundSolver>(m, "Solver")
        .def(py::init<>())
        .def("set_verbose", &MIPSolver::BranchBoundSolver::setVerbose, py::arg("verbose"))
        .def("solve", &MIPSolver::BranchBoundSolver::solve, py::arg("problem"), "Solves the given optimization problem.");
}
