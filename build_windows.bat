@echo off
echo Starting MIPSolver Windows wheel package build...

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)

REM Check if CMake is available
cmake --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: CMake is not installed or not in PATH
    echo Please install CMake from https://cmake.org/download/
    pause
    exit /b 1
)

echo Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

echo Installing build dependencies...
python -m pip install --upgrade pip setuptools wheel build pybind11

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install build dependencies
    pause
    exit /b 1
)

echo Building wheel package...
python -m build --wheel

if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo Build successful!
echo.

echo Created wheel packages:
dir dist\*.whl

echo.
echo To install the wheel package:
echo   pip install dist\mipsolver_pro-1.0.0-*.whl
echo.
echo To test the installation:
echo   python -c "import mipsolver; print('MIPSolver ready!')"
echo.

REM Optional: Test the wheel
set /p test_wheel="Would you like to test the wheel installation? (y/n): "
if /i "%test_wheel%"=="y" (
    echo Testing wheel installation...
    python -m venv test_env
    call test_env\Scripts\activate.bat
    
    for %%i in (dist\*.whl) do (
        pip install "%%i"
        python -c "import mipsolver; print('Test passed: MIPSolver imported successfully!')"
        if %ERRORLEVEL% neq 0 (
            echo ERROR: Wheel test failed!
            call deactivate
            rmdir /s /q test_env
            pause
            exit /b 1
        )
    )
    
    call deactivate
    rmdir /s /q test_env
    echo Wheel test completed successfully!
)

echo.
echo Creating test environment...
if exist "test_env" rmdir /s /q "test_env"
python -m venv test_env

echo Activating test environment...
call test_env\Scripts\activate.bat

echo Installing wheel package...
for %%f in (dist\*.whl) do (
    pip install "%%f"
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install wheel package
        pause
        exit /b 1
    )
)

echo Testing basic import...
python -c "import mipsolver; print('SUCCESS: mipsolver imported successfully')"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Import test failed
    pause
    exit /b 1
)

echo.
echo Running comprehensive tests...
python -c "
import mipsolver
print('Testing problem creation...')
problem = mipsolver.Problem('TestProblem', mipsolver.ObjectiveType.MAXIMIZE)
print('SUCCESS: Problem created')

print('Testing variable addition...')
x0 = problem.add_variable('x0', mipsolver.VariableType.BINARY)
x1 = problem.add_variable('x1', mipsolver.VariableType.BINARY)
print('SUCCESS: Variables added')

print('Testing constraint addition...')
problem.set_objective_coefficient(x0, 5.0)
problem.set_objective_coefficient(x1, 8.0)
c0 = problem.add_constraint('c0', mipsolver.ConstraintType.LESS_EQUAL, 10.0)
problem.add_constraint_coefficient(c0, x0, 2.0)
problem.add_constraint_coefficient(c0, x1, 4.0)
print('SUCCESS: Constraints added')

print('Testing solver...')
solver = mipsolver.Solver()
solution = solver.solve(problem)
print('SUCCESS: Problem solved')

print('Objective value:', solution.get_objective_value())
print('Variable values:', solution.get_values())
print('Solution status:', solution.get_status())

print('')
print('=== ALL TESTS PASSED ===')
print('MIPSolver wheel package is ready for use!')
"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Comprehensive tests failed
    pause
    exit /b 1
)

echo.
echo Deactivating test environment...
call deactivate

echo.
echo ============================================
echo BUILD COMPLETE AND TESTED SUCCESSFULLY!
echo ============================================
echo.
echo Your wheel package is ready:
for %%f in (dist\*.whl) do echo   %%f
echo.
echo To install on other machines:
echo   pip install dist\mipsolver_pro-1.0.0-*.whl
echo.
echo To upload to PyPI (optional):
echo   pip install twine
echo   twine upload dist\*.whl
echo.
pause