"""
Report generation for property analysis.
"""

import pandas as pd
from typing import Optional, Dict
from ydata_profiling import ProfileReport


class ReportGenerator:
    """Generates analysis reports."""
    
    @staticmethod
    def generate_profiling_report(
        df: pd.DataFrame,
        label: str,
        output_html: Optional[str] = None,
        minimal: bool = False
    ) -> Optional[ProfileReport]:
        """
        Generate a ydata-profiling report.
        
        Args:
            df: DataFrame to analyze
            label: Label name for the report title
            output_html: Optional path to save HTML report
            minimal: If True, generate a minimal report (faster)
            
        Returns:
            ProfileReport object or None if DataFrame is empty
        """
        if df.empty:
            print(f"No data to generate report for label: {label}")
            return None
        
        print(f"Generating profiling report for {label} (this may take a while)...")
        
        profile = ProfileReport(
            df,
            title=f"Property Analysis for {label} Nodes",
            explorative=not minimal,
            minimal=minimal
        )
        
        if output_html:
            profile.to_file(output_html)
            print(f"Report saved to: {output_html}")
        
        return profile
    
    @staticmethod
    def print_summary(summary: Dict[str, Dict], label: str):
        """
        Print a formatted property summary to console.
        
        Args:
            summary: Property analysis summary dictionary
            label: Node label being analyzed
        """
        print(f"\n{'='*60}")
        print(f"Property Summary for: {label}")
        print(f"{'='*60}")
        
        for prop_name, prop_info in summary.items():
            print(f"\n  📊 {prop_name}:")
            print(f"    Type: {prop_info['type']}")
            print(f"    Unique values: {prop_info['unique_values']:,}")
            print(f"    Unique ratio: {prop_info['unique_ratio']:.2%}")
            print(f"    Null count: {prop_info['null_count']:,}")
            
            # Display sample categorical values if available
            if prop_info.get('sample_categorical_values'):
                print(f"    Sample categorical values (with counts):")
                for value, count in prop_info['sample_categorical_values'].items():
                    print(f"      - {value}: {count:,}")

