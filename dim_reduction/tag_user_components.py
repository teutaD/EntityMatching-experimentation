"""
Tag User nodes with component_id based on shared properties.

Uses Neo4j GDS Weakly Connected Components (WCC) to find groups of User nodes
that share properties, then tags them with a component_id.
"""

import time
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load credentials
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Configuration
GRAPH_NAME = "user_property_wcc"
USER_LABEL = "User"
PROPERTY_LABEL = "Property"
REL_TYPE = "HAS"


def main() -> None:
    print("="*70)
    print("USER COMPONENT TAGGING (WCC)")
    print("="*70)
    print(f"\nConnecting to {URI}...")
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    try:
        with driver.session(database=DATABASE) as session:
            # Step 1: Drop existing projection if it exists
            print("\n📊 Step 1: Checking for existing graph projection...")
            result = session.run(
                "CALL gds.graph.exists($name) YIELD exists "
                "RETURN exists",
                name=GRAPH_NAME,
            )
            exists = result.single()["exists"]
            
            if exists:
                print(f"   Dropping existing projection '{GRAPH_NAME}'...")
                session.run(
                    "CALL gds.graph.drop($name) YIELD graphName "
                    "RETURN graphName",
                    name=GRAPH_NAME,
                )
                print("   ✓ Dropped")
            else:
                print(f"   ✓ No existing projection found")

            # Step 2: Project User-Property graph
            print(f"\n📊 Step 2: Creating graph projection '{GRAPH_NAME}'...")
            print(f"   Node labels: {USER_LABEL}, {PROPERTY_LABEL}")
            print(f"   Relationship: {REL_TYPE} (UNDIRECTED)")
            
            start_time = time.time()
            result = session.run(
                "CALL gds.graph.project(\n"
                "  $name,\n"
                "  [$user_label, $property_label],\n"
                "  {\n"
                "    HAS: {\n"
                "      type: $rel_type,\n"
                "      orientation: 'UNDIRECTED'\n"
                "    }\n"
                "  }\n"
                ") YIELD nodeCount, relationshipCount",
                name=GRAPH_NAME,
                user_label=USER_LABEL,
                property_label=PROPERTY_LABEL,
                rel_type=REL_TYPE,
            )
            record = result.single()
            elapsed = time.time() - start_time
            print(f"   ✓ Projection created in {elapsed:.2f}s")
            print(f"   Nodes: {record['nodeCount']:,}")
            print(f"   Relationships: {record['relationshipCount']:,}")

            # Step 3: Run WCC and tag User nodes
            print(f"\n📊 Step 3: Running WCC and tagging User nodes...")
            print(f"   Finding connected components...")
            
            start_time = time.time()
            result = session.run(
                "CALL gds.wcc.stream($name) "
                "YIELD nodeId, componentId "
                "WITH gds.util.asNode(nodeId) AS n, componentId "
                "WHERE n:User "
                "WITH componentId, collect(n) AS nodes, count(*) AS size "
                "WHERE size > 1 "
                "UNWIND nodes AS n "
                "SET n.component_id = componentId "
                "RETURN componentId, size "
                "ORDER BY size DESC, componentId ASC",
                name=GRAPH_NAME,
            )
            
            components = []
            total_users_tagged = 0
            for record in result:
                comp_id = record["componentId"]
                size = record["size"]
                components.append((comp_id, size))
                total_users_tagged += size
            
            elapsed = time.time() - start_time
            print(f"   ✓ WCC complete in {elapsed:.2f}s")
            print(f"   Total components found: {len(components):,}")
            print(f"   Total users tagged: {total_users_tagged:,}")

            # Step 4: Show top components
            if components:
                print(f"\n{'='*70}")
                print("TOP 20 COMPONENTS BY SIZE")
                print(f"{'='*70}")
                print(f"{'Component ID':<20} {'Size':>10}")
                print(f"{'-'*70}")
                for comp_id, size in components[:20]:
                    print(f"{comp_id:<20} {size:>10,}")
            
            # Step 5: Cleanup - drop the projection
            print(f"\n📊 Step 4: Cleaning up...")
            session.run(
                "CALL gds.graph.drop($name) YIELD graphName "
                "RETURN graphName",
                name=GRAPH_NAME,
            )
            print(f"   ✓ Dropped projection '{GRAPH_NAME}'")
            
            print(f"\n{'='*70}")
            print("✓ COMPONENT TAGGING COMPLETE")
            print(f"{'='*70}")
            
    finally:
        driver.close()
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    main()

