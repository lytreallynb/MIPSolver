# MIPSolver

高性能混合整数规划求解器，提供现代化Python API。

## 安装

```bash
pip install mipsolver
```

## 快速开始

```python
import mipsolver as mp

# 创建优化模型
model = mp.Model("example")

# 添加变量
x = model.add_var(vtype=mp.BINARY, name="x")
y = model.add_var(vtype=mp.BINARY, name="y")

# 设置目标函数
model.set_objective(5*x + 8*y, mp.MAXIMIZE)

# 添加约束
model.add_constr(2*x + 4*y <= 10, "capacity")

# 求解
model.optimize()

# 获取结果
print(f"最优值: {model.obj_val}")
print(f"x = {x.value}, y = {y.value}")
```

## 特性

- 🚀 高性能C++求解器核心
- 🐍 现代化Python API
- 📊 支持二进制、整数和连续变量
- 📁 MPS文件格式支持
- 🌐 跨平台兼容性
- 💻 完整类型提示支持

## 许可证

MIT License
