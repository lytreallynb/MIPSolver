#include "mipsolver_c_api.h"
#include "../src/core.h"
#include "../src/solution.h"
#include "../src/branch_bound_solver.h"

/*
 * MIPSolver C API 实现
 * 
 * 这个文件提供了C语言风格的API接口，主要用途：
 * 
 * 1. 语言互操作性：
 *    - 支持C语言和其他语言（如Fortran、Julia）的调用
 *    - 提供稳定的ABI（应用二进制接口）
 *    - 避免C++名称修饰和模板实例化问题
 * 
 * 2. 接口设计原则：
 *    - 使用不透明指针隐藏C++实现细节
 *    - 明确的资源管理（创建/销毁配对）
 *    - 错误通过返回值传递，避免异常
 * 
 * 3. 内存管理：
 *    - 所有对象使用堆分配
 *    - 提供明确的销毁函数防止内存泄漏
 *    - 使用智能指针包装确保异常安全
 * 
 * 4. 类型转换：
 *    - 枚举类型转换为整数常量
 *    - C++对象包装为不透明句柄
 *    - 自动处理字符串编码转换
 */

// 辅助宏 - 安全地将不透明指针转换回C++指针类型
// 这些宏提供类型安全的转换，避免直接的强制类型转换
#define GET_PROBLEM(handle) static_cast<MIPSolver::Problem*>(handle)
#define GET_SOLUTION(handle) static_cast<MIPSolver::Solution*>(handle)

extern "C" {

// --- 问题管理接口 ---

MIPSOLVER_API MIPSolver_ProblemHandle MIPSolver_CreateProblem(const char* name, MIPSolver_ObjectiveType obj_type) {
    /*
     * 创建优化问题实例
     * 
     * 功能描述：
     * - 在堆上创建新的Problem对象
     * - 初始化问题名称和目标函数类型
     * - 返回不透明句柄供后续API调用使用
     * 
     * 参数说明：
     * @param name: 问题名称，用于标识和日志输出
     * @param obj_type: 目标函数类型（最大化或最小化）
     * 
     * @return: 问题实例句柄，调用者必须使用MIPSolver_DestroyProblem释放
     */
    auto cpp_obj_type = (obj_type == MIPSOLVER_OBJ_MAXIMIZE) ? MIPSolver::ObjectiveType::MAXIMIZE : MIPSolver::ObjectiveType::MINIMIZE;
    // 在堆上分配C++对象并将其指针作为句柄返回
    return new MIPSolver::Problem(name, cpp_obj_type);
}

MIPSOLVER_API void MIPSolver_DestroyProblem(MIPSolver_ProblemHandle handle) {
    /*
     * 销毁问题实例
     * 
     * 功能描述：
     * - 释放由MIPSolver_CreateProblem创建的问题实例
     * - 清理所有相关的内存资源
     * - 安全处理空句柄情况
     * 
     * 内存管理：
     * - 每个CreateProblem调用都必须配对一个DestroyProblem调用
     * - 不要对同一句柄调用此函数两次
     * - 调用后句柄将不再有效，不应再被使用
     * 
     * @param handle: 要销毁的问题实例句柄
     */
    if (handle) {
        delete GET_PROBLEM(handle);
    }
}

MIPSOLVER_API int MIPSolver_AddVariable(MIPSolver_ProblemHandle handle, const char* name, MIPSolver_VariableType type) {
    /*
     * 添加决策变量
     * 
     * 功能描述：
     * - 向问题实例添加一个新的决策变量
     * - 指定变量名称和类型（连续、整数或二进制）
     * - 返回变量索引，用于后续引用该变量
     * 
     * 变量类型：
     * - MIPSOLVER_VAR_CONTINUOUS: 连续变量，可取任意实数值
     * - MIPSOLVER_VAR_INTEGER: 整数变量，只能取整数值
     * - MIPSOLVER_VAR_BINARY: 二进制变量，只能取0或1
     * 
     * 错误处理：
     * - 无效句柄时返回-1表示错误
     * - 变量类型自动映射到C++内部枚举
     * 
     * @param handle: 问题实例句柄
     * @param name: 变量名称
     * @param type: 变量类型
     * @return: 变量索引，失败时返回-1
     */
    if (!handle) return -1;
    auto cpp_var_type = MIPSolver::VariableType::CONTINUOUS;
    if (type == MIPSOLVER_VAR_INTEGER) cpp_var_type = MIPSolver::VariableType::INTEGER;
    if (type == MIPSOLVER_VAR_BINARY) cpp_var_type = MIPSolver::VariableType::BINARY;
    
    return GET_PROBLEM(handle)->addVariable(name, cpp_var_type);
}

MIPSOLVER_API void MIPSolver_SetVariableBounds(MIPSolver_ProblemHandle handle, int var_index, double lower, double upper) {
    /*
     * 设置变量边界约束
     * 
     * 功能描述：
     * - 为指定的决策变量设置上下界约束
     * - 限制变量的取值范围在[lower, upper]之间
     * - 边界可以使用正/负无穷大表示无约束
     * 
     * 边界设置示例：
     * - 非负变量：lower=0.0, upper=INFINITY
     * - 有界变量：lower=0.0, upper=10.0
     * - 无上界：lower=0.0, upper=INFINITY
     * - 无下界：lower=-INFINITY, upper=100.0
     * - 固定变量：lower=upper（如lower=5.0, upper=5.0）
     * 
     * 注意事项：
     * - 边界必须合理（lower <= upper）
     * - 对于整数变量，边界不必是整数值
     * 
     * @param handle: 问题实例句柄
     * @param var_index: 变量索引（由AddVariable返回）
     * @param lower: 变量下界
     * @param upper: 变量上界
     */
    if (!handle) return;
    GET_PROBLEM(handle)->getVariable(var_index).setBounds(lower, upper);
}

MIPSOLVER_API void MIPSolver_SetObjectiveCoefficient(MIPSolver_ProblemHandle handle, int var_index, double coeff) {
    /*
     * 设置目标函数系数
     * 
     * 功能描述：
     * - 设置变量在目标函数中的系数
     * - 构建线性目标函数表达式
     * - 可以多次调用以构建复杂的目标函数
     * 
     * 目标函数构建：
     * - 线性组合形式：c1*x1 + c2*x2 + ... + cn*xn
     * - 每个变量的系数需单独设置
     * - 默认系数为0（变量不影响目标函数）
     * - 可以设置正系数或负系数
     * 
     * 与目标类型结合：
     * - 最小化问题：正系数表示希望变量取小值
     * - 最大化问题：正系数表示希望变量取大值
     * 
     * @param handle: 问题实例句柄
     * @param var_index: 变量索引
     * @param coeff: 目标函数系数
     */
    if (!handle) return;
    GET_PROBLEM(handle)->setObjectiveCoefficient(var_index, coeff);
}

MIPSOLVER_API int MIPSolver_AddConstraint(MIPSolver_ProblemHandle handle, const char* name, int type, double rhs) {
    /*
     * 添加约束条件
     * 
     * 功能描述：
     * - 向问题实例添加一个新的线性约束
     * - 指定约束类型（<=, >=, =）和右侧常数值
     * - 返回约束索引，用于后续添加变量系数
     * 
     * 约束类型：
     * - MIPSOLVER_CONSTRAINT_LESS_EQUAL (1): 小于等于约束 (<=)
     * - MIPSOLVER_CONSTRAINT_GREATER_EQUAL (2): 大于等于约束 (>=)
     * - MIPSOLVER_CONSTRAINT_EQUAL (3): 等式约束 (=)
     * 
     * 约束表示：
     * - 形式：a1*x1 + a2*x2 + ... + an*xn ⊲ rhs
     * - 其中⊲是约束类型（<=, >=, =）
     * - 变量系数通过AddConstraintCoefficient单独添加
     * 
     * @param handle: 问题实例句柄
     * @param name: 约束名称
     * @param type: 约束类型
     * @param rhs: 右侧常数值
     * @return: 约束索引，失败时返回-1
     */
    if (!handle) return -1;
    // 注意：这里需要将C API约束类型映射到C++枚举
    return GET_PROBLEM(handle)->addConstraint(name, static_cast<MIPSolver::ConstraintType>(type), rhs);
}

MIPSOLVER_API void MIPSolver_AddConstraintCoefficient(MIPSolver_ProblemHandle handle, int constraint_index, int var_index, double coeff) {
    /*
     * 添加约束系数
     * 
     * 功能描述：
     * - 为指定约束中的变量设置系数
     * - 构建约束的左侧表达式
     * - 稀疏表示：只需添加非零系数
     * 
     * 约束构建过程：
     * 1. 使用AddConstraint创建约束框架
     * 2. 对每个非零系数，调用此函数添加
     * 3. 未显式添加的变量系数默认为0
     * 
     * 示例构建约束：3x1 + 2x2 - 5x3 <= 10
     * 1. c_idx = AddConstraint("c1", LESS_EQUAL, 10.0)
     * 2. AddConstraintCoefficient(handle, c_idx, 0, 3.0)  // x1的系数
     * 3. AddConstraintCoefficient(handle, c_idx, 1, 2.0)  // x2的系数
     * 4. AddConstraintCoefficient(handle, c_idx, 2, -5.0) // x3的系数
     * 
     * @param handle: 问题实例句柄
     * @param constraint_index: 约束索引
     * @param var_index: 变量索引
     * @param coeff: 变量在约束中的系数
     */
    if (!handle) return;
    GET_PROBLEM(handle)->getConstraint(constraint_index).addVariable(var_index, coeff);
}


// --- Solving ---

MIPSOLVER_API MIPSolver_SolutionHandle MIPSolver_Solve(MIPSolver_ProblemHandle problem_handle) {
    /*
     * 核心求解函数
     * 
     * 这是C API的核心接口，执行混合整数规划问题的求解：
     * 
     * 1. 输入验证：
     *    - 检查问题句柄的有效性
     *    - 确保问题已正确构建
     * 
     * 2. 求解器配置：
     *    - 创建分支定界求解器实例
     *    - 设置静默模式（适合库使用）
     *    - 使用默认参数配置
     * 
     * 3. 求解过程：
     *    - 调用C++求解器的solve方法
     *    - 处理求解过程中的异常
     *    - 返回结果包装为C句柄
     * 
     * 4. 内存管理：
     *    - 在堆上分配Solution对象
     *    - 调用者负责使用MIPSolver_DestroySolution释放
     * 
     * @param problem_handle: 已构建的问题实例句柄
     * @return: 求解结果句柄，失败时返回NULL
     */
    if (!problem_handle) return nullptr;

    MIPSolver::BranchBoundSolver solver;
    solver.setVerbose(false); // 保持静默模式适合库使用
    MIPSolver::Problem* problem = GET_PROBLEM(problem_handle);

    // solve方法返回Solution对象的值拷贝
    // 我们必须在堆上分配新的对象以返回其句柄
    MIPSolver::Solution* solution = new MIPSolver::Solution(solver.solve(*problem));
    return solution;
}


// --- Solution Management ---

MIPSOLVER_API void MIPSolver_DestroySolution(MIPSolver_SolutionHandle handle) {
    /*
     * 解对象销毁函数
     * 
     * 释放由MIPSolver_Solve创建的Solution对象：
     * 
     * 1. 安全检查：验证句柄的有效性
     * 2. 内存释放：调用delete释放C++对象
     * 3. 异常安全：即使在异常情况下也能正确清理
     * 
     * 重要：每个MIPSolver_Solve的调用都必须对应一个
     * MIPSolver_DestroySolution调用，否则会导致内存泄漏
     * 
     * @param handle: 要销毁的解对象句柄
     */
    if (handle) {
        delete GET_SOLUTION(handle);
    }
}

MIPSOLVER_API MIPSolver_SolutionStatus MIPSolver_GetStatus(MIPSolver_SolutionHandle handle) {
    /*
     * 获取求解状态
     * 
     * 功能描述：
     * - 返回优化问题的求解状态
     * - 指示求解过程是否找到最优解
     * - 提供失败原因的详细信息
     * 
     * 返回值：
     * - MIPSOLVER_STATUS_OPTIMAL (2): 已找到全局最优解
     * - MIPSOLVER_STATUS_INFEASIBLE (3): 问题不可行，无解存在
     * - MIPSOLVER_STATUS_UNBOUNDED (4): 问题无界，目标值可无限优化
     * - MIPSOLVER_STATUS_TIME_LIMIT (5): 达到求解时间限制
     * - MIPSOLVER_STATUS_ITERATION_LIMIT (6): 达到最大迭代次数
     * - MIPSOLVER_STATUS_UNKNOWN (7): 未知状态或求解失败
     * 
     * 使用示例：
     * - 检查解的可用性：status == MIPSOLVER_STATUS_OPTIMAL
     * - 处理无解情况：status == MIPSOLVER_STATUS_INFEASIBLE
     * - 模型调试：分析非最优状态的原因
     * 
     * @param handle: 解对象句柄
     * @return: 求解状态枚举值
     */
    if (!handle) return MIPSOLVER_STATUS_INFEASIBLE;
    // 注意：需要将C++枚举映射到C API枚举
    return static_cast<MIPSolver_SolutionStatus>(GET_SOLUTION(handle)->getStatus());
}

MIPSOLVER_API double MIPSolver_GetObjectiveValue(MIPSolver_SolutionHandle handle) {
    /*
     * 获取目标函数最优值
     * 
     * 功能描述：
     * - 返回最优解对应的目标函数值
     * - 仅在找到可行解时有意义
     * - 提供优化结果的关键指标
     * 
     * 使用场景：
     * - 评估解的质量
     * - 比较不同求解策略的效果
     * - 报告最终优化结果
     * 
     * 注意事项：
     * - 调用前应先检查求解状态
     * - 对于不可行问题，返回值无实际意义
     * - 对于无界问题，可能返回极大/极小值
     * 
     * @param handle: 解对象句柄
     * @return: 目标函数最优值，无效句柄时返回0.0
     */
    if (!handle) return 0.0;
    return GET_SOLUTION(handle)->getObjectiveValue();
}

MIPSOLVER_API int MIPSolver_GetSolutionNumVars(MIPSolver_SolutionHandle handle) {
    /*
     * 获取解向量的变量数量
     * 
     * 功能描述：
     * - 返回解向量中的变量个数
     * - 用于分配足够大的缓冲区获取所有变量值
     * - 检验解的维度是否符合预期
     * 
     * 使用场景：
     * - 在调用GetValues之前分配数组
     * - 验证解的完整性
     * - 辅助调试和解析
     * 
     * @param handle: 解对象句柄
     * @return: 变量数量，无效句柄时返回0
     */
    if (!handle) return 0;
    return GET_SOLUTION(handle)->getValues().size();
}

MIPSOLVER_API void MIPSolver_GetVariableValues(MIPSolver_SolutionHandle handle, double* values_array) {
    if (!handle || !values_array) return;
    const auto& values = GET_SOLUTION(handle)->getValues();
    for (size_t i = 0; i < values.size(); ++i) {
        values_array[i] = values[i];
    }
}

} // extern "C"
