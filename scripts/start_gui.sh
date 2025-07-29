#!/bin/bash
# MIPSolver GUI启动脚本

echo "启动MIPSolver GUI界面..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: 未安装tkinter"
    echo "请安装tkinter: pip install tkinter"
    exit 1
fi

# 检查mipsolver模块
python3 -c "import mipsolver" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "警告: 未找到mipsolver模块，将使用模拟数据"
fi

# 启动GUI
echo "正在启动GUI界面..."
python3 gui_solver.py

echo "GUI已关闭" 