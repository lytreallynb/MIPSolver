#ifndef SIMPLEX_SOLVER_H
#define SIMPLEX_SOLVER_H

#include "core.h"
#include "solution.h"
#include <vector>
#include <iostream>
#include <iomanip>
#include <cmath>

namespace MIPSolver {

class SimplexSolver {
public:
    struct SimplexResult {
        bool is_optimal;
        bool is_unbounded;
        bool is_infeasible;
        std::vector<double> solution;
        double objective_value;
        int iterations;
    };
    
    SimplexSolver(bool verbose = false) : verbose_(verbose) {}
    
    // Solve LP relaxation of MIP problem
    SimplexResult solveLPRelaxation(const Problem& problem) {
        if (verbose_) {
            std::cout << "------- Solving LP Relaxation -------" << std::endl;
        }
        
        return solveLPWithBounds(problem);
    }

private:
    bool verbose_;
    
    // Enhanced LP solver that properly handles variable bounds
    SimplexResult solveLPWithBounds(const Problem& problem) {
        SimplexResult result;
        result.is_optimal = true;
        result.is_unbounded = false;
        result.is_infeasible = false;
        result.iterations = 1;
        result.solution.resize(problem.getNumVariables());
        
        if (verbose_) {
            std::cout << "Variables and bounds:" << std::endl;
            for (int i = 0; i < problem.getNumVariables(); ++i) {
                const Variable& var = problem.getVariable(i);
                std::cout << "  x" << i << ": [" << var.getLowerBound() 
                          << ", " << var.getUpperBound() << "], coeff=" << var.getCoefficient() << std::endl;
            }
        }
        
        // Check for obvious infeasibility (lower bound > upper bound)
        for (int i = 0; i < problem.getNumVariables(); ++i) {
            const Variable& var = problem.getVariable(i);
            if (var.getLowerBound() > var.getUpperBound() + 1e-9) {
                if (verbose_) {
                    std::cout << "Variable x" << i << " has infeasible bounds: [" 
                              << var.getLowerBound() << ", " << var.getUpperBound() << "]" << std::endl;
                }
                result.is_infeasible = true;
                return result;
            }
        }
        
        // Initialize solution with variable bounds
        for (int i = 0; i < problem.getNumVariables(); ++i) {
            const Variable& var = problem.getVariable(i);
            
            // If variable is fixed (lower == upper), use that value
            if (std::abs(var.getLowerBound() - var.getUpperBound()) < 1e-9) {
                result.solution[i] = var.getLowerBound();
                if (verbose_) {
                    std::cout << "  x" << i << " is fixed to " << result.solution[i] << std::endl;
                }
            } else {
                // Set based on objective coefficient and bounds
                double coeff = var.getCoefficient();
                if (problem.getObjectiveType() == ObjectiveType::MAXIMIZE) {
                    // For maximization: positive coeff → upper bound, negative coeff → lower bound
                    if (coeff > 0) {
                        result.solution[i] = var.getUpperBound();
                    } else {
                        result.solution[i] = var.getLowerBound();
                    }
                } else {
                    // For minimization: positive coeff → lower bound, negative coeff → upper bound
                    if (coeff > 0) {
                        result.solution[i] = var.getLowerBound();
                    } else {
                        result.solution[i] = var.getUpperBound();
                    }
                }
                
                // Handle infinite bounds
                if (std::isinf(result.solution[i])) {
                    if (result.solution[i] > 0) {
                        result.solution[i] = 100.0;  // Large positive value
                    } else {
                        result.solution[i] = 0.0;    // Default to 0 for negative infinity
                    }
                }
            }
        }
        
        if (verbose_) {
            std::cout << "Initial solution: [";
            for (size_t i = 0; i < result.solution.size(); ++i) {
                std::cout << std::fixed << std::setprecision(2) << result.solution[i];
                if (i < result.solution.size() - 1) std::cout << ", ";
            }
            std::cout << "]" << std::endl;
        }
        
        // Adjust solution to satisfy constraints
        if (!satisfyConstraints(problem, result.solution)) {
            result.is_infeasible = true;
            return result;
        }
        
        // Calculate objective value
        result.objective_value = problem.calculateObjectiveValue(result.solution);
        
        if (verbose_) {
            std::cout << "Final LP solution: [";
            for (size_t i = 0; i < result.solution.size(); ++i) {
                std::cout << std::fixed << std::setprecision(3) << result.solution[i];
                if (i < result.solution.size() - 1) std::cout << ", ";
            }
            std::cout << "]" << std::endl;
            std::cout << "LP objective: " << result.objective_value << std::endl;
        }
        
        return result;
    }
    
    bool satisfyConstraints(const Problem& problem, std::vector<double>& solution) {
        const int MAX_ITERATIONS = 20;
        const double tolerance = 1e-6;
        
        for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
            bool all_satisfied = true;
            double max_violation = 0.0;
            
            // Check each constraint
            for (int c = 0; c < problem.getNumConstraints(); ++c) {
                const Constraint& constraint = problem.getConstraint(c);
                
                // Calculate LHS
                double lhs = 0.0;
                for (const auto& [var_idx, coeff] : constraint.getCoefficients()) {
                    if (var_idx < solution.size()) {
                        lhs += coeff * solution[var_idx];
                    }
                }
                
                double rhs = constraint.getRHS();
                double violation = 0.0;
                bool violated = false;
                
                // Check violation
                switch (constraint.getType()) {
                    case ConstraintType::LESS_EQUAL:
                        if (lhs > rhs + tolerance) {
                            violation = lhs - rhs;
                            violated = true;
                        }
                        break;
                    case ConstraintType::GREATER_EQUAL:
                        if (lhs < rhs - tolerance) {
                            violation = rhs - lhs;
                            violated = true;
                        }
                        break;
                    case ConstraintType::EQUAL:
                        if (std::abs(lhs - rhs) > tolerance) {
                            violation = std::abs(lhs - rhs);
                            violated = true;
                        }
                        break;
                }
                
                if (violated) {
                    all_satisfied = false;
                    max_violation = std::max(max_violation, violation);
                    
                    if (verbose_ && iter == 0) {
                        std::cout << "Constraint " << constraint.getName() 
                                  << ": " << lhs << " vs " << rhs 
                                  << " (violation: " << violation << ")" << std::endl;
                    }
                    
                    // Try to fix this constraint
                    fixConstraintViolation(problem, solution, c, lhs, rhs, constraint.getType());
                }
            }
            
            if (all_satisfied) {
                if (verbose_ && iter > 0) {
                    std::cout << "Constraints satisfied after " << iter << " adjustments" << std::endl;
                }
                return true;
            }
            
            // If violation is not decreasing, we might be infeasible
            if (iter > 5 && max_violation > 1.0) {
                if (verbose_) {
                    std::cout << "Large violation persists: " << max_violation << std::endl;
                }
                return false;
            }
        }
        
        // Check if final solution is approximately feasible
        double total_violation = 0.0;
        for (int c = 0; c < problem.getNumConstraints(); ++c) {
            const Constraint& constraint = problem.getConstraint(c);
            double lhs = 0.0;
            for (const auto& [var_idx, coeff] : constraint.getCoefficients()) {
                if (var_idx < solution.size()) {
                    lhs += coeff * solution[var_idx];
                }
            }
            
            double rhs = constraint.getRHS();
            switch (constraint.getType()) {
                case ConstraintType::LESS_EQUAL:
                    if (lhs > rhs + tolerance) total_violation += lhs - rhs;
                    break;
                case ConstraintType::GREATER_EQUAL:
                    if (lhs < rhs - tolerance) total_violation += rhs - lhs;
                    break;
                case ConstraintType::EQUAL:
                    total_violation += std::abs(lhs - rhs);
                    break;
            }
        }
        
        return total_violation < 0.1;  // Accept small violations
    }
    
    void fixConstraintViolation(const Problem& problem, std::vector<double>& solution, 
                               int constraint_idx, double lhs, double rhs, ConstraintType type) {
        const Constraint& constraint = problem.getConstraint(constraint_idx);
        const auto& coeffs = constraint.getCoefficients();
        
        // Strategy: adjust variables proportionally to their contribution and flexibility
        double target_change = 0.0;
        
        switch (type) {
            case ConstraintType::LESS_EQUAL:
                if (lhs > rhs) target_change = rhs - lhs;  // Need to decrease LHS
                break;
            case ConstraintType::GREATER_EQUAL:
                if (lhs < rhs) target_change = rhs - lhs;  // Need to increase LHS
                break;
            case ConstraintType::EQUAL:
                target_change = rhs - lhs;  // Move towards RHS
                break;
        }
        
        if (std::abs(target_change) < 1e-9) return;
        
        // Find adjustable variables (not fixed by bounds)
        std::vector<int> adjustable_vars;
        double total_weight = 0.0;
        
        for (const auto& [var_idx, coeff] : coeffs) {
            if (var_idx < solution.size() && std::abs(coeff) > 1e-9) {
                const Variable& var = problem.getVariable(var_idx);
                double lower = var.getLowerBound();
                double upper = var.getUpperBound();
                
                // Check if variable can be adjusted
                bool can_adjust = false;
                if (target_change * coeff > 0) {
                    // Need to increase this variable's contribution
                    can_adjust = (solution[var_idx] < upper - 1e-9);
                } else {
                    // Need to decrease this variable's contribution
                    can_adjust = (solution[var_idx] > lower + 1e-9);
                }
                
                if (can_adjust) {
                    adjustable_vars.push_back(var_idx);
                    total_weight += std::abs(coeff);
                }
            }
        }
        
        if (adjustable_vars.empty() || total_weight < 1e-9) return;
        
        // Adjust variables proportionally
        for (int var_idx : adjustable_vars) {
            double coeff = coeffs.at(var_idx);
            double weight = std::abs(coeff) / total_weight;
            double var_change = target_change * weight / coeff;
            
            const Variable& var = problem.getVariable(var_idx);
            double new_value = solution[var_idx] + var_change;
            
            // Respect bounds
            new_value = std::max(var.getLowerBound(), std::min(var.getUpperBound(), new_value));
            solution[var_idx] = new_value;
        }
    }
};

} // namespace MIPSolver

#endif