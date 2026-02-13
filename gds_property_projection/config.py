"""
Configuration for GDS Property Projection.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PropertyProjectionConfig:
    """Configuration for property-to-node projection."""
    
    # Source node configuration
    source_label: str = "User"
    source_id_property: str = "id"
    
    # Properties to project as nodes
    properties_to_project: List[str] = field(default_factory=list)
    
    # Projection configuration
    property_node_label: str = "Property"
    relationship_type: str = "HAS"
    
    # GDS projection name
    graph_name: str = "user-property-graph"
    
    # Batch processing
    batch_size: int = 10000
    
    # Optional: Filter for source nodes
    source_filter: Optional[str] = None  # e.g., "WHERE n.active = true"
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.source_label:
            raise ValueError("source_label must be specified")
        if not self.properties_to_project:
            raise ValueError("properties_to_project must contain at least one property")

