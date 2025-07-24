"""
MIPSolver - 混合整数规划求解器

现代化的Python优化库，提供简洁统一的API。

基本用法:
    import mipsolver as mp
    
    # 创建模型
    model = mp.Model("example")
    
    # 添加变量
    x = model.add_var(vtype=mp.BINARY, name="x")
    y = model.add_var(vtype=mp.BINARY, name="y")
    
    # 设置目标函数
    model.set_objective(5*x + 8*y, mp.MAXIMIZE)
    
    # 添加约束
    model.add_constr(2*x + 4*y <= 10, "capacity")
    
    # 求解
    model.optimize()
    
    # 获取结果
    print(f"最优值: {model.obj_val}")
    print(f"x = {x.value}, y = {y.value}")
"""

__version__ = "1.0.0"
__author__ = "lytreallynb"
__email__ = "lytreallynb@example.com"

# 导入常量
from .constants import *

# 导入异常类
from .exceptions import *

# 导入核心类
from .model import Model

# 导入表达式类
from .expressions import *

# 尝试导入C++求解器后端
try:
    from ._solver import *
    _has_solver = True
except ImportError as e:
    _has_solver = False
    import warnings
    warnings.warn(
        f"C++ solver backend not available: {e}. "
        "Some functionality may be limited.",
        ImportWarning
    )

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
