# Neo4j EDA Notebook Guide

## Overview

The `neo4j_eda_analysis.ipynb` notebook provides an interactive way to perform exploratory data analysis on Neo4j graph databases using the Neo4j Property Analyzer package.

## Features

### 1. **Database Exploration**
- Connect to Neo4j database
- List all node labels
- Count nodes per label

### 2. **Property Analysis**
- Analyze properties to determine if they are categorical or unique
- Two analysis modes:
  - **Fast Mode**: Uses Cypher aggregations (ideal for large graphs)
  - **Standard Mode**: Uses DataFrame analysis (more detailed insights)

### 3. **Visualizations**
- Property type distribution (pie and bar charts)
- Property uniqueness ratios
- Performance metrics visualization

### 4. **Data Extraction**
- Extract sample data to pandas DataFrames
- Perform custom analysis on extracted data

### 5. **Reporting**
- Generate HTML profiling reports (ydata-profiling)
- Save analysis results to JSON
- Export performance metrics

## Getting Started

### Prerequisites

1. Install required dependencies:
```bash
cd eda
pipenv install
```

2. Ensure you have Jupyter installed:
```bash
pipenv install jupyter
```

### Running the Notebook

1. Start Jupyter:
```bash
cd eda
pipenv run jupyter notebook
```

2. Open `neo4j_eda_analysis.ipynb` in your browser

3. Update the configuration cell with your Neo4j credentials:
```python
NEO4J_URI = "bolt://your-neo4j-host:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your-password"
```

4. Run the cells sequentially (Shift+Enter)

## Notebook Structure

### Section 1: Setup and Imports
- Import required libraries
- Configure plotting styles

### Section 2: Configuration
- Set Neo4j connection parameters
- Configure analysis settings

### Section 3: Initialize Analyzer
- Connect to database
- Explore available labels

### Section 4: Analyze Properties
- Run property analysis on all labels
- Choose between fast and standard modes

### Section 5: Visualize Results
- Create charts showing property type distribution
- Visualize property characteristics

### Section 6: Detailed Analysis
- Deep dive into specific labels
- Analyze property uniqueness ratios

### Section 7: Data Extraction
- Extract sample data to DataFrames
- Perform custom analysis

### Section 8: HTML Reports
- Generate comprehensive profiling reports
- (Only available in standard mode)

### Section 9: Performance Analysis
- View performance metrics
- Visualize operation timings

### Section 10: Save Results
- Export analysis results to JSON
- Save performance reports

### Section 11: Summary
- Display overall statistics
- Show property type breakdown

### Section 12: Cleanup
- Close database connections

## Configuration Options

### Analysis Modes

**Fast Mode** (`USE_FAST_MODE = True`)
- Uses Cypher aggregations
- Minimal memory usage
- Ideal for graphs with millions of nodes
- No DataFrame extraction

**Standard Mode** (`USE_FAST_MODE = False`)
- Extracts data to pandas DataFrames
- More detailed analysis
- Supports HTML report generation
- Higher memory usage

### Sample Size

Control how many nodes to analyze:
```python
SAMPLE_SIZE = 50000  # Analyze 50,000 nodes
SAMPLE_SIZE = None   # Analyze all nodes
```

### Fetch Size

Control batch size for data extraction:
```python
FETCH_SIZE = 2000  # Fetch 2000 records per batch
```

## Tips and Best Practices

1. **Start with Fast Mode**: For initial exploration, use fast mode to quickly understand your data

2. **Use Sampling**: For large graphs, use sampling in standard mode to reduce memory usage

3. **Generate HTML Reports Selectively**: HTML reports are comprehensive but take time to generate

4. **Monitor Performance**: Enable performance tracking to identify bottlenecks

5. **Save Results**: Always save your analysis results for future reference

## Troubleshooting

### Connection Issues
- Verify Neo4j is running
- Check URI, username, and password
- Ensure network connectivity

### Memory Issues
- Use fast mode for large graphs
- Reduce sample size
- Increase fetch size for better batching

### Slow Performance
- Enable fast mode
- Use sampling
- Check network latency to Neo4j

## Example Workflows

### Quick Exploration
1. Set `USE_FAST_MODE = True`
2. Run all cells
3. Review property type distribution
4. Identify interesting labels for deeper analysis

### Detailed Analysis
1. Set `USE_FAST_MODE = False`
2. Set `SAMPLE_SIZE = 10000`
3. Run analysis on specific labels
4. Generate HTML reports
5. Extract data for custom analysis

### Performance Benchmarking
1. Enable performance tracking
2. Run analysis with different settings
3. Compare fast vs standard mode
4. Review performance metrics

## Integration with Other Tools

The notebook can be integrated with:
- **Ontology alignment workflows**: Use property analysis to inform alignment strategies
- **Data quality pipelines**: Identify data quality issues
- **Schema design**: Understand property characteristics for schema optimization
- **Custom analysis**: Export data for use in other tools

## Additional Resources

- `examples.py`: More usage examples
- `PERFORMANCE_GUIDE.md`: Performance optimization tips
- `REFACTORING_GUIDE.md`: Architecture and design details
- `README.md`: Package documentation

