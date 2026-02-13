"""
Main entry point for Neo4j property analysis.

This script demonstrates how to use the refactored Neo4jPropertyAnalyzer package.
"""

from neo4j_analyzer import Neo4jPropertyAnalyzer
from neo4j_analyzer.report_generator import ReportGenerator
from neo4j_analyzer.performance import PerformanceMonitor
from neo4j_analyzer.results_saver import ResultsSaver


def main():
    """Main function to run the analysis."""

    # Configuration
    NEO4J_URI = "bolt://54.174.185.202"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "receipt-compasses-annexs"

    # Performance settings
    USE_FAST_MODE = True  # Set to True for very large graphs
    SAMPLE_SIZE = 50000   # Sample size for standard mode (None for all)
    FETCH_SIZE = 2000     # Batch size for data extraction
    ENABLE_PERFORMANCE_TRACKING = True  # Enable performance metrics

    # Initialize performance monitor
    perf_monitor = PerformanceMonitor() if ENABLE_PERFORMANCE_TRACKING else None

    # Store configuration in monitor
    if perf_monitor:
        perf_monitor.set_config({
            "neo4j_uri": NEO4J_URI,
            "use_fast_mode": USE_FAST_MODE,
            "sample_size": SAMPLE_SIZE,
            "fetch_size": FETCH_SIZE,
        })

    # Initialize analyzer
    analyzer = Neo4jPropertyAnalyzer(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        fetch_size=FETCH_SIZE,
        performance_monitor=perf_monitor
    )
    
    # Store all results for saving
    all_results = {}

    try:
        # Get all node labels
        labels = analyzer.get_node_labels()
        print(f"Found node labels: {labels}")

        # Analyze each label
        for label in labels:
            print(f"\n{'='*60}")
            print(f"Analyzing label: {label}")
            print(f"{'='*60}")

            # Choose analysis mode
            if USE_FAST_MODE:
                # Fast mode: Cypher aggregations, minimal memory
                summary = analyzer.get_property_summary_fast(label)
            else:
                # Standard mode: DataFrame analysis
                summary = analyzer.get_property_summary(
                    label,
                    sample_size=SAMPLE_SIZE
                )

            # Store results
            all_results[label] = summary

            # Print summary
            ReportGenerator.print_summary(summary, label)

            # Optional: Generate HTML report (only in standard mode)
            # if not USE_FAST_MODE:
            #     analyzer.analyze_properties(
            #         label,
            #         output_html=f"{label}_profile.html",
            #         sample_size=SAMPLE_SIZE,
            #         minimal=True
            #     )

    finally:
        analyzer.close()

        # Save EDA results
        if all_results:
            config = {
                "neo4j_uri": NEO4J_URI,
                "use_fast_mode": USE_FAST_MODE,
                "sample_size": SAMPLE_SIZE,
                "fetch_size": FETCH_SIZE,
            }
            ResultsSaver.save_analysis_results(all_results, config)

        # Save performance report if enabled
        if ENABLE_PERFORMANCE_TRACKING and perf_monitor:
            perf_monitor.save_report()


if __name__ == "__main__":
    main()

