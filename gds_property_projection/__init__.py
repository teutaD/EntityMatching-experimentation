"""
GDS Property Projection - Transform node properties into connected property nodes.
"""

from .config import PropertyProjectionConfig
from .projection_manager import GDSPropertyProjectionManager
from .materialized_projection import MaterializedPropertyProjection

__all__ = [
    'PropertyProjectionConfig',
    'GDSPropertyProjectionManager',
    'MaterializedPropertyProjection'
]

