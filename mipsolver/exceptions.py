# python/mipsolver/exceptions.py
"""
Exception classes for MIPSolver
"""

class MIPSolverError(Exception):
    """
    Base exception class for MIPSolver 
    
    This is raised when there are issues with model setup, 
    invalid operations, or API misuse.
    """
    pass

class OptimizationError(MIPSolverError):
    """
    Raised when optimization process fails
    
    This could be due to solver issues, numerical problems,
    or other runtime errors during the solving process.
    """
    pass

class LicenseError(MIPSolverError):
    """
    Raised when there are licensing issues
    
    Though we don't currently use licensing, this provides
    a framework for future commercial versions.
    """
    pass
