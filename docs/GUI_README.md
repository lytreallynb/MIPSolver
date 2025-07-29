# MIPSolver GUI界面使用指南

## 概述

MIPSolver提供了两种用户友好的界面：

1. **桌面GUI界面** (`gui_solver.py`) - 基于tkinter的桌面应用
2. **Web界面** (`web_gui.py`) - 基于Flask的现代化Web应用

## 功能特性

### 核心功能
- **文件上传**: 支持MPS格式文件上传
- **求解器选择**: 多种求解器可选（分支定界、单纯形法等）
- **实时求解**: 可视化求解进度
- **结果展示**: 详细的求解结果和变量取值
- **LaTeX报告**: 自动生成专业的LaTeX格式报告

### 界面特性
- **现代化设计**: 美观的用户界面
- **拖拽上传**: 支持文件拖拽上传
- **实时反馈**: 求解进度实时显示
- **响应式布局**: 适配不同屏幕尺寸

## 快速开始

### 方法一：桌面GUI界面

```bash
# 启动桌面GUI
./start_gui.sh
```

**使用步骤：**
1. 点击"浏览"选择MPS文件
2. 选择求解器（分支定界法、单纯形法等）
3. 点击"开始求解"
4. 查看求解结果
5. 生成LaTeX报告

### 方法二：Web界面

```bash
# 启动Web界面
./start_web.sh
```

然后在浏览器中访问：`http://localhost:5000`

**使用步骤：**
1. 拖拽或点击上传MPS文件
2. 选择求解器
3. 点击"开始求解"
4. 查看结果和生成报告

## 界面详解

### 文件上传标签页
- **文件选择**: 支持.mps格式文件
- **文件验证**: 自动验证文件格式
- **上传状态**: 实时显示上传进度

### 模型构建标签页
- **变量管理**: 添加、编辑变量
- **约束管理**: 添加线性约束
- **目标函数**: 设置最大化/最小化目标

### 求解结果标签页
- **求解信息**: 状态、目标值、时间、迭代次数
- **变量取值**: 表格形式显示所有变量取值
- **结果验证**: 自动验证解的可行性

### LaTeX报告标签页
- **报告选项**: 选择包含的内容
- **实时预览**: 预览LaTeX代码
- **文件下载**: 保存.tex文件

## 支持的求解器

| 求解器 | 类型 | 适用问题 | 特点 |
|--------|------|----------|------|
| 分支定界法 | 开源 | 混合整数规划 | 适合小到中等规模问题 |
| 单纯形法 | 开源 | 线性规划 | 快速求解LP问题 |
| Gurobi | 商业 | 大规模MIP | 高性能商业求解器 |
| CPLEX | 商业 | 大规模MIP | IBM商业求解器 |

## LaTeX报告内容

生成的LaTeX报告包含：

### 报告结构
1. **问题描述**
   - 数学模型
   - 变量定义
   - 约束条件

2. **求解结果**
   - 求解状态
   - 目标函数值
   - 求解时间
   - 迭代次数

3. **变量取值**
   - 变量名称
   - 最优取值
   - 变量类型

4. **问题分析**
   - 问题规模统计
   - 求解器信息
   - 算法说明

### 报告示例

```latex
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{booktabs}

\title{MIPSolver 求解报告}
\author{自动生成}
\date{\today}

\begin{document}
\maketitle

\section{问题描述}
\subsection{数学模型}
\begin{align}
\text{目标函数:} \quad & \text{minimize } \sum_{j=1}^{n} c_j x_j \\
\text{约束条件:} \quad & \sum_{j=1}^{n} a_{ij} x_j \leq b_i
\end{align}

\section{求解结果}
\subsection{求解信息}
\begin{itemize}
\item 求解状态: OPTIMAL
\item 目标函数值: 42.000000
\item 求解时间: 2.50 秒
\item 迭代次数: 15
\end{itemize}

\section{变量取值}
\begin{table}[h]
\centering
\begin{tabular}{lcc}
\toprule
变量名 & 取值 & 类型 \\
\midrule
x1 & 10.000000 & continuous \\
x2 & 5.000000 & continuous \\
x3 & 0.000000 & continuous \\
\bottomrule
\end{tabular}
\end{table}

\end{document}
```

## 技术架构

### 桌面GUI架构
```
gui_solver.py
├── tkinter界面
├── 文件处理
├── 求解器接口
└── LaTeX生成
```

### 🌐 Web界面架构
```
web_gui.py
├── Flask后端
├── Bootstrap前端
├── AJAX通信
└── RESTful API
```

### 依赖关系
- **Python 3.7+**
- **tkinter** (桌面GUI)
- **Flask** (Web界面)
- **mipsolver** (核心求解器)

## 故障排除

### 常见问题

1. **tkinter未安装**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # macOS
   brew install python-tk
   ```

2. **Flask未安装**
   ```bash
   pip3 install flask flask-cors werkzeug
   ```

3. **文件上传失败**
   - 检查文件格式是否为.mps
   - 确保文件大小不超过16MB
   - 检查文件权限

4. **求解失败**
   - 检查MPS文件格式是否正确
   - 确认问题有可行解
   - 查看错误日志

### 调试模式

```bash
# 桌面GUI调试
python3 -u gui_solver.py

# Web界面调试
python3 -u web_gui.py
```

## 扩展功能

### 插件系统
- 支持自定义求解器
- 支持自定义报告模板
- 支持自定义界面主题

### 性能优化
- 大文件分块处理
- 求解进度缓存
- 结果数据压缩

### 🔒 安全特性
- 文件类型验证
- 文件大小限制
- 临时文件清理

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: support@mipsolver.com
- 🐛 Issues: GitHub Issues
- 文档: 项目Wiki 