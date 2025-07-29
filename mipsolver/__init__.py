"""
MIPSolver - 混合整数规划求解器

这是MIPSolver Python包的初始化文件，负责：

1. 包信息定义：版本号、作者信息等元数据
2. C++求解器后端导入：尝试加载高性能的C++实现
3. 后备模式处理：当C++模块不可用时提供Python后备实现
4. 模块接口统一：确保API在不同后端下保持一致

架构设计：
- 优先使用C++后端（_solver模块）获得最佳性能
- C++模块不可用时自动切换到Python模拟实现
- 对用户代码透明，无需修改即可在不同环境下运行

性能考虑：
- C++后端：适用于大规模优化问题，提供工业级性能
- Python后备：用于开发测试环境，功能受限但保证兼容性
"""
__version__ = "1.0.5"
__author__ = "lytreallynb"
__email__ = "lytreallynb@example.com"

import warnings

# 求解器后端可用性标志 - 只在这里初始化，不要在try外部赋值None
_has_solver = False

try:
    # 尝试导入C++编译的求解器后端
    # 这个模块通过pybind11从C++代码生成，包含高性能的求解算法
    from . import _solver
    _has_solver = True
    print("MIPSolver: Using high-performance C++ solver backend")
    
except ImportError as e:
    # C++模块导入失败时的后备处理
    # 这种情况通常发生在：
    # 1. C++模块未正确编译
    # 2. 缺少必要的动态链接库
    # 3. 平台不兼容
    _solver = None
    print(f"MIPSolver: C++ solver not available ({e})")
    print("MIPSolver: Using Python fallback (limited functionality)")

    # 创建Python后备实现
    # 这些类提供与C++版本相同的接口，但功能和性能有限
    # 主要用于开发测试和保证基本兼容性
    
    class MockSolution:
        """
        模拟解决方案类 - C++求解器不可用时的后备实现
        
        提供基本的解状态和结果访问接口，但不执行实际求解
        主要用于保证代码在缺少C++后端时不会崩溃
        """
        def __init__(self):
            # 创建模拟的状态对象
            self.status = type('Status', (), {'OPTIMAL': 2})()
        
        def get_status(self):
            """返回模拟的最优解状态"""
            return self.status.OPTIMAL
        
        def get_objective_value(self):
            """返回模拟的目标函数值"""
            return 0.0
        
        def get_values(self):
            """返回模拟的变量值"""
            return [0.0, 0.0]

    class MockSolver:
        """
        模拟求解器类 - C++求解器不可用时的后备实现
        
        提供与真实求解器相同的接口，但不执行实际的优化算法
        所有求解调用都返回虚拟结果，并发出警告信息
        """
        def __init__(self): 
            pass
        
        def set_verbose(self, verbose): 
            """设置详细输出模式（模拟实现，无实际效果）"""
            pass
        
        def solve(self, problem):
            """
            执行问题求解（模拟实现）
            
            不执行实际的优化算法，直接返回模拟结果
            发出警告提醒用户当前使用的是受限功能版本
            """
            warnings.warn(
                "Using Python fallback solver with limited functionality. "
                "For full performance, install platform-specific wheels or build tools.",
                UserWarning
            )
            return MockSolution()

    class MockProblem:
        """
        模拟问题类 - 用于在C++后端不可用时保持接口兼容性
        
        提供问题建模的基本接口，但不执行实际的数据存储和处理
        主要用于保证用户代码在不同环境下的语法兼容性
        """
        def __init__(self, name, obj_type):
            self.name = name
            self.obj_type = obj_type
            self.var_count = 0
        
        def add_variable(self, name, vtype):
            """添加决策变量（模拟实现）"""
            idx = self.var_count
            self.var_count += 1
            return idx
        
        def set_objective_coefficient(self, var_idx, coeff): 
            """设置目标函数系数（模拟实现）"""
            pass
        
        def add_constraint(self, name, ctype, rhs): 
            """添加约束条件（模拟实现）"""
            return 0
        
        def add_constraint_coefficient(self, c_idx, v_idx, coeff): 
            """设置约束系数（模拟实现）"""
            pass
        
        def set_variable_bounds(self, var_idx, lb, ub): 
            """设置变量边界（模拟实现）"""
            pass

    class MockSolverModule:
        """
        模拟求解器模块 - 包装所有模拟类和常量
        
        这个类模拟C++模块的完整接口，包括：
        - 求解器和问题类
        - 变量类型常量
        - 目标函数类型常量  
        - 约束类型常量
        - 解状态常量
        
        确保Python后备模式下的API完全兼容
        """
        Solver = MockSolver
        Problem = MockProblem
        
        class VariableType:
            """变量类型常量定义"""
            CONTINUOUS = 0  # 连续变量
            BINARY = 1      # 二进制变量（0或1）
            INTEGER = 2     # 整数变量
        
        class ObjectiveType:
            """目标函数类型常量定义"""
            MINIMIZE = 1    # 最小化目标
            MAXIMIZE = -1   # 最大化目标
        
        class ConstraintType:
            """约束类型常量定义"""
            LESS_EQUAL = 1      # 小于等于约束（<=）
            GREATER_EQUAL = 2   # 大于等于约束（>=）
            EQUAL = 3           # 等式约束（=）
        
        class SolutionStatus:
            """求解状态常量定义"""
            OPTIMAL = 2      # 找到最优解
            INFEASIBLE = 3   # 问题不可行

    # 将模拟模块赋值给_solver，保持接口一致性
    _solver = MockSolverModule()

# 导入常量
try:
    from .constants import *
except ImportError as e:
    print(f"Warning: Could not import constants: {e}")
    # Define fallback constants if constants.py doesn't exist
    CONTINUOUS = 0
    BINARY = 1  
    INTEGER = 2
    MINIMIZE = 1
    MAXIMIZE = -1
    LESS_EQUAL = 1
    GREATER_EQUAL = 2
    EQUAL = 3
    OPTIMAL = 2
    INFEASIBLE = 3
    UNBOUNDED = 4
    ERROR = 5

# 导入异常类
try:
    from .exceptions import *
except ImportError as e:
    print(f"Warning: Could not import exceptions: {e}")
    # Define fallback exceptions
    class SolverError(Exception):
        pass
    class OptimizationError(SolverError):
        pass

# 导入核心类
try:
    from .model import Model
except ImportError as e:
    print(f"Warning: Could not import Model: {e}")
    # Define a minimal fallback Model class
    class Model:
        def __init__(self, name="model"):
            self.name = name
            print("Warning: Using fallback Model class with limited functionality")

# 导入表达式类
try:
    from .expressions import *
except ImportError as e:
    print(f"Warning: Could not import expressions: {e}")

# Define __all__ after all imports to ensure all items exist
__all__ = [
    '__version__', '__author__', '__email__',
    'Model',
    'CONTINUOUS', 'INTEGER', 'BINARY',
    'MAXIMIZE', 'MINIMIZE', 
    'LESS_EQUAL', 'GREATER_EQUAL', 'EQUAL',
    'OPTIMAL', 'INFEASIBLE', 'UNBOUNDED', 'ERROR',
    '_solver', '_has_solver',
]

def install_cpp_solver():
    """Print installation instructions for the C++ solver backend."""
    print("""
To install the high-performance C++ solver:

1. For Windows:
   - Install Visual Studio Build Tools 2022
   - pip install --upgrade mipsolver --force-reinstall

2. For Linux:
   - sudo apt-get install build-essential cmake
   - pip install --upgrade mipsolver --force-reinstall

3. For macOS:
   - Install Xcode Command Line Tools: xcode-select --install
   - pip install --upgrade mipsolver --force-reinstall

4. Or use conda:
   - conda install -c conda-forge mipsolver

For more help: https://github.com/lytreallynb/MIPSolver
""")