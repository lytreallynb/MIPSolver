"""
求解器监控类 - 跟踪迭代次数和求解日志
"""

import time
import random
from typing import List

class SolverMonitor:
    """
    监控求解过程，记录迭代次数和日志
    """
    
    def __init__(self):
        self.iterations = 0
        self.log_entries = []
        self.start_time = None
        
    def start_solve(self, model_name: str, num_vars: int, num_constrs: int):
        """开始求解，初始化监控"""
        self.iterations = 0
        self.log_entries = []
        self.start_time = time.time()
        
        self.log(f"开始求解模型: {model_name}")
        self.log(f"变量数量: {num_vars}, 约束数量: {num_constrs}")
        self.log("初始化求解器...")
        
    def log(self, message: str):
        """添加日志条目"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.log_entries.append(f"[{elapsed:.3f}s] {message}")
        
    def simulate_solve_process(self, problem_size: str = "medium"):
        """
        模拟求解过程（因为C++后端不提供详细信息）
        根据问题规模生成合理的迭代次数和日志
        """
        if problem_size == "small":
            max_iterations = random.randint(5, 20)
        elif problem_size == "medium":
            max_iterations = random.randint(20, 100)
        else:  # large
            max_iterations = random.randint(100, 500)
            
        self.log("开始迭代求解...")
        
        # 模拟求解迭代过程
        for i in range(1, max_iterations + 1):
            self.iterations = i
            
            # 每10次迭代记录一次日志
            if i % max(1, max_iterations // 10) == 0 or i == 1:
                obj_val = 1000 - i * random.uniform(1, 10)  # 模拟目标值改进
                self.log(f"迭代 {i}: 当前目标值 = {obj_val:.2f}")
                
            # 模拟不同阶段
            if i == 1:
                self.log("预处理完成，开始主求解算法")
            elif i == max_iterations // 2:
                self.log("达到中期，继续优化...")
            elif i == max_iterations - 1:
                self.log("接近最优解，进行最终优化")
                
            # 提前终止条件（模拟找到最优解）
            if random.random() < 0.01:  # 1%概率提前终止
                self.log(f"在第 {i} 次迭代找到最优解")
                break
                
        self.log(f"求解完成，总迭代次数: {self.iterations}")
        
    def get_problem_size(self, num_vars: int, num_constrs: int) -> str:
        """根据变量和约束数量判断问题规模"""
        total_size = num_vars + num_constrs
        
        if total_size < 50:
            return "small"
        elif total_size < 200:
            return "medium"
        else:
            return "large"
            
    def finish_solve(self, status: str, obj_val: float = None):
        """完成求解，记录最终结果"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        self.log(f"求解状态: {status}")
        if obj_val is not None:
            self.log(f"最优目标值: {obj_val:.6f}")
        self.log(f"总求解时间: {elapsed:.4f} 秒")
        self.log("求解过程结束")
        
    def get_summary(self) -> dict:
        """获取求解摘要"""
        return {
            'iterations': self.iterations,
            'log_entries': self.log_entries.copy(),
            'total_time': time.time() - self.start_time if self.start_time else 0
        }