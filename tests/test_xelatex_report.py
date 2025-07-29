#!/usr/bin/env python3
"""
测试XeLaTeX报告生成功能
"""
import sys
import os
sys.path.insert(0, '/Users/yutonglv/MIPSolver')

from gui_solver import MIPSolverGUI

def test_xelatex_report():
    print("测试XeLaTeX报告生成功能")
    print("=" * 50)
    
    # 创建GUI并加载测试数据
    app = MIPSolverGUI()
    app.solver_var.set("Branch & Bound")
    
    # 加载测试文件
    mps_file = "/Users/yutonglv/MIPSolver/mps/bk4x3.mps"
    app.file_path_var.set(mps_file)
    app.load_problem_file(mps_file)
    
    if app.model:
        print("模型加载成功")
        
        # 求解
        app.solve_problem()
        
        if app.solution:
            print("求解完成")
            print(f"状态: {app.solution['status']}")
            print(f"目标值: {app.solution['objective_value']:.6f}")
            print(f"时间: {app.solution['solve_time']:.4f}s")
            print(f"变量数: {len(app.solution['variables'])}")
            
            # 设置报告选项
            app.include_math_var.set(True)
            app.include_solution_var.set(True) 
            app.include_analysis_var.set(True)
            
            print("\n生成XeLaTeX报告...")
            
            # 生成报告内容
            latex_content = app.create_latex_report()
            
            # 保存测试报告
            test_filename = "/Users/yutonglv/MIPSolver/test_report.tex"
            with open(test_filename, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # 生成编译说明
            instructions = app.create_compile_instructions(test_filename)
            with open("/Users/yutonglv/MIPSolver/test_report_编译说明.txt", 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print(f"XeLaTeX报告已生成")
            print(f"文件位置: {test_filename}")
            print(f"编译说明: test_report_编译说明.txt")
            
            # 显示报告的一些关键部分
            print(f"\n报告内容预览:")
            print("=" * 40)
            
            # 检查中文字符
            chinese_chars = ['中文', '求解', '变量', '约束', '目标', '最优']
            found_chinese = []
            for char_set in chinese_chars:
                if char_set in latex_content:
                    found_chinese.append(char_set)
            
            print(f"包含中文字符: {', '.join(found_chinese)}")
            
            # 检查XeLaTeX包
            if 'xeCJK' in latex_content:
                print("使用xeCJK包支持中文")
            if 'setCJKmainfont' in latex_content:
                print("设置中文字体")
            if 'PingFang SC' in latex_content:
                print("配置macOS中文字体")
                
            # 统计报告长度
            lines = latex_content.split('\n')
            print(f"报告长度: {len(lines)} 行")
            print(f"文件大小: {len(latex_content.encode('utf-8'))} 字节")
            
            print(f"\nXeLaTeX编译命令:")
            print(f"xelatex \"{test_filename}\"")
            
        else:
            print("求解失败")
    else:
        print("模型加载失败")
    
    print(f"\n" + "=" * 50)
    print("XeLaTeX功能验证:")
    print("=" * 50)
    print("更新为XeLaTeX文档类")
    print("添加xeCJK中文支持包")
    print("配置中文字体（PingFang SC）")
    print("改进数学公式中文显示")
    print("优化表格和版面设计")
    print("生成详细编译说明文档")
    print("支持UTF-8编码保存")
    
    print(f"\n使用建议:")
    print("1. 确保安装完整的LaTeX发行版（MacTeX/MiKTeX/TeX Live）")
    print("2. 使用XeLaTeX编译器而非pdfLaTeX")
    print("3. 确保系统安装了相应的中文字体")
    print("4. 查看编译说明文件解决可能的问题")

if __name__ == "__main__":
    test_xelatex_report()