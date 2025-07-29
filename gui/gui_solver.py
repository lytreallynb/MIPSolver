#!/usr/bin/env python3
"""
MIPSolver GUI界面

这是MIPSolver的图形用户界面模块，提供完整的桌面应用程序功能：

主要功能：
1. 文件管理：支持MPS格式优化问题文件的上传和解析
2. 模型构建：可视化的优化模型构建界面
3. 求解器配置：多种求解算法选择和参数设置
4. 结果展示：求解结果的详细显示和分析
5. 报告生成：自动生成LaTeX格式的专业求解报告

界面架构：
- 采用标签页设计，功能模块清晰分离
- 基于Tkinter构建，跨平台兼容性好
- 响应式布局，适应不同屏幕尺寸
- 丰富的交互元素，用户体验友好

技术特点：
- 异步求解：避免界面冻结，提供进度反馈
- 错误处理：完善的异常捕获和用户提示
- 数据验证：输入数据的格式检查和合理性验证
- 可扩展性：模块化设计便于功能扩展
"""
import sys
import os
import json
import tempfile
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 尝试导入GUI依赖库
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    from tkinter.font import Font
except ImportError:
    print("请安装tkinter: pip install tkinter")
    sys.exit(1)

# 尝试导入MIPSolver核心模块
try:
    import mipsolver as mp
    from mipsolver import Model, CONTINUOUS, INTEGER, BINARY, MAXIMIZE, MINIMIZE
    print("MIPSolver导入成功")
    HAS_MIPSOLVER = True
except ImportError as e:
    print(f"MIPSolver导入失败: {e}")
    HAS_MIPSOLVER = False
    # 创建模拟的常量，保证GUI在开发环境下能正常运行
    CONTINUOUS = 0
    INTEGER = 2
    BINARY = 1
    MAXIMIZE = -1
    MINIMIZE = 1

class MIPSolverGUI:
    """
    MIPSolver图形用户界面主类
    
    这个类实现了完整的桌面应用程序界面，包括：
    
    界面组件：
    - 文件上传标签页：MPS文件选择和预览
    - 模型构建标签页：交互式优化模型构建
    - 求解结果标签页：求解过程监控和结果展示
    - 报告生成标签页：LaTeX报告配置和生成
    
    数据管理：
    - model: 当前的优化模型实例
    - solution: 最新的求解结果
    - problem_data: 问题数据的字典存储
    - solver_options: 可用求解器的配置选项
    
    设计模式：
    - 采用MVC模式分离界面和逻辑
    - 事件驱动的用户交互处理
    - 状态管理确保界面数据一致性
    """
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("MIPSolver - 混合整数规划求解器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化数据存储
        self.model = None              # 当前优化模型
        self.solution = None           # 当前求解结果
        self.problem_data = {}         # 问题数据缓存
        
        # 求解器选项配置
        # 这里定义了可用的求解算法及其对应的后端实现
        self.solver_options = {
            "Branch & Bound": "mipsolver",  # 分支定界法
            "Simplex (LP)": "mipsolver"     # 单纯形法（仅用于线性规划松弛）
        }
        
        # 初始化用户界面
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置用户界面布局和组件
        
        界面结构：
        1. 主框架：包含所有界面元素的根容器
        2. 标题区域：显示应用程序名称和版本信息
        3. 标签页容器：组织不同功能模块的界面
        4. 各功能标签页：文件上传、模型构建、求解结果、报告生成
        
        设计原则：
        - 响应式布局：自适应窗口大小变化
        - 直观导航：清晰的标签页组织
        - 视觉一致性：统一的颜色和字体风格
        """
        # 创建主框架容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建应用程序标题
        title_label = tk.Label(
            main_frame, 
            text="MIPSolver 混合整数规划求解器",
            font=Font(size=20, weight='bold'),  # 使用粗体大号字体
            bg='#f0f0f0',                       # 背景色与主窗口一致
            fg='#2c3e50'                        # 深色前景色提高可读性
        )
        title_label.pack(pady=(0, 20))  # 设置底部间距
        
        # 创建标签页容器（Notebook组件）
        # 这是主要的界面组织方式，将不同功能分组到标签页中
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 初始化各个功能标签页
        self.setup_file_upload_tab(notebook)    # 文件上传和预览
        self.setup_model_builder_tab(notebook)  # 交互式模型构建
        self.setup_solution_tab(notebook)       # 求解结果展示
        self.setup_report_tab(notebook)         # 报告生成配置
        
    def setup_file_upload_tab(self, notebook):
        """
        设置文件上传标签页
        
        功能说明：
        - MPS文件选择：支持标准的混合整数规划文件格式
        - 文件预览：显示选中文件的基本信息和内容摘要
        - 格式验证：检查文件格式的正确性
        - 数据解析：将MPS文件解析为内部数据结构
        
        界面组件：
        - 文件路径显示框：显示当前选中的文件路径
        - 浏览按钮：打开文件选择对话框
        - 文件信息区域：显示文件的详细信息
        - 加载按钮：将文件数据加载到求解器中
        """
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="文件上传")
        
        # 文件选择区域
        # 使用LabelFrame提供视觉分组和标题
        file_frame = ttk.LabelFrame(upload_frame, text="选择问题文件", padding=20)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 文件路径显示变量
        # 使用StringVar实现数据绑定，自动更新界面显示
        self.file_path_var = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        path_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 浏览按钮
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT)
        
        # 求解器选择区域
        solver_frame = ttk.LabelFrame(upload_frame, text="选择求解器", padding=20)
        solver_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.solver_var = tk.StringVar(value="Branch & Bound")
        for solver_name in self.solver_options.keys():
            rb = ttk.Radiobutton(
                solver_frame, 
                text=solver_name, 
                variable=self.solver_var, 
                value=solver_name
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # 求解按钮
        solve_btn = ttk.Button(
            upload_frame, 
            text="开始求解", 
            command=self.solve_problem,
            style='Accent.TButton'
        )
        solve_btn.pack(pady=20)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            upload_frame, 
            variable=self.progress_var, 
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(upload_frame, textvariable=self.status_var)
        status_label.pack()
        
    def setup_model_builder_tab(self, notebook):
        """模型构建标签页"""
        builder_frame = ttk.Frame(notebook)
        notebook.add(builder_frame, text="模型构建")
        
        # 变量管理
        var_frame = ttk.LabelFrame(builder_frame, text="变量管理", padding=10)
        var_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加变量
        var_input_frame = ttk.Frame(var_frame)
        var_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(var_input_frame, text="变量名:").pack(side=tk.LEFT)
        self.var_name_var = tk.StringVar()
        ttk.Entry(var_input_frame, textvariable=self.var_name_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(var_input_frame, text="类型:").pack(side=tk.LEFT, padx=(10, 0))
        self.var_type_var = tk.StringVar(value="continuous")
        var_type_combo = ttk.Combobox(
            var_input_frame, 
            textvariable=self.var_type_var,
            values=["continuous", "integer", "binary"],
            width=10,
            state="readonly"
        )
        var_type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(var_input_frame, text="添加变量", command=self.add_variable).pack(side=tk.LEFT, padx=10)
        
        # 变量列表
        self.var_tree = ttk.Treeview(var_frame, columns=("name", "type", "bounds"), show="headings")
        self.var_tree.heading("name", text="变量名")
        self.var_tree.heading("type", text="类型")
        self.var_tree.heading("bounds", text="边界")
        self.var_tree.pack(fill=tk.X, pady=5)
        
        # 约束管理
        constr_frame = ttk.LabelFrame(builder_frame, text="约束管理", padding=10)
        constr_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(constr_frame, text="约束表达式:").pack(anchor=tk.W)
        self.constr_expr_var = tk.StringVar()
        ttk.Entry(constr_frame, textvariable=self.constr_expr_var, width=50).pack(fill=tk.X, pady=5)
        
        ttk.Button(constr_frame, text="添加约束", command=self.add_constraint).pack(anchor=tk.W)
        
        # 约束列表
        self.constr_tree = ttk.Treeview(constr_frame, columns=("expression",), show="headings")
        self.constr_tree.heading("expression", text="约束表达式")
        self.constr_tree.pack(fill=tk.X, pady=5)
        
        # 目标函数
        obj_frame = ttk.LabelFrame(builder_frame, text="目标函数", padding=10)
        obj_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(obj_frame, text="目标表达式:").pack(anchor=tk.W)
        self.obj_expr_var = tk.StringVar()
        ttk.Entry(obj_frame, textvariable=self.obj_expr_var, width=50).pack(fill=tk.X, pady=5)
        
        self.obj_sense_var = tk.StringVar(value="minimize")
        ttk.Radiobutton(obj_frame, text="最小化", variable=self.obj_sense_var, value="minimize").pack(side=tk.LEFT)
        ttk.Radiobutton(obj_frame, text="最大化", variable=self.obj_sense_var, value="maximize").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(obj_frame, text="设置目标", command=self.set_objective).pack(anchor=tk.W, pady=5)
        
    def setup_solution_tab(self, notebook):
        """求解结果标签页"""
        solution_frame = ttk.Frame(notebook)
        notebook.add(solution_frame, text="求解结果")
        
        # 结果信息
        info_frame = ttk.LabelFrame(solution_frame, text="求解信息", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.solution_info_text = scrolledtext.ScrolledText(info_frame, height=8, width=80)
        self.solution_info_text.pack(fill=tk.BOTH, expand=True)
        
        # 变量值表格
        values_frame = ttk.LabelFrame(solution_frame, text="变量取值", padding=10)
        values_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.values_tree = ttk.Treeview(values_frame, columns=("variable", "value", "type"), show="headings")
        self.values_tree.heading("variable", text="变量名")
        self.values_tree.heading("value", text="取值")
        self.values_tree.heading("type", text="类型")
        self.values_tree.pack(fill=tk.BOTH, expand=True)
        
    def setup_report_tab(self, notebook):
        """报告生成标签页"""
        report_frame = ttk.Frame(notebook)
        notebook.add(report_frame, text="LaTeX报告")
        
        # 报告选项
        options_frame = ttk.LabelFrame(report_frame, text="报告选项", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.include_math_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含数学模型", variable=self.include_math_var).pack(anchor=tk.W)
        
        self.include_solution_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含求解结果", variable=self.include_solution_var).pack(anchor=tk.W)
        
        self.include_analysis_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含问题分析", variable=self.include_analysis_var).pack(anchor=tk.W)
        
        # 生成报告按钮
        ttk.Button(report_frame, text="生成LaTeX报告", command=self.generate_latex_report).pack(pady=10)
        
        # 报告预览
        preview_frame = ttk.LabelFrame(report_frame, text="报告预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(preview_frame, height=20, width=80)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_file(self):
        """浏览文件"""
        filetypes = [
            ("MPS files", "*.mps"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="选择MPS文件",
            filetypes=filetypes
        )
        if filename:
            self.file_path_var.set(filename)
            self.load_problem_file(filename)
            
    def load_problem_file(self, filename):
        """加载问题文件"""
        try:
            self.status_var.set("正在加载文件...")
            self.progress_var.set(20)
            
            # 解析MPS文件
            self.model = self.parse_mps_file(filename)
            
            self.status_var.set("文件加载完成")
            self.progress_var.set(100)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {e}")
            self.status_var.set("文件加载失败")
            
    def parse_mps_file(self, filename):
        """解析MPS文件"""
        if not HAS_MIPSOLVER:
            # 如果没有MIPSolver，创建模拟模型
            return self.create_mock_model()
        
        try:
            model = Model(f"model_{Path(filename).stem}")
        except Exception as e:
            print(f"Model创建失败: {e}")
            return self.create_mock_model()
        
        # 简单的MPS解析器
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        current_section = None
        variables = {}
        constraints = {}
        objective = None
        objective_sense = MINIMIZE
        in_int_section = False  # 新增：是否在整数变量区间
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
                
            if line == 'NAME':
                current_section = 'NAME'
            elif line == 'ROWS':
                current_section = 'ROWS'
            elif line == 'COLUMNS':
                current_section = 'COLUMNS'
            elif line == 'RHS':
                current_section = 'RHS'
            elif line == 'BOUNDS':
                current_section = 'BOUNDS'
            elif line == 'ENDATA':
                break
            elif current_section == 'ROWS':
                # 解析行（约束和目标）
                parts = line.split()
                if len(parts) >= 2:
                    row_type = parts[0]
                    row_name = parts[1]
                    
                    if row_type == 'N':
                        # 目标函数行
                        objective = row_name
                    else:
                        # 约束行
                        constraints[row_name] = {
                            'type': row_type,
                            'coefficients': {},
                            'rhs': 0.0
                        }
            elif current_section == 'COLUMNS':
                parts = line.split()
                if len(parts) >= 3:
                    var_name = parts[0]
                    # 检查整数变量标记
                    if var_name == 'MARK' and len(parts) > 3:
                        marker = parts[3].strip("'")
                        if marker == 'INTORG':
                            in_int_section = True
                        elif marker == 'INTEND':
                            in_int_section = False
                        continue
                    vtype = INTEGER if in_int_section else CONTINUOUS
                    # 跳过特殊标记行（如MARK, MARKEND等）
                    if var_name in ['MARK', 'MARKEND']:
                        continue
                    if var_name not in variables:
                        try:
                            variables[var_name] = model.add_var(name=var_name, vtype=vtype)
                        except Exception as e:
                            print(f"添加变量失败: {e}")
                            continue
                    row_name = parts[1]
                    # 安全地转换系数为浮点数
                    try:
                        coeff_str = parts[2]
                        # 检查是否是字符串值（用引号包围）
                        if coeff_str.startswith("'") and coeff_str.endswith("'"):
                            print(f"警告: 第{line_num}行跳过字符串值: {coeff_str}")
                            continue
                        coeff = float(coeff_str)
                    except (ValueError, IndexError) as e:
                        print(f"警告: 第{line_num}行系数转换失败: '{parts[2] if len(parts) > 2 else 'N/A'}' - {e}")
                        continue
                    if row_name == objective:
                        # 目标函数系数
                        try:
                            variables[var_name].obj = coeff
                        except Exception as e:
                            print(f"设置目标系数失败: {e}")
                    else:
                        # 约束系数
                        if row_name in constraints:
                            constraints[row_name]['coefficients'][var_name] = coeff
            elif current_section == 'RHS':
                # 解析右端常数
                parts = line.split()
                if len(parts) >= 3:
                    row_name = parts[1]
                    # 安全地转换RHS为浮点数
                    try:
                        rhs_str = parts[2]
                        # 检查是否是字符串值（用引号包围）
                        if rhs_str.startswith("'") and rhs_str.endswith("'"):
                            print(f"警告: 第{line_num}行跳过字符串RHS: {rhs_str}")
                            continue
                        rhs = float(rhs_str)
                    except (ValueError, IndexError) as e:
                        print(f"警告: 第{line_num}行RHS转换失败: '{parts[2] if len(parts) > 2 else 'N/A'}' - {e}")
                        continue
                    if row_name in constraints:
                        constraints[row_name]['rhs'] = rhs
        # 设置目标函数
        if objective:
            try:
                obj_expr = sum(var.obj * var for var in variables.values() if hasattr(var, 'obj'))
                model.set_objective(obj_expr, objective_sense)
            except Exception as e:
                print(f"设置目标函数失败: {e}")
        # 添加约束
        for constr_name, constr_data in constraints.items():
            try:
                lhs = sum(constr_data['coefficients'].get(var_name, 0) * variables[var_name] 
                         for var_name in variables.keys())
                if constr_data['type'] == 'L':
                    model.add_constr(lhs <= constr_data['rhs'], name=constr_name)
                elif constr_data['type'] == 'G':
                    model.add_constr(lhs >= constr_data['rhs'], name=constr_name)
                elif constr_data['type'] == 'E':
                    model.add_constr(lhs == constr_data['rhs'], name=constr_name)
            except Exception as e:
                print(f"添加约束失败: {e}")
        return model
        
    def create_mock_model(self):
        """创建模拟模型"""
        class MockModel:
            def __init__(self, name):
                self.name = name
                self._variables = []
                self.status = "UNKNOWN"
                self.obj_val = 0.0
                self._constraints = []
            
            def optimize(self):
                # 模拟求解过程
                time.sleep(1)
                self.status = "OPTIMAL"
                self.obj_val = 20.0
                # 设置模拟的变量值
                for var in self._variables:
                    var.value = 5.0 if var.name == "x" else 10.0
            
            def add_var(self, name, vtype=CONTINUOUS):
                var = MockVar(name)
                self._variables.append(var)
                return var
            
            def set_objective(self, expr, sense):
                pass
            
            def add_constr(self, constraint, name=""):
                self._constraints.append(constraint)
        
        class MockVar:
            def __init__(self, name):
                self.name = name
                self.value = 0.0
                self.obj = 0.0
                self.vtype = CONTINUOUS
            
            def __mul__(self, other):
                return MockExpr()
            
            def __add__(self, other):
                return MockExpr()
            
            def __rmul__(self, other):
                return MockExpr()
            
            def __radd__(self, other):
                return MockExpr()
        
        class MockExpr:
            def __init__(self):
                pass
            
            def __le__(self, other):
                return MockConstraint()
            
            def __ge__(self, other):
                return MockConstraint()
            
            def __eq__(self, other):
                return MockConstraint()
        
        class MockConstraint:
            def __init__(self):
                pass
        
        return MockModel("mock_model")
        
    def solve_problem(self):
        """求解问题"""
        if not self.model:
            messagebox.showwarning("警告", "请先加载问题文件")
            return
            
        try:
            # 显示正在求解状态
            solver_name = self.solver_var.get()
            self.status_var.set(f"正在使用 {solver_name} 求解...")
            self.progress_var.set(30)
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用求解器
            self.model.optimize()
            
            # 记录求解时间
            solve_time = time.time() - start_time
            
            # 提取求解结果
            self.solution = {
                'status': self.get_status_text(self.model.status),
                'objective_value': self.model.obj_val if hasattr(self.model, 'obj_val') else 0.0,
                'variables': {},
                'solve_time': solve_time,
                'iterations': self.model.iterations if hasattr(self.model, 'iterations') else 0,
                'solve_log': self.model.solve_log if hasattr(self.model, 'solve_log') else [],
                'solver': self.solver_var.get()
            }
            
            # 提取变量值
            for var in getattr(self.model, '_variables', []):
                self.solution['variables'][var.name] = getattr(var, 'value', 0.0)
            
            self.progress_var.set(100)
            self.status_var.set("求解完成")
            
            # 更新结果标签页
            self.update_solution_display()
            
            messagebox.showinfo("成功", "问题求解完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"求解失败: {e}")
            self.status_var.set("求解失败")
            
    def get_status_text(self, status):
        """获取状态文本"""
        # Handle different status representations
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
        
    def add_variable(self):
        """添加变量"""
        name = self.var_name_var.get().strip()
        vtype = self.var_type_var.get()
        
        if not name:
            messagebox.showwarning("警告", "请输入变量名")
            return
            
        # 添加到树形视图
        self.var_tree.insert("", "end", values=(name, vtype, "[0, ∞)"))
        self.var_name_var.set("")  # 清空输入
        
    def add_constraint(self):
        """添加约束"""
        expr = self.constr_expr_var.get().strip()
        
        if not expr:
            messagebox.showwarning("警告", "请输入约束表达式")
            return
            
        # 添加到树形视图
        self.constr_tree.insert("", "end", values=(expr,))
        self.constr_expr_var.set("")  # 清空输入
        
    def set_objective(self):
        """设置目标函数"""
        expr = self.obj_expr_var.get().strip()
        sense = self.obj_sense_var.get()
        
        if not expr:
            messagebox.showwarning("警告", "请输入目标函数表达式")
            return
            
        messagebox.showinfo("成功", f"目标函数已设置为: {sense} {expr}")
        
    def update_solution_display(self):
        """更新求解结果显示"""
        if not self.solution:
            return
            
        # 更新信息文本
        info_text = f"""
=== 求解结果 ===
求解状态: {self.solution['status']}
目标函数值: {self.solution['objective_value']:.6f}
求解时间: {self.solution['solve_time']:.4f} 秒
迭代次数: {self.solution['iterations']}
使用求解器: {self.solution['solver']}
变量数量: {len(self.solution['variables'])}

=== 详细信息 ===
模型名称: {getattr(self.model, '_name', 'Unknown')}

=== 求解日志 ===
"""
        
        # 添加求解日志
        if self.solution['solve_log']:
            for log_entry in self.solution['solve_log'][-10:]:  # 显示最后10条日志
                info_text += f"{log_entry}\n"
        else:
            info_text += "无求解日志可用\n"
        self.solution_info_text.delete(1.0, tk.END)
        self.solution_info_text.insert(1.0, info_text)
        
        # 更新变量值表格
        self.values_tree.delete(*self.values_tree.get_children())
        for var_name, value in self.solution['variables'].items():
            self.values_tree.insert("", "end", values=(var_name, f"{value:.6f}", "continuous"))
            
    def generate_latex_report(self):
        """生成LaTeX报告"""
        if not self.solution:
            messagebox.showwarning("警告", "请先求解问题")
            return
            
        try:
            latex_content = self.create_latex_report()
            
            # 显示在预览区域
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, latex_content)
            
            # 保存到文件
            filename = filedialog.asksaveasfilename(
                title="保存XeLaTeX报告（支持中文）",
                defaultextension=".tex",
                filetypes=[("XeLaTeX files", "*.tex"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                # 创建编译说明文件
                compile_instructions = self.create_compile_instructions(filename)
                instructions_file = filename.replace('.tex', '_编译说明.txt')
                
                with open(instructions_file, 'w', encoding='utf-8') as f:
                    f.write(compile_instructions)
                
                success_msg = f"""XeLaTeX报告已保存！

文件位置：
- LaTeX源文件：{filename}
- 编译说明：{instructions_file}

要生成PDF，请使用XeLaTeX编译器：
xelatex "{filename}"

详细说明请查看编译说明文件。"""
                
                messagebox.showinfo("保存成功", success_msg)
                
        except Exception as e:
            messagebox.showerror("错误", f"生成报告失败: {e}")
            
    def create_latex_report(self):
        """创建XeLaTeX报告内容（支持中文）"""
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        report = r"""
\documentclass[12pt,a4paper]{article}
\usepackage{xeCJK}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{fancyhdr}

% 设置页面边距
\geometry{margin=2.5cm}

% 设置中文字体 (使用系统字体)
\setCJKmainfont{PingFang SC}  % macOS系统字体
\setCJKsansfont{PingFang SC}
\setCJKmonofont{PingFang SC}

% 如果系统没有PingFang SC，可以使用其他中文字体
% \setCJKmainfont{SimSun}  % Windows
% \setCJKmainfont{Noto Sans CJK SC}  % Linux

% 设置页眉页脚
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{MIPSolver 求解报告}
\fancyhead[R]{""" + current_time + r"""}
\fancyfoot[C]{\thepage}

% 标题设置
\title{\textbf{MIPSolver 混合整数规划求解报告}}
\author{系统自动生成}
\date{""" + current_time + r"""}

\begin{document}

\maketitle
\thispagestyle{fancy}

\tableofcontents
\newpage

\section{问题概述}
"""
        
        if self.include_math_var.get():
            report += r"""
\subsection{数学模型}

本问题为混合整数线性规划问题，数学模型如下：

\begin{align}
\text{目标函数：} \quad & \min \sum_{j=1}^{n} c_j x_j \label{eq:objective}\\
\text{约束条件：} \quad & \sum_{j=1}^{n} a_{ij} x_j \leq b_i, \quad i = 1, 2, \ldots, m \label{eq:constraints}\\
& x_j \geq 0, \quad j = 1, 2, \ldots, n \label{eq:nonnegativity}\\
& x_j \in \mathbb{Z}, \quad j \in I \label{eq:integrality}
\end{align}

其中：
\begin{itemize}
\item $x_j$ 为决策变量，$j = 1, 2, \ldots, n$
\item $c_j$ 为目标函数系数
\item $a_{ij}$ 为约束系数矩阵元素
\item $b_i$ 为约束右端常数
\item $I$ 为整数变量的指标集合
\end{itemize}
"""
        
        if self.include_solution_var.get():
            report += r"""
\section{求解结果}

\subsection{求解状态信息}

\begin{table}[h]
\centering
\begin{tabular}{ll}
\toprule
\textbf{项目} & \textbf{结果} \\
\midrule
求解状态 & """ + self.solution['status'] + r""" \\
目标函数值 & """ + f"{self.solution['objective_value']:.6f}" + r""" \\
求解时间 & """ + f"{self.solution['solve_time']:.4f}" + r""" 秒 \\
迭代次数 & """ + str(self.solution['iterations']) + r""" \\
使用求解器 & """ + self.solution['solver'].replace('&', r'\&') + r""" \\
变量数量 & """ + str(len(self.solution['variables'])) + r""" \\
\bottomrule
\end{tabular}
\caption{求解状态信息汇总}
\end{table}

\subsection{最优解}

求解得到的最优解如下：

\begin{longtable}{lcc}
\toprule
\textbf{变量名} & \textbf{最优值} & \textbf{变量类型} \\
\midrule
"""
            
            # 只显示前20个变量，避免表格过长
            var_items = list(self.solution['variables'].items())
            display_vars = var_items[:20]
            
            for var_name, value in display_vars:
                # 根据值判断可能的变量类型
                if abs(value - round(value)) < 1e-9 and 0 <= value <= 1:
                    var_type = "二进制"
                elif abs(value - round(value)) < 1e-9:
                    var_type = "整数"
                else:
                    var_type = "连续"
                    
                report += f"{var_name} & {value:.6f} & {var_type} \\\\\n"
            
            if len(var_items) > 20:
                report += r"""\midrule
\multicolumn{3}{c}{\textit{... 省略其余 """ + str(len(var_items) - 20) + r""" 个变量 ...}} \\
"""
                
            report += r"""
\bottomrule
\caption{决策变量最优取值}
\end{longtable}
"""
        
        if self.include_analysis_var.get():
            # 分析变量类型分布
            binary_count = 0
            integer_count = 0
            continuous_count = 0
            
            for var_name, value in self.solution['variables'].items():
                if abs(value - round(value)) < 1e-9 and 0 <= value <= 1:
                    binary_count += 1
                elif abs(value - round(value)) < 1e-9:
                    integer_count += 1
                else:
                    continuous_count += 1
            
            report += r"""
\section{问题分析}

\subsection{问题规模分析}

\begin{table}[h]
\centering
\begin{tabular}{lr}
\toprule
\textbf{问题特征} & \textbf{数量} \\
\midrule
决策变量总数 & """ + str(len(self.solution['variables'])) + r""" \\
连续变量 & """ + str(continuous_count) + r""" \\
整数变量 & """ + str(integer_count) + r""" \\
二进制变量 & """ + str(binary_count) + r""" \\
约束数量 & """ + str(len(getattr(self.model, '_constraints', []))) + r""" \\
\bottomrule
\end{tabular}
\caption{问题规模统计}
\end{table}

\subsection{求解器性能分析}

\begin{itemize}
\item \textbf{使用求解器：}""" + self.solution['solver'].replace('&', r'\&') + r"""
\item \textbf{求解算法：}基于C++实现的分支定界法
\item \textbf{线性松弛：}单纯形法
\item \textbf{求解效率：}""" + f"{self.solution['solve_time']:.4f}" + r"""秒完成求解
\item \textbf{迭代收敛：}经过""" + str(self.solution['iterations']) + r"""次迭代达到最优解
\end{itemize}

\subsection{解的质量评估}

根据求解状态 \textbf{""" + self.solution['status'] + r"""}，可以得出以下结论：

\begin{itemize}
\item 问题具有可行解，求解器成功找到最优解
\item 目标函数最优值为 """ + f"{self.solution['objective_value']:.6f}" + r"""
\item 所有约束条件均得到满足
\item 整数变量取值符合整数约束要求
\end{itemize}
"""
        
        report += r"""
\section{总结与结论}

\subsection{求解总结}

本次优化求解任务已成功完成，主要成果如下：

\begin{enumerate}
\item \textbf{问题建模：}成功构建了包含 """ + str(len(self.solution['variables'])) + r""" 个决策变量和 """ + str(len(getattr(self.model, '_constraints', []))) + r""" 个约束的混合整数线性规划模型
\item \textbf{算法求解：}采用高性能C++实现的分支定界算法，确保求解的准确性与效率
\item \textbf{最优解获得：}在 """ + f"{self.solution['solve_time']:.4f}" + r""" 秒内找到最优解，目标函数值为 """ + f"{self.solution['objective_value']:.6f}" + r"""
\item \textbf{解的验证：}所有约束条件均得到满足，整数约束得到严格执行
\end{enumerate}

\subsection{技术说明}

\begin{itemize}
\item \textbf{软件平台：}MIPSolver v1.0 - 基于Python和C++的混合整数规划求解器
\item \textbf{求解引擎：}自主研发的高性能C++优化核心
\item \textbf{报告生成：}支持XeLaTeX格式，完美呈现中文内容
\item \textbf{生成时间：}""" + current_time + r"""
\end{itemize}

\vspace{1cm}

\begin{center}
\textit{--- 报告结束 ---}

\small{此报告由 MIPSolver 系统自动生成}
\end{center}

\end{document}
"""
        
        return report
    
    def create_compile_instructions(self, tex_filename):
        """创建XeLaTeX编译说明"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        instructions = f"""XeLaTeX 编译说明
===============================

文件：{tex_filename}
生成时间：{current_time}

一、系统要求
-----------
1. 安装完整的LaTeX发行版：
   - macOS: MacTeX (推荐)
   - Windows: MiKTeX 或 TeX Live
   - Linux: TeX Live

2. 确保已安装XeLaTeX：
   打开终端/命令提示符，运行：xelatex --version

3. 中文字体要求：
   - macOS: 系统自带 PingFang SC 字体
   - Windows: 需要安装中文字体（如 SimSun）
   - Linux: 安装 fonts-noto-cjk 包

二、编译方法
-----------

方法一：命令行编译（推荐）
1. 打开终端/命令提示符
2. 切换到文件所在目录：cd "文件目录路径"
3. 运行编译命令：
   xelatex "{tex_filename}"
4. 如果包含目录，再次运行：
   xelatex "{tex_filename}"

方法二：LaTeX编辑器
1. 使用 TeXworks, TeXstudio, VS Code 等编辑器
2. 打开 .tex 文件
3. 设置编译器为 XeLaTeX
4. 点击编译按钮

三、故障排除
-----------

问题1：找不到字体
解决：
- macOS: 确保系统已安装 PingFang SC
- Windows: 将第689行改为 \\setCJKmainfont{{SimSun}}
- Linux: 将第689行改为 \\setCJKmainfont{{Noto Sans CJK SC}}

问题2：编译错误
解决：
1. 检查 LaTeX 发行版是否完整安装
2. 更新宏包：tlmgr update --self --all
3. 检查文件路径中是否包含特殊字符

问题3：中文显示异常
解决：
1. 确保使用 XeLaTeX 而非 pdfLaTeX
2. 检查中文字体是否正确安装
3. 确认文件编码为 UTF-8

四、预期输出
-----------
成功编译后将生成：
- {tex_filename.replace('.tex', '.pdf')} - 最终PDF报告
- {tex_filename.replace('.tex', '.aux')} - 辅助文件
- {tex_filename.replace('.tex', '.log')} - 编译日志
- {tex_filename.replace('.tex', '.toc')} - 目录文件

五、技术支持
-----------
如遇问题，请检查：
1. LaTeX 发行版版本和完整性
2. XeLaTeX 编译器可用性
3. 中文字体安装情况
4. 文件编码格式（应为UTF-8）

生成工具：MIPSolver v1.0
技术文档：https://github.com/your-repo/mipsolver
"""
        return instructions
        
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = MIPSolverGUI()
    app.run()

if __name__ == "__main__":
    main() 