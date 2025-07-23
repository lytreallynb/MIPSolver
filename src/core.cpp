#include "core.h"
#include <iostream>

using namespace MIPSolver;

// Simple test function to verify core functionality
void testCoreClasses() {
    std::cout << "Testing core classes...\n";
    
    // Create a simple problem
    Problem problem("Test Problem", ObjectiveType::MINIMIZE);
    
    // Add variables
    int x1 = problem.addVariable("x1", VariableType::CONTINUOUS);
    int x2 = problem.addVariable("x2", VariableType::BINARY);
    
    // Set variable bounds
    problem.getVariable(x1).setBounds(0.0, 10.0);
    problem.getVariable(x2).setBounds(0.0, 1.0);
    
    // Set objective coefficients
    problem.setObjectiveCoefficient(x1, 2.0);
    problem.setObjectiveCoefficient(x2, 3.0);
    
    // Add constraint: x1 + 2*x2 <= 5
    int c1 = problem.addConstraint("constraint1", ConstraintType::LESS_EQUAL, 5.0);
    problem.getConstraint(c1).addVariable(x1, 1.0);
    problem.getConstraint(c1).addVariable(x2, 2.0);
    
    // Print problem statistics
    problem.printStatistics();
    
    // Test a solution
    std::vector<double> test_solution = {1.0, 1.0};
    std::cout << "\nTesting solution [1.0, 1.0]:\n";
    std::cout << "Valid: " << (problem.isValidSolution(test_solution) ? "Yes" : "No") << "\n";
    std::cout << "Objective: " << problem.calculateObjectiveValue(test_solution) << "\n";
    
    std::cout << "Core classes test completed.\n";
}

int main() {
    std::cout << "-------MIPSolver Demo-------\n";
    testCoreClasses();
    return 0;
}