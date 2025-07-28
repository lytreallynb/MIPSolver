"""
MIPSolver - 混合整数规划求解器

现代化的Python优化库，提供简洁统一的API。
支持C++高性能求解器和Python fallback。
"""

__version__ = "1.0.9"
__author__ = "lytreallynb"
__email__ = "lytreallynb@example.com"

import warnings
import sys
import os

# 尝试导入C++求解器后端
_has_solver = False
_solver = None

def _import_solver():
    """延迟导入C++求解器，避免循环导入问题"""
    global _solver, _has_solver
    
    if _solver is not None:
        return _solver
        
    try:
        # 使用绝对导入避免相对导入的问题
        import mipsolver._solver as solver_module
        _solver = solver_module
        _has_solver = True
        print("MIPSolver: Using high-performance C++ solver backend")
        return _solver
    except ImportError as e:
        _has_solver = False
        print(f"MIPSolver: C++ solver not available ({e})")
        print("MIPSolver: Using Python fallback (limited functionality)")
        return None

# 立即尝试导入
_import_solver()

# 如果没有C++求解器，创建fallback实现
if not _has_solver:
    # 创建fallback实现
    class MockSolution:
        def __init__(self):
            self.status = type('Status', (), {'OPTIMAL': 2})()
            
        def get_status(self):
            return self.status.OPTIMAL
            
        def get_objective_value(self):
            return 0.0
            
        def get_values(self):
            return [0.0, 0.0]
    
    class MockSolver:
        def __init__(self):
            pass
            
        def set_verbose(self, verbose):
            pass
            
        def solve(self, problem):
            warnings.warn(
                "Using Python fallback solver with limited functionality. "
                "For full performance, install platform-specific wheels or build tools.",
                UserWarning
            )
            return MockSolution()
    
    class MockProblem:
        def __init__(self, name, obj_type):
            self.name = name
            self.obj_type = obj_type
            self.var_count = 0
            
        def add_variable(self, name, vtype):
            idx = self.var_count
            self.var_count += 1
            return idx
            
        def set_objective_coefficient(self, var_idx, coeff):
            pass
            
        def add_constraint(self, name, ctype, rhs):
            return 0
            
        def add_constraint_coefficient(self, c_idx, v_idx, coeff):
            pass
            
        def set_variable_bounds(self, var_idx, lb, ub):
            pass
    
    # 创建mock模块覆盖_solver变量
    class _solver:
        Solver = MockSolver
        Problem = MockProblem
        
        class VariableType:
            CONTINUOUS = 0
            BINARY = 1
            INTEGER = 2
            
        class ObjectiveType:
            MINIMIZE = 1
            MAXIMIZE = -1
            
        class ConstraintType:
            LESS_EQUAL = 1
            GREATER_EQUAL = 2
            EQUAL = 3
            
        class SolutionStatus:
            OPTIMAL = 2
            INFEASIBLE = 3

# 导入常量
from .constants import *

# 导入异常类
from .exceptions import *

# 导入核心类
from .model import Model

# 导入表达式类
from .expressions import *

# 便利导入
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    '__email__',
    
    # 核心类
    'Model',
    
    # 变量类型常量
    'CONTINUOUS',
    'INTEGER', 
    'BINARY',
    
    # 目标类型常量
    'MAXIMIZE',
    'MINIMIZE',
    
    # 约束类型常量
    'LESS_EQUAL',
    'GREATER_EQUAL',
    'EQUAL',
    
    # 求解状态常量
    'OPTIMAL',
    'INFEASIBLE',
    'UNBOUNDED',
    'ERROR',
]

# 安装提示函数
def install_cpp_solver():
    """
    提供安装C++求解器的指导
    """
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

# 如果没有C++求解器，显示帮助信息
if not _has_solver:
    def _show_install_help():
        print("\n" + "="*60)
        print("MIPSolver: Enhanced functionality requires C++ solver")
        print("="*60)
        print("Current mode: Python fallback (basic functionality only)")
        print("For full performance, run: mipsolver.install_cpp_solver()")
        print("="*60 + "\n")
    
    # 延迟显示，避免导入时的噪音
    import atexit
    atexit.register(lambda: None)  # 可以在需要时启用帮助信息