#!/usr/bin/env python3
"""
MIPSolver 交互式求解器
"""
import sys
import os
import json
import argparse
from pathlib import Path

try:
    import mipsolver as mp
    print("MIPSolver导入成功")
except ImportError as e:
    print(f"MIPSolver导入失败: {e}")
    sys.exit(1)

class InteractiveSolver:
    def __init__(self):
        self.model = None
        self.variables = {}
        self.constraints = {}
        
    def display_banner(self):
        print("=" * 60)
        print("        MIPSolver 交互式求解器")
        print("=" * 60)
        
    def show_help(self):
        print("""
可用命令:
  new <name>               - 创建新模型
  add_var <name> <type>    - 添加变量 (continuous/binary/integer)
  set_objective <expr> <sense> - 设置目标函数 (maximize/minimize)
  add_constraint <expr>    - 添加约束 (如: x + y <= 10)
  solve                    - 求解模型
  load <filename>          - 从文件加载模型 (.mps格式)
  status                   - 显示模型状态  
  example                  - 运行示例问题
  help                     - 显示帮助
  quit/exit               - 退出

示例:
  > new my_problem  
  > add_var x integer
  > add_var y integer
  > set_objective x + 2*y maximize
  > add_constraint x + y <= 10
  > solve
        """)
        
    def create_model(self, name="model"):
        self.model = mp.Model(name)
        self.variables = {}
        self.constraints = {}
        print(f"创建模型: {name}")
        
    def add_variable(self, name, vtype="continuous"):
        if not self.model:
            print("请先创建模型")
            return
            
        type_map = {
            'continuous': mp.CONTINUOUS,
            'integer': mp.INTEGER, 
            'binary': mp.BINARY
        }
        
        if vtype.lower() not in type_map:
            print(f"未知变量类型: {vtype}")
            return
            
        var = self.model.add_var(name=name, vtype=type_map[vtype.lower()], lb=0)
        self.variables[name] = var
        print(f"添加变量: {name} ({vtype})")
        
    def parse_expression(self, expr_str):
        """简单的表达式解析"""
        expr_str = expr_str.replace(' ', '')
        expr = None
        
        # 分割项
        terms = expr_str.replace('-', '+-').split('+')
        
        for term in terms:
            if not term:
                continue
                
            if term.replace('-', '').isdigit():
                # 常数项
                const = float(term)
                if expr is None:
                    expr = const
                else:
                    expr += const
            elif '*' in term:
                # 系数*变量
                parts = term.split('*')
                coeff = float(parts[0])
                var_name = parts[1]
                if var_name in self.variables:
                    if expr is None:
                        expr = coeff * self.variables[var_name]
                    else:
                        expr += coeff * self.variables[var_name]
                else:
                    print(f"未定义变量: {var_name}")
                    return None
            else:
                # 单个变量
                var_name = term.replace('-', '') if term.startswith('-') else term
                coeff = -1 if term.startswith('-') else 1
                if var_name in self.variables:
                    if expr is None:
                        expr = coeff * self.variables[var_name]
                    else:
                        expr += coeff * self.variables[var_name]
                else:
                    print(f"未定义变量: {var_name}")
                    return None
                    
        return expr
        
    def set_objective(self, expr_str, sense="minimize"):
        if not self.model:
            print("请先创建模型")
            return
            
        obj_sense = mp.MAXIMIZE if sense.lower() in ['max', 'maximize'] else mp.MINIMIZE
        expr = self.parse_expression(expr_str)
        
        if expr is not None:
            self.model.set_objective(expr, obj_sense)
            print(f"设置目标: {sense} {expr_str}")
            
    def add_constraint(self, constraint_str):
        if not self.model:
            print("请先创建模型")
            return
            
        for op in ['<=', '>=', '==']:
            if op in constraint_str:
                lhs_str, rhs_str = constraint_str.split(op)
                lhs = self.parse_expression(lhs_str.strip())
                rhs = float(rhs_str.strip())
                
                if lhs is not None:
                    if op == '<=':
                        constraint = lhs <= rhs
                    elif op == '>=':
                        constraint = lhs >= rhs
                    else:
                        constraint = lhs == rhs
                        
                    self.model.add_constr(constraint)
                    print(f"添加约束: {constraint_str}")
                return
                
        print(f"无效约束格式: {constraint_str}")
        
    def solve_model(self):
        if not self.model:
            print("请先创建模型")
            return
            
        print("开始求解...")
        try:
            self.model.optimize()
            
            print("\n" + "="*50)
            print("求解结果:")
            print("="*50)
            
            if hasattr(self.model, 'status') and self.model.status == mp.OPTIMAL:
                print("状态: 最优解")
                print(f"目标值: {self.model.obj_val:.6f}")
                print("\n变量值:")
                for name, var in self.variables.items():
                    print(f"  {name} = {var.value:.6f}")
            else:
                print(f"状态: {getattr(self.model, 'status', 'UNKNOWN')}")
                
        except Exception as e:
            print(f"求解失败: {e}")
            
    def load_mps_file(self, filename):
        """加载MPS文件"""
        if not os.path.exists(filename):
            print(f"文件不存在: {filename}")
            return
            
        print(f"加载MPS文件: {filename}")
        print("(MPS解析功能开发中...)")
        
    def show_status(self):
        if not self.model:
            print("当前没有活动模型")
            return
            
        print(f"\n模型状态:")
        print(f"  名称: {self.model.name}")
        print(f"  变量数: {len(self.variables)}")
        print(f"  约束数: {len(self.constraints)}")
        
    def run_example(self):
        print("运行示例问题...")
        print("问题: 最大化 x + 2*y, 约束: x + y <= 10")
        
        self.create_model("example")
        self.add_variable("x", "integer")
        self.add_variable("y", "integer") 
        self.set_objective("x + 2*y", "maximize")
        self.add_constraint("x + y <= 10")
        self.solve_model()
        
    def interactive_mode(self):
        self.display_banner()
        self.show_help()
        
        while True:
            try:
                command = input("\nMIPSolver> ").strip()
                if not command:
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd in ['quit', 'exit']:
                    print("再见!")
                    break
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'new':
                    name = parts[1] if len(parts) > 1 else "model"
                    self.create_model(name)
                elif cmd == 'add_var':
                    if len(parts) < 3:
                        print("用法: add_var <name> <type>")
                        continue
                    self.add_variable(parts[1], parts[2])
                elif cmd == 'set_objective':
                    if len(parts) < 2:
                        print("用法: set_objective <expression> [sense]")
                        continue
                    expr = ' '.join(parts[1:-1]) if len(parts) > 2 and parts[-1].lower() in ['maximize', 'minimize'] else ' '.join(parts[1:])
                    sense = parts[-1] if len(parts) > 2 and parts[-1].lower() in ['maximize', 'minimize'] else 'minimize'
                    self.set_objective(expr, sense)
                elif cmd == 'add_constraint':
                    if len(parts) < 2:
                        print("用法: add_constraint <expression>")
                        continue
                    constraint = ' '.join(parts[1:])
                    self.add_constraint(constraint)
                elif cmd == 'solve':
                    self.solve_model()
                elif cmd == 'load':
                    if len(parts) < 2:
                        print("用法: load <filename>")
                        continue
                    self.load_mps_file(parts[1])
                elif cmd == 'status':
                    self.show_status()
                elif cmd == 'example':
                    self.run_example()
                else:
                    print(f"未知命令: {cmd}")
                    
            except KeyboardInterrupt:
                print("\n使用 'quit' 退出")
            except Exception as e:
                print(f"错误: {e}")

def main():
    parser = argparse.ArgumentParser(description='MIPSolver 交互式求解器')
    parser.add_argument('--file', '-f', help='直接加载文件')
    
    args = parser.parse_args()
    solver = InteractiveSolver()
    
    if args.file:
        solver.create_model("file_model")
        solver.load_mps_file(args.file)
        solver.solve_model()
    else:
        solver.interactive_mode()

if __name__ == "__main__":
    main()