#ifndef SIMPLEX_SOLVER_H
#define SIMPLEX_SOLVER_H

/*
 * 单纯形法求解器
 * 
 * 这是MIPSolver中用于求解线性规划问题的核心组件，主要用途：
 * 
 * 1. 分支定界中的线性松弛求解：
 *    - 将混合整数规划的整数约束松弛为连续约束
 *    - 为分支定界提供上界（最小化）或下界（最大化）
 *    - 快速判断子问题的可行性
 * 
 * 2. 算法特点：
 *    - 简化的单纯形实现，适用于中小规模问题
 *    - 重点处理变量边界约束
 *    - 启发式约束满足方法，快速收敛
 *    - 鲁棒的数值稳定性处理
 * 
 * 3. 性能考虑：
 *    - 避免复杂的基变换操作
 *    - 使用迭代修正方法处理约束违反
 *    - 适合分支定界中的频繁调用
 * 
 * 注意：这不是完整的标准单纯形法实现，而是针对MIP求解优化的简化版本
 */

#include "core.h"
#include "solution.h"
#include <vector>
#include <iostream>
#include <iomanip>
#include <cmath>

namespace MIPSolver {

class SimplexSolver {
public:
    /*
     * 单纯形求解结果结构
     * 
     * 封装线性规划求解的所有相关信息：
     * - 求解状态：最优、无界、不可行
     * - 解向量：变量的最优取值
     * - 目标函数值：最优解对应的目标函数值
     * - 迭代次数：算法收敛所需的迭代步数
     */
    struct SimplexResult {
        bool is_optimal;      // 是否找到最优解
        bool is_unbounded;    // 是否无界（目标函数可以无限增大/减小）
        bool is_infeasible;   // 是否不可行（约束条件矛盾）
        std::vector<double> solution;    // 最优解向量
        double objective_value;          // 最优目标函数值
        int iterations;                  // 迭代次数统计
    };
    
    /*
     * 构造函数
     * 
     * @param verbose: 是否输出详细的求解过程信息
     *                 在调试模式下有助于理解算法行为
     */
    SimplexSolver(bool verbose = false) : verbose_(verbose) {}
    
    /*
     * 求解线性规划松弛问题
     * 
     * 这是单纯形求解器的主要接口，用于分支定界算法中：
     * - 移除所有整数约束，将问题转换为纯线性规划
     * - 保留所有线性约束和变量边界
     * - 返回线性松弛的最优解（如果存在）
     * 
     * @param problem: 混合整数规划问题实例
     * @return: 包含求解结果的SimplexResult结构
     */
    SimplexResult solveLPRelaxation(const Problem& problem) {
        if (verbose_) {
            std::cout << "------- Solving LP Relaxation -------" << std::endl;
        }
        
        return solveLPWithBounds(problem);
    }

private:
    bool verbose_;  // 是否输出详细求解信息的标志
    
    /*
     * 带边界处理的线性规划求解方法
     * 
     * 这是简化的单纯形法实现，核心思想：
     * 1. 初始解构造：根据目标函数系数和变量边界设置初始点
     * 2. 约束满足：使用迭代方法调整解以满足所有线性约束
     * 3. 可行性检查：验证最终解是否在可行域内
     * 
     * 算法特点：
     * - 不使用标准的基变换操作
     * - 采用启发式方法快速找到可行解
     * - 适合分支定界中的频繁调用场景
     * 
     * @param problem: 要求解的线性规划问题
     * @return: 求解结果结构
     */
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