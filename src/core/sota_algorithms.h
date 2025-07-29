#ifndef SOTA_ALGORITHMS_H
#define SOTA_ALGORITHMS_H

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
class AdaptiveLargeNeighborhoodSearch {
public:
    struct ALNSParameters {
        int max_iterations = 1000;
        double alpha = 0.1;  // 权重衰减因子
        double temperature_start = 100.0;
        double temperature_end = 1.0;
        int segment_size = 100;
        double best_reward = 30.0;
        double better_reward = 15.0;
        double accepted_reward = 5.0;
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
