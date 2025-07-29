# MIPSolver - 混合整数规划求解器

高性能的混合整数线性规划（MIP）求解器，提供直观的图形界面和强大的求解能力。

## 项目特点

- 高性能C++求解器后端
- 直观的Python GUI界面
- 支持MPS格式文件
- 分支定界和单纯形算法
- LaTeX报告生成（支持中文）
- 跨平台桌面应用程序

## 项目结构

```
MIPSolver/
├── README.md                    # 项目说明
├── main.py                      # 桌面应用程序入口
├── setup.py                     # 安装脚本
├── pyproject.toml              # 项目配置
│
├── docs/                        # 文档
│   ├── CROSS_PLATFORM_GUIDE.md # 跨平台指南
│   ├── WINDOWS_USAGE.md         # Windows使用说明
│   └── GUI_README.md            # GUI使用说明
│
├── src/                         # C++源代码
│   ├── core/                    # 核心求解器
│   ├── solvers/                 # 算法实现
│   ├── api/                     # C API接口
│   └── bindings/                # Python绑定
│
├── mipsolver/                   # Python包
│   ├── model.py                 # 模型定义
│   ├── expressions.py          # 表达式处理
│   └── solver_monitor.py       # 求解监控
│
├── gui/                         # 图形界面
│   ├── gui_solver.py           # 主GUI应用
│   ├── web_gui.py              # Web界面
│   └── api_server.py           # API服务器
│
├── examples/                    # 示例文件
│   └── mps/                    # MPS测试文件
│
├── tests/                       # 测试文件
│   └── test_reports/           # 测试报告
│
├── scripts/                     # 脚本工具
│   ├── start_gui.sh            # 启动GUI
│   └── create_tools.sh         # 创建工具
│
├── build/                       # 构建系统
│   ├── build.py                # 主构建脚本
│   ├── mipsolver.spec          # PyInstaller配置
│   └── assets/                 # 构建资源
│
├── dist/                        # 分发文件
└── temp/                        # 临时文件
```

## 快速开始

### 开发环境

1. **安装依赖**
   ```bash
   # 完整开发环境
   pip install -r requirements-dev.txt
   
   # 或仅安装运行时依赖
   pip install -r requirements.txt
   ```

2. **启动GUI应用**
   ```bash
   python main.py
   # 或使用脚本
   ./scripts/start_gui.sh
   ```

3. **Web界面**
   ```bash
   python gui/web_gui.py
   # 或使用脚本
   ./scripts/start_web.sh
   ```

### 桌面应用程序

1. **构建桌面应用**
   ```bash
   cd build
   python build.py
   ```

2. **运行构建的应用**
   - **macOS**: 双击 `dist/MIPSolver.app`
   - **Windows**: 双击 `dist/MIPSolver.exe`
   - **Linux**: 运行 `./dist/MIPSolver`

## 使用说明

### 基本操作

1. **导入问题文件**: 选择MPS格式文件
2. **选择求解器**: Branch & Bound 或 Simplex LP
3. **开始求解**: 查看实时进度和结果
4. **生成报告**: 创建专业的LaTeX报告

### 支持的文件格式

- **MPS**: Mathematical Programming System格式
- **示例文件**: `examples/mps/` 目录包含测试文件

## 开发指南

### 构建系统

- **C++编译**: 使用CMake构建核心库
- **Python打包**: 使用PyInstaller创建独立应用
- **跨平台**: 支持macOS、Windows、Linux

### 测试

```bash
# 运行测试
python -m pytest tests/

# 测试报告生成
python tests/test_xelatex_report.py
```

## 文档

- [跨平台部署指南](docs/CROSS_PLATFORM_GUIDE.md)
- [Windows使用说明](docs/WINDOWS_USAGE.md)
- [GUI界面说明](docs/GUI_README.md)

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交Issue和Pull Request来改进项目。

---

© 2025 MIPSolver Team. All rights reserved.