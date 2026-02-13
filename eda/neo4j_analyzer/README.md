# Neo4j Property Analyzer

A modular, well-structured package for analyzing Neo4j graph properties.

## Package Structure

```
neo4j_analyzer/
├── __init__.py              # Package initialization
├── analyzer.py              # Main analyzer orchestration
├── config.py                # Configuration classes
├── connection.py            # Neo4j connection management
├── enums.py                 # Enumerations (PropertyType, AnalysisMode)
├── extractor.py             # Data extraction to DataFrames
├── property_analyzer.py     # Property analysis logic
└── report_generator.py      # Report generation
```

## Architecture

### Separation of Concerns

1. **Connection Layer** (`connection.py`)
   - Manages Neo4j driver lifecycle
   - Handles database queries
   - Provides basic database operations

2. **Data Extraction** (`extractor.py`)
   - Extracts data from Neo4j to pandas
   - Handles batching and streaming
   - Supports sampling and limiting

3. **Analysis Logic** (`property_analyzer.py`)
   - Analyzes property characteristics
   - Classifies properties (UNIQUE, CATEGORICAL, etc.)
   - Supports both DataFrame and Cypher-based analysis

4. **Report Generation** (`report_generator.py`)
   - Generates ydata-profiling reports
   - Formats console output
   - Handles report persistence

5. **Configuration** (`config.py`)
   - Centralized configuration management
   - Type-safe configuration classes
   - Easy configuration from dictionaries

6. **Main Orchestrator** (`analyzer.py`)
   - Coordinates all components
   - Provides high-level API
   - Manages component lifecycle

## Usage Examples

### Basic Usage

```python
from neo4j_analyzer import Neo4jPropertyAnalyzer

# Initialize
analyzer = Neo4jPropertyAnalyzer(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Get labels
labels = analyzer.get_node_labels()

# Analyze properties (fast mode)
summary = analyzer.get_property_summary_fast("Person")

# Close connection
analyzer.close()
```

### Using Context Manager

```python
from neo4j_analyzer import Neo4jPropertyAnalyzer

with Neo4jPropertyAnalyzer(uri, user, password) as analyzer:
    labels = analyzer.get_node_labels()
    for label in labels:
        summary = analyzer.get_property_summary_fast(label)
        print(summary)
```

### Standard Mode with Sampling

```python
analyzer = Neo4jPropertyAnalyzer(uri, user, password, fetch_size=2000)

# Analyze with sampling
summary = analyzer.get_property_summary(
    label="Person",
    sample_size=50000
)

# Generate HTML report
analyzer.analyze_properties(
    label="Person",
    sample_size=50000,
    output_html="person_report.html",
    minimal=True
)
```

## Design Patterns Used

1. **Single Responsibility Principle**: Each class has one clear purpose
2. **Dependency Injection**: Components receive dependencies via constructor
3. **Context Manager**: Proper resource management with `__enter__`/`__exit__`
4. **Strategy Pattern**: Different analysis strategies (fast vs standard)
5. **Configuration Object**: Type-safe configuration management
6. **Static Methods**: Utility functions that don't need instance state

## Benefits of This Architecture

✅ **Testability**: Each component can be tested independently
✅ **Maintainability**: Clear separation makes changes easier
✅ **Reusability**: Components can be used independently
✅ **Extensibility**: Easy to add new features
✅ **Type Safety**: Type hints throughout
✅ **Documentation**: Clear docstrings for all public methods

