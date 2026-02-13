"""
Property analysis logic for determining categorical vs unique properties.
"""

import pandas as pd
from typing import Dict, Optional, TYPE_CHECKING
from .enums import PropertyType

if TYPE_CHECKING:
    from .performance import PerformanceMonitor


class PropertyAnalyzer:
    """Analyzes properties to determine if they are categorical or unique."""

    @staticmethod
    def analyze_dataframe(df: pd.DataFrame, performance_monitor: Optional['PerformanceMonitor'] = None) -> Dict[str, Dict]:
        """
        Analyze properties in a DataFrame.

        Args:
            df: DataFrame containing node properties
            performance_monitor: Optional performance monitor for tracking

        Returns:
            Dictionary with property analysis summary
        """
        if df.empty:
            return {}

        summary = {}
        total_nodes = len(df)

        for column in df.columns:
            # Track analysis per column
            metric = None
            if performance_monitor:
                metric = performance_monitor.start("analyze_column", column=column)

            try:
                unique_count = df[column].nunique()
                unique_ratio = unique_count / total_nodes

                # Determine property type
                prop_type = PropertyType.from_unique_ratio(unique_ratio)

                # Get sample values for categorical properties
                sample_values = None
                if prop_type in [PropertyType.CATEGORICAL, PropertyType.HIGHLY_CATEGORICAL]:
                    value_counts = df[column].value_counts().head(10)
                    sample_values = value_counts.to_dict()

                summary[column] = {
                    "unique_values": unique_count,
                    "total_values": total_nodes,
                    "unique_ratio": unique_ratio,
                    "type": prop_type.value,
                    "null_count": int(df[column].isna().sum()),
                    "sample_categorical_values": sample_values
                }
            finally:
                if performance_monitor and metric:
                    performance_monitor.stop(metric)

        return summary
    
    @staticmethod
    def get_property_stats_cypher(
        driver,
        label: str,
        prop_key: str,
        total_count: int,
        performance_monitor: Optional['PerformanceMonitor'] = None
    ) -> Dict:
        """
        Get property statistics using Cypher aggregations (optimized).

        Args:
            driver: Neo4j driver instance
            label: Node label
            prop_key: Property key to analyze
            total_count: Total number of nodes with this label
            performance_monitor: Optional performance monitor for tracking

        Returns:
            Dictionary with property statistics
        """
        with driver.session() as session:
            # Track stats query
            stats_metric = None
            if performance_monitor:
                stats_metric = performance_monitor.start("cypher_stats_query", label=label, property=prop_key)

            try:
                # Optimized: Get stats and determine if we need categorical samples in one pass
                stats_query = f"""
                MATCH (n:{label})
                WITH count(n) as total,
                     count(DISTINCT n.`{prop_key}`) as unique_count,
                     count(n) - count(n.`{prop_key}`) as null_count
                RETURN total, unique_count, null_count,
                       toFloat(unique_count) / toFloat(total) as unique_ratio
                """

                result = session.run(stats_query)
                stats = result.single()

                unique_count = stats["unique_count"]
                null_count = stats["null_count"]
                total = stats["total"]
                unique_ratio = stats["unique_ratio"]
            finally:
                if performance_monitor and stats_metric:
                    performance_monitor.stop(stats_metric)

            # Determine property type
            prop_type = PropertyType.from_unique_ratio(unique_ratio)

            # Get sample categorical values ONLY if categorical
            # This avoids the second query for UNIQUE and SEMI_UNIQUE properties
            sample_values = None
            if prop_type in [PropertyType.CATEGORICAL, PropertyType.HIGHLY_CATEGORICAL]:
                # Track categorical sample query
                sample_metric = None
                if performance_monitor:
                    sample_metric = performance_monitor.start("cypher_categorical_query", label=label, property=prop_key)

                try:
                    # Optimized query with aggregation first
                    sample_query = f"""
                    MATCH (n:{label})
                    WHERE n.`{prop_key}` IS NOT NULL
                    WITH n.`{prop_key}` as value, count(*) as count
                    ORDER BY count DESC
                    LIMIT 10
                    RETURN value, count
                    """
                    sample_result = session.run(sample_query)
                    sample_values = {
                        record["value"]: record["count"]
                        for record in sample_result
                    }
                finally:
                    if performance_monitor and sample_metric:
                        performance_monitor.stop(sample_metric)

            return {
                "unique_values": unique_count,
                "total_values": total,
                "unique_ratio": unique_ratio,
                "type": prop_type.value,
                "null_count": null_count,
                "sample_categorical_values": sample_values
            }

