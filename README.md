# MIPSolver

高性能混合整数规划求解器，提供现代Python API。

## 特性

- 高性能C++求解器核心
- 友好的Python API
- 支持线性规划和混合整数规划
- 跨平台支持（macOS, Windows, Linux）

## 安装

```bash
pip install mipsolver
```

## 快速开始

```python
import mipsolver as mp

# 创建模型
model = mp.Model("example")

# 添加变量
x = model.add_var(name="x", vtype=mp.BINARY)
y = model.add_var(name="y", vtype=mp.CONTINUOUS, lb=0, ub=10)

# 设置目标函数
model.set_objective(3*x + 5*y, mp.MAXIMIZE)

# 添加约束
model.add_constr(x + 2*y <= 10)
model.add_constr(x >= 0)

# 求解
model.optimize()

# 输出结果
print(f"最优值: {model.obj_val}")
print(f"x = {x.value}")
print(f"y = {y.value}")
```

## 许可证

MIT License
