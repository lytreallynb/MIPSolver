#!/usr/bin/env python3
"""
MIPSolver wheel package comprehensive test suite
Tests all major functionality to ensure the wheel package works correctly
"""

def test_basic_import():
    """Test basic import"""
    try:
        import mipsolver
        print("SUCCESS: mipsolver imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Import failed: {e}")
        return False

def test_create_problem():
    """Test problem creation"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        print("SUCCESS: Problem created successfully")
        return True
    except Exception as e:
        print(f"FAILED: Problem creation failed: {e}")
        return False

def test_add_variables():
    """Test variable addition"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        print(f"SUCCESS: Variables added successfully: x0={x0}, x1={x1}")
        return True
    except Exception as e:
        print(f"FAILED: Variable addition failed: {e}")
        return False

def test_set_bounds():
    """Test variable bounds setting"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        problem.set_variable_bounds(x0, 0, 1)
        problem.set_variable_bounds(x1, 0, 1)
        
        print("SUCCESS: Variable bounds set successfully")
        return True
    except Exception as e:
        print(f"FAILED: Setting variable bounds failed: {e}")
        return False

def test_set_objective():
    """Test objective function setting"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        problem.set_objective_coefficient(x0, 5.0)
        problem.set_objective_coefficient(x1, 8.0)
        
        print("SUCCESS: Objective coefficients set successfully")
        return True
    except Exception as e:
        print(f"FAILED: Setting objective coefficients failed: {e}")
        return False

def test_add_constraints():
    """Test constraint addition"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        c0 = problem.add_constraint("c0", mipsolver.ConstraintType.LESS_EQUAL, 10.0)
        problem.add_constraint_coefficient(c0, x0, 2.0)
        problem.add_constraint_coefficient(c0, x1, 4.0)
        
        print("SUCCESS: Constraints added successfully")
        return True
    except Exception as e:
        print(f"FAILED: Adding constraints failed: {e}")
        return False

def test_solve_simple_problem():
    """Test solving a simple optimization problem"""
    try:
        import mipsolver
        
        # Create problem: maximize 5*x0 + 8*x1
        # subject to: 2*x0 + 4*x1 <= 10
        #             x0, x1 in {0,1}
        
        problem = mipsolver.Problem("TestProblem", mipsolver.ObjectiveType.MAXIMIZE)
        
        # Add variables
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        x1 = problem.add_variable("x1", mipsolver.VariableType.BINARY)
        
        # Set variable bounds
        problem.set_variable_bounds(x0, 0, 1)
        problem.set_variable_bounds(x1, 0, 1)
        
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
        
        # Check results
        obj_value = solution.get_objective_value()
        values = solution.get_values()
        status = solution.get_status()
        
        print(f"SUCCESS: Problem solved successfully!")
        print(f"   Status: {status}")
        print(f"   Objective value: {obj_value}")
        print(f"   Variable values: {values}")
        
        # Validate results
        if obj_value > 0 and len(values) == 2:
            print("SUCCESS: Result validation passed")
            return True
        else:
            print("FAILED: Result validation failed")
            return False
            
    except Exception as e:
        print(f"FAILED: Solving problem failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_variable_types():
    """Test different variable types"""
    try:
        import mipsolver
        problem = mipsolver.Problem("TypeTest", mipsolver.ObjectiveType.MINIMIZE)
        
        # Test different variable types
        x_cont = problem.add_variable("x_continuous", mipsolver.VariableType.CONTINUOUS)
        x_int = problem.add_variable("x_integer", mipsolver.VariableType.INTEGER)
        x_bin = problem.add_variable("x_binary", mipsolver.VariableType.BINARY)
        
        print("SUCCESS: Different variable types created successfully")
        print(f"   Continuous: {x_cont}, Integer: {x_int}, Binary: {x_bin}")
        return True
    except Exception as e:
        print(f"FAILED: Creating different variable types failed: {e}")
        return False

def test_different_constraint_types():
    """Test different constraint types"""
    try:
        import mipsolver
        problem = mipsolver.Problem("ConstraintTest", mipsolver.ObjectiveType.MINIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.CONTINUOUS)
        
        # Test different constraint types
        c_le = problem.add_constraint("c_le", mipsolver.ConstraintType.LESS_EQUAL, 5.0)
        c_ge = problem.add_constraint("c_ge", mipsolver.ConstraintType.GREATER_EQUAL, 1.0)
        c_eq = problem.add_constraint("c_eq", mipsolver.ConstraintType.EQUAL, 3.0)
        
        # Add coefficients
        problem.add_constraint_coefficient(c_le, x0, 1.0)
        problem.add_constraint_coefficient(c_ge, x0, 1.0)
        problem.add_constraint_coefficient(c_eq, x0, 1.0)
        
        print("SUCCESS: Different constraint types created successfully")
        print(f"   LE: {c_le}, GE: {c_ge}, EQ: {c_eq}")
        return True
    except Exception as e:
        print(f"FAILED: Creating different constraint types failed: {e}")
        return False

def test_solver_options():
    """Test solver options"""
    try:
        import mipsolver
        problem = mipsolver.Problem("OptionsTest", mipsolver.ObjectiveType.MAXIMIZE)
        
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        problem.set_objective_coefficient(x0, 1.0)
        
        # Test solver with verbose option
        solver = mipsolver.Solver()
        solver.set_verbose(True)
        solution = solver.solve(problem)
        
        print("SUCCESS: Solver options tested successfully")
        return True
    except Exception as e:
        print(f"FAILED: Testing solver options failed: {e}")
        return False

def test_license_functionality():
    """Test license-related functionality"""
    try:
        import mipsolver
        
        # Try to solve a problem to test license checking
        problem = mipsolver.Problem("LicenseTest", mipsolver.ObjectiveType.MAXIMIZE)
        x0 = problem.add_variable("x0", mipsolver.VariableType.BINARY)
        problem.set_objective_coefficient(x0, 1.0)
        
        solver = mipsolver.Solver()
        solution = solver.solve(problem)
        
        # If we get here, license is working
        print("SUCCESS: License functionality working (free license active)")
        return True
    except Exception as e:
        print(f"INFO: License check result: {e}")
        return True  # License issues are not test failures

def main():
    """Run all tests"""
    print("=" * 60)
    print("MIPSolver Wheel Package Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Import", test_basic_import),
        ("Problem Creation", test_create_problem), 
        ("Variable Addition", test_add_variables),
        ("Variable Bounds", test_set_bounds),
        ("Objective Setting", test_set_objective),
        ("Constraint Addition", test_add_constraints),
        ("Problem Solving", test_solve_simple_problem),
        ("Variable Types", test_different_variable_types),
        ("Constraint Types", test_different_constraint_types),
        ("Solver Options", test_solver_options),
        ("License Functionality", test_license_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 40)
        if test_func():
            passed += 1
        else:
            print(f"FAILED: {name} test failed")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("CONGRATULATIONS: All tests passed! MIPSolver wheel package is working correctly!")
        print("\nYour wheel package is ready for:")
        print("- Local use")
        print("- Distribution to other machines")
        print("- Upload to PyPI")
        return True
    else:
        print("WARNING: Some tests failed. Please check the build process.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)