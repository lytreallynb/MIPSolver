import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

class CMakeExtension(Extension):
    def __init__(self, name: str) -> None:
        super().__init__(name, sources=[])

class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        extdir = Path(self.get_ext_fullpath(ext.name)).parent.resolve()
        build_type = "Release"  # 强制Release模式
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        cmake_list_dir = Path(__file__).parent.resolve()

        # 确保pybind11可用
        try:
            import pybind11
            pybind11_cmake_dir = pybind11.get_cmake_dir()
        except ImportError:
            print("pybind11 not found, installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pybind11[global]"])
            import pybind11
            pybind11_cmake_dir = pybind11.get_cmake_dir()

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            f"-Dpybind11_DIR={pybind11_cmake_dir}",
            "-DBUILD_PYTHON_BINDINGS=ON",
        ]
        
        build_args = ["--config", build_type, "--parallel", "4"]

        # Windows特殊设置
        if sys.platform == "win32":
            cmake_args += [
                "-A", "x64" if sys.maxsize > 2**32 else "Win32",
                "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=ON"
            ]

        print(f"Building in {build_temp}")
        print(f"CMake args: {' '.join(cmake_args)}")

        # 运行CMake配置
        subprocess.run(
            ["cmake", str(cmake_list_dir)] + cmake_args, 
            cwd=build_temp, 
            check=True
        )
        
        # 运行CMake构建
        subprocess.run(
            ["cmake", "--build", ".", "--target", "mipsolver"] + build_args, 
            cwd=build_temp, 
            check=True
        )

# 禁用源码分发 - 这是关键的保护措施
class NoSdist(sdist):
    def run(self):
        raise RuntimeError(
            "Source distribution is disabled to protect intellectual property.\n"
            "This software can only be distributed as pre-compiled wheel packages.\n"
            "Please use: python -m build --wheel"
        )

# 主要设置
setup(
    name="mipsolver-pro",
    version="1.0.0",
    author="Yutong Lv", 
    author_email="your.email@example.com",
    description="High-performance Mixed-Integer Programming solver (Professional Edition)",
    long_description="""
# MIPSolver Pro

High-performance C++ Mixed-Integer Programming solver with Python interface.

## Features
- Optimized Branch & Bound algorithm
- Support for MPS standard file format  
- Simple and easy-to-use Python API
- Commercial-grade algorithm protection
- Cross-platform support (Windows/Linux/macOS)

## Quick Start

```python
import mipsolver

# Create optimization problem
problem = mipsolver.Problem("MyProblem", mipsolver.ObjectiveType.MAXIMIZE)

# Add binary variables
x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)

# Set objective function
problem.set_objective_coefficient(x0, 5.0)
problem.set_objective_coefficient(x1, 8.0)

# Add constraints
c0 = problem.add_constraint("c0", mipsolver.ConstraintType.LESS_EQUAL, 10.0)
problem.add_constraint_coefficient(c0, x0, 2.0)
problem.add_constraint_coefficient(c0, x1, 4.0)

# Solve
solver = mipsolver.Solver()
solution = solver.solve(problem)

print(f"Optimal solution: {solution.get_objective_value()}")
print(f"Variable values: {solution.get_values()}")
```

## License
This software is commercial software protected by intellectual property rights. 
Use of this software indicates agreement to the relevant license terms.
    """,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MIPSolver",
    
    # 关键：只有CMake扩展，没有Python源码包
    ext_modules=[CMakeExtension("mipsolver")],
    
    # 自定义命令
    cmdclass={
        "build_ext": CMakeBuild,
        "sdist": NoSdist,  # 禁止源码分发
    },
    
    zip_safe=False,
    python_requires=">=3.7",
    
    # 运行时依赖
    install_requires=[
        "pybind11>=2.6",
    ],
    
    # 元数据
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research", 
        "License :: Other/Proprietary License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    
    keywords="optimization mip solver integer programming commercial",
    
    # 重要：不包含任何源码文件
    include_package_data=False,
    package_data={},
    
    # 项目URL
    project_urls={
        "Bug Reports": "https://github.com/yourusername/MIPSolver/issues",
        "Source": "https://github.com/yourusername/MIPSolver",
        "Documentation": "https://mipsolver.readthedocs.io/",
    },
)