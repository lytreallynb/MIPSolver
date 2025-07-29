#ifndef SOLUTION_H
#define SOLUTION_H

#include "core.h"
#include <vector>
#include <iostream>

namespace MIPSolver {

class Solution {
    public:
        enum class Status {
            FEASIBLE,
            INFEASIBLE,
            OPTIMAL,
            UNBOUNDED,
            ITERATION_LIMIT,
            TIME_LIMIT,
            UNKNOWN
        };

        Solution(int num_variables)
            :values_(num_variables, 0.0),
             objective_value_(0.0),
             status_(Status::UNKNOWN),
             solve_time_(0.0),
             iterations_(0) {}

        // Getters/Setters
        void setValue(int var_index, double value) {
            if (var_index >= 0 && var_index < values_.size()) {
                values_[var_index] = value;
            } else {
                throw std::out_of_range("Variable index out of range");
            }
        } 

        double getValue(int var_index) const {
            if (var_index >= 0 && var_index < values_.size()) {
                return values_[var_index];
            } else {
                throw std::out_of_range("Variable index out of range");
            }
        }

        void setObjectiveValue(double value) { objective_value_ = value; }
        double getObjectiveValue() const { return objective_value_; }

        void setStatus(Status status) { status_ = status; }
        Status getStatus() const { return status_; }

        void setSolveTime(double time) { solve_time_ = time; }
        double getSolveTime() const { return solve_time_; }

        void setIterations(int iterations) { iterations_ = iterations; }
        int getIterations() const { return iterations_; }

        const std::vector<double>& getValues() const { return values_; }

        void print() const {
            std::cout << "Solution Status: ";
            switch (status_) {
                case Status::FEASIBLE: std::cout << "Feasible"; break;
                case Status::INFEASIBLE: std::cout << "Infeasible"; break;
                case Status::OPTIMAL: std::cout << "Optimal"; break;
                case Status::UNBOUNDED: std::cout << "Unbounded"; break;
                case Status::ITERATION_LIMIT: std::cout << "Iteration Limit Reached"; break;
                case Status::TIME_LIMIT: std::cout << "Time Limit Reached"; break;
                case Status::UNKNOWN: std::cout << "Unknown"; break;
            }
            std::cout << "\nObjective Value: " << objective_value_ << "\n";
            std::cout << "Solve Time: " << solve_time_ << " seconds\n";
            std::cout << "Iterations: " << iterations_ << "\n";
            std::cout << "Variable Values:\n";
            for (int i = 0; i < values_.size(); ++i) {
                if (std::abs(values_[i]) > 1e-6) { // Only print non-zero values
                    std::cout << " - Variable " << i << ": " << values_[i] << "\n";
                }
            }
        }

    private:
        std::vector<double> values_;
        double objective_value_;
        Status status_;
        double solve_time_;
        int iterations_;
};

class SolverInterface {
    public:
        virtual ~SolverInterface() = default;

        // Solve the problem and return a Solution object
        virtual Solution solve(const Problem& problem) = 0;

        // Set parameters for the solver
        virtual void setTimeLimit(double seconds) { time_limit_ = seconds; };
        virtual void setIterationLimit(int iterations) { iteration_limit_ = iterations; };
        virtual void setVerbose(bool verbose) { verbose_ = verbose; };
    
    protected:
        double time_limit_ = 3600.0; // Default time limit in seconds ( 1 hour)
        int iteration_limit_ = 100000; // Default iteration limit
        bool verbose_ = false; // Verbose output flag
};

} // namespace MIPSolver

#endif