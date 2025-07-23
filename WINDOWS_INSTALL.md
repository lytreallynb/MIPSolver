# Windows Installation Guide for MIPSolver Professional

This guide will help Windows users install and use MIPSolver Professional Edition.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (64-bit) or Windows 11
- **Python**: 3.7 or higher (3.8+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 200MB free space

### Recommended Development Environment
- **Visual Studio**: Visual Studio 2019 or 2022 (for building from source)
- **CMake**: 3.12 or higher (for custom builds)
- **Git**: For version control

## Installation Methods

### Method 1: Install from Pre-built Wheel (Recommended)

1. **Download the Windows wheel package**:
   ```cmd
   # For Python 3.12 on Windows x64
   pip install mipsolver_pro-1.0.0-cp312-cp312-win_amd64.whl
   ```

2. **Verify installation**:
   ```cmd
   python -c "import mipsolver; print('MIPSolver Professional Edition - Ready!')"
   ```

### Method 2: Install from PyPI (When Available)

```cmd
pip install mipsolver-pro
```

### Method 3: Build from Source (Advanced Users)

1. **Install prerequisites**:
   - Install Python from [python.org](https://python.org)
   - Install CMake from [cmake.org](https://cmake.org)
   - Install Visual Studio Build Tools

2. **Clone the repository**:
   ```cmd
   git clone https://github.com/yourusername/MIPSolver.git
   cd MIPSolver
   ```

3. **Run the build script**:
   ```cmd
   # Using batch script
   build_windows.bat
   
   # Or using PowerShell script
   powershell -ExecutionPolicy Bypass -File build_windows.ps1
   ```

4. **Install the built wheel**:
   ```cmd
   pip install dist\mipsolver_pro-1.0.0-*.whl
   ```

## Quick Start Example

Create a file `test_mipsolver.py`:

```python
import mipsolver

# Create a simple optimization problem
def test_basic_optimization():
    # Create optimization problem
    problem = mipsolver.Problem("Portfolio", mipsolver.ObjectiveType.MAXIMIZE)
    
    # Add binary decision variables
    stock_a = problem.add_variable("stock_a", mipsolver.VariableType.BINARY)
    stock_b = problem.add_variable("stock_b", mipsolver.VariableType.BINARY)
    stock_c = problem.add_variable("stock_c", mipsolver.VariableType.BINARY)
    
    # Set objective coefficients (expected returns)
    problem.set_objective_coefficient(stock_a, 0.12)  # 12% return
    problem.set_objective_coefficient(stock_b, 0.08)  # 8% return
    problem.set_objective_coefficient(stock_c, 0.15)  # 15% return
    
    # Add constraint: can select at most 2 stocks
    budget_constraint = problem.add_constraint("budget", 
                                             mipsolver.ConstraintType.LESS_EQUAL, 
                                             2.0)
    
    problem.add_constraint_coefficient(budget_constraint, stock_a, 1.0)
    problem.add_constraint_coefficient(budget_constraint, stock_b, 1.0)
    problem.add_constraint_coefficient(budget_constraint, stock_c, 1.0)
    
    # Solve the problem
    solver = mipsolver.Solver()
    solution = solver.solve(problem)
    
    # Display results
    print(f"Status: {solution.get_status()}")
    print(f"Maximum Return: {solution.get_objective_value():.4f}")
    print(f"Selected Stocks: {solution.get_values()}")

if __name__ == "__main__":
    test_basic_optimization()
```

Run the test:
```cmd
python test_mipsolver.py
```

Expected output:
```
Status: 2
Maximum Return: 0.2700
Selected Stocks: [1.0, 0.0, 1.0]
```

## Troubleshooting

### Common Issues

#### 1. Import Error
```
ImportError: No module named 'mipsolver'
```
**Solution**:
```cmd
pip install --upgrade mipsolver-pro
# Or install the specific wheel file
pip install mipsolver_pro-1.0.0-cp312-cp312-win_amd64.whl
```

#### 2. DLL Load Failed
```
ImportError: DLL load failed while importing mipsolver
```
**Solution**:
- Install Visual C++ Redistributable from Microsoft
- Make sure you're using the correct Python architecture (64-bit recommended)

#### 3. CMake Not Found (when building from source)
```
ERROR: CMake is not installed or not in PATH
```
**Solution**:
- Download and install CMake from [cmake.org](https://cmake.org/download/)
- Make sure to add CMake to your system PATH during installation

#### 4. Visual Studio Build Tools Missing
```
Microsoft Visual C++ 14.0 is required
```
**Solution**:
- Install "Microsoft C++ Build Tools" from Visual Studio Installer
- Or install full Visual Studio Community Edition (free)

#### 5. Python Architecture Mismatch
```
The wheel is not compatible with this platform
```
**Solution**:
- Check your Python architecture: `python -c "import platform; print(platform.machine())"`
- Download the correct wheel for your architecture (x64 vs x86)

### Performance Tips for Windows

1. **Use 64-bit Python** for better performance with large problems
2. **Set thread affinity** for multi-core optimization:
   ```python
   import os
   os.environ['OMP_NUM_THREADS'] = '4'  # Use 4 cores
   ```

3. **Increase process priority** for time-critical applications:
   ```python
   import psutil
   p = psutil.Process()
   p.nice(psutil.HIGH_PRIORITY_CLASS)  # Windows-specific
   ```

## Windows-Specific Features

### Integration with Excel
```python
import pandas as pd
import mipsolver

# Read data from Excel file
data = pd.read_excel('optimization_data.xlsx')

# Create optimization problem
problem = mipsolver.Problem("ExcelOptimization", mipsolver.ObjectiveType.MAXIMIZE)

# Process Excel data and create variables/constraints
# ... optimization logic ...

# Export results back to Excel
results_df = pd.DataFrame({
    'Variable': ['x1', 'x2', 'x3'],
    'Value': solution.get_values()
})
results_df.to_excel('optimization_results.xlsx', index=False)
```

### Windows Task Scheduler Integration
Create a batch file for scheduled optimization:

```bat
@echo off
cd /d "C:\path\to\your\project"
python daily_optimization.py > logs\optimization_%date%.log 2>&1
```

### PowerShell Integration
```powershell
# Run optimization from PowerShell
$result = python -c "
import mipsolver
# ... your optimization code ...
print(solution.get_objective_value())
"

Write-Host "Optimization result: $result"
```

## License and Support

- **License**: Commercial license required for production use
- **Support**: Windows-specific support available at support@mipsolver.com
- **Documentation**: Complete API reference at docs.mipsolver.com

## Getting Help

1. **Check the FAQ**: [https://docs.mipsolver.com/faq](https://docs.mipsolver.com/faq)
2. **Email Support**: support@mipsolver.com
3. **GitHub Issues**: Report bugs and request features
4. **Community Forum**: Join discussions with other users

---

**MIPSolver Professional Edition** - Optimizing Windows environments since 2025.
