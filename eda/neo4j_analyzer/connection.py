"""
Neo4j database connection management.
"""

from neo4j import GraphDatabase, Driver
from typing import List
from .config import Neo4jConnectionConfig


class Neo4jConnection:
    """Manages Neo4j database connections."""
    
    def __init__(self, config: Neo4jConnectionConfig):
        """
        Initialize Neo4j connection.
        
        Args:
            config: Neo4j connection configuration
        """
        self.config = config
        self.driver: Driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password),
            max_connection_pool_size=config.max_connection_pool_size,
            connection_acquisition_timeout=config.connection_acquisition_timeout
        )
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_node_labels(self) -> List[str]:
        """
        Retrieve all node labels in the database.
        
        Returns:
            List of node labels
        """
        with self.driver.session() as session:
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
        return labels
    
    def get_node_count(self, label: str) -> int:
        """
        Get the total count of nodes with a specific label.
        
        Args:
            label: The node label to count
            
        Returns:
            Total number of nodes with that label
        """
        query = f"MATCH (n:{label}) RETURN count(n) as count"
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()["count"]
    
    def get_property_keys(self, label: str, sample_limit: int = 1000) -> List[str]:
        """
        Get all property keys for a given label.
        
        Args:
            label: The node label
            sample_limit: Number of nodes to sample for property discovery
            
        Returns:
            List of property keys
        """
        query = f"""
        MATCH (n:{label})
        WITH n LIMIT {sample_limit}
        UNWIND keys(n) as key
        RETURN DISTINCT key
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            property_keys = [record["key"] for record in result]
        
        return property_keys

