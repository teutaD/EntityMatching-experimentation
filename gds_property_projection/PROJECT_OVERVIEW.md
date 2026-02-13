# GDS Property Projection - Project Overview

## 🎯 Project Goal

Transform User node properties into separate Property nodes connected via HAS relationships, enabling advanced graph analytics on property-based similarities and patterns using Neo4j Graph Data Science (GDS).

## 📁 Project Structure

```
OntoAligner/
├── common/                          # Shared Neo4j utilities
│   ├── __init__.py
│   └── neo4j_connector.py          # Reusable Neo4j connector
│
└── gds_property_projection/        # Main project
    ├── __init__.py                 # Package exports
    ├── config.py                   # Configuration classes
    ├── projection_manager.py       # Virtual GDS projections
    ├── materialized_projection.py  # Physical Property nodes
    ├── example_usage.py            # Virtual projection example
    ├── example_materialized.py     # Materialized projection example
    ├── requirements.txt            # Python dependencies
    ├── README.md                   # Full documentation
    ├── GETTING_STARTED.md          # Quick start guide
    └── PROJECT_OVERVIEW.md         # This file
```

## 🔧 Components

### 1. Common Module (`common/`)

**Purpose**: Reusable Neo4j connection management for all projects

**Key Classes**:
- `Neo4jConfig`: Connection configuration dataclass
- `Neo4jConnector`: Connection manager with context manager support

**Features**:
- Connection pooling
- Session management
- Query execution helpers
- Basic database utilities

### 2. Configuration (`config.py`)

**Purpose**: Define projection parameters

**Key Classes**:
- `PropertyProjectionConfig`: Configuration for property-to-node transformation

**Configurable Options**:
- Source node label and properties
- Property node label and relationship type
- Graph projection name
- Filtering and batch processing

### 3. Virtual Projection (`projection_manager.py`)

**Purpose**: Create GDS projections without modifying the database

**Key Classes**:
- `GDSPropertyProjectionManager`: Manages Cypher-based GDS projections

**Features**:
- Virtual Property nodes in GDS memory
- No database modifications
- Fast for one-time analysis
- Built-in analytics: similarity, PageRank, communities

**Use When**:
- Testing and exploration
- One-time analysis
- Don't want to modify database
- Need quick results

### 4. Materialized Projection (`materialized_projection.py`)

**Purpose**: Create physical Property nodes in Neo4j database

**Key Classes**:
- `MaterializedPropertyProjection`: Creates and manages physical Property nodes

**Features**:
- Persistent Property nodes
- Queryable with standard Cypher
- Better for ongoing analysis
- Property distribution analysis

**Use When**:
- Need persistent analysis
- Want to query Property nodes directly
- Building applications on top
- Long-term analytics

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r gds_property_projection/requirements.txt

# Ensure Neo4j GDS plugin is installed
# Check in Neo4j: RETURN gds.version()
```

### Basic Usage

```python
from common import Neo4jConnector, Neo4jConfig
from gds_property_projection import GDSPropertyProjectionManager, PropertyProjectionConfig

# Configure
neo4j_config = Neo4jConfig(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

projection_config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["country", "age_group"]
)

# Create and analyze
with Neo4jConnector(neo4j_config) as conn:
    manager = GDSPropertyProjectionManager(conn, projection_config)
    manager.create_cypher_projection()
    similar_users = manager.run_node_similarity()
```

## 📊 Use Cases

### 1. User Segmentation
Group users by shared characteristics for targeted marketing or personalization.

### 2. Recommendation Systems
Find similar users to recommend products, content, or connections.

### 3. Influence Analysis
Identify influential users based on property-based network structure.

### 4. Anomaly Detection
Find users with unusual property combinations.

### 5. Community Discovery
Discover natural groupings of users with similar attributes.

## 🔄 Two Approaches Comparison

| Feature | Virtual Projection | Materialized Projection |
|---------|-------------------|------------------------|
| **Database Changes** | None | Creates Property nodes |
| **Persistence** | In-memory only | Permanent |
| **Speed** | Fast | Moderate |
| **Queryability** | GDS only | Standard Cypher + GDS |
| **Memory Usage** | Lower | Higher |
| **Best For** | Quick analysis | Ongoing analytics |
| **Cleanup** | Drop projection | Delete nodes |

## 📚 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step tutorial
- **[README.md](README.md)** - Complete reference documentation
- **[example_usage.py](example_usage.py)** - Virtual projection example
- **[example_materialized.py](example_materialized.py)** - Materialized example

## 🛠️ Available Analytics

### Node Similarity
Find users with similar property values
```python
manager.run_node_similarity(top_k=10, similarity_cutoff=0.3)
```

### PageRank
Identify influential users
```python
manager.run_pagerank(max_iterations=20)
```

### Community Detection
Discover user communities
```python
manager.run_community_detection(algorithm="louvain")
```

### Custom Queries
Run any GDS algorithm on the projection
```python
query = f"CALL gds.betweenness.stream('{graph_name}')"
results = connector.execute_query(query)
```

## 🎓 Learning Path

1. **Start Here**: Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Run Examples**: Execute `example_usage.py` and `example_materialized.py`
3. **Customize**: Modify configuration for your data
4. **Explore**: Try different GDS algorithms
5. **Integrate**: Build your application

## 🔗 Resources

- [Neo4j GDS Documentation](https://neo4j.com/docs/graph-data-science/)
- [Cypher Projections Guide](https://neo4j.com/docs/graph-data-science/current/management-ops/projections/graph-project-cypher/)
- [GDS Algorithms](https://neo4j.com/docs/graph-data-science/current/algorithms/)

## 💡 Tips

1. **Start small**: Test with filtered subset first
2. **Monitor memory**: Use `get_projection_stats()`
3. **Choose wisely**: Only project properties you'll analyze
4. **Clean up**: Drop projections when done
5. **Experiment**: Try both approaches to see what fits

## 🤝 Integration with Existing Code

The `common/neo4j_connector.py` module can be used across all your Neo4j projects:

```python
# In any project
from common import Neo4jConnector, Neo4jConfig

config = Neo4jConfig(uri="...", user="...", password="...")
with Neo4jConnector(config) as conn:
    results = conn.execute_query("MATCH (n) RETURN count(n)")
```

## 📈 Next Steps

1. ✅ Review your User node properties
2. ✅ Choose properties for projection
3. ✅ Run example scripts
4. ✅ Analyze results
5. ✅ Integrate into your workflow

