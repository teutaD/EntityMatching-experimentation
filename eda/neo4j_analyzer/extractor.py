"""
Data extraction from Neo4j to pandas DataFrames.
"""

import pandas as pd
import time
from typing import Optional
from neo4j import Driver


class DataExtractor:
    """Extracts data from Neo4j into pandas DataFrames."""
    
    def __init__(self, driver: Driver, fetch_size: int = 1000):
        """
        Initialize data extractor.
        
        Args:
            driver: Neo4j driver instance
            fetch_size: Number of records to fetch per batch
        """
        self.driver = driver
        self.fetch_size = fetch_size
    
    def extract_nodes_to_dataframe(
        self,
        label: str,
        total_count: int,
        limit: Optional[int] = None,
        sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extract nodes of a specific label into a pandas DataFrame.
        
        Args:
            label: The node label to extract
            total_count: Total number of nodes with this label
            limit: Maximum number of nodes to extract (None for all)
            sample_size: If set, randomly sample this many nodes
            
        Returns:
            pandas DataFrame containing node properties
        """
        print(f"Total nodes with label '{label}': {total_count:,}")
        
        # Build query based on parameters
        query = self._build_extraction_query(label, total_count, limit, sample_size)
        
        # Extract data
        start_time = time.time()
        records = self._execute_extraction(query)
        elapsed = time.time() - start_time
        
        print(f"Extracted {len(records):,} nodes in {elapsed:.2f} seconds")
        
        return pd.DataFrame(records)
    
    def _build_extraction_query(
        self,
        label: str,
        total_count: int,
        limit: Optional[int],
        sample_size: Optional[int]
    ) -> str:
        """Build the Cypher query for data extraction."""
        if sample_size and sample_size < total_count:
            print(f"Randomly sampling {sample_size:,} nodes...")
            return f"""
            MATCH (n:{label})
            WITH n, rand() as r
            ORDER BY r
            LIMIT {sample_size}
            RETURN properties(n) as props, elementId(n) as element_id
            """
        elif limit and limit < total_count:
            print(f"Fetching first {limit:,} nodes...")
            return f"""
            MATCH (n:{label})
            RETURN properties(n) as props, elementId(n) as element_id
            LIMIT {limit}
            """
        else:
            print(f"Fetching all {total_count:,} nodes...")
            return f"""
            MATCH (n:{label})
            RETURN properties(n) as props, elementId(n) as element_id
            """
    
    def _execute_extraction(self, query: str) -> list:
        """Execute the extraction query and return records."""
        records = []
        
        with self.driver.session(fetch_size=self.fetch_size) as session:
            result = session.run(query)
            
            batch_count = 0
            for record in result:
                node_data = record["props"].copy()
                node_data['_node_element_id'] = record["element_id"]
                records.append(node_data)
                
                batch_count += 1
                if batch_count % 10000 == 0:
                    print(f"  Processed {batch_count:,} nodes...")
        
        return records

