# Neo4j Graph Analysis Workflow

This document describes the complete workflow for analyzing and reducing dimensionality in your Neo4j graph database.

## Directory Structure

```
OntoAligner/
├── eda/                          # Exploratory Data Analysis
│   ├── neo4j_analyzer/           # Modular EDA package
│   ├── run_analysis.py           # Main EDA script
│   ├── examples.py               # Usage examples
│   ├── PERFORMANCE_GUIDE.md      # Performance optimization guide
│   └── REFACTORING_GUIDE.md      # Code architecture guide
│
├── dim_reduction/                # Dimensionality Reduction
│   ├── placeholder_identifier.py # Degree centrality analysis
│   └── README.md                 # Usage guide
│
└── WORKFLOW.md                   # This file
```

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STEP 1: EDA                              │
│  Understand your graph structure and property patterns      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: Placeholder Identification             │
│  Find high-degree nodes that may be descriptors             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            STEP 3: Dimensionality Reduction                 │
│  Transform or remove placeholder nodes                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Exploratory Data Analysis (EDA)

**Location**: `eda/` directory

**Purpose**: Understand your graph structure, node types, and property characteristics.

### What EDA Tells You

1. **Node Labels**: What types of nodes exist in your graph
2. **Property Classification**:
   - **UNIQUE**: Properties that are unique per node (e.g., IDs)
   - **SEMI_UNIQUE**: Properties with many different values
   - **CATEGORICAL**: Properties with limited repeating values
   - **HIGHLY_CATEGORICAL**: Properties with very few distinct values
3. **Null Counts**: How many nodes are missing each property
4. **Sample Values**: For categorical properties, see the most common values

### Running EDA

```bash
cd eda
pipenv run python run_analysis.py
```

### Configuration

Edit `run_analysis.py`:
```python
USE_FAST_MODE = True      # Fast for large graphs
SAMPLE_SIZE = 50000       # Sample size (or None for all)
ENABLE_PERFORMANCE_TRACKING = True  # Track performance metrics
```

### Output

- **Console**: Property summaries for each node label
- **EDA Results**: `eda_results_TIMESTAMP.json` with property classifications
- **Performance Report**: `performance_report_TIMESTAMP.txt` with timing and memory usage

### Example Output

```
📊 description:
    Type: HIGHLY_CATEGORICAL
    Unique values: 3,892
    Unique ratio: 0.08%
    Null count: 4,674,281
    Sample categorical values (with counts):
      - Unknown: 450,000
      - N/A: 320,000
      - Other: 180,000
```

**Insight**: The "description" property has very few unique values and many nulls - these might be placeholder values!

---

## Step 2: Placeholder Identification

**Location**: `dim_reduction/` directory

**Purpose**: Identify nodes with high degree centrality that may be acting as placeholders or descriptors.

### What Placeholder Identification Tells You

1. **Identifiers from EDA**: Automatically loads UNIQUE/SEMI_UNIQUE properties from EDA results
2. **Degree Centrality**: How many connections each node has
3. **Placeholder Nodes**: Nodes above a threshold (e.g., 90th percentile)
4. **Statistics**: Average degree, max degree, percentage of placeholders
5. **Identifier Values**: Shows identifier property values for each placeholder node

### Running Placeholder Identification

```bash
cd dim_reduction
pipenv run python placeholder_identifier.py
```

### Configuration

Edit `placeholder_identifier.py`:
```python
NODE_LABELS = ["Entity", "Concept"]  # Node types from EDA
THRESHOLD_PERCENTILE = 90.0          # Top 10% by degree
DIRECTION = "BOTH"                   # "BOTH", "OUTGOING", "INCOMING"
RELATIONSHIP_TYPES = None            # None = all, or specify types
EDA_RESULTS_FILE = None              # None = auto-find latest EDA results
```

**Note**: The script automatically loads the latest EDA results to identify which properties are identifiers (UNIQUE/SEMI_UNIQUE).

### Output

- **Console**: Statistics and top 10 placeholder nodes
- **CSV Files**:
  - `placeholder_analysis_all_nodes_TIMESTAMP.csv`
  - `placeholder_analysis_placeholders_TIMESTAMP.csv`

### Example Output

```
📊 Loading EDA results from: eda/eda_results_20260209_123456.json

======================================================================
IDENTIFIERS FROM EDA (UNIQUE/SEMI_UNIQUE Properties)
======================================================================

Entity:
  • id
  • uuid
  • name

Concept:
  • concept_id
======================================================================

PLACEHOLDER IDENTIFICATION RESULTS
======================================================================
Node Labels: ['Entity']
Direction: BOTH
Total Nodes Analyzed: 100,000
Degree Centrality Threshold (90th percentile): 150.00
Identified Placeholders: 10,000 (10.00%)
Average Degree (All): 45.23
Average Degree (Placeholders): 287.50
Max Degree: 5,432
======================================================================

Top 10 Placeholder Nodes (Highest Degree):
----------------------------------------------------------------------
  Degree:  5,432 | Labels: ['Entity']
           Identifiers: id: e12345, name: Unknown Entity
           Properties: type: Unknown, category: Other
  Degree:  4,821 | Labels: ['Entity']
           Identifiers: id: e67890, name: N/A
           Properties: type: N/A, category: Unspecified
```

**Insight**: Nodes with "Unknown", "N/A", "Other" are high-degree placeholders! The identifiers help you see exactly which nodes they are.

---

## Step 3: Dimensionality Reduction Strategies

Based on EDA and placeholder identification results, choose a strategy:

### Strategy 1: Convert Placeholders to Properties

**When**: Placeholders represent categories or types

```cypher
// Example: Convert "Unknown" type nodes to a property
MATCH (e:Entity)-[:HAS_TYPE]->(t:Type {name: "Unknown"})
SET e.type = "Unknown"
DETACH DELETE t
```

### Strategy 2: Remove Placeholder Nodes

**When**: Placeholders don't add meaningful information

```cypher
// Example: Remove nodes with very high degree
MATCH (n:Entity)
WHERE size((n)--()) > 1000
DETACH DELETE n
```

### Strategy 3: Mark Placeholders

**When**: You want to keep them but identify them

```cypher
// Example: Add a flag to placeholder nodes
MATCH (n:Entity)
WHERE size((n)--()) > 150
SET n.is_placeholder = true
```

### Strategy 4: Create Summary Nodes

**When**: Placeholders represent aggregations

```cypher
// Example: Create a summary node for a category
MATCH (e:Entity)-[:HAS_CATEGORY]->(c:Category {name: "Electronics"})
WITH c, count(e) as entity_count
SET c.entity_count = entity_count
```

---

## Complete Example Workflow

### 1. Run EDA

```bash
cd eda
pipenv run python run_analysis.py
```

**Result**: Discovered that "Entity" nodes have a "type" property that is HIGHLY_CATEGORICAL with only 50 unique values.

### 2. Investigate Those 50 Types

```bash
cd ../dim_reduction
# Edit placeholder_identifier.py:
# NODE_LABELS = ["Entity"]
# DIRECTION = "INCOMING"  # How many entities point to them?

pipenv run python placeholder_identifier.py
```

**Result**: Found that 45 of the 50 types are placeholder nodes with degree > 1000.

### 3. Decide on Action

Based on the results:
- 5 types are meaningful (low degree)
- 45 types are placeholders (high degree)

**Action**: Convert the 45 placeholder types to properties on Entity nodes.

### 4. Execute Transformation

```cypher
// Convert high-degree type nodes to properties
MATCH (e:Entity)-[:HAS_TYPE]->(t:Type)
WHERE size((t)<--()) > 1000
SET e.type_name = t.name
WITH t
DETACH DELETE t
```

### 5. Verify

Run EDA again to see the impact:
```bash
cd ../eda
pipenv run python run_analysis.py
```

---

## Tips and Best Practices

1. **Start with EDA**: Always understand your data before making changes
2. **Use Performance Tracking**: Monitor memory and time for large graphs
3. **Experiment with Thresholds**: Try different percentiles (85%, 90%, 95%)
4. **Backup First**: Always backup your graph before transformations
5. **Iterate**: Run EDA → Identify → Transform → Verify in cycles
6. **Document**: Keep notes on what you discover and why you made changes

---

## Next Steps

After completing this workflow, you can:
- Run graph algorithms (PageRank, Community Detection, etc.)
- Perform embeddings on the reduced graph
- Build machine learning models
- Visualize the simplified structure

