# MIPSolver 项目结构整理计划

## 当前目录分析

### 核心问题
- 文件分散在根目录，缺乏组织结构
- 临时文件和测试文件混杂在主目录
- 构建产物和源代码未分离
- 文档文件位置不统一

## 建议的新目录结构

```
MIPSolver/
├── README.md                           # 主要说明文档
├── LICENSE                             # 开源许可证
├── pyproject.toml                      # Python 项目配置
├── setup.py                            # 安装脚本
├── MANIFEST.in                         # 打包配置
│
├── docs/                               # 文档目录
│   ├── README.md                       # 详细使用说明
│   ├── CROSS_PLATFORM_GUIDE.md        # 跨平台指南
│   ├── WINDOWS_USAGE.md                # Windows 使用说明
│   ├── GUI_README.md                   # GUI 使用说明
│   └── API_REFERENCE.md                # API 参考文档
│
├── src/                                # C++ 源代码
│   ├── core/                           # 核心求解器
│   │   ├── core.cpp
│   │   ├── core.h
│   │   ├── solution.h
│   │   └── sota_algorithms.h
│   ├── solvers/                        # 具体算法实现
│   │   ├── branch_bound_solver.h
│   │   ├── simplex_solver.h
│   │   └── parser.h
│   ├── api/                            # C API 接口
│   │   ├── mipsolver_c_api.cpp
│   │   └── mipsolver_c_api.h
│   └── bindings/                       # Python 绑定
│       └── python_bindings.cpp
│
├── mipsolver/                          # Python 包
│   ├── __init__.py
│   ├── model.py
│   ├── expressions.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── solver_monitor.py
│   └── _solver.cpython-312-darwin.so
│
├── gui/                                # 图形界面
│   ├── gui_solver.py                   # 主 GUI 应用
│   ├── web_gui.py                      # Web 界面
│   ├── interactive_solver.py           # 交互式求解器
│   └── api_server.py                   # API 服务器
│
├── examples/                           # 示例文件
│   ├── mps/                            # MPS 测试文件
│   │   ├── bal8x12.mps
│   │   ├── bk4x3.mps
│   │   └── ...
│   └── python/                         # Python 示例
│       └── basic_usage.py
│
├── tests/                              # 测试文件
│   ├── test_core.py
│   ├── test_mps.py
│   ├── test_gui.py
│   └── test_reports/
│       ├── test_xelatex_report.py
│       └── sample_reports/
│
├── scripts/                            # 脚本工具
│   ├── start_gui.sh
│   ├── start_web.sh
│   ├── start_api.sh
│   ├── start_interactive.sh
│   └── create_tools.sh
│
├── build/                              # 构建系统
│   ├── CMakeLists.txt
│   ├── build.py                        # 主构建脚本
│   ├── build_windows.bat
│   ├── build_linux.sh
│   ├── mipsolver.spec                  # PyInstaller 配置
│   └── assets/                         # 构建资源
│       └── icon_info.txt
│
├── dist/                               # 分发文件（构建产物）
│   └── [构建生成的文件]
│
└── temp/                               # 临时文件
    ├── uploads/                        # 上传临时文件
    ├── reports/                        # 生成的报告
    └── cache/                          # 缓存文件
```

## 文件移动计划

### 1. 文档整理
- `docs/` 目录：收集所有 `.md` 文档文件
- 移动：`CROSS_PLATFORM_GUIDE.md`, `WINDOWS_USAGE.md`, `GUI_README.md`

### 2. 源代码整理
- `src/core/`：核心 C++ 代码
- `src/solvers/`：算法实现
- `src/api/` 和 `src/bindings/`：接口代码

### 3. GUI 应用整理
- `gui/`：所有图形界面相关文件
- 移动：`gui_solver.py`, `web_gui.py`, `interactive_solver.py`, `api_server.py`

### 4. 示例和测试
- `examples/mps/`：MPS 测试文件
- `tests/`：所有测试相关文件

### 5. 构建系统
- `build/`：构建脚本和配置
- `scripts/`：启动脚本

### 6. 临时文件清理
- `temp/`：临时和缓存文件
- 清理：测试报告、日志文件、缓存

## 优势

1. **清晰的模块分离**：核心库、GUI、文档、测试分离
2. **易于维护**：相关文件聚集在一起
3. **标准化结构**：符合 Python 项目最佳实践
4. **构建友好**：构建脚本和产物分离
5. **开发友好**：测试、示例、文档组织有序