# Getting Started with GDS Property Projection

This guide will help you get started with transforming User properties into Property nodes for graph analytics.

## Two Approaches

This project provides two approaches for property projection:

### 1. **Virtual Projection** (Cypher-based)
- Creates virtual Property nodes in GDS memory only
- No changes to your database
- Faster for one-time analysis
- Use: `GDSPropertyProjectionManager`

### 2. **Materialized Projection** (Physical nodes)
- Creates actual Property nodes in Neo4j
- Persistent and queryable
- Better for ongoing analysis
- Use: `MaterializedPropertyProjection`

## Quick Start Guide

### Step 1: Verify Your Setup

```python
from common import Neo4jConnector, Neo4jConfig

config = Neo4jConfig(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password"
)

with Neo4jConnector(config) as conn:
    # Check if you have User nodes
    result = conn.execute_query("MATCH (n:User) RETURN count(n) as count")
    print(f"User nodes: {result[0]['count']}")
    
    # Check available properties
    result = conn.execute_query("""
        MATCH (n:User)
        WITH n LIMIT 1000
        UNWIND keys(n) as key
        RETURN DISTINCT key
    """)
    print(f"Available properties: {[r['key'] for r in result]}")
```

### Step 2: Choose Your Properties

Select which User properties you want to analyze:

```python
from gds_property_projection import PropertyProjectionConfig

config = PropertyProjectionConfig(
    source_label="User",
    source_id_property="id",  # Your User ID property
    properties_to_project=[
        "country",
        "age_group", 
        "subscription_type",
        "interests"
    ]
)
```

### Step 3: Create Projection

#### Option A: Virtual Projection (Recommended for first try)

```python
from gds_property_projection import GDSPropertyProjectionManager

with Neo4jConnector(neo4j_config) as conn:
    manager = GDSPropertyProjectionManager(conn, config)
    
    # Check GDS is available
    if manager.check_gds_available():
        # Create projection
        stats = manager.create_cypher_projection()
        print(f"Created projection with {stats['nodeCount']} nodes")
```

#### Option B: Materialized Projection (For persistent analysis)

```python
from gds_property_projection.materialized_projection import MaterializedPropertyProjection

with Neo4jConnector(neo4j_config) as conn:
    manager = MaterializedPropertyProjection(conn, config)
    
    # Create physical Property nodes
    stats = manager.create_property_nodes()
    print(f"Created {stats['properties_created']} property nodes")
    
    # Create GDS projection
    manager.create_gds_projection()
```

### Step 4: Run Analytics

```python
# Find similar users
similar = manager.run_node_similarity(top_k=10)
for result in similar[:5]:
    print(f"User {result['node1_id']} similar to {result['node2_id']}: {result['similarity']:.2f}")

# Detect communities
communities = manager.run_community_detection()
print(f"Found {len(set(r['communityId'] for r in communities))} communities")

# Find influential users
pagerank = manager.run_pagerank()
for i, result in enumerate(pagerank[:10], 1):
    print(f"{i}. User {result['node_id']}: score {result['score']:.6f}")
```

## Complete Examples

### Example 1: Quick Analysis (Virtual)

```bash
# Edit credentials in example_usage.py
python gds_property_projection/example_usage.py
```

### Example 2: Persistent Analysis (Materialized)

```bash
# Edit credentials in example_materialized.py
python gds_property_projection/example_materialized.py
```

## Common Use Cases

### Use Case 1: User Segmentation

Find groups of users with similar characteristics:

```python
config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["country", "age_group", "subscription_type"]
)

# Run community detection
communities = manager.run_community_detection(algorithm="louvain")

# Analyze each community
for comm_id in set(r['communityId'] for r in communities):
    users = [r['node_id'] for r in communities if r['communityId'] == comm_id]
    print(f"Community {comm_id}: {len(users)} users")
```

### Use Case 2: Recommendation System

Find similar users for recommendations:

```python
config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["interests", "purchase_history", "browsing_category"]
)

# Find similar users
similar = manager.run_node_similarity(top_k=20, similarity_cutoff=0.5)

# For each user, get their top similar users
user_recommendations = {}
for result in similar:
    user1 = result['node1_id']
    if user1 not in user_recommendations:
        user_recommendations[user1] = []
    user_recommendations[user1].append({
        'user': result['node2_id'],
        'similarity': result['similarity']
    })
```

### Use Case 3: Influence Analysis

Identify influential users in the network:

```python
config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["follower_count_tier", "engagement_level", "content_category"]
)

# Run PageRank
influential = manager.run_pagerank()

# Get top influencers
top_influencers = influential[:50]
```

## Filtering Large Datasets

If you have millions of User nodes, use filtering:

```python
config = PropertyProjectionConfig(
    source_label="User",
    properties_to_project=["country", "subscription_type"],
    # Only analyze active users from last year
    source_filter="WHERE n.active = true AND n.created_date > date('2024-01-01')"
)
```

## Performance Tips

1. **Start small**: Test with filtered data first
2. **Choose properties wisely**: Only project properties you'll analyze
3. **Monitor memory**: Use `get_projection_stats()` to check memory usage
4. **Batch processing**: Adjust `batch_size` for materialized projections
5. **Drop projections**: Clean up when done to free memory

## Troubleshooting

### "GDS not available"
Install Neo4j GDS plugin from Neo4j Desktop or download from neo4j.com

### "Out of memory"
- Reduce number of nodes with `source_filter`
- Increase Neo4j heap size in neo4j.conf
- Use fewer properties in `properties_to_project`

### "No results from analytics"
- Check projection was created: `manager.get_projection_info()`
- Verify source nodes exist: `manager.get_source_node_count()`
- Check property values are not all NULL

## Next Steps

1. ✅ Run the example scripts
2. ✅ Customize configuration for your data
3. ✅ Experiment with different GDS algorithms
4. ✅ Integrate results into your application
5. ✅ Read the full README.md for advanced features

## Resources

- [README.md](README.md) - Full documentation
- [example_usage.py](example_usage.py) - Virtual projection example
- [example_materialized.py](example_materialized.py) - Materialized projection example
- [Neo4j GDS Docs](https://neo4j.com/docs/graph-data-science/)

