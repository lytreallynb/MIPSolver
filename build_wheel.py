#!/usr/bin/env python3
"""
Cross-platform wheel distribution script for MIPSolver Professional
Builds wheels for Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class WheelBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous build artifacts...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            
        # Clean egg-info directories
        for egg_info in self.project_root.glob("*.egg-info"):
            if egg_info.is_dir():
                shutil.rmtree(egg_info)
                
        print("✅ Clean completed")
    
    def check_prerequisites(self):
        """Check if all required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check Python
        try:
            python_version = sys.version_info
            if python_version < (3, 7):
                raise RuntimeError(f"Python 3.7+ required, found {python_version}")
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False
            
        # Check CMake
        try:
            result = subprocess.run(["cmake", "--version"], 
                                  capture_output=True, text=True, check=True)
            cmake_version = result.stdout.split('\n')[0]
            print(f"✅ {cmake_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ CMake not found. Please install from https://cmake.org")
            return False
            
        # Platform-specific checks
        if platform.system() == "Windows":
            return self._check_windows_prerequisites()
        elif platform.system() == "Darwin":
            return self._check_macos_prerequisites()
        else:
            return self._check_linux_prerequisites()
    
    def _check_windows_prerequisites(self):
        """Windows-specific prerequisite checks"""
        print("🪟 Checking Windows prerequisites...")
        
        # Check for Visual Studio Build Tools
        vs_paths = [
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community",
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools",
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
        ]
        
        vs_found = any(Path(path).exists() for path in vs_paths)
        if vs_found:
            print("✅ Visual Studio Build Tools found")
        else:
            print("⚠️ Visual Studio Build Tools not found (may still work)")
            
        return True
    
    def _check_macos_prerequisites(self):
        """macOS-specific prerequisite checks"""
        print("🍎 Checking macOS prerequisites...")
        
        # Check for Xcode Command Line Tools
        try:
            subprocess.run(["xcode-select", "--print-path"], 
                          capture_output=True, check=True)
            print("✅ Xcode Command Line Tools found")
        except subprocess.CalledProcessError:
            print("❌ Xcode Command Line Tools not found")
            print("   Install with: xcode-select --install")
            return False
            
        return True
    
    def _check_linux_prerequisites(self):
        """Linux-specific prerequisite checks"""
        print("🐧 Checking Linux prerequisites...")
        
        # Check for build essentials
        try:
            subprocess.run(["gcc", "--version"], 
                          capture_output=True, check=True)
            print("✅ GCC compiler found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ GCC not found. Install with: sudo apt-get install build-essential")
            return False
            
        return True
    
    def install_dependencies(self):
        """Install Python build dependencies"""
        print("📦 Installing build dependencies...")
        
        dependencies = [
            "pip>=21.0",
            "setuptools>=50.0",
            "wheel>=0.36",
            "build>=0.7",
            "pybind11>=2.6",
        ]
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + dependencies, check=True)
            
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def build_wheel(self):
        """Build the wheel package"""
        print("🔨 Building wheel package...")
        
        # Set environment variables for build
        env = os.environ.copy()
        env["CMAKE_BUILD_PARALLEL_LEVEL"] = "4"
        
        if platform.system() == "Windows":
            env["CMAKE_GENERATOR"] = "Visual Studio 16 2019"
        
        try:
            subprocess.run([
                sys.executable, "-m", "build", "--wheel"
            ], cwd=self.project_root, env=env, check=True)
            
            print("✅ Wheel built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def test_wheel(self):
        """Test the built wheel"""
        print("🧪 Testing wheel installation...")
        
        # Find the built wheel
        wheels = list(self.dist_dir.glob("*.whl"))
        if not wheels:
            print("❌ No wheel files found")
            return False
            
        wheel_path = wheels[0]
        print(f"📦 Testing wheel: {wheel_path.name}")
        
        # Create temporary virtual environment
        test_env = self.project_root / "test_wheel_env"
        
        try:
            # Create venv
            subprocess.run([
                sys.executable, "-m", "venv", str(test_env)
            ], check=True)
            
            # Determine activation script
            if platform.system() == "Windows":
                python_exe = test_env / "Scripts" / "python.exe"
                pip_exe = test_env / "Scripts" / "pip.exe"
            else:
                python_exe = test_env / "bin" / "python"
                pip_exe = test_env / "bin" / "pip"
            
            # Install wheel in test environment
            subprocess.run([
                str(pip_exe), "install", str(wheel_path)
            ], check=True)
            
            # Test import
            subprocess.run([
                str(python_exe), "-c", 
                "import mipsolver; print('✅ MIPSolver imported successfully!')"
            ], check=True)
            
            print("✅ Wheel test passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Wheel test failed: {e}")
            return False
        finally:
            # Cleanup test environment
            if test_env.exists():
                shutil.rmtree(test_env)
    
    def show_results(self):
        """Show build results"""
        print("\n🎉 Build completed!")
        print("📁 Created wheel packages:")
        
        for wheel in self.dist_dir.glob("*.whl"):
            size_mb = wheel.stat().st_size / (1024 * 1024)
            print(f"   📦 {wheel.name} ({size_mb:.1f} MB)")
        
        print(f"\n📍 Location: {self.dist_dir.absolute()}")
        print("\n🚀 To install:")
        print(f"   pip install {self.dist_dir}/*.whl")
        
        print("\n📧 To distribute:")
        print("   - Upload to PyPI: twine upload dist/*.whl")
        print("   - Share wheel files directly with users")
        print("   - Use in CI/CD pipelines")

def main():
    """Main build process"""
    print("🏗️ MIPSolver Professional - Wheel Builder")
    print("=" * 50)
    
    builder = WheelBuilder()
    
    # Build process
    steps = [
        ("clean", builder.clean_build),
        ("check", builder.check_prerequisites),
        ("deps", builder.install_dependencies),
        ("build", builder.build_wheel),
        ("test", builder.test_wheel),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print(f"\n❌ Build failed at step: {step_name}")
                sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n⚠️ Build interrupted at step: {step_name}")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 Unexpected error at step {step_name}: {e}")
            sys.exit(1)
    
    builder.show_results()
    print("\n🎊 All done! Happy optimizing!")

if __name__ == "__main__":
    main()
