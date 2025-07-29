#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Needed for automatic conversion of std::vector, etc.
#include "../src/core.h"
#include "../src/solution.h"
#include "../src/branch_bound_solver.h"

/*
 * Python绑定模块
 * 
 * 这个文件使用pybind11库将C++实现的MIPSolver核心功能暴露给Python：
 * 
 * 1. 主要目的：
 *    - 提供高性能的C++求解器给Python用户
 *    - 保持API的一致性和易用性
 *    - 自动处理Python和C++之间的类型转换
 * 
 * 2. 绑定策略：
 *    - 直接暴露核心C++类（Problem, Solution, Solver等）
 *    - 使用pybind11的自动类型转换功能
 *    - 保持C++和Python接口的语义一致性
 * 
 * 3. 性能优化：
 *    - 最小化Python/C++边界的数据拷贝
 *    - 利用pybind11的智能指针管理
 *    - 支持numpy数组的零拷贝访问
 * 
 * 4. 错误处理：
 *    - C++异常自动转换为Python异常
 *    - 保持错误信息的完整性和可读性
 */

namespace py = pybind11;

// PYBIND11_MODULE定义Python扩展模块的入口点
/*
 * 模块定义宏
 * 
 * 这个宏创建了名为"_solver"的Python模块，包含所有绑定的C++功能。
 * 模块名前的下划线表示这是一个内部实现模块，不建议用户直接使用。
 * 用户应该通过mipsolver包的高级接口访问这些功能。
 */
PYBIND11_MODULE(_solver, m) {
    m.doc() = "MIPSolver C++ core solver module";

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
