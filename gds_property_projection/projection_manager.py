"""
GDS Property Projection Manager - Creates graph projections with properties as nodes.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from common import Neo4jConnector
from .config import PropertyProjectionConfig


class GDSPropertyProjectionManager:
    """
    Manages GDS graph projections where node properties become separate nodes.
    
    This class helps create graph projections using Neo4j GDS where properties
    of a source node (e.g., User) are represented as separate Property nodes
    connected via HAS relationships for graph analytics.
    """
    
    def __init__(self, connector: Neo4jConnector, config: PropertyProjectionConfig):
        """
        Initialize the projection manager.
        
        Args:
            connector: Neo4j connector instance
            config: Property projection configuration
        """
        self.connector = connector
        self.config = config
    
    def check_gds_available(self) -> bool:
        """
        Check if GDS library is available in Neo4j.
        
        Returns:
            True if GDS is available, False otherwise
        """
        try:
            query = "RETURN gds.version() AS version"
            result = self.connector.execute_query(query)
            if result:
                print(f"✓ GDS version: {result[0]['version']}")
                return True
        except Exception as e:
            print(f"✗ GDS not available: {e}")
            return False
    
    def get_source_node_count(self) -> int:
        """
        Get count of source nodes that will be projected.
        
        Returns:
            Number of source nodes
        """
        filter_clause = self.config.source_filter or ""
        query = f"""
        MATCH (n:{self.config.source_label})
        {filter_clause}
        RETURN count(n) as count
        """
        result = self.connector.execute_query(query)
        return result[0]["count"] if result else 0
    
    def create_cypher_projection(self) -> Dict[str, Any]:
        """
        Create a GDS graph projection using Cypher projection.
        
        This creates a virtual graph where:
        - Source nodes (e.g., User) are included
        - Each property value becomes a Property node
        - HAS relationships connect source nodes to their property nodes
        
        Returns:
            Projection statistics
        """
        # First, drop existing projection if it exists
        self.drop_projection()
        
        filter_clause = self.config.source_filter or ""
        
        # Build property projection clauses
        property_projections = []
        for prop in self.config.properties_to_project:
            property_projections.append(f"""
            // Property: {prop}
            OPTIONAL MATCH (source:{self.config.source_label})
            {filter_clause}
            WHERE source.{prop} IS NOT NULL
            WITH source, source.{prop} AS propValue_{prop}
            RETURN 
                id(source) AS source,
                gds.util.asNode(
                    gds.graph.project.remote.nodeId(
                        '{self.config.property_node_label}:' + '{prop}:' + toString(propValue_{prop})
                    )
                ) AS target,
                '{self.config.relationship_type}' AS type
            """)
        
        # Create the main projection query
        projection_query = f"""
        CALL gds.graph.project.cypher(
            '{self.config.graph_name}',
            '
            // Source nodes
            MATCH (n:{self.config.source_label})
            {filter_clause}
            RETURN id(n) AS id, labels(n) AS labels
            
            UNION ALL
            
            // Property nodes (virtual)
            MATCH (n:{self.config.source_label})
            {filter_clause}
            UNWIND {self.config.properties_to_project} AS propKey
            WITH n, propKey, n[propKey] AS propValue
            WHERE propValue IS NOT NULL
            RETURN 
                gds.util.asNode(
                    gds.graph.project.remote.nodeId(
                        '{self.config.property_node_label}:' + propKey + ':' + toString(propValue)
                    )
                ) AS id,
                ['{self.config.property_node_label}'] AS labels
            ',
            '
            // Relationships from source to properties
            MATCH (source:{self.config.source_label})
            {filter_clause}
            UNWIND {self.config.properties_to_project} AS propKey
            WITH source, propKey, source[propKey] AS propValue
            WHERE propValue IS NOT NULL
            RETURN 
                id(source) AS source,
                gds.util.asNode(
                    gds.graph.project.remote.nodeId(
                        '{self.config.property_node_label}:' + propKey + ':' + toString(propValue)
                    )
                ) AS target,
                '{self.config.relationship_type}' AS type
            '
        )
        YIELD graphName, nodeCount, relationshipCount, projectMillis
        RETURN graphName, nodeCount, relationshipCount, projectMillis
        """
        
        print(f"Creating GDS projection '{self.config.graph_name}'...")
        result = self.connector.execute_query(projection_query)
        
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
        """
        Drop the GDS graph projection if it exists.

        Returns:
            True if projection was dropped, False if it didn't exist
        """
        try:
            query = f"""
            CALL gds.graph.drop('{self.config.graph_name}')
            YIELD graphName
            RETURN graphName
            """
            result = self.connector.execute_query(query)
            if result:
                print(f"✓ Dropped existing projection: {result[0]['graphName']}")
                return True
        except Exception as e:
            if "does not exist" in str(e).lower():
                return False
            raise
        return False

    def list_projections(self) -> List[Dict[str, Any]]:
        """
        List all GDS graph projections.

        Returns:
            List of projection information
        """
        query = "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount, memoryUsage"
        return self.connector.execute_query(query)

    def get_projection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current projection.

        Returns:
            Projection information or None if not found
        """
        projections = self.list_projections()
        for proj in projections:
            if proj['graphName'] == self.config.graph_name:
                return proj
        return None

    def run_node_similarity(self, top_k: int = 10, similarity_cutoff: float = 0.0) -> List[Dict[str, Any]]:
        """
        Run Node Similarity algorithm on the projected graph.

        This finds similar source nodes based on shared property values.

        Args:
            top_k: Number of similar nodes to return per node
            similarity_cutoff: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of similarity results
        """
        query = f"""
        CALL gds.nodeSimilarity.stream('{self.config.graph_name}', {{
            topK: {top_k},
            similarityCutoff: {similarity_cutoff}
        }})
        YIELD node1, node2, similarity
        RETURN
            gds.util.asNode(node1).{self.config.source_id_property} AS node1_id,
            gds.util.asNode(node2).{self.config.source_id_property} AS node2_id,
            similarity
        ORDER BY similarity DESC
        LIMIT 100
        """
        return self.connector.execute_query(query)

    def run_pagerank(self, max_iterations: int = 20, damping_factor: float = 0.85) -> List[Dict[str, Any]]:
        """
        Run PageRank algorithm on the projected graph.

        Args:
            max_iterations: Maximum number of iterations
            damping_factor: Damping factor (typically 0.85)

        Returns:
            List of nodes with PageRank scores
        """
        query = f"""
        CALL gds.pageRank.stream('{self.config.graph_name}', {{
            maxIterations: {max_iterations},
            dampingFactor: {damping_factor}
        }})
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        WHERE '{self.config.source_label}' IN labels(node)
        RETURN
            node.{self.config.source_id_property} AS node_id,
            score
        ORDER BY score DESC
        LIMIT 100
        """
        return self.connector.execute_query(query)

    def run_community_detection(self, algorithm: str = "louvain") -> List[Dict[str, Any]]:
        """
        Run community detection algorithm on the projected graph.

        Args:
            algorithm: Algorithm to use ('louvain', 'labelPropagation', 'wcc')

        Returns:
            List of nodes with community assignments
        """
        algo_map = {
            "louvain": "gds.louvain.stream",
            "labelPropagation": "gds.labelPropagation.stream",
            "wcc": "gds.wcc.stream"
        }

        if algorithm not in algo_map:
            raise ValueError(f"Unknown algorithm: {algorithm}. Choose from {list(algo_map.keys())}")

        query = f"""
        CALL {algo_map[algorithm]}('{self.config.graph_name}')
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        WHERE '{self.config.source_label}' IN labels(node)
        RETURN
            node.{self.config.source_id_property} AS node_id,
            communityId
        ORDER BY communityId
        LIMIT 1000
        """
        return self.connector.execute_query(query)

    def get_projection_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about the projection.

        Returns:
            Dictionary with projection statistics
        """
        stats = {}

        # Basic info
        info = self.get_projection_info()
        if info:
            stats['exists'] = True
            stats['node_count'] = info['nodeCount']
            stats['relationship_count'] = info['relationshipCount']
            stats['memory_usage'] = info['memoryUsage']
        else:
            stats['exists'] = False
            return stats

        # Degree distribution
        degree_query = f"""
        CALL gds.degree.stream('{self.config.graph_name}')
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        WHERE '{self.config.source_label}' IN labels(node)
        RETURN
            min(score) AS min_degree,
            max(score) AS max_degree,
            avg(score) AS avg_degree,
            percentileCont(score, 0.5) AS median_degree
        """
        degree_result = self.connector.execute_query(degree_query)
        if degree_result:
            stats['degree_stats'] = degree_result[0]

        return stats

