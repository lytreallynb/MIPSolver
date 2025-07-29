# MIPSolver 跨平台桌面应用程序指南

## 跨平台支持证明

MIPSolver 是真正的跨平台应用程序，支持以下操作系统：

### 支持的平台
- **macOS** (Intel x64 / Apple Silicon arm64)
- **Windows** (x64 / x86)
- **Linux** (x64 / arm64)

## 跨平台架构设计

### 1. C++ 求解器后端
- **macOS**: `_solver.cpython-312-darwin.so`
- **Windows**: `_solver.cpython-312-win_amd64.pyd`
- **Linux**: `_solver.cpython-312-linux-x86_64.so`

### 2. Python GUI 前端
- 使用 `tkinter` - Python 标准库，所有平台原生支持
- 自动适配系统外观和字体

### 3. 构建系统
- **PyInstaller** 自动检测平台并生成对应格式：
  - macOS: `.app` 应用程序包
  - Windows: `.exe` 可执行文件
  - Linux: 可执行二进制文件

## Windows 使用指南

### 在 Windows 上构建
```bash
# 在 Windows 系统上运行
python build.py
# 输出: MIPSolver-v1.0-Windows-x64.zip
```

### Windows 安装步骤
1. **下载**: `MIPSolver-v1.0-Windows-x64.zip`
2. **解压**: 解压到任意文件夹（如 `C:\MIPSolver\`）
3. **运行**: 双击 `MIPSolver.exe` 启动

### Windows 系统要求
- **操作系统**: Windows 10/11 (x64)
- **运行库**: 无需额外安装（已打包所有依赖）
- **内存**: 最少 512MB RAM
- **磁盘**: 100MB 可用空间

## Linux 使用指南

### 在 Linux 上构建
```bash
# 在 Linux 系统上运行
python3 build.py
# 输出: MIPSolver-v1.0-Linux-x86_64.zip
```

### Linux 安装步骤
1. **下载**: `MIPSolver-v1.0-Linux-x86_64.zip`
2. **解压**: `unzip MIPSolver-v1.0-Linux-x86_64.zip`
3. **授权**: `chmod +x MIPSolver-v1.0-Linux-x86_64/MIPSolver`
4. **运行**: `./MIPSolver-v1.0-Linux-x86_64/MIPSolver`

### Linux 系统要求
- **发行版**: Ubuntu 18.04+, CentOS 7+, Debian 9+ 等
- **桌面环境**: GNOME, KDE, XFCE 等（需要 X11 支持）
- **依赖**: 系统已包含所需库

## 跨平台特性验证

### 1. 界面适配
- **macOS**: 原生 Aqua 外观，支持深色模式
- **Windows**: Windows 10/11 原生样式
- **Linux**: 根据 GTK 主题自动适配

### 2. 文件路径处理
```python
# 使用 pathlib 确保跨平台兼容
from pathlib import Path
file_path = Path("examples") / "test.mps"  # 自动适配路径分隔符
```

### 3. 字体支持
- **macOS**: 系统字体 + PingFang SC (中文)
- **Windows**: 系统字体 + Microsoft YaHei (中文)
- **Linux**: 系统字体 + 文泉驿/思源黑体 (中文)

### 4. LaTeX 报告
- **XeLaTeX** 引擎，所有平台统一支持中文
- 自动检测系统可用字体

## 构建输出对比

| 平台 | 应用程序文件 | 分发包名称 | 大小预估 |
|------|--------------|------------|----------|
| **macOS** | `MIPSolver.app` | `MIPSolver-v1.0-macOS-arm64.zip` | ~50MB |
| **Windows** | `MIPSolver.exe` | `MIPSolver-v1.0-Windows-x64.zip` | ~45MB |
| **Linux** | `MIPSolver` | `MIPSolver-v1.0-Linux-x86_64.zip` | ~40MB |

## 自动化构建流程

### GitHub Actions 支持 (可选)
```yaml
# .github/workflows/build.yml
name: Cross-platform Build
on: [push, pull_request]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Build Application
        run: python build.py
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: MIPSolver-${{ matrix.os }}
          path: dist/*.zip
```

## 平台特定注意事项

### Windows
- 可能需要添加防病毒软件白名单
- 首次运行可能显示"Windows 保护了你的电脑"提示，点击"仍要运行"

### macOS
- 首次运行可能需要在"系统偏好设置 > 安全性与隐私"中允许运行
- 支持 Apple Silicon (M1/M2) 和 Intel 处理器

### Linux
- 需要图形桌面环境
- 部分发行版可能需要安装额外的 GUI 库

## 验证跨平台兼容性

可以通过以下方式验证应用程序的跨平台特性：

1. **虚拟机测试**: 在 VirtualBox/VMware 中测试不同操作系统
2. **容器化测试**: 使用 Docker 容器模拟不同 Linux 发行版
3. **云端测试**: 使用 GitHub Actions 或 GitLab CI 自动构建
4. **用户测试**: 分发给不同平台用户进行实际测试

---

这样的架构设计确保了 MIPSolver 能够在各个主流操作系统上提供一致的用户体验，同时充分利用各平台的原生特性。