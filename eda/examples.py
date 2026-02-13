"""
Example usage patterns for Neo4j Property Analyzer.
"""

from neo4j_analyzer import Neo4jPropertyAnalyzer
from neo4j_analyzer.report_generator import ReportGenerator


# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


def example_1_basic_usage():
    """Example 1: Basic usage with fast mode."""
    print("\n" + "="*60)
    print("Example 1: Basic Fast Mode Analysis")
    print("="*60)
    
    analyzer = Neo4jPropertyAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        labels = analyzer.get_node_labels()
        print(f"Found labels: {labels}")
        
        for label in labels:
            summary = analyzer.get_property_summary_fast(label)
            ReportGenerator.print_summary(summary, label)
    finally:
        analyzer.close()


def example_2_context_manager():
    """Example 2: Using context manager for automatic cleanup."""
    print("\n" + "="*60)
    print("Example 2: Context Manager Usage")
    print("="*60)
    
    with Neo4jPropertyAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) as analyzer:
        labels = analyzer.get_node_labels()
        
        for label in labels[:1]:  # Analyze first label only
            summary = analyzer.get_property_summary_fast(label)
            ReportGenerator.print_summary(summary, label)


def example_3_sampling():
    """Example 3: Standard mode with sampling."""
    print("\n" + "="*60)
    print("Example 3: Standard Mode with Sampling")
    print("="*60)
    
    with Neo4jPropertyAnalyzer(
        NEO4J_URI, 
        NEO4J_USER, 
        NEO4J_PASSWORD,
        fetch_size=2000
    ) as analyzer:
        
        label = analyzer.get_node_labels()[0]
        
        # Analyze with sampling
        summary = analyzer.get_property_summary(
            label=label,
            sample_size=10000
        )
        
        ReportGenerator.print_summary(summary, label)


def example_4_html_report():
    """Example 4: Generate HTML profiling report."""
    print("\n" + "="*60)
    print("Example 4: Generate HTML Report")
    print("="*60)
    
    with Neo4jPropertyAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) as analyzer:
        label = analyzer.get_node_labels()[0]
        
        # Generate HTML report
        analyzer.analyze_properties(
            label=label,
            sample_size=5000,
            output_html=f"{label}_report.html",
            minimal=True  # Faster generation
        )
        
        print(f"HTML report generated: {label}_report.html")


def example_5_single_label():
    """Example 5: Analyze a specific label."""
    print("\n" + "="*60)
    print("Example 5: Analyze Specific Label")
    print("="*60)
    
    LABEL_TO_ANALYZE = "Person"  # Change this to your label
    
    with Neo4jPropertyAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) as analyzer:
        # Check if label exists
        labels = analyzer.get_node_labels()
        
        if LABEL_TO_ANALYZE in labels:
            count = analyzer.get_node_count(LABEL_TO_ANALYZE)
            print(f"Found {count:,} nodes with label '{LABEL_TO_ANALYZE}'")
            
            # Fast analysis
            summary = analyzer.get_property_summary_fast(LABEL_TO_ANALYZE)
            ReportGenerator.print_summary(summary, LABEL_TO_ANALYZE)
        else:
            print(f"Label '{LABEL_TO_ANALYZE}' not found in database")
            print(f"Available labels: {labels}")


def example_6_compare_modes():
    """Example 6: Compare fast mode vs standard mode."""
    print("\n" + "="*60)
    print("Example 6: Compare Analysis Modes")
    print("="*60)
    
    import time
    
    with Neo4jPropertyAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) as analyzer:
        label = analyzer.get_node_labels()[0]
        
        # Fast mode
        print("\n--- Fast Mode ---")
        start = time.time()
        summary_fast = analyzer.get_property_summary_fast(label)
        fast_time = time.time() - start
        print(f"Fast mode completed in {fast_time:.2f} seconds")
        
        # Standard mode with sampling
        print("\n--- Standard Mode (with sampling) ---")
        start = time.time()
        summary_standard = analyzer.get_property_summary(label, sample_size=10000)
        standard_time = time.time() - start
        print(f"Standard mode completed in {standard_time:.2f} seconds")
        
        print(f"\nSpeed difference: {standard_time/fast_time:.1f}x")


if __name__ == "__main__":
    # Run examples (comment out the ones you don't want to run)
    
    # example_1_basic_usage()
    # example_2_context_manager()
    # example_3_sampling()
    # example_4_html_report()
    # example_5_single_label()
    # example_6_compare_modes()
    
    print("\nUncomment the examples you want to run in the __main__ section")

