"""
Performance monitoring and metrics collection.
"""

import time
import functools
import psutil
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PerformanceMetric:
    """Single performance metric."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    start_memory_mb: Optional[float] = None
    end_memory_mb: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

    def stop(self, end_memory_mb: Optional[float] = None):
        """Stop timing and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        if end_memory_mb is not None and self.start_memory_mb is not None:
            self.end_memory_mb = end_memory_mb
            self.memory_delta_mb = end_memory_mb - self.start_memory_mb
        return self.duration

    def __str__(self):
        if self.duration:
            mem_str = f", Δmem: {self.memory_delta_mb:+.1f}MB" if self.memory_delta_mb else ""
            return f"{self.name}: {self.duration:.3f}s{mem_str}"
        return f"{self.name}: In progress..."


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: List[PerformanceMetric] = []
        self.current_metric: Optional[PerformanceMetric] = None
        self.enabled = True
        self.process = psutil.Process(os.getpid())
        self.config: Dict[str, Any] = {}

    def set_config(self, config: Dict[str, Any]):
        """Store configuration for reporting."""
        self.config = config

    def _get_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def start(self, name: str, **metadata) -> PerformanceMetric:
        """
        Start timing an operation.

        Args:
            name: Name of the operation
            **metadata: Additional metadata to store

        Returns:
            PerformanceMetric instance
        """
        if not self.enabled:
            return None

        metric = PerformanceMetric(
            name=name,
            start_time=time.time(),
            start_memory_mb=self._get_memory_mb(),
            metadata=metadata
        )
        self.metrics.append(metric)
        self.current_metric = metric
        return metric
    
    def stop(self, metric: Optional[PerformanceMetric] = None):
        """
        Stop timing an operation.

        Args:
            metric: Specific metric to stop, or current if None
        """
        if not self.enabled:
            return

        if metric is None:
            metric = self.current_metric

        if metric:
            metric.stop(end_memory_mb=self._get_memory_mb())
    
    def get_summary(self) -> Dict:
        """
        Get performance summary.

        Returns:
            Dictionary with performance statistics
        """
        if not self.metrics:
            return {}

        total_time = sum(m.duration for m in self.metrics if m.duration)

        # Get memory stats
        memory_deltas = [m.memory_delta_mb for m in self.metrics if m.memory_delta_mb is not None]
        peak_memory = max((m.end_memory_mb for m in self.metrics if m.end_memory_mb), default=0)

        # Group by operation name
        by_name = {}
        for metric in self.metrics:
            if metric.duration:
                if metric.name not in by_name:
                    by_name[metric.name] = {
                        "durations": [],
                        "memory_deltas": []
                    }
                by_name[metric.name]["durations"].append(metric.duration)
                if metric.memory_delta_mb is not None:
                    by_name[metric.name]["memory_deltas"].append(metric.memory_delta_mb)

        # Calculate statistics per operation
        stats = {}
        for name, data in by_name.items():
            durations = data["durations"]
            mem_deltas = data["memory_deltas"]

            stats[name] = {
                "count": len(durations),
                "total_time": sum(durations),
                "avg_time": sum(durations) / len(durations),
                "min_time": min(durations),
                "max_time": max(durations)
            }

            if mem_deltas:
                stats[name]["avg_memory_delta_mb"] = sum(mem_deltas) / len(mem_deltas)
                stats[name]["max_memory_delta_mb"] = max(mem_deltas)

        return {
            "total_time": total_time,
            "total_operations": len(self.metrics),
            "peak_memory_mb": peak_memory,
            "total_memory_delta_mb": sum(memory_deltas) if memory_deltas else 0,
            "by_operation": stats
        }
    
    def save_report(self, filename: Optional[str] = None):
        """
        Save performance report to a file.

        Args:
            filename: Optional filename. If None, generates dated filename.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.txt"

        summary = self.get_summary()

        with open(filename, 'w') as f:
            f.write("="*70 + "\n")
            f.write("PERFORMANCE REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")

            # Configuration
            if self.config:
                f.write("CONFIGURATION:\n")
                f.write("-"*70 + "\n")
                for key, value in self.config.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

            # Summary
            f.write("SUMMARY:\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Time: {summary['total_time']:.3f}s\n")
            f.write(f"Total Operations: {summary['total_operations']}\n")
            f.write(f"Peak Memory: {summary['peak_memory_mb']:.1f} MB\n")
            f.write(f"Total Memory Delta: {summary['total_memory_delta_mb']:+.1f} MB\n")
            f.write("\n")

            # By Operation
            f.write("BY OPERATION:\n")
            f.write("-"*70 + "\n")
            for name, stats in summary['by_operation'].items():
                f.write(f"\n  {name}:\n")
                f.write(f"    Count: {stats['count']}\n")
                f.write(f"    Total Time: {stats['total_time']:.3f}s\n")
                f.write(f"    Average Time: {stats['avg_time']:.3f}s\n")
                f.write(f"    Min Time: {stats['min_time']:.3f}s\n")
                f.write(f"    Max Time: {stats['max_time']:.3f}s\n")
                if 'avg_memory_delta_mb' in stats:
                    f.write(f"    Avg Memory Delta: {stats['avg_memory_delta_mb']:+.1f} MB\n")
                    f.write(f"    Max Memory Delta: {stats['max_memory_delta_mb']:+.1f} MB\n")

            f.write("\n")

            # Timeline
            f.write("TIMELINE:\n")
            f.write("-"*70 + "\n")
            for i, metric in enumerate(self.metrics, 1):
                duration_str = f"{metric.duration:.3f}s" if metric.duration else "In progress"
                mem_str = f" | Δmem: {metric.memory_delta_mb:+.1f}MB" if metric.memory_delta_mb else ""
                metadata_str = ""
                if metric.metadata:
                    metadata_str = " | " + ", ".join(f"{k}={v}" for k, v in metric.metadata.items())
                f.write(f"{i:3d}. {metric.name:40s} {duration_str:>10s}{mem_str}{metadata_str}\n")

            f.write("="*70 + "\n")

        print(f"\nPerformance report saved to: {filename}")
        return filename
    
    def print_timeline(self):
        """Print a timeline of all operations."""
        if not self.metrics:
            print("No performance metrics collected")
            return
        
        print("\n" + "="*70)
        print("PERFORMANCE TIMELINE")
        print("="*70)
        
        for i, metric in enumerate(self.metrics, 1):
            duration_str = f"{metric.duration:.3f}s" if metric.duration else "In progress"
            metadata_str = ""
            if metric.metadata:
                metadata_str = " | " + ", ".join(f"{k}={v}" for k, v in metric.metadata.items())
            print(f"{i:3d}. {metric.name:40s} {duration_str:>10s}{metadata_str}")
        
        print("="*70)
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.current_metric = None


def timed(monitor: PerformanceMonitor, operation_name: Optional[str] = None):
    """
    Decorator to automatically time a function.
    
    Args:
        monitor: PerformanceMonitor instance
        operation_name: Optional custom name (defaults to function name)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            metric = monitor.start(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.stop(metric)
        return wrapper
    return decorator


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_global_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _global_monitor

