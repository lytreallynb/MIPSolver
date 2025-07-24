# python/mipsolver/constants.py
"""
Constants
This lets users write: from mipsolver import MAXIMIZE, BINARY
instead of from mipsolver.constants import MAXIMIZE, BINARY
"""

# Variable types
CONTINUOUS = 0
BINARY = 1  
INTEGER = 2

# Objective senses
MINIMIZE = 1
MAXIMIZE = -1

# Constraint types
LESS_EQUAL = 1
GREATER_EQUAL = 2  
EQUAL = 3

# Solution statuses
OPTIMAL = 2
INFEASIBLE = 3
UNBOUNDED = 5
UNKNOWN = 0