# MIPSolver 安装指南

## 安装方式选择

根据您的使用需求选择合适的安装方式：

### 1. 最终用户 - 桌面应用程序

**推荐方式**：下载预编译的桌面应用程序，无需安装 Python。

- **macOS**: 下载 `MIPSolver-v1.0-macOS-arm64.zip`
- **Windows**: 下载 `MIPSolver-v1.0-Windows-x64.zip`
- **Linux**: 下载 `MIPSolver-v1.0-Linux-x86_64.zip`

解压后直接运行应用程序即可。

### 2. Python 开发者 - 包安装

如果您想在 Python 代码中使用 MIPSolver：

```bash
# 从源码安装
pip install .

# 或从 setup.py 安装
python setup.py install
```

### 3. 开发者 - 源码开发

如果您想参与开发或修改源码：

## 开发环境安装

### 前置要求

#### 系统要求
- **Python**: 3.8+ (推荐 3.11+)
- **C++ 编译器**: 
  - macOS: Xcode Command Line Tools
  - Windows: Visual Studio 2019+ 或 MinGW
  - Linux: GCC 7+ 或 Clang 10+
- **CMake**: 3.12+

#### 安装系统依赖

**macOS**:
```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 使用 Homebrew 安装 CMake
brew install cmake
```

**Windows**:
```bash
# 使用 Chocolatey
choco install cmake visualstudio2022buildtools

# 或下载安装包
# https://cmake.org/download/
# https://visualstudio.microsoft.com/downloads/
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install build-essential cmake python3-dev python3-tk
```

**CentOS/RHEL**:
```bash
sudo yum groupinstall "Development Tools"
sudo yum install cmake3 python3-devel tkinter
```

### Python 依赖安装

#### 方式一：开发环境（推荐）
```bash
# 克隆仓库
git clone https://github.com/lytreallynb/MIPSolver.git
cd MIPSolver

# 安装完整开发依赖
pip install -r requirements-dev.txt

# 以开发模式安装包
pip install -e .
```

#### 方式二：最小环境
```bash
# 仅安装运行时依赖
pip install -r requirements.txt

# 安装包
pip install .
```

#### 方式三：用户环境
```bash
# 最小依赖（生产使用）
pip install -r requirements-minimal.txt
```

## 构建系统

### 构建 C++ 扩展

```bash
# 手动构建 C++ 扩展
python setup.py build_ext --inplace

# 或使用 CMake
mkdir build && cd build
cmake ..
make -j4
```

### 构建桌面应用程序

```bash
# 构建当前平台的桌面应用
cd build
python build.py

# 构建特定平台（如果支持交叉编译）
python build.py --platform windows
python build.py --platform linux
```

## 验证安装

### 测试核心功能
```python
import mipsolver
print(f"MIPSolver 版本: {mipsolver.__version__}")
print(f"C++ 求解器可用: {mipsolver._has_solver}")
```

### 测试 GUI 应用
```bash
# 启动 GUI 界面
python main.py

# 或使用脚本
./scripts/start_gui.sh
```

### 运行测试套件
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_mps.py
python tests/test_xelatex_report.py
```

## 常见问题

### tkinter 未找到

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Arch Linux
sudo pacman -S tk
```

### C++ 编译错误

**检查编译器**:
```bash
# 检查 GCC 版本
gcc --version

# 检查 CMake 版本
cmake --version

# 检查 Python 开发头文件
python3-config --includes
```

### PyInstaller 构建失败

```bash
# 清理构建缓存
rm -rf build/ dist/ *.egg-info/

# 重新安装 PyInstaller
pip uninstall PyInstaller
pip install PyInstaller>=6.14.0

# 重新构建
cd build && python build.py
```

### 权限问题

**macOS**:
```bash
# 允许运行未签名应用
sudo spctl --master-disable
# 使用后重新启用: sudo spctl --master-enable
```

**Linux**:
```bash
# 添加执行权限
chmod +x dist/MIPSolver
```

## 高级配置

### 开发工具配置

**代码格式化**:
```bash
# 安装 pre-commit hooks
pre-commit install

# 手动运行格式化
black .
isort .
```

**类型检查**:
```bash
mypy mipsolver/
```

### 性能优化

**编译优化**:
```bash
# 使用优化编译
export CXXFLAGS="-O3 -march=native"
python setup.py build_ext --inplace
```

**内存配置**:
```bash
# 设置最大内存使用
export MIPSOLVER_MAX_MEMORY=8GB
```

## 卸载

### 卸载 Python 包
```bash
pip uninstall mipsolver
```

### 清理构建文件
```bash
rm -rf build/ dist/ *.egg-info/
rm -rf __pycache__/ .pytest_cache/
find . -name "*.pyc" -delete
```

## 技术支持

- **文档**: [README.md](README.md)
- **问题报告**: GitHub Issues
- **开发讨论**: GitHub Discussions

---

安装过程中遇到问题？请查看 [故障排除指南](docs/TROUBLESHOOTING.md) 或提交 Issue。