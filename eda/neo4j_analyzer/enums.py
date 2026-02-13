"""
Enumerations for the Neo4j Property Analyzer.
"""

from enum import Enum


class PropertyType(Enum):
    """Classification of property uniqueness."""
    UNIQUE = "UNIQUE"
    SEMI_UNIQUE = "SEMI_UNIQUE"
    CATEGORICAL = "CATEGORICAL"
    HIGHLY_CATEGORICAL = "HIGHLY_CATEGORICAL"
    
    @classmethod
    def from_unique_ratio(cls, ratio: float) -> "PropertyType":
        """
        Determine property type from unique ratio.
        
        Args:
            ratio: Ratio of unique values to total values (0.0 to 1.0)
            
        Returns:
            PropertyType enum value
        """
        if ratio == 1.0:
            return cls.UNIQUE
        elif ratio < 0.05:
            return cls.HIGHLY_CATEGORICAL
        elif ratio < 0.5:
            return cls.CATEGORICAL
        else:
            return cls.SEMI_UNIQUE


class AnalysisMode(Enum):
    """Analysis mode for property analysis."""
    FAST = "fast"  # Uses Cypher aggregations
    STANDARD = "standard"  # Loads data into DataFrame

