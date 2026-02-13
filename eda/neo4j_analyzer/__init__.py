"""
Neo4j Property Analyzer Package

A modular package for analyzing Neo4j graph properties to determine
if they are categorical or unique per node.
"""

from .analyzer import Neo4jPropertyAnalyzer
from .config import AnalyzerConfig
from .enums import PropertyType
from .performance import PerformanceMonitor

__version__ = "1.0.0"
__all__ = ["Neo4jPropertyAnalyzer", "AnalyzerConfig", "PropertyType", "PerformanceMonitor"]

