"""
Quick test of performance monitoring with memory tracking.
"""

from neo4j_analyzer.performance import PerformanceMonitor
import time

def main():
    monitor = PerformanceMonitor()
    
    # Set some config
    monitor.set_config({
        "test_mode": True,
        "sample_size": 1000
    })
    
    # Test operation 1
    metric1 = monitor.start("test_operation_1")
    time.sleep(0.1)
    # Allocate some memory
    data = [i for i in range(100000)]
    monitor.stop(metric1)
    
    # Test operation 2
    metric2 = monitor.start("test_operation_2", label="TestLabel")
    time.sleep(0.05)
    monitor.stop(metric2)
    
    # Save report
    filename = monitor.save_report("test_performance_report.txt")
    print(f"Test report saved to: {filename}")

if __name__ == "__main__":
    main()

