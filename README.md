# MIPSolver Professional Edition

![License](https://img.shields.io/badge/license-Commercial-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

A high-performance **Mixed-Integer Programming (MIP)** solver implemented in C++ with Python bindings. Features an optimized Branch & Bound algorithm for solving complex optimization problems efficiently.

## Features

### Core Capabilities
- **High-Performance C++ Engine** - Optimized Branch & Bound algorithm
- **Multiple Variable Types** - Continuous, Integer, and Binary variables
- **Flexible Constraints** - Support for ≤, ≥, and = constraints
- **Standard File Format** - MPS file import/export support
- **Cross-Platform** - Windows, Linux, and macOS support

### Technical Advantages
- **Algorithm Protection** - Proprietary implementation with IP protection
- **Memory Efficient** - Optimized data structures and algorithms
- **Scalable Performance** - Handles problems from small to enterprise-scale
- **Python Integration** - Seamless integration with Python data science stack

### Professional Features
- **Commercial License** - Full commercial usage rights
- **Technical Support** - Professional email and phone support
- **Regular Updates** - Continuous algorithm improvements
- **Custom Solutions** - Enterprise customization available

## Installation

### System Requirements
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+), or macOS 11.0+
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for installation

### Quick Install

#### For All Platforms (PyPI)
```bash
pip install mipsolver-pro
```

#### Platform-Specific Wheels

**Windows (x64)**:
```cmd
pip install mipsolver_pro-1.0.0-cp312-cp312-win_amd64.whl
```

**macOS (Apple Silicon)**:
```bash
pip install mipsolver_pro-1.0.0-cp312-cp312-macosx_15_0_arm64.whl
```

**Linux (x64)**:
```bash
pip install mipsolver_pro-1.0.0-cp312-cp312-linux_x86_64.whl
```

### Building from Source

#### Windows Users
1. Install [Python](https://python.org) and [CMake](https://cmake.org)
2. Run the build script:
   ```cmd
   build_windows.bat
   ```
   Or use PowerShell:
   ```powershell
   powershell -ExecutionPolicy Bypass -File build_windows.ps1
   ```

#### macOS/Linux Users
```bash
python build_wheel.py
```

### Verify Installation
```python
import mipsolver
print("MIPSolver Professional Edition - Ready!")
```

**📋 Windows-specific installation guide**: See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)

## Quick Start

### Basic Example
```python
import mipsolver

# Create optimization problem
problem = mipsolver.Problem("Portfolio", mipsolver.ObjectiveType.MAXIMIZE)

# Add decision variables
stocks = []
for i in range(3):
    stock = problem.add_variable(f"stock_{i}", mipsolver.VariableType.BINARY)
    stocks.append(stock)

# Set objective function (maximize expected return)
returns = [0.12, 0.08, 0.15]  # Expected returns
for i, stock in enumerate(stocks):
    problem.set_objective_coefficient(stock, returns[i])

# Add budget constraint
budget_constraint = problem.add_constraint("budget", 
                                          mipsolver.ConstraintType.LESS_EQUAL, 
                                          2.0)  # Can select at most 2 stocks

for stock in stocks:
    problem.add_constraint_coefficient(budget_constraint, stock, 1.0)

# Solve the problem
solver = mipsolver.Solver()
solution = solver.solve(problem)

# Display results
print(f"Optimization Status: {solution.get_status()}")
print(f"Maximum Return: {solution.get_objective_value():.4f}")
print("Selected Stocks:")
for i, value in enumerate(solution.get_values()):
    if value > 0.5:  # Binary variable is selected
        print(f"  Stock {i}: Expected Return {returns[i]:.1%}")
```

### Advanced Example
```python
import mipsolver

# Production Planning Problem
problem = mipsolver.Problem("Production", mipsolver.ObjectiveType.MAXIMIZE)

# Decision variables: production quantities
products = ["A", "B", "C"]
production = {}
for product in products:
    var = problem.add_variable(f"produce_{product}", 
                              mipsolver.VariableType.INTEGER)
    problem.set_variable_bounds(var, 0, 1000)  # Production limits
    production[product] = var

# Objective: maximize profit
profits = {"A": 40, "B": 50, "C": 60}
for product, var in production.items():
    problem.set_objective_coefficient(var, profits[product])

# Resource constraints
# Labor constraint: 2*A + 3*B + 4*C <= 100
labor_constraint = problem.add_constraint("labor", 
                                         mipsolver.ConstraintType.LESS_EQUAL, 
                                         100)
labor_usage = {"A": 2, "B": 3, "C": 4}
for product, var in production.items():
    problem.add_constraint_coefficient(labor_constraint, var, labor_usage[product])

# Material constraint: A + 2*B + C <= 80
material_constraint = problem.add_constraint("material", 
                                           mipsolver.ConstraintType.LESS_EQUAL, 
                                           80)
material_usage = {"A": 1, "B": 2, "C": 1}
for product, var in production.items():
    problem.add_constraint_coefficient(material_constraint, var, material_usage[product])

# Solve with detailed output
solver = mipsolver.Solver()
solver.set_verbose(True)
solution = solver.solve(problem)

# Analyze results
if solution.get_status() == mipsolver.SolutionStatus.OPTIMAL:
    print(f"\nOptimal Solution Found!")
    print(f"Maximum Profit: ${solution.get_objective_value():,.2f}")
    print("\nProduction Plan:")
    
    values = solution.get_values()
    total_labor = 0
    total_material = 0
    
    for i, product in enumerate(products):
        quantity = values[i]
        revenue = quantity * profits[product]
        labor_used = quantity * labor_usage[product]
        material_used = quantity * material_usage[product]
        
        print(f"  {product}: {quantity:3.0f} units → ${revenue:6.0f} revenue")
        total_labor += labor_used
        total_material += material_used
    
    print(f"\nResource Utilization:")
    print(f"  Labor: {total_labor:5.1f} / 100 hours ({total_labor/100:.1%})")
    print(f"  Material: {total_material:5.1f} / 80 units ({total_material/80:.1%})")
```

## API Reference

### Problem Class
```python
class Problem:
    def __init__(self, name: str, objective_type: ObjectiveType)
    def add_variable(self, name: str, var_type: VariableType) -> int
    def set_variable_bounds(self, var_index: int, lower: float, upper: float)
    def set_objective_coefficient(self, var_index: int, coefficient: float)
    def add_constraint(self, name: str, constraint_type: ConstraintType, rhs: float) -> int
    def add_constraint_coefficient(self, constraint_index: int, var_index: int, coefficient: float)
```

### Solver Class
```python
class Solver:
    def __init__(self)
    def solve(self, problem: Problem) -> Solution
    def set_verbose(self, verbose: bool)
    def set_time_limit(self, seconds: float)
    def set_iteration_limit(self, iterations: int)
```

### Solution Class
```python
class Solution:
    def get_status(self) -> SolutionStatus
    def get_objective_value(self) -> float
    def get_values(self) -> List[float]
    def get_solve_time(self) -> float
    def get_iterations(self) -> int
```

### Enumerations
```python
class ObjectiveType:
    MINIMIZE = 0
    MAXIMIZE = 1

class VariableType:
    CONTINUOUS = 0
    INTEGER = 1
    BINARY = 2

class ConstraintType:
    LESS_EQUAL = 0
    GREATER_EQUAL = 1
    EQUAL = 2

class SolutionStatus:
    OPTIMAL = 2
    INFEASIBLE = 1
    UNBOUNDED = 3
    ITERATION_LIMIT = 4
    TIME_LIMIT = 5
```

## Performance Benchmarks

### Problem Size Capabilities
| License Type | Variables | Constraints | Performance |
|--------------|-----------|-------------|-------------|
| Free | ≤ 100 | ≤ 100 | Educational use |
| Professional | ≤ 10,000 | Unlimited | Production ready |
| Enterprise | Unlimited | Unlimited | Industrial scale |

### Benchmark Results
Tested on Apple MacBook Pro (M1 Pro, 16GB RAM):

| Problem Size | Variables | Constraints | Solve Time | Memory Usage |
|--------------|-----------|-------------|------------|--------------|
| Small | 50 | 25 | < 0.1s | 10MB |
| Medium | 500 | 250 | < 1s | 50MB |
| Large | 5,000 | 2,500 | < 30s | 200MB |
| Enterprise | 50,000+ | 25,000+ | Contact us | Custom |

### Comparison with Commercial Solvers
| Solver | License Cost | Performance | Python API | Support |
|--------|--------------|-------------|------------|---------|
| Gurobi | $12,000+/year | Excellent | ✓ | Premium |
| CPLEX | $15,000+/year | Excellent | ✓ | Premium |
| COPT | $2,000+/year | Very Good | ✓ | Good |
| **MIPSolver Pro** | **$299/year** | **Very Good** | **✓** | **Professional** |

## Applications

### Industry Use Cases
- **Supply Chain Optimization** - Inventory, routing, scheduling
- **Financial Portfolio** - Asset allocation, risk management
- **Manufacturing** - Production planning, resource allocation
- **Energy Systems** - Power generation, grid optimization
- **Transportation** - Vehicle routing, logistics planning
- **Telecommunications** - Network design, capacity planning

### Academic Applications
- **Operations Research** - Algorithm development and testing
- **Economics** - Market modeling and optimization
- **Engineering** - Design optimization problems
- **Computer Science** - Combinatorial optimization research

## Installation Troubleshooting

### Common Issues

#### Import Error
```python
# Problem
ImportError: No module named 'mipsolver'

# Solution
pip install --upgrade mipsolver-pro
```

#### Platform Compatibility
```bash
# Check your platform
python -c "import platform; print(platform.platform())"

# Install platform-specific wheel
pip install mipsolver-pro --only-binary=all
```

#### Memory Issues
```python
# For large problems, increase iteration limit
solver = mipsolver.Solver()
solver.set_iteration_limit(10000)
solver.set_time_limit(300)  # 5 minutes
```

### Performance Tips
1. **Problem Formulation** - Use binary variables sparingly
2. **Constraint Tightening** - Add valid inequalities when possible
3. **Variable Bounds** - Set tight bounds on continuous variables
4. **Solver Parameters** - Tune time limits for your use case

## Licensing

### License Types

#### Professional License ($299/year)
- Commercial usage permitted
- Email technical support
- Regular updates included
- Up to 10,000 variables

#### Enterprise License ($999/year)
- Unlimited problem size
- Priority phone support
- Custom feature development
- On-site training available
- Source code access (optional)

#### Academic License (50% discount)
- All Professional features
- Educational use only
- Proof of academic affiliation required

### Purchase and Support
- **Sales**: sales@mipsolver.com
- **Support**: support@mipsolver.com
- **Website**: https://www.mipsolver.com
- **Documentation**: https://docs.mipsolver.com

## Contributing

We welcome contributions from the community:

### Bug Reports
- Use GitHub Issues for bug reports
- Include minimal reproducible examples
- Specify your platform and Python version

### Feature Requests
- Discuss new features via GitHub Discussions
- Provide detailed use cases and requirements
- Consider sponsoring development for priority features

### Development
- Fork the repository
- Create feature branches
- Submit pull requests with tests
- Follow our coding standards

## Changelog

### Version 1.0.0 (Current)
- Initial commercial release
- Branch & Bound algorithm implementation
- Python bindings with pybind11
- Cross-platform wheel packages
- Professional documentation
- Commercial licensing

### Roadmap
- **v1.1** - Cutting plane algorithms
- **v1.2** - Heuristic methods
- **v1.3** - Parallel processing
- **v2.0** - GPU acceleration

## Citation

If you use MIPSolver in academic research, please cite:

```bibtex
@software{mipsolver2025,
  title={MIPSolver: A High-Performance Mixed-Integer Programming Solver},
  author={Lv, Yutong},
  year={2025},
  version={1.0.0},
  url={https://www.mipsolver.com}
}
```

## Legal

### Copyright
Copyright (c) 2025 Yutong Lv. All rights reserved.

### Disclaimer
This software is provided "as is" without warranty of any kind. Users assume all risks associated with its use.

### Patent Notice
This software may be protected by patents. Commercial use requires a valid license.

---

**MIPSolver Professional Edition** - Solving optimization problems with commercial-grade performance and support.

For more information, visit [www.mipsolver.com](https://www.mipsolver.com) or contact [support@mipsolver.com](mailto:support@mipsolver.com).