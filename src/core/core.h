#ifndef MIP_SOLVER_CORE_H
#define MIP_SOLVER_CORE_H

#include <vector>
#include <string>
#include <unordered_map>
#include <limits>
#include <iostream>

namespace MIPSolver {

// Forward declarations
class Variable;
class Constraint;
class Problem;

// Enum classes for variable types, constraint types, and objective types
enum class VariableType {
    CONTINUOUS,
    INTEGER,
    BINARY
};

enum class ConstraintType {
    LESS_EQUAL,
    GREATER_EQUAL,
    EQUAL
};

enum class ObjectiveType {
    MAXIMIZE,
    MINIMIZE
};

// Variable class --> represent decision variables in MIP problems
class Variable {
    public:
        Variable (const std::string& name, VariableType type = VariableType::CONTINUOUS)
            : name_(name), type_(type), lower_bound_(-std::numeric_limits<double>::infinity()),
              upper_bound_(std::numeric_limits<double>::infinity()),
              coefficient_(0.0) {}

        // Getters
        const std::string& getName() const { return name_; }
        VariableType getType() const { return type_; }
        double getLowerBound() const { return lower_bound_; }
        double getUpperBound() const { return upper_bound_; }
        double getCoefficient() const { return coefficient_; }

        // Setters
        void setType(VariableType type) { type_ = type; }
        void setBounds(double lower, double upper) {
            lower_bound_ = lower;
            upper_bound_ = upper;
        }
        void setCoefficient(double coeff) { coefficient_ = coeff; }

    private:
        std::string name_;
        VariableType type_;
        double lower_bound_;
        double upper_bound_;
        double coefficient_; // Coefficient in objective function   
};

// Constraint class --> represent linear constraints in MIP problems
class Constraint {
    public:
        Constraint(const std::string& name, ConstraintType type, double rhs)
            : name_(name), type_(type), rhs_(rhs) {}

        // Add a variable to the constraint with its coefficient
        void addVariable(int var_index, double coeff) {
            coefficients_[var_index] = coeff;
        }

        // Getters
        const std::string& getName() const { return name_; }
        ConstraintType getType() const { return type_; }
        double getRHS() const { return rhs_; }
        const std::unordered_map<int, double>& getCoefficients() const { return coefficients_; }
        
        // Check if constraint is satisfied by a given solution
        bool isSatisfied (const std::vector<double>& solution) const {
            double lhs = 0.0;
            for (const auto& [var_index, coeff] : coefficients_) {
                if (var_index < solution.size()) {  // Add bounds check
                    lhs += coeff * solution[var_index];
                }
            }
            // 浮点计算， 比较精度
            switch (type_) {
                case ConstraintType::LESS_EQUAL: return lhs <= rhs_ + 1e-9;
                case ConstraintType::GREATER_EQUAL: return lhs >= rhs_ - 1e-9;
                case ConstraintType::EQUAL: return std::abs(lhs - rhs_) < 1e-9;
                default: return false;
            }
        }
        
        // Setters
        void setName(const std::string& name) { name_ = name; }
        void setType(ConstraintType type) { type_ = type; }
        void setRHS(double rhs) { rhs_ = rhs; }

    private:
        std::string name_;
        ConstraintType type_;
        double rhs_; // Right-hand side value
        std::unordered_map<int, double> coefficients_; // Map of variable index to coefficient
};

// Problem class --> main container for the optimization problem
class Problem {
    public:
        // default minimization problem
        Problem(const std::string& name = "MIP", ObjectiveType objective_type = ObjectiveType::MINIMIZE)
            : name_(name), objective_type_(objective_type) {}
    
        // Add a variable to the problem
        int addVariable(const std::string& name, VariableType type = VariableType::CONTINUOUS) {
            variables_.emplace_back(name, type);
            return variables_.size() - 1;  // Return variable index
        }

        Variable& getVariable(int index) { return variables_[index]; }
        const Variable& getVariable(int index) const { return variables_[index]; }
        int getNumVariables() const { return variables_.size(); }

        // Add a constraint to the problem
        int addConstraint(const std::string& name, ConstraintType type, double rhs) {
            constraints_.emplace_back(name, type, rhs);
            return constraints_.size() - 1;  // Return constraint index
        }

        Constraint& getConstraint(int index) { return constraints_[index]; }
        const Constraint& getConstraint(int index) const { return constraints_[index]; }
        int getNumConstraints() const { return constraints_.size(); }

        // Objective function management
        void setObjectiveType(ObjectiveType type) { objective_type_ = type; }
        ObjectiveType getObjectiveType() const { return objective_type_; }

        void setObjectiveCoefficient(int var_index, double coeff) {
            if (var_index >= 0 && var_index < variables_.size()) {
                variables_[var_index].setCoefficient(coeff);
            }
        }

        // Problem validation
        bool isValidSolution(const std::vector<double>& solution) const {
            if (solution.size() != variables_.size()) {
                return false; // Solution size must match number of variables
            }

            // Check variable bounds
            for (int i = 0; i < variables_.size(); ++i) {
                const auto& var = variables_[i];
                if (solution[i] < var.getLowerBound() - 1e-9 || solution[i] > var.getUpperBound() + 1e-9) {
                    return false; // Variable out of bounds
                }
            }   
            for (const auto& constraint : constraints_) {
                if (!constraint.isSatisfied(solution)) {
                    return false; // At least one constraint is not satisfied
                }
            }
            return true; // All constraints are satisfied
        }

        // Calculate the objective value for a given solution
        double calculateObjectiveValue(const std::vector<double>& solution) const {
            double value = 0.0;
            for (int i = 0; i < variables_.size() && i < solution.size(); ++i) {
                value += variables_[i].getCoefficient() * solution[i];
            }
            return value;  // Return raw value - don't flip for maximize
        }   

        // Problem statistics
        void printStatistics() const {
            std::cout << "Problem Name: " << name_ << "\n";
            std::cout << "Objective Type: " << (objective_type_ == ObjectiveType::MAXIMIZE ? "Maximize" : "Minimize") << "\n";
            std::cout << "Number of Variables: " << variables_.size() << "\n";
            std::cout << "Number of Constraints: " << constraints_.size() << "\n";

            int continuous_count = 0, integer_count = 0, binary_count = 0;
            for (const auto& var : variables_) {
                switch (var.getType()) {
                    case VariableType::CONTINUOUS: continuous_count++; break;
                    case VariableType::INTEGER: integer_count++; break;
                    case VariableType::BINARY: binary_count++; break;
                }
            }

            std::cout << " - Continuous Variables: " << continuous_count << "\n";
            std::cout << " - Integer Variables: " << integer_count << "\n";
            std::cout << " - Binary Variables: " << binary_count << "\n";
        }

    private:
        std::string name_;
        ObjectiveType objective_type_;
        std::vector<Variable> variables_; // List of decision variables
        std::vector<Constraint> constraints_; // List of constraints
        // REMOVED: objective_value_ - this should be in Solution class, not Problem class
};

// Forward declarations for classes that should be in separate headers
class Solution;
class SolverInterface;

} // namespace MIPSolver

#endif