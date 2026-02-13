"""
Materialized Property Projection - Creates physical Property nodes in the database.

This is an alternative approach that creates actual Property nodes in Neo4j
rather than virtual nodes in GDS. This can be more practical for:
- Persistent analysis
- Easier querying
- Integration with existing workflows
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from common import Neo4jConnector
from .config import PropertyProjectionConfig


class MaterializedPropertyProjection:
    """
    Creates physical Property nodes in the database and then projects them with GDS.
    
    This approach:
    1. Creates actual Property nodes in Neo4j
    2. Creates HAS relationships from source nodes to properties
    3. Creates a standard GDS projection over the materialized graph
    """
    
    def __init__(self, connector: Neo4jConnector, config: PropertyProjectionConfig):
        """
        Initialize the materialized projection manager.
        
        Args:
            connector: Neo4j connector instance
            config: Property projection configuration
        """
        self.connector = connector
        self.config = config
    
    def create_property_nodes(self, batch_size: int = 10000) -> Dict[str, int]:
        """
        Create physical Property nodes in the database.
        
        Args:
            batch_size: Number of nodes to process per batch
            
        Returns:
            Statistics about created nodes and relationships
        """
        stats = {'properties_created': 0, 'relationships_created': 0}
        
        filter_clause = self.config.source_filter or ""
        
        print(f"Creating Property nodes for {len(self.config.properties_to_project)} properties...")
        
        for prop_name in self.config.properties_to_project:
            print(f"  Processing property: {prop_name}")
            
            # Create Property nodes and relationships in batches
            query = f"""
            MATCH (source:{self.config.source_label})
            {filter_clause}
            WHERE source.{prop_name} IS NOT NULL
            WITH source, source.{prop_name} AS propValue
            
            // Create or match Property node
            MERGE (p:{self.config.property_node_label} {{
                name: '{prop_name}',
                value: toString(propValue)
            }})
            
            // Create relationship
            MERGE (source)-[:{self.config.relationship_type}]->(p)
            
            RETURN count(DISTINCT p) AS props_created, count(*) AS rels_created
            """
            
            result = self.connector.execute_write(query)
            if result:
                stats['properties_created'] += result[0]['props_created']
                stats['relationships_created'] += result[0]['rels_created']
                print(f"    ✓ Created {result[0]['props_created']} property nodes, "
                      f"{result[0]['rels_created']} relationships")
        
        print(f"\n✓ Total: {stats['properties_created']} property nodes, "
              f"{stats['relationships_created']} relationships")
        
        return stats
    
    def create_gds_projection(self) -> Dict[str, Any]:
        """
        Create a GDS projection over the materialized property graph.
        
        Returns:
            Projection statistics
        """
        # Drop existing projection if it exists
        self.drop_projection()
        
        filter_clause = self.config.source_filter or ""
        
        # Create native projection (faster than Cypher projection for materialized graphs)
        query = f"""
        CALL gds.graph.project(
            '{self.config.graph_name}',
            ['{self.config.source_label}', '{self.config.property_node_label}'],
            {{
                {self.config.relationship_type}: {{
                    orientation: 'NATURAL'
                }}
            }}
        )
        YIELD graphName, nodeCount, relationshipCount, projectMillis
        RETURN graphName, nodeCount, relationshipCount, projectMillis
        """
        
        print(f"\nCreating GDS projection '{self.config.graph_name}'...")
        result = self.connector.execute_query(query)
        
        if result:
            stats = result[0]
            print(f"✓ Projection created successfully!")
            print(f"  - Graph name: {stats['graphName']}")
            print(f"  - Nodes: {stats['nodeCount']:,}")
            print(f"  - Relationships: {stats['relationshipCount']:,}")
            print(f"  - Time: {stats['projectMillis']}ms")
            return stats
        
        return {}
    
    def drop_projection(self) -> bool:
        """Drop the GDS graph projection if it exists."""
        try:
            query = f"CALL gds.graph.drop('{self.config.graph_name}')"
            self.connector.execute_query(query)
            return True
        except Exception:
            return False
    
    def delete_property_nodes(self) -> int:
        """
        Delete all Property nodes created by this projection.
        
        WARNING: This will delete all Property nodes with the configured label.
        
        Returns:
            Number of nodes deleted
        """
        query = f"""
        MATCH (p:{self.config.property_node_label})
        DETACH DELETE p
        RETURN count(p) AS deleted
        """
        
        result = self.connector.execute_write(query)
        deleted = result[0]['deleted'] if result else 0
        print(f"✓ Deleted {deleted} Property nodes")
        return deleted
    
    def get_property_distribution(self, property_name: str) -> List[Dict[str, Any]]:
        """
        Get distribution of values for a specific property.
        
        Args:
            property_name: Name of the property to analyze
            
        Returns:
            List of value counts
        """
        query = f"""
        MATCH (p:{self.config.property_node_label} {{name: '{property_name}'}})
        MATCH (source:{self.config.source_label})-[:{self.config.relationship_type}]->(p)
        RETURN p.value AS value, count(source) AS count
        ORDER BY count DESC
        LIMIT 50
        """
        return self.connector.execute_query(query)

