"""
Configuration classes for Neo4j Property Analyzer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Neo4jConnectionConfig:
    """Configuration for Neo4j database connection."""
    uri: str
    user: str
    password: str
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: int = 60
    fetch_size: int = 1000


@dataclass
class AnalysisConfig:
    """Configuration for property analysis."""
    limit: Optional[int] = None
    sample_size: Optional[int] = None
    minimal_report: bool = False
    output_html: Optional[str] = None


@dataclass
class AnalyzerConfig:
    """Main configuration for the analyzer."""
    connection: Neo4jConnectionConfig
    analysis: AnalysisConfig
    max_workers: int = 4
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "AnalyzerConfig":
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            AnalyzerConfig instance
        """
        connection_config = Neo4jConnectionConfig(
            uri=config_dict.get("uri", "bolt://localhost:7687"),
            user=config_dict.get("user", "neo4j"),
            password=config_dict.get("password", "password"),
            max_connection_pool_size=config_dict.get("max_connection_pool_size", 50),
            connection_acquisition_timeout=config_dict.get("connection_acquisition_timeout", 60),
            fetch_size=config_dict.get("fetch_size", 1000)
        )
        
        analysis_config = AnalysisConfig(
            limit=config_dict.get("limit"),
            sample_size=config_dict.get("sample_size"),
            minimal_report=config_dict.get("minimal_report", False),
            output_html=config_dict.get("output_html")
        )
        
        return cls(
            connection=connection_config,
            analysis=analysis_config,
            max_workers=config_dict.get("max_workers", 4)
        )

