#!/usr/bin/env python3
"""
MIPSolver 跨平台构建脚本
Cross-platform build script for MIPSolver desktop application
"""

import os
import sys
import platform
import subprocess
import zipfile
import shutil
from pathlib import Path

class MIPSolverBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.dist_dir = self.base_dir / 'dist'
        self.build_dir = self.base_dir / 'build'
        self.platform = platform.system().lower()
        self.arch = platform.machine()
        
        print(f"构建平台: {self.platform} ({self.arch})")
        print(f"Python版本: {sys.version}")
        
    def clean_build(self):
        """清理之前的构建文件"""
        print("清理构建目录...")
        
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"   删除: {directory}")
        
        # 清理PyInstaller缓存
        pycache_dirs = list(self.base_dir.rglob('__pycache__'))
        for cache_dir in pycache_dirs:
            shutil.rmtree(cache_dir)
            
        print("清理完成")
    
    def check_dependencies(self):
        """检查构建依赖"""
        print("检查构建依赖...")
        
        try:
            import PyInstaller
            print(f"   PyInstaller: {PyInstaller.__version__}")
        except ImportError:
            print("错误: PyInstaller未安装")
            return False
            
        try:
            import mipsolver
            print(f"   MIPSolver: {mipsolver.__version__}")
            print(f"   C++求解器: {'可用' if mipsolver._has_solver else '不可用'}")
        except ImportError:
            print("错误: MIPSolver模块未找到")
            return False
            
        return True
    
    def create_assets(self):
        """创建应用程序资源"""
        print("创建应用程序资源...")
        
        assets_dir = self.base_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        
        # 创建简单的应用程序图标（文本形式，实际应用中应该使用真实图标）
        self.create_simple_icon(assets_dir)
        
        # 创建版本信息文件（Windows）
        if self.platform == 'windows':
            self.create_version_info()
            
        print("资源创建完成")
    
    def create_simple_icon(self, assets_dir):
        """创建简单的应用程序图标"""
        # 这里应该放置真实的图标文件
        # 现在创建一个占位符
        icon_info = assets_dir / 'icon_info.txt'
        with open(icon_info, 'w', encoding='utf-8') as f:
            f.write("""
MIPSolver 应用程序图标说明
========================

要添加自定义图标，请将以下文件放在 assets/ 目录中：

Windows: icon.ico (建议大小: 256x256, 包含多种尺寸)
macOS: icon.icns (使用 iconutil 从 iconset 创建)
Linux: icon.png (建议大小: 256x256)

图标设计建议：
- 使用简洁的数学符号或图表元素
- 主色调：蓝色或绿色（专业感）
- 包含"MIP"字样或优化相关符号
""")
    
    def create_version_info(self):
        """创建Windows版本信息文件"""
        version_info = """
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'MIPSolver Team'),
        StringStruct(u'FileDescription', u'Mixed Integer Programming Solver'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'MIPSolver'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025'),
        StringStruct(u'OriginalFilename', u'MIPSolver.exe'),
        StringStruct(u'ProductName', u'MIPSolver'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
        with open(self.base_dir / 'version_info.txt', 'w') as f:
            f.write(version_info)
    
    def build_application(self):
        """构建应用程序"""
        print("开始构建应用程序...")
        
        # 运行PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'mipsolver.spec'
        ]
        
        print(f"运行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.base_dir, check=True, 
                                  capture_output=True, text=True)
            print("构建成功！")
            
            if result.stdout:
                print("构建输出:")
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            print("构建失败！")
            print("错误输出:")
            print(e.stderr)
            return False
            
        return True
    
    def create_distribution(self):
        """创建分发包"""
        print("创建分发包...")
        
        if self.platform == 'darwin':
            app_name = 'MIPSolver.app'
            dist_name = f'MIPSolver-v1.0-macOS-{self.arch}'
        elif self.platform == 'windows':
            app_name = 'MIPSolver.exe'
            dist_name = f'MIPSolver-v1.0-Windows-{self.arch}'
        else:  # Linux
            app_name = 'MIPSolver'
            dist_name = f'MIPSolver-v1.0-Linux-{self.arch}'
        
        app_path = self.dist_dir / app_name
        
        if not app_path.exists():
            print(f"错误: 应用程序文件未找到: {app_path}")
            return False
        
        # 创建分发目录
        dist_package_dir = self.dist_dir / dist_name
        dist_package_dir.mkdir(exist_ok=True)
        
        # 复制应用程序
        if self.platform == 'darwin':
            shutil.copytree(app_path, dist_package_dir / app_name)
        else:
            shutil.copy2(app_path, dist_package_dir / app_name)
        
        # 创建README文件
        self.create_readme(dist_package_dir)
        
        # 复制示例文件
        if (self.base_dir.parent / 'examples' / 'mps').exists():
            shutil.copytree(self.base_dir.parent / 'examples' / 'mps', dist_package_dir / 'examples')
        
        # 创建压缩包
        zip_path = self.dist_dir / f'{dist_name}.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dist_package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(dist_package_dir)
                    zipf.write(file_path, dist_name / arcname)
        
        print(f"分发包已创建: {zip_path}")
        return True
    
    def create_readme(self, dist_dir):
        """创建分发包的README文件"""
        readme_content = f"""
# MIPSolver v1.0 - 混合整数规划求解器

## 系统要求

### {self.platform.title()}
- 操作系统: {platform.platform()}
- 架构: {self.arch}

## 安装说明

### 快速启动
1. 解压缩文件到任意目录
2. 双击运行 MIPSolver{'应用程序' if self.platform == 'darwin' else '.exe' if self.platform == 'windows' else ''}
3. 开始使用！

### 功能特点
- 混合整数线性规划求解
- 支持MPS格式文件导入
- 分支定界和单纯形算法
- LaTeX报告生成（支持中文）
- 直观的图形用户界面

### 使用说明
1. **文件上传**: 点击"浏览"按钮选择MPS格式的问题文件
2. **求解器选择**: 选择"Branch & Bound"或"Simplex (LP)"
3. **开始求解**: 点击"开始求解"按钮
4. **查看结果**: 在"求解结果"标签页查看详细结果
5. **生成报告**: 在"LaTeX报告"标签页生成专业报告

### 示例文件
- examples/ 目录包含多个测试用的MPS文件
- 可以用这些文件测试软件功能

### 技术支持
- 求解引擎: 高性能C++实现
- 界面框架: Python Tkinter
- 支持格式: MPS (Mathematical Programming System)

### 版本信息
- 版本: v1.0.0
- 构建时间: {platform.platform()}
- Python版本: {sys.version.split()[0]}

---
© 2025 MIPSolver Team. All rights reserved.
"""
        
        with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def build(self):
        """完整构建流程"""
        print("开始 MIPSolver 桌面应用程序构建")
        print("=" * 50)
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 清理构建
        self.clean_build()
        
        # 创建资源
        self.create_assets()
        
        # 构建应用程序
        if not self.build_application():
            return False
        
        # 创建分发包
        if not self.create_distribution():
            return False
        
        print("\n构建完成！")
        print("=" * 50)
        print(f"分发文件位置: {self.dist_dir}")
        print("\n可分发的文件:")
        for file_path in self.dist_dir.glob('*.zip'):
            print(f"  {file_path.name}")
        
        return True

def main():
    """主函数"""
    builder = MIPSolverBuilder()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        builder.clean_build()
        return
    
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()