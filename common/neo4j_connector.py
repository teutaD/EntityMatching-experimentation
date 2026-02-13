"""
Common Neo4j database connection management for all projects.
"""

from neo4j import GraphDatabase, Driver, Session
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j database connection."""
    uri: str
    user: str
    password: str
    database: str = "neo4j"
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: int = 60


class Neo4jConnector:
    """Manages Neo4j database connections with common utilities."""
    
    def __init__(self, config: Neo4jConfig):
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
    
    @contextmanager
    def session(self, database: Optional[str] = None) -> Session:
        """
        Get a Neo4j session as a context manager.
        
        Args:
            database: Optional database name (uses config default if not provided)
            
        Yields:
            Neo4j session
        """
        db = database or self.config.database
        session = self.driver.session(database=db)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                     database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Optional database name
            
        Returns:
            List of result records as dictionaries
        """
        with self.session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                     database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a write query in a transaction.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Optional database name
            
        Returns:
            List of result records as dictionaries
        """
        def _write_tx(tx):
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.session(database) as session:
            return session.execute_write(_write_tx)
    
    def get_node_labels(self) -> List[str]:
        """
        Retrieve all node labels in the database.
        
        Returns:
            List of node labels
        """
        result = self.execute_query("CALL db.labels()")
        return [record["label"] for record in result]
    
    def get_node_count(self, label: str) -> int:
        """
        Get the total count of nodes with a specific label.
        
        Args:
            label: The node label to count
            
        Returns:
            Total number of nodes with that label
        """
        query = f"MATCH (n:{label}) RETURN count(n) as count"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0
    
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
        result = self.execute_query(query)
        return [record["key"] for record in result]

