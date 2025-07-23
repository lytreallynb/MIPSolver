// src/branch_bound_solver.h (简化版，暂时不包含许可证检查)
#ifndef BRANCH_BOUND_SOLVER_H
#define BRANCH_BOUND_SOLVER_H

#include "core.h"
#include "solution.h"
#include "simplex_solver.h"
#include <queue>
#include <chrono>
#include <limits>

namespace MIPSolver {

class BranchBoundSolver : public SolverInterface {
public:
    BranchBoundSolver() : simplex_solver_(false) {}
    
    Solution solve(const Problem& problem) override {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        if (verbose_) {
            std::cout << "\n------- Branch & Bound Solver -------" << std::endl;
            problem.printStatistics();
        }
        
        Solution solution(problem.getNumVariables());
        
        // Initialize branch and bound
        double best_objective = (problem.getObjectiveType() == ObjectiveType::MINIMIZE) ? 
                               std::numeric_limits<double>::infinity() : 
                               -std::numeric_limits<double>::infinity();
        std::vector<double> best_solution(problem.getNumVariables(), 0.0);
        
        // Create root node - use a STACK for depth-first search
        std::vector<BBNode> node_stack;
        
        BBNode root_node;
        root_node.problem = problem;
        root_node.depth = 0;
        root_node.bound = (problem.getObjectiveType() == ObjectiveType::MINIMIZE) ? 
                          -std::numeric_limits<double>::infinity() : 
                          std::numeric_limits<double>::infinity();
        
        node_stack.push_back(root_node);
        
        int nodes_processed = 0;
        int nodes_pruned = 0;
        
        while (!node_stack.empty() && nodes_processed < iteration_limit_) {
            BBNode current_node = node_stack.back();
            node_stack.pop_back();
            nodes_processed++;
            
            if (verbose_ && nodes_processed % 10 == 0) {
                std::cout << "Processed " << nodes_processed << " nodes, best: " << best_objective << std::endl;
            }
            
            // Solve LP relaxation for current node
            SimplexSolver::SimplexResult lp_result = simplex_solver_.solveLPRelaxation(current_node.problem);
            
            // Check if LP is infeasible
            if (lp_result.is_infeasible) {
                nodes_pruned++;
                if (verbose_) {
                    std::cout << "Node " << nodes_processed << ": LP infeasible, pruned" << std::endl;
                }
                continue;
            }
            
            // Check if LP is unbounded
            if (lp_result.is_unbounded) {
                if (problem.getObjectiveType() == ObjectiveType::MINIMIZE) {
                    solution.setStatus(Solution::Status::UNBOUNDED);
                    return solution;
                }
            }
            
            if (verbose_) {
                std::cout << "Node " << nodes_processed << " at depth " << current_node.depth 
                          << ": LP obj = " << lp_result.objective_value << std::endl;
            }
            
            // Check bound (pruning condition)
            if (shouldPrune(lp_result.objective_value, best_objective, problem.getObjectiveType())) {
                nodes_pruned++;
                if (verbose_) {
                    std::cout << "Node " << nodes_processed << ": Bound " << lp_result.objective_value 
                              << " pruned (current best: " << best_objective << ")" << std::endl;
                }
                continue;
            }
            
            // Check if solution is integer feasible
            if (isIntegerFeasible(lp_result.solution, problem)) {
                // Found feasible integer solution
                if (isBetterSolution(lp_result.objective_value, best_objective, problem.getObjectiveType())) {
                    best_objective = lp_result.objective_value;
                    best_solution = lp_result.solution;
                    
                    if (verbose_) {
                        std::cout << "Node " << nodes_processed << ": New integer solution found! Objective: " 
                                  << best_objective << " [";
                        for (size_t i = 0; i < best_solution.size(); ++i) {
                            std::cout << best_solution[i];
                            if (i < best_solution.size() - 1) std::cout << ", ";
                        }
                        std::cout << "]" << std::endl;
                    }
                }
                continue;
            }
            
            // Branch: find most fractional variable
            int branch_var = findBranchingVariable(lp_result.solution, problem);
            if (branch_var == -1) {
                if (verbose_) {
                    std::cout << "Node " << nodes_processed << ": No fractional variables found, skipping" << std::endl;
                }
                continue;
            }
            
            double branch_value = lp_result.solution[branch_var];
            
            if (verbose_) {
                std::cout << "Node " << nodes_processed << ": Branching on x" << branch_var 
                          << " = " << branch_value << std::endl;
            }
            
            // Create two child nodes
            BBNode right_child = current_node;
            BBNode left_child = current_node;
            
            left_child.depth = current_node.depth + 1;
            right_child.depth = current_node.depth + 1;
            
            // Left child: x[branch_var] <= floor(branch_value)
            double floor_val = std::floor(branch_value);
            addBound(left_child.problem, branch_var, -std::numeric_limits<double>::infinity(), floor_val);
            left_child.bound = lp_result.objective_value;
            
            // Right child: x[branch_var] >= ceil(branch_value)  
            double ceil_val = std::ceil(branch_value);
            addBound(right_child.problem, branch_var, ceil_val, std::numeric_limits<double>::infinity());
            right_child.bound = lp_result.objective_value;
            
            // Add children to stack
            node_stack.push_back(right_child);
            node_stack.push_back(left_child);
            
            if (verbose_) {
                std::cout << "Node " << nodes_processed << ": Created 2 children (depths " 
                          << left_child.depth << ", " << right_child.depth << ")" << std::endl;
            }
        }
        
        // Set final solution
        for (int i = 0; i < problem.getNumVariables(); ++i) {
            solution.setValue(i, best_solution[i]);
        }
        solution.setObjectiveValue(best_objective);
        solution.setIterations(nodes_processed);
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        solution.setSolveTime(duration.count() / 1000.0);
        
        // Set solution status
        if (best_objective == std::numeric_limits<double>::infinity() || 
            best_objective == -std::numeric_limits<double>::infinity()) {
            solution.setStatus(Solution::Status::INFEASIBLE);
        } else if (nodes_processed >= iteration_limit_) {
            solution.setStatus(Solution::Status::ITERATION_LIMIT);
        } else {
            solution.setStatus(Solution::Status::OPTIMAL);
        }
        
        if (verbose_) {
            std::cout << "\n------- Branch & Bound Complete -------" << std::endl;
            std::cout << "Nodes processed: " << nodes_processed << std::endl;
            std::cout << "Nodes pruned: " << nodes_pruned << std::endl;
            solution.print();
        }
        
        return solution;
    }

private:
    SimplexSolver simplex_solver_;
    
    struct BBNode {
        Problem problem;
        double bound;
        int depth;
    };
    
    bool shouldPrune(double node_bound, double best_objective, ObjectiveType obj_type) {
        const double tolerance = 1e-6;
        
        if (obj_type == ObjectiveType::MINIMIZE) {
            return node_bound >= best_objective - tolerance;
        } else {
            return node_bound <= best_objective + tolerance;
        }
    }
    
    bool isBetterSolution(double new_obj, double current_best, ObjectiveType obj_type) {
        const double tolerance = 1e-6;
        
        if (obj_type == ObjectiveType::MINIMIZE) {
            return new_obj < current_best - tolerance;
        } else {
            return new_obj > current_best + tolerance;
        }
    }
    
    bool isIntegerFeasible(const std::vector<double>& solution, const Problem& problem) {
        const double tolerance = 1e-6;
        
        for (int i = 0; i < problem.getNumVariables(); ++i) {
            const Variable& var = problem.getVariable(i);
            if (var.getType() == VariableType::INTEGER || var.getType() == VariableType::BINARY) {
                double val = solution[i];
                if (std::abs(val - std::round(val)) > tolerance) {
                    return false;
                }
            }
        }
        return true;
    }
    
    int findBranchingVariable(const std::vector<double>& solution, const Problem& problem) {
        int branch_var = -1;
        double max_fractional = 0.0;
        const double tolerance = 1e-6;
        
        for (int i = 0; i < problem.getNumVariables(); ++i) {
            const Variable& var = problem.getVariable(i);
            if (var.getType() == VariableType::INTEGER || var.getType() == VariableType::BINARY) {
                double val = solution[i];
                double fractional_part = std::abs(val - std::round(val));
                
                if (fractional_part > tolerance && fractional_part > max_fractional) {
                    max_fractional = fractional_part;
                    branch_var = i;
                }
            }
        }
        
        return branch_var;
    }
    
    void addBound(Problem& problem, int var_index, double lower, double upper) {
        Variable& var = problem.getVariable(var_index);
        double current_lower = var.getLowerBound();
        double current_upper = var.getUpperBound();
        
        double new_lower = std::max(current_lower, lower);
        double new_upper = std::min(current_upper, upper);
        
        var.setBounds(new_lower, new_upper);
    }
};

} // namespace MIPSolver

#endif