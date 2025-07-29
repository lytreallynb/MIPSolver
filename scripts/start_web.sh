#!/bin/bash
# MIPSolver Web界面启动脚本

echo "启动MIPSolver Web界面..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Flask
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装Flask..."
    pip3 install flask flask-cors werkzeug
fi

# 检查mipsolver模块
python3 -c "import mipsolver" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "警告: 未找到mipsolver模块，将使用模拟数据"
fi

# 创建uploads目录
mkdir -p uploads

# 启动Web服务器
echo "正在启动Web服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
python3 web_gui.py 