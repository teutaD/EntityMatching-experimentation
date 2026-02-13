# GDS Property Projection

Transform node properties into connected property nodes for advanced graph analytics using Neo4j Graph Data Science (GDS).

## Overview

This project enables you to create GDS graph projections where properties of nodes (e.g., User properties) become separate Property nodes connected via HAS relationships. This transformation allows you to:

- **Find similar entities** based on shared property values
- **Detect communities** of entities with similar characteristics
- **Analyze influence** using centrality algorithms
- **Discover patterns** in property distributions

## Architecture

```
Original Graph:                    Projected Graph:
┌──────────┐                      ┌──────────┐
│  User    │                      │  User    │
│  id: 1   │                      │  id: 1   │
│  age: 25 │      ──────>         └────┬─────┘
│  city: NY│                           │ HAS
└──────────┘                           ▼
                                  ┌──────────┐
                                  │ Property │
                                  │ age: 25  │
                                  └──────────┘
                                       │ HAS
                                       ▼
                                  ┌──────────┐
                                  │ Property │
                                  │ city: NY │
                                  └──────────┘
```

## Features

- ✅ **Cypher-based GDS projections** - Efficient virtual graph creation
- ✅ **Configurable property selection** - Choose which properties to project
- ✅ **Built-in analytics** - Node similarity, PageRank, community detection
- ✅ **Batch processing** - Handle millions of nodes efficiently
- ✅ **Flexible filtering** - Apply filters to source nodes
- ✅ **Reusable connector** - Common Neo4j connection management

## Prerequisites

1. **Neo4j Database** (version 4.4+)
2. **Neo4j GDS Plugin** installed and enabled
3. **Python 3.8+**
4. **neo4j-driver** Python package

### Installing Neo4j GDS

```bash
# For Neo4j Desktop: Install GDS plugin from the Plugins tab
# For Neo4j Server: Download from https://neo4j.com/download-center/

# Verify GDS is installed
RETURN gds.version()
```

## Installation

```bash
# Install required Python packages
pip install neo4j pandas
```

## Quick Start

### 1. Basic Usage

```python
from common import Neo4jConnector, Neo4jConfig
from gds_property_projection import GDSPropertyProjectionManager, PropertyProjectionConfig

# Configure Neo4j connection
neo4j_config = Neo4jConfig(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password"
)

# Configure property projection
projection_config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["country", "age_group", "interests"],
    graph_name="user-property-graph"
)

# Create projection and run analytics
with Neo4jConnector(neo4j_config) as connector:
    manager = GDSPropertyProjectionManager(connector, projection_config)
    
    # Create projection
    manager.create_cypher_projection()
    
    # Find similar users
    similar_users = manager.run_node_similarity(top_k=10)
    
    # Detect communities
    communities = manager.run_community_detection()
```

### 2. Run Example Script

```bash
# Edit example_usage.py with your Neo4j credentials
python gds_property_projection/example_usage.py
```

## Configuration

### PropertyProjectionConfig Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source_label` | str | "User" | Label of source nodes to project |
| `source_id_property` | str | "id" | Property to use as node identifier |
| `properties_to_project` | List[str] | [] | List of properties to convert to nodes |
| `property_node_label` | str | "Property" | Label for property nodes |
| `relationship_type` | str | "HAS" | Relationship type connecting nodes |
| `graph_name` | str | "user-property-graph" | Name of GDS projection |
| `batch_size` | int | 10000 | Batch size for processing |
| `source_filter` | str | None | Optional Cypher WHERE clause |

### Example with Filtering

```python
projection_config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["country", "subscription_type"],
    source_filter="WHERE n.active = true AND n.created_date > date('2024-01-01')"
)
```

## Available Analytics

### 1. Node Similarity

Find nodes with similar property values:

```python
results = manager.run_node_similarity(
    top_k=10,              # Top K similar nodes per node
    similarity_cutoff=0.3  # Minimum similarity score (0-1)
)
```

### 2. PageRank

Identify influential nodes:

```python
results = manager.run_pagerank(
    max_iterations=20,
    damping_factor=0.85
)
```

### 3. Community Detection

Discover groups of similar nodes:

```python
# Louvain algorithm
results = manager.run_community_detection(algorithm="louvain")

# Other options: "labelPropagation", "wcc"
```

## Project Structure

```
gds_property_projection/
├── __init__.py              # Package initialization
├── config.py                # Configuration classes
├── projection_manager.py    # Main projection manager
├── example_usage.py         # Example script
└── README.md               # This file

common/
├── __init__.py
└── neo4j_connector.py      # Reusable Neo4j connector
```

## Advanced Usage

### Custom Analytics Query

```python
# Run custom GDS algorithm on projection
query = f"""
CALL gds.betweenness.stream('{manager.config.graph_name}')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS user_id, score
ORDER BY score DESC
LIMIT 20
"""
results = connector.execute_query(query)
```

### Projection Statistics

```python
stats = manager.get_projection_stats()
print(f"Nodes: {stats['node_count']}")
print(f"Relationships: {stats['relationship_count']}")
print(f"Avg degree: {stats['degree_stats']['avg_degree']}")
```

### List All Projections

```python
projections = manager.list_projections()
for proj in projections:
    print(f"{proj['graphName']}: {proj['nodeCount']} nodes")
```

## Performance Considerations

- **Memory**: GDS projections are stored in-memory. Monitor with `get_projection_stats()`
- **Large graphs**: Use `source_filter` to limit nodes
- **Batch size**: Adjust `batch_size` in config for optimal performance
- **Property selection**: Only project properties needed for analysis

## Troubleshooting

### GDS Not Available
```
ERROR: GDS not available
```
**Solution**: Install Neo4j GDS plugin from Neo4j Desktop or download from neo4j.com

### Out of Memory
```
ERROR: Java heap space
```
**Solution**: Increase Neo4j heap size in neo4j.conf:
```
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
```

### Projection Already Exists
The manager automatically drops existing projections with the same name before creating new ones.

## Next Steps

1. **Customize** the configuration for your specific use case
2. **Experiment** with different GDS algorithms
3. **Integrate** results into your application
4. **Scale** to production with appropriate memory settings

## Resources

- [Neo4j GDS Documentation](https://neo4j.com/docs/graph-data-science/)
- [GDS Algorithms Guide](https://neo4j.com/docs/graph-data-science/current/algorithms/)
- [Cypher Projections](https://neo4j.com/docs/graph-data-science/current/management-ops/projections/graph-project-cypher/)

