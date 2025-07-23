#include "core.h"
#include "parser.h"
#include "solution.h"
#include "simplex_solver.h"
#include "branch_bound_solver.h"
#include <iostream>
#include <string>

using namespace MIPSolver;

int main(int argc, char* argv[]) {
    std::string filename;
    
    // 检查命令行参数
    if (argc > 1) {
        filename = argv[1];
        std::cout << "使用文件: " << filename << std::endl;
    } else {
        std::cout << "用法: " << argv[0] << " <mps_file>" << std::endl;
        std::cout << "例如: " << argv[0] << " data/bk4x3.mps" << std::endl;
        return 1;
    }
    
    try {
        std::cout << "\n------- 解析MPS文件: " << filename << " -------" << std::endl;
        Problem mps_problem = MPSParser::parseFromFile(filename);

        // 显示问题统计信息
        mps_problem.printStatistics();

        // 创建求解器
        BranchBoundSolver mps_solver;
        mps_solver.setVerbose(true);
        mps_solver.setIterationLimit(5000);

        // 求解
        std::cout << "\n------- 开始求解 -------" << std::endl;
        Solution mps_solution = mps_solver.solve(mps_problem);
        
        // 显示结果
        std::cout << "\n------- 求解完成 -------" << std::endl;
        mps_solution.print();
        
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        std::cerr << "请确保文件存在且格式正确。" << std::endl;
        return 1;
    }
    
    return 0;
}