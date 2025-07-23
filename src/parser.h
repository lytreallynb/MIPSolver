#include "core.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <unordered_map>
#include <unordered_set>

namespace MIPSolver {
    class MPSParser {
        private:
            enum class Section {
                NONE,
                NAME,
                ROWS,
                COLUMNS,
                RHS,
                BOUNDS,
                ENDATA
            };

            // Helper function to trim whitespace from a string
            static std::string trim(const std::string& str) {
                size_t first = str.find_first_not_of(" \t\n\r");
                if (first == std::string::npos) return "";
                size_t last = str.find_last_not_of(" \t\n\r");
                return str.substr(first, (last - first + 1));
            }

            // Helper function to split string by whitespace
            static std::vector<std::string> split(const std::string& str) {
                std::istringstream iss(str);
                std::vector<std::string> tokens;
                std::string token;
                while (iss >> token) {
                    tokens.push_back(token);
                }
                return tokens;
            }

        public:
            static Problem parseFromFile(const std::string& filename) {
                std::ifstream file(filename);
                if (!file.is_open()) {
                    throw std::runtime_error("Could not open file: " + filename);
                }
                Problem problem(filename);
                Section currentSection = Section::NONE;

                // Maps to track variables and constraints by name
                std::unordered_map<std::string, int> variableMap;
                std::unordered_map<std::string, int> constraintMap;
                std::unordered_set<std::string> integerVariables;

                std::string line;
                bool inIntegerSection = false;

                while (std::getline(file, line)) {
                    line = trim(line);
                    if (line.empty() || line[0] == '*') continue; // Skip empty lines and comments

                    // Determine current section
                    if (line.find("NAME") == 0) {
                        currentSection = Section::NAME;
                        continue;
                    } else if (line == "ROWS") {
                        currentSection = Section::ROWS;
                        continue;
                    } else if (line == "COLUMNS") {
                        currentSection = Section::COLUMNS;
                        continue;
                    } else if (line == "RHS") {
                        currentSection = Section::RHS;
                        continue;
                    } else if (line == "BOUNDS") {
                        currentSection = Section::BOUNDS;
                        continue;
                    } else if (line == "ENDATA") {
                        currentSection = Section::ENDATA;
                        break;
                    } 
                    // Process each section
                    switch (currentSection) {
                        case Section::NAME:
                            // Problem name is already set in constructor
                            break;
                            
                        case Section::ROWS:
                            parseRowsLine(line, problem, constraintMap);
                            break;
                            
                        case Section::COLUMNS:
                            parseColumnsLine(line, problem, variableMap, constraintMap, 
                                        inIntegerSection, integerVariables);
                            break;
                            
                        case Section::RHS:
                            parseRHSLine(line, problem, constraintMap);
                            break;
                            
                        case Section::BOUNDS:
                            parseBoundsLine(line, problem, variableMap);
                            break;
                            
                        default:
                            break;
                    }
                }

                // Set integer variable types
                for (const auto& varName : integerVariables) {
                    if (variableMap.find(varName) != variableMap.end()) {
                        int varIndex = variableMap[varName];
                        problem.getVariable(varIndex).setType(VariableType::INTEGER);
                    }
                }
                
                file.close();
                return problem;
            }



        private:
            static void parseRowsLine(const std::string& line, Problem& problem, 
                                    std::unordered_map<std::string, int>& constraintMap) {
                std::vector<std::string> tokens = split(line);
                if (tokens.size() < 2) return;
                
                std::string rowType = tokens[0];
                std::string rowName = tokens[1];
                
                if (rowType == "N") {
                    // Objective function - don't create constraint
                    return;
                }
                
                ConstraintType type;
                if (rowType == "E") {
                    type = ConstraintType::EQUAL;
                } else if (rowType == "L") {
                    type = ConstraintType::LESS_EQUAL;
                } else if (rowType == "G") {
                    type = ConstraintType::GREATER_EQUAL;
                } else {
                    return; // Unknown constraint type
                }
                
                int constraintIndex = problem.addConstraint(rowName, type, 0.0);
                constraintMap[rowName] = constraintIndex;
            }
            
            static void parseColumnsLine(const std::string& line, Problem& problem,
                                    std::unordered_map<std::string, int>& variableMap,
                                    std::unordered_map<std::string, int>& constraintMap,
                                    bool& inIntegerSection,
                                    std::unordered_set<std::string>& integerVariables) {
                std::vector<std::string> tokens = split(line);
                if (tokens.size() < 3) return;
                
                // Check for integer markers
                if (tokens.size() >= 3 && tokens[1] == "'MARKER'") {
                    if (tokens[2] == "'INTORG'") {
                        inIntegerSection = true;
                    } else if (tokens[2] == "'INTEND'") {
                        inIntegerSection = false;
                    }
                    return;
                }
                
                std::string varName = tokens[0];
                
                // Create variable if it doesn't exist
                if (variableMap.find(varName) == variableMap.end()) {
                    int varIndex = problem.addVariable(varName, VariableType::CONTINUOUS);
                    variableMap[varName] = varIndex;
                    
                    if (inIntegerSection) {
                        integerVariables.insert(varName);
                    }
                }
                
                int varIndex = variableMap[varName];
                
                // Process coefficient pairs (constraint_name coefficient)
                for (size_t i = 1; i + 1 < tokens.size(); i += 2) {
                    std::string constraintName = tokens[i];
                    double coefficient = std::stod(tokens[i + 1]);
                    
                    if (constraintName == "COST") {
                        // This is objective function coefficient
                        problem.setObjectiveCoefficient(varIndex, coefficient);
                    } else if (constraintMap.find(constraintName) != constraintMap.end()) {
                        // This is a constraint coefficient
                        int constraintIndex = constraintMap[constraintName];
                        problem.getConstraint(constraintIndex).addVariable(varIndex, coefficient);
                    }
                }
            }
            
            static void parseRHSLine(const std::string& line, Problem& problem,
                                std::unordered_map<std::string, int>& constraintMap) {
                std::vector<std::string> tokens = split(line);
                if (tokens.size() < 3) return;
                
                // Skip RHS name (tokens[0])
                // Process constraint_name rhs_value pairs
                for (size_t i = 1; i + 1 < tokens.size(); i += 2) {
                    std::string constraintName = tokens[i];
                    double rhsValue = std::stod(tokens[i + 1]);
                    
                    if (constraintMap.find(constraintName) != constraintMap.end()) {
                        int constraintIndex = constraintMap[constraintName];
                        // Update constraint RHS (need to modify Constraint class)
                        // For now, we'll store it - you may need to add a setRHS method
                        problem.getConstraint(constraintIndex).setRHS(rhsValue);
                    }
                }
            }
            
            static void parseBoundsLine(const std::string& line, Problem& problem,
                                    std::unordered_map<std::string, int>& variableMap) {
                std::vector<std::string> tokens = split(line);
                if (tokens.size() < 3) return;
                
                std::string boundType = tokens[0];
                std::string boundName = tokens[1]; // Usually "bnd"
                std::string varName = tokens[2];
                
                if (variableMap.find(varName) == variableMap.end()) {
                    return; // Variable not found
                }
                
                int varIndex = variableMap[varName];
                Variable& var = problem.getVariable(varIndex);
                
                if (boundType == "BV") {
                    // Binary variable: 0 <= x <= 1
                    var.setType(VariableType::BINARY);
                    var.setBounds(0.0, 1.0);
                } else if (boundType == "LO") {
                    // Lower bound
                    if (tokens.size() >= 4) {
                        double lowerBound = std::stod(tokens[3]);
                        var.setBounds(lowerBound, var.getUpperBound());
                    }
                } else if (boundType == "UP") {
                    // Upper bound
                    if (tokens.size() >= 4) {
                        double upperBound = std::stod(tokens[3]);
                        var.setBounds(var.getLowerBound(), upperBound);
                    }
                } else if (boundType == "FX") {
                    // Fixed variable
                    if (tokens.size() >= 4) {
                        double fixedValue = std::stod(tokens[3]);
                        var.setBounds(fixedValue, fixedValue);
                    }
                }
            }
        };
}