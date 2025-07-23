@echo off
echo.
echo ====================================
echo MIPSolver Professional for Windows
echo ====================================
echo.

echo Welcome to MIPSolver Professional Edition!
echo This script will help you get started on Windows.
echo.

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Found Python installation:
python --version
echo.

REM Check if MIPSolver is already installed
echo Checking if MIPSolver is already installed...
python -c "import mipsolver; print('MIPSolver is already installed!')" 2>nul
if %ERRORLEVEL% equ 0 (
    echo.
    echo MIPSolver is already installed and working!
    goto :run_example
)

echo MIPSolver not found. Let's install it...
echo.

REM Check if we have a wheel file
if exist "dist\mipsolver_pro-*.whl" (
    echo Found local wheel file. Installing...
    for %%i in (dist\mipsolver_pro-*.whl) do (
        pip install "%%i" --force-reinstall
        if %ERRORLEVEL% neq 0 (
            echo ERROR: Failed to install wheel file
            pause
            exit /b 1
        )
    )
) else (
    echo No local wheel found. Trying to install from PyPI...
    pip install mipsolver-pro
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install from PyPI
        echo.
        echo You may need to build the wheel first:
        echo   1. Run: build_windows.bat
        echo   2. Then run this script again
        echo.
        pause
        exit /b 1
    )
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import mipsolver; print('✅ MIPSolver Professional Edition installed successfully!')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Installation verification failed
    pause
    exit /b 1
)

:run_example
echo.
set /p run_example="Would you like to run the Windows example? (y/n): "
if /i "%run_example%"=="y" (
    echo.
    echo Running Windows example...
    echo.
    if exist "examples\windows_example.py" (
        python examples\windows_example.py
    ) else (
        echo Creating and running a simple test...
        python -c "
import mipsolver
print('🏗️ MIPSolver Quick Test')
print('=' * 30)

# Create simple problem
problem = mipsolver.Problem('Test', mipsolver.ObjectiveType.MAXIMIZE)
x = problem.add_variable('x', mipsolver.VariableType.BINARY)
y = problem.add_variable('y', mipsolver.VariableType.BINARY)

# Objective: maximize x + 2*y
problem.set_objective_coefficient(x, 1.0)
problem.set_objective_coefficient(y, 2.0)

# Constraint: x + y <= 1
c = problem.add_constraint('budget', mipsolver.ConstraintType.LESS_EQUAL, 1.0)
problem.add_constraint_coefficient(c, x, 1.0)
problem.add_constraint_coefficient(c, y, 1.0)

# Solve
solver = mipsolver.Solver()
solution = solver.solve(problem)

print(f'Status: {solution.get_status()}')
print(f'Optimal value: {solution.get_objective_value()}')
print(f'Solution: x={solution.get_values()[0]}, y={solution.get_values()[1]}')
print()
print('✅ MIPSolver is working correctly on Windows!')
"
    )
)

echo.
echo ============================================
echo MIPSolver Professional is ready to use!
echo ============================================
echo.
echo Quick commands:
echo   python -c "import mipsolver; print('Ready!')"
echo.
echo Documentation and examples:
echo   - README.md - Main documentation
echo   - WINDOWS_INSTALL.md - Windows-specific guide
echo   - examples/ - Example scripts
echo.
echo Support:
echo   - Email: support@mipsolver.com
echo   - Website: https://www.mipsolver.com
echo.
pause
