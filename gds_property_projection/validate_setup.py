"""
Validation script to check your Neo4j setup and data before running projections.

This script helps you:
1. Verify Neo4j connection
2. Check GDS availability
3. Analyze your User nodes
4. Suggest configuration
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common import Neo4jConnector, Neo4jConfig


def validate_connection(config: Neo4jConfig) -> bool:
    """Validate Neo4j connection."""
    print("\n[1] Testing Neo4j Connection...")
    try:
        with Neo4jConnector(config) as conn:
            result = conn.execute_query("RETURN 1 as test")
            if result and result[0]['test'] == 1:
                print("    ✓ Connection successful!")
                return True
    except Exception as e:
        print(f"    ✗ Connection failed: {e}")
        return False
    return False


def check_gds(connector: Neo4jConnector) -> bool:
    """Check if GDS is available."""
    print("\n[2] Checking GDS Availability...")
    try:
        result = connector.execute_query("RETURN gds.version() AS version")
        if result:
            print(f"    ✓ GDS version: {result[0]['version']}")
            return True
    except Exception as e:
        print(f"    ✗ GDS not available: {e}")
        print("    → Install Neo4j GDS plugin from Neo4j Desktop or neo4j.com")
        return False
    return False


def analyze_user_nodes(connector: Neo4jConnector, label: str = "User") -> dict:
    """Analyze User nodes in the database."""
    print(f"\n[3] Analyzing {label} Nodes...")
    
    analysis = {}
    
    # Count nodes
    try:
        result = connector.execute_query(f"MATCH (n:{label}) RETURN count(n) as count")
        count = result[0]['count'] if result else 0
        analysis['count'] = count
        print(f"    ✓ Found {count:,} {label} nodes")
        
        if count == 0:
            print(f"    ⚠ No {label} nodes found!")
            print(f"    → Check if your node label is '{label}' or use a different label")
            return analysis
    except Exception as e:
        print(f"    ✗ Error counting nodes: {e}")
        return analysis
    
    # Get properties
    try:
        query = f"""
        MATCH (n:{label})
        WITH n LIMIT 1000
        UNWIND keys(n) as key
        RETURN DISTINCT key
        ORDER BY key
        """
        result = connector.execute_query(query)
        properties = [r['key'] for r in result]
        analysis['properties'] = properties
        print(f"    ✓ Found {len(properties)} properties:")
        for prop in properties:
            print(f"        - {prop}")
    except Exception as e:
        print(f"    ✗ Error getting properties: {e}")
        return analysis
    
    # Analyze property distributions
    print(f"\n[4] Analyzing Property Distributions...")
    property_stats = {}
    
    for prop in properties[:10]:  # Limit to first 10 properties
        try:
            query = f"""
            MATCH (n:{label})
            WHERE n.{prop} IS NOT NULL
            WITH n.{prop} AS value
            RETURN 
                count(DISTINCT value) AS unique_values,
                count(value) AS total_values
            """
            result = connector.execute_query(query)
            if result:
                stats = result[0]
                property_stats[prop] = stats
                
                # Determine if categorical or unique
                ratio = stats['unique_values'] / stats['total_values'] if stats['total_values'] > 0 else 0
                prop_type = "UNIQUE" if ratio > 0.9 else "CATEGORICAL"
                
                print(f"    {prop}:")
                print(f"        Type: {prop_type}")
                print(f"        Unique values: {stats['unique_values']:,}")
                print(f"        Total values: {stats['total_values']:,}")
                print(f"        Uniqueness: {ratio:.2%}")
        except Exception as e:
            print(f"    ⚠ Could not analyze {prop}: {e}")
    
    analysis['property_stats'] = property_stats
    
    return analysis


def suggest_configuration(analysis: dict, label: str = "User") -> None:
    """Suggest configuration based on analysis."""
    print("\n[5] Configuration Suggestions...")
    
    if not analysis.get('properties'):
        print("    ⚠ No properties found to suggest")
        return
    
    # Find categorical properties (good for projection)
    categorical_props = []
    if 'property_stats' in analysis:
        for prop, stats in analysis['property_stats'].items():
            ratio = stats['unique_values'] / stats['total_values'] if stats['total_values'] > 0 else 0
            if ratio < 0.9 and stats['unique_values'] > 1:  # Categorical with multiple values
                categorical_props.append(prop)
    
    if categorical_props:
        print("    ✓ Recommended properties for projection (categorical):")
        for prop in categorical_props[:5]:  # Top 5
            print(f"        - {prop}")
        
        print("\n    Suggested configuration:")
        print("    " + "=" * 60)
        print(f"""
    projection_config = PropertyProjectionConfig(
        source_label="{label}",
        source_id_property="id",  # ← Adjust if needed
        properties_to_project={categorical_props[:5]},
        graph_name="{label.lower()}-property-graph"
    )
        """)
        print("    " + "=" * 60)
    else:
        print("    ⚠ No suitable categorical properties found")
        print("    → Properties should have multiple values but not be unique identifiers")


def main():
    """Main validation workflow."""
    print("=" * 80)
    print("GDS PROPERTY PROJECTION - SETUP VALIDATION")
    print("=" * 80)
    
    # Configuration
    print("\nEnter your Neo4j connection details:")
    print("(Press Enter to use defaults shown in brackets)")
    
    uri = input("URI [bolt://localhost:7687]: ").strip() or "bolt://44.204.34.69"
    user = input("User [neo4j]: ").strip() or "neo4j"
    password = input("Password: ").strip() or "decibels-defenses-president"
    
    if not password:
        print("\n⚠ No password provided. Using 'password' as default.")
        password = "password"
    
    label = input("Node label to analyze [User]: ").strip() or "User"
    
    config = Neo4jConfig(uri=uri, user=user, password=password)
    
    # Validate
    if not validate_connection(config):
        print("\n✗ Validation failed: Cannot connect to Neo4j")
        return
    
    with Neo4jConnector(config) as conn:
        if not check_gds(conn):
            print("\n⚠ Warning: GDS not available. Install it to use projections.")
        
        analysis = analyze_user_nodes(conn, label)
        
        if analysis.get('count', 0) > 0:
            suggest_configuration(analysis, label)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Copy the suggested configuration above")
    print("  2. Edit example_usage.py or example_materialized.py")
    print("  3. Run the example script")
    print("  4. Analyze the results")


if __name__ == "__main__":
    main()

