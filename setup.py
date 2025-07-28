# setup.py - 处理C++编译并创建单一包
"""
此setup.py创建包含以下两部分的单一包:
1. 纯Python接口 (我们的优化求解器API)
2. 编译的C++求解器 (实际的优化引擎)

采用成熟的优化求解器分发模式 - 一个包，包含所有功能。
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import pybind11

class CMakeExtension(Extension):
    """
    使用CMake构建C++代码的扩展
    
    这与普通Extension不同，因为我们使用CMake而不是setuptools的
    内置C++编译。CMake为复杂的C++构建提供更好的控制。
    """
    
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    """
    使用CMake编译C++求解器的自定义构建命令
    
    此类处理以下复杂性:
    1. 为目标平台配置CMake
    2. 编译C++源代码
    3. 使用pybind11创建Python绑定
    4. 将所有内容安装到正确位置
    
    最终结果是Python可以导入的编译扩展模块。
    """
    
    def build_extension(self, ext: CMakeExtension) -> None:
        # 找到setuptools希望我们放置编译扩展的位置
        extdir = Path(self.get_ext_fullpath(ext.name)).parent.resolve()
        extdir = os.path.join(extdir, "mipsolver")
        
        # 使用Release模式以获得性能
        build_type = "Release"
        
        # 创建构建目录
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        
        # CMake配置参数
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            f"-Dpybind11_DIR={pybind11.get_cmake_dir()}",
            "-DBUILD_PYTHON_BINDINGS=ON",
        ]
        
        # 平台特定的CMake设置
        if sys.platform == "win32":
            # Windows: 使用Visual Studio生成器
            cmake_args += [
                "-A", "x64" if sys.maxsize > 2**32 else "Win32",
                "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=ON"
            ]
        elif sys.platform == "darwin":
            # macOS: 处理Intel和Apple Silicon
            cmake_args += [
                "-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64"
            ]
        
        # 构建参数
        build_args = ["--config", build_type, "--parallel"]
        
        print(f"在{build_temp}中构建")
        print(f"CMake参数: {' '.join(cmake_args)}")
        
        # 运行CMake配置
        subprocess.run(
            ["cmake", str(ext.sourcedir)] + cmake_args,
            cwd=build_temp,
            check=True
        )
        
        # 运行CMake构建
        subprocess.run(
            ["cmake", "--build", ".", "--target", "_solver"] + build_args,
            cwd=build_temp,
            check=True
        )

def main():
    """
    主setup函数 - 创建单一统一包
    
    这个设计遵循现代优化求解器的最佳实践:
    1. Python API层提供友好接口
    2. C++求解器核心提供高性能计算
    3. pybind11绑定层实现无缝交互
    
    用户通过 'pip install mipsolver' 获得完整功能。
    """
    
    # 查找mipsolver包
    packages = find_packages(include=['mipsolver', 'mipsolver.*'])
    
    # 定义C++扩展模块
    ext_modules = [
        CMakeExtension("_solver", sourcedir=".")
    ]
    
    # 包数据 - 包含类型提示
    package_data = {
        "mipsolver": ["py.typed"]
    }
    
    setup(
        # 包结构
        packages=packages,
        package_data=package_data,
        
        # C++扩展
        ext_modules=ext_modules,
        cmdclass={"build_ext": CMakeBuild},
        
        # 确保包正确工作
        zip_safe=False,
        include_package_data=True,
    )

if __name__ == "__main__":
    main()