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