"""
Main analyzer class that orchestrates the analysis workflow.
"""

from typing import Dict, Optional
import pandas as pd

from .config import Neo4jConnectionConfig, AnalysisConfig
from .connection import Neo4jConnection
from .extractor import DataExtractor
from .property_analyzer import PropertyAnalyzer
from .report_generator import ReportGenerator
from .performance import PerformanceMonitor


class Neo4jPropertyAnalyzer:
    """
    Main analyzer class for Neo4j property analysis.

    Orchestrates the workflow of connecting to Neo4j, extracting data,
    analyzing properties, and generating reports.
    """

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        max_workers: int = 4,
        fetch_size: int = 1000,
        performance_monitor: Optional[PerformanceMonitor] = None
    ):
        """
        Initialize the analyzer.

        Args:
            uri: Neo4j database URI
            user: Database username
            password: Database password
            max_workers: Number of parallel workers (for future use)
            fetch_size: Number of records to fetch per batch
            performance_monitor: Optional performance monitor for tracking metrics
        """
        # Create connection config
        conn_config = Neo4jConnectionConfig(
            uri=uri,
            user=user,
            password=password,
            fetch_size=fetch_size
        )

        # Initialize components
        self.connection = Neo4jConnection(conn_config)
        self.extractor = DataExtractor(
            self.connection.driver,
            fetch_size=fetch_size
        )
        self.property_analyzer = PropertyAnalyzer()
        self.report_generator = ReportGenerator()
        self.max_workers = max_workers
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        self.performance_monitor.enabled = performance_monitor is not None
    
    def close(self):
        """Close the Neo4j connection."""
        self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_node_labels(self):
        """Get all node labels in the database."""
        metric = self.performance_monitor.start("get_node_labels")
        try:
            return self.connection.get_node_labels()
        finally:
            self.performance_monitor.stop(metric)

    def get_node_count(self, label: str) -> int:
        """Get the count of nodes with a specific label."""
        metric = self.performance_monitor.start("get_node_count", label=label)
        try:
            return self.connection.get_node_count(label)
        finally:
            self.performance_monitor.stop(metric)
    
    def extract_nodes_to_dataframe(
        self,
        label: str,
        limit: Optional[int] = None,
        sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extract nodes to a DataFrame.

        Args:
            label: Node label to extract
            limit: Maximum number of nodes
            sample_size: Random sample size

        Returns:
            DataFrame with node properties
        """
        metric = self.performance_monitor.start("extract_nodes_to_dataframe", label=label)
        try:
            total_count = self.get_node_count(label)
            return self.extractor.extract_nodes_to_dataframe(
                label, total_count, limit, sample_size
            )
        finally:
            self.performance_monitor.stop(metric)
    
    def get_property_summary(
        self,
        label: str,
        limit: Optional[int] = None,
        sample_size: Optional[int] = None
    ) -> Dict:
        """
        Get property summary using DataFrame analysis.

        Args:
            label: Node label to analyze
            limit: Maximum number of nodes
            sample_size: Random sample size

        Returns:
            Dictionary with property analysis
        """
        metric = self.performance_monitor.start("get_property_summary", label=label, mode="standard")
        try:
            df = self.extract_nodes_to_dataframe(label, limit, sample_size)
            return self.property_analyzer.analyze_dataframe(df)
        finally:
            self.performance_monitor.stop(metric)
    
    def get_property_summary_fast(self, label: str) -> Dict:
        """
        Get property summary using Cypher aggregations (fast mode).

        Args:
            label: Node label to analyze

        Returns:
            Dictionary with property analysis
        """
        metric = self.performance_monitor.start("get_property_summary_fast", label=label, mode="fast")
        try:
            print(f"\nFast analysis mode for label: {label}")

            # Get property keys
            prop_metric = self.performance_monitor.start("get_property_keys", label=label)
            property_keys = self.connection.get_property_keys(label)
            self.performance_monitor.stop(prop_metric)
            print(f"Found properties: {property_keys}")

            total_count = self.get_node_count(label)
            summary = {}

            # Analyze each property
            for prop_key in property_keys:
                print(f"  Analyzing property: {prop_key}...")
                prop_analysis_metric = self.performance_monitor.start(
                    "analyze_property_cypher",
                    label=label,
                    property=prop_key
                )
                summary[prop_key] = self.property_analyzer.get_property_stats_cypher(
                    self.connection.driver,
                    label,
                    prop_key,
                    total_count
                )
                self.performance_monitor.stop(prop_analysis_metric)

            return summary
        finally:
            self.performance_monitor.stop(metric)
    
    def analyze_properties(
        self,
        label: str,
        output_html: Optional[str] = None,
        limit: Optional[int] = None,
        sample_size: Optional[int] = None,
        minimal: bool = False
    ):
        """
        Analyze properties and generate profiling report.
        
        Args:
            label: Node label to analyze
            output_html: Path to save HTML report
            limit: Maximum number of nodes
            sample_size: Random sample size
            minimal: Generate minimal report
            
        Returns:
            ProfileReport object
        """
        print(f"\nAnalyzing properties for label: {label}")
        df = self.extract_nodes_to_dataframe(label, limit, sample_size)
        
        if df.empty:
            print(f"No nodes found with label: {label}")
            return None
        
        print(f"Found {len(df)} nodes with {len(df.columns)} properties")
        
        return self.report_generator.generate_profiling_report(
            df, label, output_html, minimal
        )

