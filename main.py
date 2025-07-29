#!/usr/bin/env python3
"""
MIPSolver 桌面应用程序启动入口
Mixed Integer Programming Solver - Desktop Application

这是MIPSolver的主启动文件，负责：
1. 初始化应用程序环境
2. 检查核心依赖是否可用
3. 启动图形用户界面
4. 处理启动过程中的错误

主要组件说明：
- 环境检查：验证MIPSolver核心模块是否正确安装
- GUI启动：创建并运行基于Tkinter的图形界面
- 错误处理：捕获并显示启动过程中的异常信息
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# 添加当前目录到路径，确保能找到模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_application():
    """
    设置应用程序环境
    
    功能描述：
    - 检查MIPSolver核心模块是否可用
    - 验证C++求解器后端是否正确编译和链接
    - 输出版本信息和求解器状态
    
    返回值：
    - True: 环境检查通过，可以正常启动
    - False: 环境检查失败，缺少必要组件
    
    异常处理：
    - ImportError: 核心模块导入失败时显示错误消息
    """
    try:
        # 检查关键依赖
        import mipsolver
        print(f"MIPSolver版本: {mipsolver.__version__}")
        print(f"C++求解器可用: {mipsolver._has_solver}")
        
        return True
    except ImportError as e:
        error_msg = f"无法导入核心模块: {e}"
        messagebox.showerror("启动错误", error_msg)
        return False

def main():
    """
    主函数 - 应用程序入口点
    
    执行流程：
    1. 显示启动横幅信息
    2. 调用环境设置函数检查依赖
    3. 导入并创建GUI应用实例
    4. 配置窗口属性（标题、图标等）
    5. 启动GUI主事件循环
    
    错误处理：
    - 环境检查失败时退出程序
    - GUI启动异常时显示详细错误信息
    - 所有异常都会被捕获并显示给用户
    """
    print("=" * 50)
    print("MIPSolver 桌面应用程序")
    print("Mixed Integer Programming Solver")
    print("=" * 50)
    
    # 设置应用程序
    if not setup_application():
        sys.exit(1)
    
    try:
        # 导入并启动GUI
        from gui.gui_solver import MIPSolverGUI
        
        # 创建并运行应用程序
        app = MIPSolverGUI()
        
        # 设置窗口属性
        app.root.title("MIPSolver - 混合整数规划求解器 v1.0")
        
        # 尝试设置窗口图标（如果存在）
        try:
            icon_path = os.path.join(current_dir, "assets", "icon.ico")
            if os.path.exists(icon_path):
                app.root.iconbitmap(icon_path)
        except:
            pass  # 图标加载失败不影响程序运行
        
        print("GUI界面已启动")
        print("准备就绪，可以开始使用！")
        
        # 启动GUI主循环
        app.run()
        
    except Exception as e:
        error_msg = f"启动失败: {str(e)}\n\n详细错误信息:\n{traceback.format_exc()}"
        print(error_msg)
        
        # 创建一个简单的错误对话框
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("MIPSolver 启动错误", error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    main()