#!/bin/bash
# create_tools.sh - 创建MIPSolver工具套件

echo "创建MIPSolver工具套件..."
cd ~/MIPSolver

# 1. 创建交互式求解器
cat > interactive_solver.py << 'EOF'
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
    print("✓ MIPSolver导入成功")
except ImportError as e:
    print(f"✗ MIPSolver导入失败: {e}")
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
        print(f"✓ 创建模型: {name}")
        
    def add_variable(self, name, vtype="continuous"):
        if not self.model:
            print("✗ 请先创建模型")
            return
            
        type_map = {
            'continuous': mp.CONTINUOUS,
            'integer': mp.INTEGER, 
            'binary': mp.BINARY
        }
        
        if vtype.lower() not in type_map:
            print(f"✗ 未知变量类型: {vtype}")
            return
            
        var = self.model.add_var(name=name, vtype=type_map[vtype.lower()], lb=0)
        self.variables[name] = var
        print(f"✓ 添加变量: {name} ({vtype})")
        
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
                    print(f"✗ 未定义变量: {var_name}")
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
                    print(f"✗ 未定义变量: {var_name}")
                    return None
                    
        return expr
        
    def set_objective(self, expr_str, sense="minimize"):
        if not self.model:
            print("✗ 请先创建模型")
            return
            
        obj_sense = mp.MAXIMIZE if sense.lower() in ['max', 'maximize'] else mp.MINIMIZE
        expr = self.parse_expression(expr_str)
        
        if expr is not None:
            self.model.set_objective(expr, obj_sense)
            print(f"✓ 设置目标: {sense} {expr_str}")
            
    def add_constraint(self, constraint_str):
        if not self.model:
            print("✗ 请先创建模型")
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
                    print(f"✓ 添加约束: {constraint_str}")
                return
                
        print(f"✗ 无效约束格式: {constraint_str}")
        
    def solve_model(self):
        if not self.model:
            print("✗ 请先创建模型")
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
            print(f"✗ 求解失败: {e}")
            
    def load_mps_file(self, filename):
        """加载MPS文件"""
        if not os.path.exists(filename):
            print(f"✗ 文件不存在: {filename}")
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
                print(f"✗ 错误: {e}")

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
EOF

# 2. 创建简单的API服务器
cat > api_server.py << 'EOF'
#!/usr/bin/env python3
"""
MIPSolver 简单API服务器
"""
import json
from datetime import datetime
from typing import Dict, Any
import uuid

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
except ImportError:
    print("请安装Flask: pip install flask flask-cors")
    exit(1)

try:
    import mipsolver as mp
except ImportError as e:
    print(f"MIPSolver导入失败: {e}")
    exit(1)

app = Flask(__name__)
CORS(app)

# 全局存储
active_models: Dict[str, Dict] = {}

@app.route('/')
def index():
    """API文档"""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>MIPSolver API 文档</title></head>
    <body>
        <h1>MIPSolver API 文档</h1>
        <h2>基本用法</h2>
        <p>创建模型: POST /api/models</p>
        <p>添加变量: POST /api/models/{id}/variables</p> 
        <p>设置目标: POST /api/models/{id}/objective</p>
        <p>添加约束: POST /api/models/{id}/constraints</p>
        <p>求解: POST /api/models/{id}/solve</p>
        
        <h2>示例</h2>
        <pre>
# 创建模型
curl -X POST http://localhost:8080/api/models -H "Content-Type: application/json" -d '{"name": "test"}'

# 添加变量  
curl -X POST http://localhost:8080/api/models/{model_id}/variables -H "Content-Type: application/json" -d '{"name": "x", "type": "integer"}'

# 求解
curl -X POST http://localhost:8080/api/models/{model_id}/solve
        </pre>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/models', methods=['POST'])
def create_model():
    """创建模型"""
    try:
        data = request.get_json()
        name = data.get('name', 'api_model')
        model_id = str(uuid.uuid4())
        
        model_data = {
            'id': model_id,
            'name': name,
            'model': mp.Model(name),
            'variables': {},
            'created_at': datetime.now().isoformat()
        }
        active_models[model_id] = model_data
        
        return jsonify({
            'success': True,
            'model_id': model_id,
            'name': name
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/<model_id>/variables', methods=['POST']) 
def add_variable(model_id):
    """添加变量"""
    try:
        if model_id not in active_models:
            return jsonify({'success': False, 'error': '模型不存在'}), 404
            
        data = request.get_json()
        name = data.get('name')
        vtype = data.get('type', 'continuous')
        
        if not name:
            return jsonify({'success': False, 'error': '变量名不能为空'}), 400
            
        type_map = {
            'continuous': mp.CONTINUOUS,
            'integer': mp.INTEGER,
            'binary': mp.BINARY
        }
        
        model_data = active_models[model_id]
        var = model_data['model'].add_var(name=name, vtype=type_map[vtype], lb=0)
        model_data['variables'][name] = var
        
        return jsonify({
            'success': True,
            'message': f'变量 {name} 添加成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/<model_id>/solve', methods=['POST'])
def solve_model(model_id):
    """求解模型"""
    try:
        if model_id not in active_models:
            return jsonify({'success': False, 'error': '模型不存在'}), 404
            
        model_data = active_models[model_id]
        model = model_data['model']
        
        model.optimize()
        
        result = {
            'status': 'optimal' if hasattr(model, 'status') and model.status == mp.OPTIMAL else 'unknown',
            'variables': {},
            'objective_value': None
        }
        
        if hasattr(model, 'status') and model.status == mp.OPTIMAL:
            result['objective_value'] = model.obj_val
            for name, var in model_data['variables'].items():
                result['variables'][name] = var.value
                
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    print(f"启动 MIPSolver API 服务器: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
EOF

# 3. 创建测试脚本
cat > test_mps.py << 'EOF'
#!/usr/bin/env python3
"""
测试MPS文件加载
"""
import os
import mipsolver as mp

def test_basic_solver():
    """测试基本求解功能"""
    print("测试基本求解功能...")
    
    model = mp.Model("basic_test")
    x = model.add_var(name="x", vtype=mp.INTEGER, lb=0, ub=10)
    y = model.add_var(name="y", vtype=mp.INTEGER, lb=0, ub=10)
    
    model.set_objective(x + 2*y, mp.MAXIMIZE)
    model.add_constr(x + y <= 10)
    
    model.optimize()
    
    print(f"状态: {getattr(model, 'status', 'UNKNOWN')}")
    if hasattr(model, 'obj_val'):
        print(f"目标值: {model.obj_val}")
        print(f"解: x={x.value}, y={y.value}")
    else:
        print("无法获取解值")

def list_mps_files():
    """列出可用的MPS文件"""
    mps_dir = "mps"
    if os.path.exists(mps_dir):
        mps_files = [f for f in os.listdir(mps_dir) if f.endswith('.mps')]
        print(f"找到 {len(mps_files)} 个MPS文件:")
        for f in sorted(mps_files):
            print(f"  {f}")
        return mps_files
    else:
        print("MPS目录不存在")
        return []

if __name__ == "__main__":
    print("MIPSolver 测试")
    print("=" * 40)
    
    # 测试基本功能
    test_basic_solver()
    
    print("\n" + "=" * 40)
    
    # 列出MPS文件
    list_mps_files()
    
    print("\n要测试MPS文件，请使用:")
    print("python interactive_solver.py --file mps/文件名.mps")
EOF

# 4. 创建启动脚本
cat > start_interactive.sh << 'EOF'
#!/bin/bash
echo "启动MIPSolver交互式求解器..."
python interactive_solver.py
EOF

cat > start_api.sh << 'EOF' 
#!/bin/bash
echo "启动MIPSolver API服务器..."
echo "访问 http://localhost:8080 查看API文档"
python api_server.py --host 0.0.0.0 --port 8080
EOF

# 设置执行权限
chmod +x interactive_solver.py
chmod +x api_server.py
chmod +x test_mps.py
chmod +x start_interactive.sh
chmod +x start_api.sh

echo "✓ 工具套件创建完成!"
echo ""
echo "现在您可以使用:"
echo "1. python interactive_solver.py  - 交互式求解器"
echo "2. python api_server.py          - API服务器"
echo "3. python test_mps.py            - 测试脚本"
echo "4. ./start_interactive.sh        - 快速启动交互式"
echo "5. ./start_api.sh               - 快速启动API"
EOF

chmod +x create_tools.sh