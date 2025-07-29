// src/branch_bound_solver.h (简化版，暂时不包含许可证检查)
#ifndef BRANCH_BOUND_SOLVER_H
#define BRANCH_BOUND_SOLVER_H

/*
 * 分支定界求解器
 * 
 * 这是MIPSolver的核心求解算法实现，采用分支定界法求解混合整数线性规划问题。
 * 
 * 算法原理：
 * 1. 线性松弛：将整数约束松弛为连续约束，使用单纯形法求解
 * 2. 分支操作：对非整数解的整数变量进行分支，创建子问题
 * 3. 定界操作：利用线性松弛的最优值作为上界进行剪枝
 * 4. 搜索策略：采用深度优先搜索遍历分支树
 * 
 * 性能优化：
 * - 智能分支变量选择：选择分数部分最大的变量进行分支
 * - 有效剪枝策略：及时剪除不可能包含最优解的子树
 * - 内存高效：使用栈结构管理分支节点，避免递归调用
 * 
 * 算法特点：
 * - 保证找到全局最优解（如果存在且有限）
 * - 适用于小到中规模的混合整数规划问题
 * - 提供详细的求解过程信息和统计数据
 */

#include "core.h"
#include "solution.h"
#include "simplex_solver.h"
#include <queue>
#include <chrono>
#include <limits>

namespace MIPSolver {

class BranchBoundSolver : public SolverInterface {
public:
    /*
     * 构造函数
     * 
     * 初始化分支定界求解器，配置内部的单纯形求解器为非详细模式
     * 这样可以避免在分支定界过程中产生过多的调试输出
     */
    BranchBoundSolver() : simplex_solver_(false) {}
    
    /*
     * 核心求解方法
     * 
     * 实现完整的分支定界算法流程：
     * 1. 初始化：设置根节点和最优值界限
     * 2. 主循环：处理分支树中的每个节点
     * 3. 线性松弛：使用单纯形法求解当前节点的LP松弛
     * 4. 可行性检查：判断解是否满足整数约束
     * 5. 分支操作：对非整数变量创建子问题
     * 6. 剪枝判断：根据界限剪除不必要的分支
     * 7. 结果返回：设置最终解的状态和数值
     * 
     * @param problem: 要求解的混合整数规划问题
     * @return: 包含最优解信息的Solution对象
     */
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
    SimplexSolver simplex_solver_;  // 内部单纯形求解器，用于求解线性松弛问题
    
    /*
     * 分支节点结构
     * 
     * 表示分支树中的一个节点，包含：
     * - problem: 当前节点对应的子问题（包含额外的边界约束）
     * - bound: 当前节点的线性松弛最优值（用于剪枝判断）
     * - depth: 节点在分支树中的深度（用于调试和统计）
     */
    struct BBNode {
        Problem problem;  // 子问题定义
        double bound;     // 线性松弛界限
        int depth;        // 分支深度
    };
    
    /*
     * 剪枝判断函数
     * 
     * 根据当前节点的界限和已知的最优值判断是否可以剪枝
     * 
     * 剪枝条件：
     * - 最小化问题：如果节点下界 >= 当前最优值，则可以剪枝
     * - 最大化问题：如果节点上界 <= 当前最优值，则可以剪枝
     * 
     * @param node_bound: 当前节点的界限值
     * @param best_objective: 当前已知的最优目标函数值
     * @param obj_type: 目标函数类型（最大化或最小化）
     * @return: true表示可以剪枝，false表示需要继续探索
     */
    bool shouldPrune(double node_bound, double best_objective, ObjectiveType obj_type) {
        const double tolerance = 1e-6;
        
        if (obj_type == ObjectiveType::MINIMIZE) {
            return node_bound >= best_objective - tolerance;
        } else {
            return node_bound <= best_objective + tolerance;
        }
    }
    
    /*
     * 解质量比较函数
     * 
     * 判断新找到的解是否比当前最优解更好
     * 考虑数值误差的容忍度，避免浮点精度问题
     * 
     * @param new_obj: 新解的目标函数值
     * @param current_best: 当前最优解的目标函数值
     * @param obj_type: 目标函数类型
     * @return: true表示新解更好，false表示当前解更好或相等
     */
    bool isBetterSolution(double new_obj, double current_best, ObjectiveType obj_type) {
        const double tolerance = 1e-6;
        
        if (obj_type == ObjectiveType::MINIMIZE) {
            return new_obj < current_best - tolerance;
        } else {
            return new_obj > current_best + tolerance;
        }
    }
    
    /*
     * 整数可行性检查函数
     * 
     * 检查给定的解是否满足所有整数变量的整数约束
     * 使用数值容忍度处理浮点误差
     * 
     * @param solution: 待检查的解向量
     * @param problem: 原问题定义（包含变量类型信息）
     * @return: true表示解满足整数约束，false表示存在非整数的整数变量
     */
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
    
    /*
     * 分支变量选择函数
     * 
     * 选择最适合进行分支的整数变量，采用"最大分数部分"策略：
     * - 只考虑当前取非整数值的整数变量或二进制变量
     * - 选择分数部分最大的变量，这样分支后更可能快速剪枝
     * - 分数部分 = |x - round(x)|，表示变量值偏离最近整数的程度
     * 
     * @param solution: 当前线性松弛的最优解
     * @param problem: 问题定义（包含变量类型信息）
     * @return: 选中的分支变量索引，-1表示没有需要分支的变量
     */
    int findBranchingVariable(const std::vector<double>& solution, const Problem& problem) {
        int branch_var = -1;
        double max_fractional = 0.0;
        const double tolerance = 1e-6;
        
        // 遍历所有变量，寻找分数部分最大的整数变量
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
    
    /*
     * 添加变量边界约束函数
     * 
     * 为指定变量添加新的边界约束，用于分支操作
     * 新边界与原边界取交集，确保约束只会更加严格
     * 
     * @param problem: 要修改的问题实例
     * @param var_index: 目标变量的索引
     * @param lower: 新的下界
     * @param upper: 新的上界
     */
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