# python/mipsolver/expressions.py
"""
Linear expression class for building mathematical expressions
This allows users to write: 3*x + 5*y <= 10
"""

from typing import Dict, List, Tuple, Union

class LinExpr:
    """
    Linear expression class
    
    This class represents mathematical expressions like "3*x + 5*y + 10"
    
    The magic happens through operator overloading - when users write
    "3*x + 5*y", Python automatically creates LinExpr objects behind
    the scenes.
    """
    
    def __init__(self):
        self._terms: Dict = {}  # Maps variables to coefficients
        self._constant: float = 0.0
    
    def add_term(self, coeff: float, var):
        """Add a term like 3.5*x to the expression"""
        if var in self._terms:
            self._terms[var] += coeff
        else:
            self._terms[var] = coeff
        
        # Remove zero coefficients to keep expression clean
        if abs(self._terms[var]) < 1e-10:
            del self._terms[var]
    
    def add_constant(self, constant: float):
        """Add a constant term to the expression"""
        self._constant += constant
    
    def get_terms(self) -> List[Tuple]:
        """Return list of (variable, coefficient) pairs"""
        return [(var, coeff) for var, coeff in self._terms.items()]
    
    def get_constant(self) -> float:
        """Return the constant term"""
        return self._constant
    
    # Operator overloading - this is what makes "3*x + 5*y" work naturally
    def __add__(self, other):
        result = LinExpr()
        
        # Copy our terms
        for var, coeff in self._terms.items():
            result.add_term(coeff, var)
        result.add_constant(self._constant)
        
        # Add the other expression/variable/constant
        if isinstance(other, LinExpr):
            for var, coeff in other._terms.items():
                result.add_term(coeff, var)
            result.add_constant(other._constant)
        elif hasattr(other, '_index'):  # It's a Var
            result.add_term(1.0, other)
        elif isinstance(other, (int, float)):
            result.add_constant(float(other))
        
        return result
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, coeff):
        result = LinExpr()
        for var, c in self._terms.items():
            result.add_term(c * coeff, var)
        result.add_constant(self._constant * coeff)
        return result
    
    def __rmul__(self, coeff):
        return self.__mul__(coeff)
    
    def __le__(self, rhs):
        # Create constraint: expression <= rhs
        from .constants import LESS_EQUAL
        from .model import Constraint
        return Constraint(self, LESS_EQUAL, rhs)
    
    def __ge__(self, rhs):
        # Create constraint: expression >= rhs
        from .constants import GREATER_EQUAL
        from .model import Constraint
        return Constraint(self, GREATER_EQUAL, rhs)
    
    def __eq__(self, rhs):
        # Create constraint: expression == rhs
        from .constants import EQUAL
        from .model import Constraint
        return Constraint(self, EQUAL, rhs)
    
    def __str__(self):
        if not self._terms and self._constant == 0:
            return "0"
        
        parts = []
        for var, coeff in self._terms.items():
            if coeff == 1:
                parts.append(str(var))
            elif coeff == -1:
                parts.append(f"-{var}")
            else:
                parts.append(f"{coeff}*{var}")
        
        if self._constant != 0:
            parts.append(str(self._constant))
        
        return " + ".join(parts).replace("+ -", "- ")
