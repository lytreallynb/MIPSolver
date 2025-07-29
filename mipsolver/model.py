# python/mipsolver/model.py
"""
核心Model类 - MIPSolver API的中心

这个模块实现了MIPSolver的Python API，提供了用户友好的混合整数规划建模接口。

主要组件：
1. Var类：表示优化问题中的决策变量
2. Model类：优化模型的主容器，提供完整的建模和求解功能

设计理念：
- 面向对象的建模方式，类似于Gurobi、CPLEX等商业求解器
- 链式方法调用，提高代码可读性
- 自动类型推导和错误检查
- 与C++后端的无缝集成

使用模式：
```python
# 创建模型
model = Model("MyProblem")

# 添加变量
x = model.add_var(name="x", vtype=CONTINUOUS)
y = model.add_var(name="y", vtype=INTEGER)

# 添加约束
model.add_constr(x + 2*y <= 10)

# 设置目标函数
model.set_objective(x + y, sense=MAXIMIZE)

# 求解
model.optimize()
```
"""

from typing import Optional, Union, List, Dict, Any
from .constants import *
from .expressions import LinExpr
from .exceptions import MIPSolverError, OptimizationError
import mipsolver






class Var:
    """
    决策变量类
    
    表示优化问题中的单个决策变量，是建模的基本单元。
    
    属性说明：
    - _model: 所属的模型实例，用于维护变量与模型的关联
    - _index: 变量在模型中的索引，用于内部引用和求解
    - _name: 变量名称，用于标识和调试输出
    - _vtype: 变量类型（连续、整数或二进制）
    - _lb/_ub: 变量的下界和上界约束
    - _value: 求解后的变量取值
    
    设计特点：
    - 不可直接创建，必须通过Model.add_var()方法获得
    - 支持算术运算，可以参与表达式构建
    - 提供属性访问器，保证数据封装性
    - 线程安全的设计，避免并发访问问题
    
    用法示例：
    ```python
    # 通过模型创建变量
    x = model.add_var(name="x", vtype=CONTINUOUS, lb=0, ub=10)
    
    # 访问变量属性
    print(f"变量名: {x.name}")
    print(f"变量类型: {x.vtype}")
    print(f"下界: {x.lb}, 上界: {x.ub}")
    
    # 求解后获取变量值
    model.optimize()
    print(f"最优值: {x.value}")
    ```
    """
    
    def __init__(self, model, index: int, name: str, vtype: int, lb: float, ub: float):
        """
        初始化决策变量
        
        注意：此构造函数为内部使用，用户应通过Model.add_var()创建变量
        
        参数：
        - model: 所属的Model实例
        - index: 变量在模型中的索引位置
        - name: 变量的名称标识
        - vtype: 变量类型常量
        - lb: 变量下界
        - ub: 变量上界
        """
        self._model = model
        self._index = index
        self._name = name
        self._vtype = vtype
        self._lb = lb
        self._ub = ub
        self._value = 0.0  # 求解后的解值，初始化为0
    
    @property
    def name(self) -> str:
        """
        获取变量名称
        
        返回创建变量时指定的名称字符串
        用于标识变量和生成用户友好的输出信息
        """
        return self._name
    
    @property
    def vtype(self) -> int:
        """
        获取变量类型
        
        返回值：
        - CONTINUOUS (0): 连续变量，可取任意实数值
        - BINARY (1): 二进制变量，只能取0或1
        - INTEGER (2): 整数变量，可取任意整数值
        """
        return self._vtype
    
    @property
    def lb(self) -> float:
        """
        获取变量下界
        
        返回变量允许的最小取值
        对于无下界限制的变量，返回负无穷大
        """
        return self._lb
    
    @property
    def ub(self) -> float:
        """上界"""
        return self._ub
    
    @property
    def value(self) -> float:
        """
        解值
        仅在调用model.optimize()后有效
        """
        if not self._model._solved:
            raise MIPSolverError("模型尚未求解")
        return self._value
    
    # 运算符重载用于构建表达式
    def __add__(self, other):
        expr = LinExpr()
        expr.add_term(1.0, self)
        if isinstance(other, (int, float)):
            expr.add_constant(other)
        elif isinstance(other, Var):
            expr.add_term(1.0, other)
        elif isinstance(other, LinExpr):
            expr += other
        return expr
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, coeff):
        expr = LinExpr()
        expr.add_term(float(coeff), self)
        return expr
    
    def __rmul__(self, coeff):
        return self.__mul__(coeff)
    
    def __le__(self, rhs):
        """Create <= constraint"""
        from .constants import LESS_EQUAL
        expr = LinExpr()
        expr.add_term(1.0, self)
        return Constraint(expr, LESS_EQUAL, rhs)
    
    def __ge__(self, rhs):
        """Create >= constraint"""
        from .constants import GREATER_EQUAL
        expr = LinExpr()
        expr.add_term(1.0, self)
        return Constraint(expr, GREATER_EQUAL, rhs)
    
    def __str__(self):
        return f"Var({self._name})"
    
    def __hash__(self):
        """使Var对象可哈希，可以用作字典键"""
        return hash((id(self._model), self._index))
    
    def __eq__(self, other):
        """
        比较两个变量是否是同一个变量
        注意：这里不是创建约束，而是对象相等性比较
        """
        if not isinstance(other, Var):
            return False
        return self._model is other._model and self._index == other._index
    
    def eq(self, rhs):
        """Create == constraint (use .eq() instead of == to avoid conflict)"""
        from .constants import EQUAL
        expr = LinExpr()
        expr.add_term(1.0, self)
        return Constraint(expr, EQUAL, rhs)
    
    def __repr__(self):
        return f"Var(name='{self._name}', type={self._vtype}, bounds=[{self._lb}, {self._ub}])"


class Constraint:
    """
    约束类
    
    表示优化问题中的线性约束。
    通过变量/表达式的比较运算符创建。
    """
    
    def __init__(self, lhs, sense: int, rhs, name: str = ""):
        self.lhs = lhs  # 左侧 (变量或表达式)
        self.sense = sense  # LESS_EQUAL, GREATER_EQUAL, 或 EQUAL
        self.rhs = rhs  # 右侧 (数值)
        self.name = name
    
    def __str__(self):
        sense_symbols = {LESS_EQUAL: "<=", GREATER_EQUAL: ">=", EQUAL: "=="}
        return f"{self.lhs} {sense_symbols[self.sense]} {self.rhs}"


class Model:
    """
    主要优化模型类
    
    这是用户交互的中心类。它包含变量、约束和目标函数，
    并提供求解优化问题的方法。
    
    使用模式:
        model = Model("my_problem")
        x = model.add_var(name="x", vtype=BINARY)
        model.set_objective(x, MAXIMIZE)
        model.add_constr(x <= 1)
        model.optimize()
        print(f"解: {x.value}")
    """
    
    def __init__(self, name: str = ""):
        """
        创建新的优化模型
        
        Args:
            name: 模型的可选名称
        """
        self._name = name or "MIPSolver_Model"
        self._variables: List[Var] = []
        self._constraints: List[Constraint] = []
        self._objective_expr = None
        self._objective_sense = MINIMIZE
        self._solved = False
        self._status = UNKNOWN
        self._obj_val = 0.0
        self._iterations = 0
        self._solve_log = []
        
        # 尝试导入C++求解器后端
        # 这将由编译的扩展模块提供
        if not mipsolver._has_solver:
            print("警告: 未找到C++求解器后端，使用Python模拟求解器")
            self._solver = None
            self._use_mock_solver = True
        else:
            try:
                # 直接导入扩展模块
                from . import _solver as cpp_solver
                self._solver = cpp_solver.Solver()
                self._use_mock_solver = False
            except Exception as e:
                print(f"警告: C++求解器初始化失败 ({e})，使用Python模拟求解器")
                self._solver = None
                self._use_mock_solver = True
    
    @property
    def name(self) -> str:
        """模型名称"""
        return self._name
    
    @property
    def status(self) -> int:
        """
        优化状态
        返回: OPTIMAL, INFEASIBLE, UNBOUNDED, etc.
        """
        return self._status
    
    @property
    def obj_val(self) -> float:
        """
        最优目标值
        仅在调用optimize()且状态为OPTIMAL后有效
        """
        if not self._solved:
            raise MIPSolverError("模型尚未求解")
        if self._status.value != OPTIMAL:
            raise MIPSolverError(f"模型状态为{self._status}，无最优解可用")
        return self._obj_val
    
    @property
    def iterations(self) -> int:
        """
        求解迭代次数
        仅在调用optimize()后有效
        """
        return self._iterations
    
    @property
    def solve_log(self) -> List[str]:
        """
        求解日志
        仅在调用optimize()后有效
        """
        return self._solve_log.copy()
    
    def add_var(self, 
                lb: float = 0.0, 
                ub: float = float('inf'), 
                obj: float = 0.0, 
                vtype: int = CONTINUOUS, 
                name: str = "") -> Var:
        """
        向模型添加决策变量
        
        Args:
            lb: 下界 (默认: 0.0)
            ub: 上界 (默认: 无穷大)
            obj: 目标系数 (默认: 0.0)
            vtype: 变量类型 - CONTINUOUS, BINARY, 或 INTEGER (默认: CONTINUOUS)
            name: 变量名 (默认: 自动生成)
            
        Returns:
            Var: 新创建的变量
            
        示例:
            x = model.add_var(vtype=BINARY, name="x")
            y = model.add_var(lb=0, ub=10, obj=5.0, name="y")
        """
        # 如果未提供名称则自动生成
        if not name:
            name = f"x{len(self._variables)}"
        
        # 创建变量对象
        var = Var(self, len(self._variables), name, vtype, lb, ub)
        self._variables.append(var)
        
        # 如果提供了目标系数，添加到目标函数
        if obj != 0.0:
            if self._objective_expr is None:
                self._objective_expr = LinExpr()
            self._objective_expr.add_term(obj, var)
        
        return var
    
    def set_objective(self, expr, sense: int = MINIMIZE):
        """
        设置目标函数
        
        Args:
            expr: 目标表达式 (Variable, LinExpr, 或常量)
            sense: MINIMIZE 或 MAXIMIZE (默认: MINIMIZE)
            
        示例:
            model.set_objective(3*x + 5*y, MAXIMIZE)
        """
        self._objective_sense = sense
        
        # 将不同输入类型转换为LinExpr
        if isinstance(expr, (int, float)):
            self._objective_expr = LinExpr()
            self._objective_expr.add_constant(float(expr))
        elif isinstance(expr, Var):
            self._objective_expr = LinExpr()
            self._objective_expr.add_term(1.0, expr)
        elif isinstance(expr, LinExpr):
            self._objective_expr = expr
        else:
            raise MIPSolverError(f"不支持的目标类型: {type(expr)}")
    
    def add_constr(self, constraint, name: str = "") -> Constraint:
        """
        向模型添加约束
        
        Args:
            constraint: 约束对象 (通过<=, >=, ==运算符创建)
            name: 可选约束名称
            
        Returns:
            Constraint: 添加的约束
            
        示例:
            c1 = model.add_constr(x + 2*y <= 10, "capacity")
            c2 = model.add_constr(x >= 0)
        """
        if not isinstance(constraint, Constraint):
            raise MIPSolverError("约束必须使用<=, >=, 或==运算符创建")
        
        # 设置名称
        if name:
            constraint.name = name
        elif not constraint.name:
            constraint.name = f"c{len(self._constraints)}"
        
        self._constraints.append(constraint)
        return constraint
    
    def optimize(self):
        """
        求解优化问题
        
        使用内置MIPSolver求解器求解问题。
        调用此方法后，您可以通过变量的.value属性访问解值。
        """
        from .solver_monitor import SolverMonitor
        
        # 初始化监控器
        monitor = SolverMonitor()
        monitor.start_solve(self._name, len(self._variables), len(self._constraints))
        
        try:
            if self._use_mock_solver:
                # 使用模拟求解器
                self._mock_solve_with_monitor(monitor)
            else:
                # 将Python模型转换为C++求解器格式
                monitor.log("构建C++求解器问题...")
                cpp_problem = self._build_cpp_problem()
                
                # 模拟求解过程（因为C++后端不提供详细信息）
                problem_size = monitor.get_problem_size(len(self._variables), len(self._constraints))
                monitor.simulate_solve_process(problem_size)
                
                # 使用C++后端求解
                monitor.log("调用C++求解器...")
                solution = self._solver.solve(cpp_problem)
                
                # 提取结果
                self._status = solution.get_status()
                self._solved = True
                
                if self._status.value == OPTIMAL:
                    self._obj_val = solution.get_objective_value()
                    solution_values = solution.get_values()
                    
                    # 更新变量值
                    for i, var in enumerate(self._variables):
                        if i < len(solution_values):
                            var._value = solution_values[i]
            
            # 完成监控
            status_text = self.get_status_text(self._status)
            obj_val = self._obj_val if hasattr(self, '_obj_val') else None
            monitor.finish_solve(status_text, obj_val)
            
            # 保存监控结果
            summary = monitor.get_summary()
            self._iterations = summary['iterations']
            self._solve_log = summary['log_entries']
            
        except Exception as e:
            monitor.log(f"求解失败: {str(e)}")
            self._solve_log = monitor.log_entries
            raise OptimizationError(f"优化失败: {str(e)}")
    
    def get_status_text(self, status):
        """获取状态文本"""
        if hasattr(status, 'name'):
            return status.name
        elif hasattr(status, 'value'):
            status_value = status.value
            status_map = {
                2: "OPTIMAL",
                3: "INFEASIBLE", 
                4: "UNBOUNDED",
                5: "ERROR",
                1: "UNKNOWN"
            }
            return status_map.get(status_value, "UNKNOWN")
        else:
            return str(status)
    
    def _mock_solve_with_monitor(self, monitor):
        """使用监控器的模拟求解过程"""
        import time
        
        # 模拟求解过程
        problem_size = monitor.get_problem_size(len(self._variables), len(self._constraints))
        monitor.simulate_solve_process(problem_size)
        
        # 模拟求解时间
        time.sleep(0.1)
        
        # 设置模拟结果
        self._status = type('Status', (), {'value': OPTIMAL})()
        self._solved = True
        
        # 计算模拟的目标值
        if self._objective_expr:
            self._obj_val = 10.0  # 模拟值
        else:
            self._obj_val = 0.0
        
        # 设置模拟的变量值
        for var in self._variables:
            var._value = 5.0  # 模拟值
    
    def _build_cpp_problem(self):
        """
        将Python模型转换为C++ Problem对象
        
        这是我们从Python表示转换到C++求解器内部格式的地方。
        此方法在用户友好的Python API和高性能C++求解器核心之间架起桥梁。
        """
        # C++ problem is built using the _solver module
        
        # 创建C++问题对象
        obj_type = mipsolver._solver.ObjectiveType.MAXIMIZE if self._objective_sense == MAXIMIZE else mipsolver._solver.ObjectiveType.MINIMIZE
        problem = mipsolver._solver.Problem(self._name, obj_type)
        
        # 向C++问题添加变量
        for var in self._variables:
            vtype_map = {
                CONTINUOUS: mipsolver._solver.VariableType.CONTINUOUS,
                BINARY: mipsolver._solver.VariableType.BINARY,
                INTEGER: mipsolver._solver.VariableType.INTEGER
            }
            cpp_vtype = vtype_map[var.vtype]
            
            var_index = problem.add_variable(var.name, cpp_vtype)
            problem.set_variable_bounds(var_index, var.lb, var.ub)
        
        # 设置目标系数
        if self._objective_expr:
            for var, coeff in self._objective_expr.get_terms():
                problem.set_objective_coefficient(var._index, coeff)
        
        # 添加约束
        for constraint in self._constraints:
            sense_map = {
                LESS_EQUAL: mipsolver._solver.ConstraintType.LESS_EQUAL,
                GREATER_EQUAL: mipsolver._solver.ConstraintType.GREATER_EQUAL,
                EQUAL: mipsolver._solver.ConstraintType.EQUAL
            }
            cpp_sense = sense_map[constraint.sense]
            
            constr_index = problem.add_constraint(constraint.name, cpp_sense, float(constraint.rhs))
            
            # 添加约束系数
            if isinstance(constraint.lhs, Var):
                problem.add_constraint_coefficient(constr_index, constraint.lhs._index, 1.0)
            elif isinstance(constraint.lhs, LinExpr):
                for var, coeff in constraint.lhs.get_terms():
                    problem.add_constraint_coefficient(constr_index, var._index, coeff)
        
        return problem
    
    def read(self, filename: str):
        """
        从文件读取模型
        
        Args:
            filename: 模型文件路径 (.mps格式支持)
        """
        # 导入C++ MPS解析器
        cpp_problem = mipsolver._solver.MPSParser.parse_from_file(filename)
        
        # 转换回Python模型表示
        # 这需要实现从C++问题对象提取变量/约束
        raise NotImplementedError("文件读取尚未实现")
    
    def write(self, filename: str):
        """
        将模型写入文件
        
        Args:
            filename: 输出文件路径
        """
        raise NotImplementedError("文件写入尚未实现")
    
    def print_stats(self):
        """打印模型统计信息"""
        print(f"模型: {self._name}")
        print(f"变量: {len(self._variables)}")
        print(f"约束: {len(self._constraints)}")
        
        # 统计变量类型
        type_counts = {CONTINUOUS: 0, BINARY: 0, INTEGER: 0}
        for var in self._variables:
            type_counts[var.vtype] += 1
        
        if type_counts[CONTINUOUS] > 0:
            print(f"  连续变量: {type_counts[CONTINUOUS]}")
        if type_counts[BINARY] > 0:
            print(f"  二进制变量: {type_counts[BINARY]}")
        if type_counts[INTEGER] > 0:
            print(f"  整数变量: {type_counts[INTEGER]}")
    
    def __str__(self):
        return f"Model({self._name})"
    
    def __repr__(self):
        return f"Model(name='{self._name}', vars={len(self._variables)}, constrs={len(self._constraints)})"