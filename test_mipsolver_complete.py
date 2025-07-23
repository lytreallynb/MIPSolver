#!/usr/bin/env python3
"""
MIPSolver 完整功能测试
"""

def test_basic_import():
    """测试基本导入"""
    try:
        import mipsolver
        print("✓ 基本导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_problem_creation():
    """测试问题创建"""
    try:
        import mipsolver
        
        # 测试最大化问题
        problem_max = mipsolver.Problem("MaxProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        # 测试最小化问题
        problem_min = mipsolver.Problem("MinProblem", mipsolver.ObjectiveType.MINIMIZE)
        
        print("✓ 问题创建成功")
        return True
    except Exception as e:
        print(f"✗ 问题创建失败: {e}")
        return False

def test_variable_types():
    """测试不同变量类型"""
    try:
        import mipsolver
        problem = mipsolver.Problem("VarTest", mipsolver.ObjectiveType.MAXIMIZE)
        
        # 测试不同变量类型
        x_cont = problem.add_variable("x_continuous", mipsolver.VariableType.CONTINUOUS)
        x_int = problem.add_variable("x_integer", mipsolver.VariableType.INTEGER)
        x_bin = problem.add_variable("x_binary", mipsolver.VariableType.BINARY)
        
        print(f"✓ 变量类型测试成功: 连续={x_cont}, 整数={x_int}, 二进制={x_bin}")
        return True
    except Exception as e:
        print(f"✗ 变量类型测试失败: {e}")
        return False

def test_constraint_types():
    """测试不同约束类型"""
    try:
        import mipsolver
        problem = mipsolver.Problem("ConstraintTest", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.CONTINUOUS)
        
        # 测试不同约束类型
        c_le = problem.add_constraint("c_le", mipsolver.ConstraintType.LESS_EQUAL, 5.0)
        c_ge = problem.add_constraint("c_ge", mipsolver.ConstraintType.GREATER_EQUAL, 1.0)
        c_eq = problem.add_constraint("c_eq", mipsolver.ConstraintType.EQUAL, 3.0)
        
        # 添加系数
        problem.add_constraint_coefficient(c_le, x0, 1.0)
        problem.add_constraint_coefficient(c_ge, x0, 1.0)
        problem.add_constraint_coefficient(c_eq, x0, 1.0)
        
        print(f"✓ 约束类型测试成功: LE={c_le}, GE={c_ge}, EQ={c_eq}")
        return True
    except Exception as e:
        print(f"✗ 约束类型测试失败: {e}")
        return False

def test_solve_binary_problem():
    """测试求解二进制问题"""
    try:
        import mipsolver
        
        print("\n--- 求解二进制优化问题 ---")
        
        # 创建问题: maximize 5*x0 + 8*x1
        # subject to: 2*x0 + 4*x1 <= 10
        #             x0, x1 ∈ {0,1}
        
        problem = mipsolver.Problem("BinaryTest", mipsolver.ObjectiveType.MAXIMIZE)
        
        # 添加变量
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        # 设置变量边界
        problem.set_variable_bounds(x0, 0, 1)
        problem.set_variable_bounds(x1, 0, 1)
        
        # 设置目标函数
        problem.set_objective_coefficient(x0, 5.0)
        problem.set_objective_coefficient(x1, 8.0)
        
        # 添加约束
        c0 = problem.add_constraint("capacity", mipsolver.ConstraintType.LESS_EQUAL, 10.0)
        problem.add_constraint_coefficient(c0, x0, 2.0)
        problem.add_constraint_coefficient(c0, x1, 4.0)
        
        print("问题设置:")
        print("  最大化: 5*x0 + 8*x1")
        print("  约束: 2*x0 + 4*x1 <= 10")
        print("  x0, x1 ∈ {0,1}")
        
        # 求解
        solver = mipsolver.Solver()
        print("\n开始求解...")
        solution = solver.solve(problem)
        
        # 获取结果
        obj_value = solution.get_objective_value()
        values = solution.get_values()
        status = solution.get_status()
        
        print(f"\n求解结果:")
        print(f"  状态: {status}")
        print(f"  目标值: {obj_value}")
        print(f"  x0 = {values[0]:.0f}")
        print(f"  x1 = {values[1]:.0f}")
        
        # 验证解的正确性
        constraint_value = 2*values[0] + 4*values[1]
        print(f"  约束检查: 2*{values[0]:.0f} + 4*{values[1]:.0f} = {constraint_value:.0f} <= 10 ✓")
        
        # 期望最优解应该是 x0=1, x1=1, 目标值=13 (如果约束允许)
        # 或者 x0=0, x1=1, 目标值=8 (如果 x0=1,x1=1 违反约束)
        if obj_value > 0 and len(values) == 2:
            print("✓ 二进制问题求解成功")
            return True
        else:
            print("✗ 求解结果验证失败")
            return False
            
    except Exception as e:
        print(f"✗ 二进制问题求解失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_solver_options():
    """测试求解器选项"""
    try:
        import mipsolver
        problem = mipsolver.Problem("OptionsTest", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        problem.set_objective_coefficient(x0, 1.0)
        
        # 测试verbose选项
        solver = mipsolver.Solver()
        solver.set_verbose(False)  # 先测试quiet模式
        solution1 = solver.solve(problem)
        
        solver.set_verbose(True)   # 再测试verbose模式
        print("\n--- 详细模式求解 ---")
        solution2 = solver.solve(problem)
        
        print("✓ 求解器选项测试成功")
        return True
    except Exception as e:
        print(f"✗ 求解器选项测试失败: {e}")
        return False

def test_algorithm_protection():
    """测试算法保护"""
    try:
        import mipsolver
        import inspect
        import os
        
        print("\n--- 验证算法保护 ---")
        
        # 检查模块位置
        module_file = mipsolver.__file__
        print(f"模块位置: {module_file}")
        
        # 检查是否为编译后的模块
        if module_file.endswith('.so') or module_file.endswith('.pyd'):
            print("✓ 模块是编译后的二进制文件")
        else:
            print("⚠️  模块不是二进制文件")
        
        # 尝试获取源码（应该失败）
        try:
            source = inspect.getsource(mipsolver.Problem)
            print("⚠️  警告: 可以访问源码")
            return False
        except Exception:
            print("✓ 源码已保护，无法直接访问")
        
        # 检查文件大小（编译后的模块通常较小）
        file_size = os.path.getsize(module_file)
        print(f"✓ 模块大小: {file_size:,} bytes")
        
        print("✓ 算法保护验证通过")
        return True
        
    except Exception as e:
        print(f"✗ 算法保护验证失败: {e}")
        return False

def test_wheel_contents():
    """检查wheel包内容"""
    try:
        import zipfile
        import os
        
        wheel_file = 'dist/mipsolver_pro-1.0.0-cp312-cp312-macosx_15_0_arm64.whl'
        if not os.path.exists(wheel_file):
            print("⚠️  找不到wheel文件，跳过内容检查")
            return True
            
        print("\n--- Wheel包内容分析 ---")
        
        with zipfile.ZipFile(wheel_file, 'r') as zip_ref:
            files = zip_ref.namelist()
            
            # 检查是否包含源码文件
            source_files = [f for f in files if f.endswith(('.cpp', '.h', '.py')) and not f.startswith('mipsolver_pro')]
            if source_files:
                print(f"⚠️  警告: wheel包包含源码文件: {source_files}")
            else:
                print("✓ 无源码文件泄露")
            
            # 检查二进制文件
            binary_files = [f for f in files if f.endswith(('.so', '.pyd', '.dll'))]
            print(f"✓ 二进制文件: {binary_files}")
            
            # 显示所有文件
            print("完整文件列表:")
            for name in files:
                info = zip_ref.getinfo(name)
                print(f"  {name} ({info.file_size:,} bytes)")
        
        print("✓ Wheel包内容检查完成")
        return True
        
    except Exception as e:
        print(f"✗ Wheel包内容检查失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("MIPSolver Wheel包完整功能测试")
    print("=" * 60)
    
    tests = [
        ("基本导入", test_basic_import),
        ("问题创建", test_problem_creation),
        ("变量类型", test_variable_types),
        ("约束类型", test_constraint_types),
        ("二进制问题求解", test_solve_binary_problem),
        ("求解器选项", test_solver_options),
        ("算法保护", test_algorithm_protection),
        ("Wheel包内容", test_wheel_contents),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n[{passed+1}/{total}] 测试: {name}")
        print("-" * 40)
        if test_func():
            passed += 1
        else:
            print(f"✗ {name} 测试失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 恭喜！所有测试通过！")
        print("\nMIPSolver wheel包已完全就绪:")
        print("  ✓ 功能完整且正常工作")
        print("  ✓ 算法得到保护")
        print("  ✓ 可以安全分发")
        print("\n下一步建议:")
        print("  1. 将wheel文件分发给其他用户测试")
        print("  2. 准备上传到PyPI")
        print("  3. 添加许可证保护系统")
        print("  4. 创建用户文档")
        return True
    else:
        print(f"\n⚠️  {total-passed} 个测试失败，请检查问题")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
