#ifndef SOTA_ALGORITHMS_H
#define SOTA_ALGORITHMS_H

/*
 * SOTA（State-of-the-Art）算法集合
 * 
 * 这个头文件实现了混合整数规划领域最先进的求解技术，包括：
 * 
 * 1. 自适应大邻域搜索 (Adaptive Large Neighborhood Search, ALNS)
 *    - 启发式搜索算法，适用于大规模问题的快速求解
 *    - 动态调整破坏和修复算子的权重
 *    - 结合模拟退火接受准则，平衡探索和开发
 * 
 * 2. 机器学习驱动的分支选择 (ML-guided Branching)
 *    - 使用特征提取和预测模型改进分支变量选择
 *    - 基于历史求解经验学习最优分支策略
 *    - 显著提高分支定界算法的效率
 * 
 * 3. 启发式预处理 (Heuristic Preprocessing)
 *    - 问题规模缩减技术，消除冗余变量和约束
 *    - 变量固定和约束聚合
 *    - 隐含边界检测和系数强化
 * 
 * 4. 动态割平面生成 (Dynamic Cutting Planes)
 *    - 多种类型的有效不等式生成
 *    - 自适应割平面选择和管理
 *    - 改善线性松弛的紧致性
 * 
 * 设计理念：
 * - 模块化架构，各算法可独立使用或组合
 * - 参数自适应，减少人工调参需求
 * - 高效实现，适用于工业级应用
 * - 理论保证与实践效果的良好平衡
 */

#include "core.h"
#include "solution.h"
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>

namespace MIPSolver {

/**
 * @brief SOTA算法集合 - 实现最先进的优化技术
 * 
 * 包含以下最先进的算法：
 * 1. 自适应大邻域搜索 (Adaptive Large Neighborhood Search)
 * 2. 机器学习驱动的分支选择
 * 3. 启发式预处理
 * 4. 动态割平面生成
 */

// 自适应大邻域搜索 (ALNS)
/*
 * 自适应大邻域搜索算法类
 * 
 * ALNS是一种元启发式算法，特别适用于组合优化问题。算法核心思想：
 * 
 * 1. 破坏-修复机制：
 *    - 破坏算子：从当前解中移除一部分变量的赋值
 *    - 修复算子：为被移除的变量重新赋值，构造新解
 * 
 * 2. 自适应权重调整：
 *    - 根据算子的历史表现动态调整选择概率
 *    - 好的算子获得更高权重，差的算子权重降低
 * 
 * 3. 接受准则：
 *    - 使用模拟退火策略接受劣解
 *    - 避免陷入局部最优，增强全局搜索能力
 * 
 * 适用场景：
 * - 大规模混合整数规划问题
 * - 需要快速获得高质量可行解的情况
 * - 精确算法求解时间过长的复杂问题
 */
class AdaptiveLargeNeighborhoodSearch {
public:
    /*
     * ALNS算法参数结构
     * 
     * 包含算法运行所需的所有可调参数：
     * - max_iterations: 最大迭代次数，控制算法运行时间
     * - alpha: 权重衰减因子，控制历史信息的重要性
     * - temperature_start/end: 模拟退火的初始和终止温度
     * - segment_size: 权重更新的周期长度
     * - 奖励参数: 不同质量解的奖励分值
     */
    struct ALNSParameters {
        int max_iterations = 1000;         // 最大迭代次数
        double alpha = 0.1;                // 权重衰减因子（0-1之间）
        double temperature_start = 100.0;  // 初始温度（接受劣解的概率较高）
        double temperature_end = 1.0;      // 终止温度（接受劣解的概率较低）
        int segment_size = 100;            // 权重更新周期
        double best_reward = 30.0;         // 找到新最优解的奖励
        double better_reward = 15.0;       // 找到更好解的奖励
        double accepted_reward = 5.0;      // 解被接受的基础奖励
    };

private:
    ALNSParameters params_;
    std::mt19937 rng_;
    
    // 破坏算子
    std::vector<std::function<std::vector<int>(const std::vector<double>&, int)>> destroy_operators_;
    // 修复算子
    std::vector<std::function<std::vector<double>(const Problem&, const std::vector<int>&)>> repair_operators_;
    
    // 权重向量
    std::vector<double> destroy_weights_;
    std::vector<double> repair_weights_;
    
public:
    AdaptiveLargeNeighborhoodSearch(unsigned seed = 42);
    
    Solution solve(const Problem& problem, const Solution& initial_solution);
    
private:
    void initializeOperators();
    int selectOperator(const std::vector<double>& weights);
    void updateWeights(int operator_idx, double reward, std::vector<double>& weights);
    
    // 破坏算子实现
    std::vector<int> randomDestroy(const std::vector<double>& solution, int remove_count);
    std::vector<int> worstDestroy(const std::vector<double>& solution, int remove_count);
    std::vector<int> clusterDestroy(const std::vector<double>& solution, int remove_count);
    
    // 修复算子实现
    std::vector<double> greedyRepair(const Problem& problem, const std::vector<int>& removed_vars);
    std::vector<double> regretRepair(const Problem& problem, const std::vector<int>& removed_vars);
};

// 机器学习驱动的分支选择
class MLBranchingStrategy {
public:
    struct BranchingFeatures {
        double pseudocost_up;
        double pseudocost_down;
        double infeasibility;
        double obj_coefficient;
        double constraint_density;
        double variable_age;
    };
    
private:
    // 简化的线性模型权重 (在实际SOTA实现中会使用神经网络)
    std::vector<double> feature_weights_;
    bool is_trained_;
    
public:
    MLBranchingStrategy();
    
    // 选择最佳分支变量
    int selectBranchingVariable(const Problem& problem, 
                               const std::vector<double>& lp_solution,
                               const std::vector<BranchingFeatures>& features);
    
    // 更新模型 (简化版本)
    void updateModel(const std::vector<BranchingFeatures>& features, 
                     const std::vector<double>& outcomes);
    
private:
    BranchingFeatures extractFeatures(const Problem& problem, int var_index, 
                                     const std::vector<double>& lp_solution);
    double predictScore(const BranchingFeatures& features);
};

// 启发式预处理器
class HeuristicPreprocessor {
public:
    struct PreprocessingResult {
        Problem processed_problem;
        std::vector<int> variable_mapping;
        std::vector<int> constraint_mapping;
        bool problem_reduced;
        int variables_eliminated;
        int constraints_eliminated;
    };
    
    PreprocessingResult preprocess(const Problem& original_problem);
    
private:
    // 变量固定
    void fixVariables(Problem& problem, std::vector<int>& eliminated_vars);
    
    // 约束聚合
    void aggregateConstraints(Problem& problem, std::vector<int>& eliminated_constraints);
    
    // 系数强化
    void strengthenCoefficients(Problem& problem);
    
    // 隐含边界检测
    void detectImpliedBounds(Problem& problem);
};

// 动态割平面生成器
class DynamicCuttingPlanes {
public:
    enum class CutType {
        GOMORY,
        KNAPSACK_COVER,
        MIXED_INTEGER_ROUNDING,
        ZERO_HALF,
        CLIQUE
    };
    
    struct Cut {
        std::vector<double> coefficients;
        double rhs;
        CutType type;
        double efficacy;
        double violation;
    };
    
private:
    double min_efficacy_;
    double min_violation_;
    int max_cuts_per_round_;
    
public:
    DynamicCuttingPlanes(double min_efficacy = 0.1, 
                        double min_violation = 1e-6,
                        int max_cuts = 50);
    
    std::vector<Cut> generateCuts(const Problem& problem, 
                                 const std::vector<double>& lp_solution);
    
private:
    std::vector<Cut> generateGomoryCuts(const Problem& problem, 
                                       const std::vector<double>& lp_solution);
    
    std::vector<Cut> generateKnapsackCoverCuts(const Problem& problem, 
                                              const std::vector<double>& lp_solution);
    
    std::vector<Cut> generateMIRCuts(const Problem& problem, 
                                    const std::vector<double>& lp_solution);
    
    double calculateEfficacy(const Cut& cut, const std::vector<double>& lp_solution);
    double calculateViolation(const Cut& cut, const std::vector<double>& lp_solution);
};

// SOTA求解器集成器
class SOTASolver : public SolverInterface {
private:
    std::unique_ptr<AdaptiveLargeNeighborhoodSearch> alns_;
    std::unique_ptr<MLBranchingStrategy> ml_branching_;
    std::unique_ptr<HeuristicPreprocessor> preprocessor_;
    std::unique_ptr<DynamicCuttingPlanes> cutting_planes_;
    
    bool use_preprocessing_;
    bool use_cutting_planes_;
    bool use_ml_branching_;
    bool use_alns_;
    
public:
    SOTASolver();
    ~SOTASolver() = default;
    
    Solution solve(const Problem& problem) override;
    
    // 配置选项
    void enablePreprocessing(bool enable = true) { use_preprocessing_ = enable; }
    void enableCuttingPlanes(bool enable = true) { use_cutting_planes_ = enable; }
    void enableMLBranching(bool enable = true) { use_ml_branching_ = enable; }
    void enableALNS(bool enable = true) { use_alns_ = enable; }
    
private:
    Solution solveWithSOTATechniques(const Problem& problem);
    Solution hybridSearch(const Problem& problem, const Solution& initial_solution);
};

} // namespace MIPSolver

#endif // SOTA_ALGORITHMS_H
