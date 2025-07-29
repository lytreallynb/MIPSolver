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