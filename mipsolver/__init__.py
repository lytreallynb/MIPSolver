"""
MIPSolver - 混合整数规划求解器
"""
__version__ = "1.0.5"
__author__ = "lytreallynb"
__email__ = "lytreallynb@example.com"

import warnings

# 只在这里初始化，不要在try外部赋值None
_has_solver = False

try:
    from . import _solver
    _has_solver = True
    print("MIPSolver: Using high-performance C++ solver backend")
    
except ImportError as e:
    _solver = None
    print(f"MIPSolver: C++ solver not available ({e})")
    print("MIPSolver: Using Python fallback (limited functionality)")

    # fallback实现
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

    class MockSolverModule:
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