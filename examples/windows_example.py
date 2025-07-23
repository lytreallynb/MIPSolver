"""
MIPSolver Professional - Windows Example
Demonstrates optimization with Windows-specific features
"""

import mipsolver
import os
import platform
import time
from pathlib import Path

def print_system_info():
    """Print Windows system information"""
    print("🪟 Windows System Information")
    print("=" * 40)
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Working Directory: {os.getcwd()}")
    print()

def create_portfolio_optimization():
    """Create a portfolio optimization problem"""
    print("📊 Portfolio Optimization Problem")
    print("=" * 40)
    
    # Stock data (simplified)
    stocks = {
        'MSFT': {'return': 0.12, 'risk': 0.08, 'sector': 'Tech'},
        'AAPL': {'return': 0.15, 'risk': 0.12, 'sector': 'Tech'},
        'JPM':  {'return': 0.09, 'risk': 0.06, 'sector': 'Finance'},
        'JNJ':  {'return': 0.07, 'risk': 0.04, 'sector': 'Healthcare'},
        'XOM':  {'return': 0.08, 'risk': 0.10, 'sector': 'Energy'},
    }
    
    # Create optimization problem
    problem = mipsolver.Problem("WindowsPortfolio", mipsolver.ObjectiveType.MAXIMIZE)
    
    # Decision variables: binary selection for each stock
    stock_vars = {}
    print("📈 Adding stocks to portfolio:")
    for stock, data in stocks.items():
        var = problem.add_variable(f"select_{stock}", mipsolver.VariableType.BINARY)
        stock_vars[stock] = var
        
        # Set objective coefficient (expected return)
        problem.set_objective_coefficient(var, data['return'])
        print(f"  {stock}: Expected Return {data['return']:.1%}, Risk {data['risk']:.1%}")
    
    print()
    
    # Constraint 1: Select at most 3 stocks
    budget_constraint = problem.add_constraint("max_stocks", 
                                             mipsolver.ConstraintType.LESS_EQUAL, 
                                             3.0)
    
    for var in stock_vars.values():
        problem.add_constraint_coefficient(budget_constraint, var, 1.0)
    
    # Constraint 2: At least one from each sector (diversification)
    sectors = {}
    for stock, data in stocks.items():
        sector = data['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock_vars[stock])
    
    for sector, sector_stocks in sectors.items():
        if len(sector_stocks) > 1:  # Only add constraint if multiple stocks in sector
            sector_constraint = problem.add_constraint(f"min_{sector.lower()}", 
                                                     mipsolver.ConstraintType.GREATER_EQUAL, 
                                                     1.0)
            for var in sector_stocks:
                problem.add_constraint_coefficient(sector_constraint, var, 1.0)
    
    return problem, stocks, stock_vars

def solve_with_timing(problem):
    """Solve the problem with detailed timing"""
    print("⚡ Solving optimization problem...")
    
    # Create solver with Windows-optimized settings
    solver = mipsolver.Solver()
    solver.set_verbose(True)
    solver.set_time_limit(30.0)  # 30 seconds max
    
    # Record start time
    start_time = time.perf_counter()
    
    # Solve the problem
    solution = solver.solve(problem)
    
    # Record end time
    end_time = time.perf_counter()
    solve_time = end_time - start_time
    
    print(f"⏱️ Solve completed in {solve_time:.4f} seconds")
    print()
    
    return solution, solve_time

def analyze_results(solution, stocks, stock_vars, solve_time):
    """Analyze and display optimization results"""
    print("📋 Optimization Results")
    print("=" * 40)
    
    status = solution.get_status()
    status_names = {
        0: "UNKNOWN",
        1: "INFEASIBLE", 
        2: "OPTIMAL",
        3: "UNBOUNDED",
        4: "ITERATION_LIMIT",
        5: "TIME_LIMIT"
    }
    
    print(f"Status: {status_names.get(status, 'UNKNOWN')} ({status})")
    
    if status == 2:  # OPTIMAL
        obj_value = solution.get_objective_value()
        values = solution.get_values()
        
        print(f"Maximum Expected Return: {obj_value:.4f} ({obj_value:.2%})")
        print(f"Solve Time: {solve_time:.4f} seconds")
        print()
        
        print("Selected Portfolio:")
        selected_stocks = []
        total_risk = 0.0
        
        for i, (stock, data) in enumerate(stocks.items()):
            if values[i] > 0.5:  # Binary variable is selected
                selected_stocks.append(stock)
                total_risk += data['risk']
                print(f"  ✅ {stock}: Return {data['return']:.1%}, Risk {data['risk']:.1%}, Sector: {data['sector']}")
        
        if selected_stocks:
            avg_risk = total_risk / len(selected_stocks)
            print(f"\nPortfolio Summary:")
            print(f"  📊 Stocks Selected: {len(selected_stocks)}")
            print(f"  💰 Expected Return: {obj_value:.2%}")
            print(f"  ⚠️ Average Risk: {avg_risk:.2%}")
            
            # Risk-Return Ratio
            if avg_risk > 0:
                risk_return_ratio = obj_value / avg_risk
                print(f"  📈 Risk-Return Ratio: {risk_return_ratio:.2f}")
        
    else:
        print("❌ No optimal solution found")
        if status == 1:
            print("   The problem constraints are infeasible")
        elif status == 5:
            print("   Time limit exceeded")

def save_results_to_file(solution, stocks, stock_vars):
    """Save results to a Windows-compatible CSV file"""
    if solution.get_status() != 2:
        return
        
    print("\n💾 Saving results to file...")
    
    # Create results directory
    results_dir = Path("optimization_results")
    results_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"portfolio_optimization_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write("Stock,Selected,Expected_Return,Risk,Sector\n")
            
            values = solution.get_values()
            for i, (stock, data) in enumerate(stocks.items()):
                selected = "Yes" if values[i] > 0.5 else "No"
                f.write(f"{stock},{selected},{data['return']:.4f},{data['risk']:.4f},{data['sector']}\n")
        
        print(f"✅ Results saved to: {filename.absolute()}")
        
        # Try to open with default CSV application (Windows-specific)
        if platform.system() == "Windows":
            try:
                os.startfile(str(filename.absolute()))
                print("📊 Opening results in default CSV application...")
            except OSError:
                print("💡 You can open the CSV file manually with Excel or similar")
                
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

def demonstrate_windows_features():
    """Demonstrate Windows-specific features"""
    print("\n🔧 Windows-Specific Features")
    print("=" * 40)
    
    # Process information
    try:
        import psutil
        process = psutil.Process()
        print(f"Process ID: {process.pid}")
        print(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
        print(f"CPU Percent: {process.cpu_percent(interval=1):.1f}%")
    except ImportError:
        print("Install psutil for process monitoring: pip install psutil")
    
    # Environment variables
    print(f"Number of CPU cores: {os.cpu_count()}")
    print(f"TEMP directory: {os.environ.get('TEMP', 'Not set')}")
    
    # Windows path handling
    current_path = Path.cwd()
    print(f"Current path (Windows format): {current_path}")
    print(f"Drive: {current_path.drive if current_path.drive else 'N/A'}")

def main():
    """Main demonstration function"""
    print("🏗️ MIPSolver Professional - Windows Demo")
    print("=" * 50)
    print()
    
    # Show system info
    print_system_info()
    
    try:
        # Create optimization problem
        problem, stocks, stock_vars = create_portfolio_optimization()
        
        # Solve the problem
        solution, solve_time = solve_with_timing(problem)
        
        # Analyze results
        analyze_results(solution, stocks, stock_vars, solve_time)
        
        # Save results to file
        save_results_to_file(solution, stocks, stock_vars)
        
        # Demonstrate Windows features
        demonstrate_windows_features()
        
        print("\n🎉 Demo completed successfully!")
        print("💡 This example shows MIPSolver working on Windows with:")
        print("   - Binary optimization variables")
        print("   - Multiple constraints")
        print("   - File I/O operations")
        print("   - Windows-specific features")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("💡 Make sure MIPSolver is properly installed:")
        print("   pip install mipsolver-pro")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
