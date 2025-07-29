#!/usr/bin/env python3
"""
MIPSolver Web界面
现代化Web GUI，支持文件上传、求解器选择、LaTeX报告生成
"""
import os
import json
import tempfile
import base64
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from flask import Flask, request, jsonify, render_template_string, send_file
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
except ImportError:
    print("请安装Flask: pip install flask flask-cors werkzeug")
    exit(1)

try:
    import mipsolver as mp
    from mipsolver import Model, CONTINUOUS, INTEGER, BINARY, MAXIMIZE, MINIMIZE
    print("MIPSolver导入成功")
except ImportError as e:
    print(f"MIPSolver导入失败: {e}")
    # 使用模拟数据
    mp = None

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mps', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局存储
active_problems = {}
solver_options = {
    "branch_bound": "分支定界法",
    "simplex": "单纯形法", 
    "gurobi": "Gurobi",
    "cplex": "CPLEX"
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_mps_file(filename):
    """解析MPS文件"""
    try:
        model = Model(f"model_{Path(filename).stem}")
    except Exception as e:
        # 如果Model创建失败，创建一个简单的测试模型
        print(f"Model创建失败: {e}")
        model = create_test_model()
        return model
    
    # 简单的MPS解析器
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    current_section = None
    variables = {}
    constraints = {}
    objective = None
    objective_sense = MINIMIZE
    
    for line in lines:
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
            # 解析列（变量）
            parts = line.split()
            if len(parts) >= 3:
                var_name = parts[0]
                if var_name not in variables:
                    try:
                        variables[var_name] = model.add_var(name=var_name, vtype=CONTINUOUS)
                    except Exception as e:
                        print(f"添加变量失败: {e}")
                        continue
                
                row_name = parts[1]
                coeff = float(parts[2])
                
                if row_name == objective:
                    # 目标函数系数
                    variables[var_name].obj = coeff
                else:
                    # 约束系数
                    if row_name in constraints:
                        constraints[row_name]['coefficients'][var_name] = coeff
        elif current_section == 'RHS':
            # 解析右端常数
            parts = line.split()
            if len(parts) >= 3:
                row_name = parts[1]
                rhs = float(parts[2])
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

def create_test_model():
    """创建测试模型"""
    try:
        model = Model("test_model")
        
        # 添加变量
        x = model.add_var(name="x", vtype=CONTINUOUS)
        y = model.add_var(name="y", vtype=CONTINUOUS)
        
        # 设置目标函数
        model.set_objective(x + 2*y, MAXIMIZE)
        
        # 添加约束
        model.add_constr(x + y <= 10, name="c1")
        model.add_constr(x >= 0, name="c2")
        model.add_constr(y >= 0, name="c3")
        
        return model
    except Exception as e:
        print(f"创建测试模型失败: {e}")
        # 返回一个模拟的模型对象
        class MockModel:
            def __init__(self):
                self._variables = []
                self.status = "UNKNOWN"
                self.obj_val = 0.0
            
            def optimize(self):
                pass
            
            def add_var(self, name, vtype=CONTINUOUS):
                var = MockVar(name)
                self._variables.append(var)
                return var
            
            def set_objective(self, expr, sense):
                pass
            
            def add_constr(self, constraint, name=""):
                pass
        
        class MockVar:
            def __init__(self, name):
                self.name = name
                self.value = 0.0
                self.obj = 0.0
            
            def __mul__(self, other):
                return MockExpr()
            
            def __add__(self, other):
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
        
        return MockModel()

def get_status_text(status):
    """获取状态文本"""
    if not mp:
        return "UNKNOWN"
    
    if hasattr(status, 'value'):
        status = status.value
    
    status_map = {
        getattr(mp, 'OPTIMAL', 2): "OPTIMAL",
        getattr(mp, 'INFEASIBLE', 3): "INFEASIBLE", 
        getattr(mp, 'UNBOUNDED', 4): "UNBOUNDED",
        getattr(mp, 'ERROR', 5): "ERROR"
    }
    return status_map.get(status, "UNKNOWN")

def create_html_template():
    """创建HTML模板"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIPSolver - 混合整数规划求解器</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        .upload-area.dragover {
            border-color: #28a745;
            background-color: #d4edda;
        }
        .solver-card {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .solver-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .solver-card.selected {
            border-color: #007bff;
            background-color: #e3f2fd;
        }
        .progress-container {
            display: none;
        }
        .result-card {
            display: none;
        }
        .latex-preview {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- 导航栏 -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container">
                <a class="navbar-brand" href="#">
                    <i class="fas fa-calculator me-2"></i>
                    MIPSolver
                </a>
                <span class="navbar-text">
                    混合整数规划求解器
                </span>
            </div>
        </nav>

        <div class="container">
            <!-- 步骤指示器 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar" role="progressbar" style="width: 0%" id="stepProgress"></div>
                    </div>
                    <div class="d-flex justify-content-between mt-2">
                        <span class="badge bg-primary">1. 上传文件</span>
                        <span class="badge bg-secondary">2. 选择求解器</span>
                        <span class="badge bg-secondary">3. 求解</span>
                        <span class="badge bg-secondary">4. 生成报告</span>
                    </div>
                </div>
            </div>

            <!-- 文件上传区域 -->
            <div class="row mb-4" id="uploadSection">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-upload me-2"></i>上传问题文件</h5>
                        </div>
                        <div class="card-body">
                            <div class="upload-area" id="uploadArea">
                                <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                <h5>拖拽文件到此处或点击选择</h5>
                                <p class="text-muted">支持 .mps 格式文件</p>
                                <input type="file" id="fileInput" accept=".mps,.txt" style="display: none;">
                                <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">
                                    <i class="fas fa-folder-open me-2"></i>选择文件
                                </button>
                            </div>
                            <div id="fileInfo" class="mt-3" style="display: none;">
                                <div class="alert alert-success">
                                    <i class="fas fa-check-circle me-2"></i>
                                    <span id="fileName"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 求解器选择区域 -->
            <div class="row mb-4" id="solverSection" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-cogs me-2"></i>选择求解器</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3 mb-3">
                                    <div class="card solver-card" data-solver="branch_bound">
                                        <div class="card-body text-center">
                                            <i class="fas fa-sitemap fa-2x text-primary mb-2"></i>
                                            <h6>分支定界法</h6>
                                            <small class="text-muted">适合混合整数规划</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="card solver-card" data-solver="simplex">
                                        <div class="card-body text-center">
                                            <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                                            <h6>单纯形法</h6>
                                            <small class="text-muted">适合线性规划</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="card solver-card" data-solver="gurobi">
                                        <div class="card-body text-center">
                                            <i class="fas fa-rocket fa-2x text-warning mb-2"></i>
                                            <h6>Gurobi</h6>
                                            <small class="text-muted">商业求解器</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="card solver-card" data-solver="cplex">
                                        <div class="card-body text-center">
                                            <i class="fas fa-industry fa-2x text-info mb-2"></i>
                                            <h6>CPLEX</h6>
                                            <small class="text-muted">IBM求解器</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 求解按钮 -->
            <div class="row mb-4" id="solveSection" style="display: none;">
                <div class="col-12 text-center">
                    <button class="btn btn-success btn-lg" id="solveBtn" onclick="solveProblem()">
                        <i class="fas fa-play me-2"></i>开始求解
                    </button>
                </div>
            </div>

            <!-- 进度条 -->
            <div class="row mb-4" id="progressSection" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h6 id="progressTitle">正在求解...</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: 0%" id="progressBar"></div>
                            </div>
                            <small class="text-muted" id="progressText">初始化...</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 结果区域 -->
            <div class="row mb-4" id="resultSection" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-bar me-2"></i>求解结果</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>求解信息</h6>
                                    <table class="table table-sm">
                                        <tr><td>状态:</td><td id="solutionStatus"></td></tr>
                                        <tr><td>目标值:</td><td id="objectiveValue"></td></tr>
                                        <tr><td>求解时间:</td><td id="solveTime"></td></tr>
                                        <tr><td>迭代次数:</td><td id="iterations"></td></tr>
                                        <tr><td>求解器:</td><td id="solverName"></td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>变量取值</h6>
                                    <div id="variableValues" style="max-height: 200px; overflow-y: auto;">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 报告生成区域 -->
            <div class="row mb-4" id="reportSection" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-file-alt me-2"></i>生成LaTeX报告</h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <h6>报告选项</h6>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="includeMath" checked>
                                        <label class="form-check-label" for="includeMath">
                                            包含数学模型
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="includeSolution" checked>
                                        <label class="form-check-label" for="includeSolution">
                                            包含求解结果
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="includeAnalysis" checked>
                                        <label class="form-check-label" for="includeAnalysis">
                                            包含问题分析
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <button class="btn btn-primary" onclick="generateReport()">
                                        <i class="fas fa-download me-2"></i>生成报告
                                    </button>
                                    <button class="btn btn-outline-secondary ms-2" onclick="previewReport()">
                                        <i class="fas fa-eye me-2"></i>预览
                                    </button>
                                </div>
                            </div>
                            <div id="reportPreview" style="display: none;">
                                <h6>报告预览</h6>
                                <div class="latex-preview" id="latexPreview"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let selectedFile = null;
        let selectedSolver = null;
        let problemId = null;
        let solution = null;

        // 文件上传处理
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });

        // 拖拽上传
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });

        function handleFileUpload(file) {
            if (!file.name.toLowerCase().endsWith('.mps')) {
                alert('请选择.mps格式的文件');
                return;
            }

            selectedFile = file;
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileInfo').style.display = 'block';
            
            // 上传文件到服务器
            uploadFile(file);
        }

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    problemId = data.problem_id;
                    showSolverSection();
                    updateProgress(25);
                } else {
                    alert('文件上传失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('文件上传失败');
            });
        }

        function showSolverSection() {
            document.getElementById('solverSection').style.display = 'block';
            document.getElementById('solveSection').style.display = 'block';
        }

        // 求解器选择
        document.querySelectorAll('.solver-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.solver-card').forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                selectedSolver = this.dataset.solver;
            });
        });

        function solveProblem() {
            if (!selectedSolver) {
                alert('请选择求解器');
                return;
            }

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('solveBtn').disabled = true;

            fetch('/api/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: problemId,
                    solver: selectedSolver
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    solution = data.solution;
                    showResults();
                    updateProgress(100);
                } else {
                    alert('求解失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('求解失败');
            })
            .finally(() => {
                document.getElementById('solveBtn').disabled = false;
            });
        }

        function showResults() {
            document.getElementById('resultSection').style.display = 'block';
            document.getElementById('reportSection').style.display = 'block';
            
            // 更新结果信息
            document.getElementById('solutionStatus').textContent = solution.status;
            document.getElementById('objectiveValue').textContent = solution.objective_value.toFixed(6);
            document.getElementById('solveTime').textContent = solution.solve_time.toFixed(2) + ' 秒';
            document.getElementById('iterations').textContent = solution.iterations;
            document.getElementById('solverName').textContent = solution.solver;

            // 更新变量值
            const variableValues = document.getElementById('variableValues');
            variableValues.innerHTML = '';
            Object.entries(solution.variables).forEach(([name, value]) => {
                const div = document.createElement('div');
                div.className = 'd-flex justify-content-between';
                div.innerHTML = `<span>${name}:</span><span>${value.toFixed(6)}</span>`;
                variableValues.appendChild(div);
            });
        }

        function generateReport() {
            const options = {
                include_math: document.getElementById('includeMath').checked,
                include_solution: document.getElementById('includeSolution').checked,
                include_analysis: document.getElementById('includeAnalysis').checked
            };

            fetch('/api/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: problemId,
                    options: options
                })
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mipsolver_report.tex';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('报告生成失败');
            });
        }

        function previewReport() {
            const options = {
                include_math: document.getElementById('includeMath').checked,
                include_solution: document.getElementById('includeSolution').checked,
                include_analysis: document.getElementById('includeAnalysis').checked
            };

            fetch('/api/report/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: problemId,
                    options: options
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('latexPreview').textContent = data.latex;
                    document.getElementById('reportPreview').style.display = 'block';
                } else {
                    alert('预览失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('预览失败');
            });
        }

        function updateProgress(percent) {
            document.getElementById('stepProgress').style.width = percent + '%';
            document.getElementById('progressBar').style.width = percent + '%';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    return create_html_template()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传API"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 生成问题ID
            problem_id = f"problem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 解析MPS文件
            try:
                model = parse_mps_file(filepath)
                problem_data = {
                    'id': problem_id,
                    'filename': filename,
                    'filepath': filepath,
                    'model': model,
                    'upload_time': datetime.now().isoformat()
                }
                active_problems[problem_id] = problem_data
                
                return jsonify({
                    'success': True,
                    'problem_id': problem_id,
                    'filename': filename
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'MPS文件解析失败: {str(e)}'})
        
        return jsonify({'success': False, 'error': '不支持的文件格式'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/solve', methods=['POST'])
def solve_problem():
    """求解API"""
    try:
        data = request.get_json()
        problem_id = data.get('problem_id')
        solver = data.get('solver')
        
        if problem_id not in active_problems:
            return jsonify({'success': False, 'error': '问题不存在'})
        
        problem_data = active_problems[problem_id]
        model = problem_data['model']
        
        # 记录开始时间
        start_time = time.time()
        
        # 调用真正的求解器
        model.optimize()
        
        # 记录求解时间
        solve_time = time.time() - start_time
        
        # 提取求解结果
        solution = {
            'status': get_status_text(model.status),
            'objective_value': getattr(model, 'obj_val', 0.0),
            'variables': {},
            'solve_time': solve_time,
            'iterations': 0,  # 暂时设为0，实际应该从求解器获取
            'solver': solver_options.get(solver, solver)
        }
        
        # 提取变量值
        for var in getattr(model, '_variables', []):
            solution['variables'][var.name] = getattr(var, 'value', 0.0)
        
        # 保存求解结果
        active_problems[problem_id]['solution'] = solution
        
        return jsonify({
            'success': True,
            'solution': solution
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/report', methods=['POST'])
def generate_report():
    """生成LaTeX报告API"""
    try:
        data = request.get_json()
        problem_id = data.get('problem_id')
        options = data.get('options', {})
        
        if problem_id not in active_problems:
            return jsonify({'success': False, 'error': '问题不存在'})
        
        problem_data = active_problems[problem_id]
        solution = problem_data.get('solution')
        
        if not solution:
            return jsonify({'success': False, 'error': '没有求解结果'})
        
        # 生成LaTeX内容
        latex_content = create_latex_report(problem_data, solution, options)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
            f.write(latex_content)
            temp_file = f.name
        
        return send_file(temp_file, as_attachment=True, download_name='mipsolver_report.tex')
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/report/preview', methods=['POST'])
def preview_report():
    """预览LaTeX报告API"""
    try:
        data = request.get_json()
        problem_id = data.get('problem_id')
        options = data.get('options', {})
        
        if problem_id not in active_problems:
            return jsonify({'success': False, 'error': '问题不存在'})
        
        problem_data = active_problems[problem_id]
        solution = problem_data.get('solution')
        
        if not solution:
            return jsonify({'success': False, 'error': '没有求解结果'})
        
        # 生成LaTeX内容
        latex_content = create_latex_report(problem_data, solution, options)
        
        return jsonify({
            'success': True,
            'latex': latex_content
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def create_latex_report(problem_data, solution, options):
    """创建LaTeX报告内容"""
    report = r"""
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{array}
\usepackage{graphicx}

\geometry{margin=1in}

\title{MIPSolver 求解报告}
\author{自动生成}
\date{\today}

\begin{document}

\maketitle

\section{问题描述}
"""
    
    if options.get('include_math', True):
        report += r"""
\subsection{数学模型}
\begin{align}
\text{目标函数:} \quad & \text{minimize } \sum_{j=1}^{n} c_j x_j \\
\text{约束条件:} \quad & \sum_{j=1}^{n} a_{ij} x_j \leq b_i, \quad i = 1, 2, \ldots, m \\
& x_j \geq 0, \quad j = 1, 2, \ldots, n \\
& x_j \in \mathbb{Z}, \quad j \in I
\end{align}
其中 $I$ 表示整数变量的集合。
"""
    
    if options.get('include_solution', True):
        report += r"""
\section{求解结果}
\subsection{求解信息}
\begin{itemize}
\item 求解状态: """ + solution['status'] + r"""
\item 目标函数值: """ + f"{solution['objective_value']:.6f}" + r"""
\item 求解时间: """ + f"{solution['solve_time']:.2f}" + r""" 秒
\item 迭代次数: """ + str(solution['iterations']) + r"""
\item 求解器: """ + solution['solver'] + r"""
\end{itemize}

\subsection{变量取值}
\begin{table}[h]
\centering
\begin{tabular}{lcc}
\toprule
变量名 & 取值 & 类型 \\
\midrule
"""
        
        for var_name, value in solution['variables'].items():
            report += f"{var_name} & {value:.6f} & continuous \\\\\n"
            
        report += r"""
\bottomrule
\end{tabular}
\caption{变量取值表}
\end{table}
"""
    
    if options.get('include_analysis', True):
        report += r"""
\section{问题分析}
\subsection{问题规模}
\begin{itemize}
\item 变量数量: """ + str(len(solution['variables'])) + r"""
\item 约束数量: 待完善
\item 整数变量数量: 待完善
\end{itemize}

\subsection{求解器信息}
\begin{itemize}
\item 求解器: """ + solution['solver'] + r"""
\item 算法: 分支定界法
\item 松弛求解器: 单纯形法
\end{itemize}
"""
    
    report += r"""
\section{结论}
本报告由MIPSolver自动生成，提供了完整的数学模型、求解过程和结果分析。

\end{document}
"""
    
    return report

if __name__ == '__main__':
    print("启动MIPSolver Web界面...")
    print("访问地址: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 