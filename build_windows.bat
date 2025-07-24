@echo off
echo Building MIPSolver on Windows...

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found
    exit /b 1
)

REM Check CMake  
cmake --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: CMake not found
    exit /b 1
)

REM Install dependencies
python -m pip install --upgrade pip setuptools wheel pybind11

REM Build package
echo Building wheel...
python setup.py bdist_wheel

echo Build complete!
