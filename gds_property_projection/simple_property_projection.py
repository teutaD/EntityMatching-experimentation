"""
Simple script to create Property nodes from User properties.
No over-engineering - just gets the job done.
"""

from neo4j import GraphDatabase

# ========================================
# CONFIGURATION - Edit these values
# ========================================

NEO4J_URI = "bolt://44.204.34.69"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "decibels-defenses-president"

# Projecting all properties of User
# NODE_TYPE="User"
# PROPERTIES_TO_PROJECT = ["name", "id", "createdAt", "description", "url", "followers", "total_view_count"]
# Project properties of Team chosen by EDA to be semi-unique to get rid of those with high centrality
NODE_TYPE="Team"
PROPERTIES_TO_PROJECT = ["name"]
# Limit to 5k users
USER_LIMIT = 5000


# ========================================
# MAIN SCRIPT
# ========================================

def create_property_nodes():
    """Create Property nodes from User properties."""
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print("=" * 60)
    print("Creating Property Nodes from User Properties")
    print("=" * 60)
    
    with driver.session() as session:
        
        # Check how many Users we have
        result = session.run(f"MATCH (n:{NODE_TYPE}) RETURN count(n) as count")
        total_users = result.single()["count"]
        print(f"\nTotal User nodes: {total_users:,}")
        print(f"Processing in batches of : {USER_LIMIT:,}")
        
        # For each property, create Property nodes
        for prop_name in PROPERTIES_TO_PROJECT:
            print(f"\n[{prop_name}]")
            
            query = f"""
            MATCH (u:{NODE_TYPE})
            WHERE u.{prop_name} IS NOT NULL
            WITH u LIMIT {USER_LIMIT}
            
            // Create Property node for each unique value
            WITH u, u.{prop_name} AS propValue
            MERGE (p:Property {{name: '{prop_name}', value: toString(propValue)}})
            
            // Create HAS relationship
            MERGE (u)-[:HAS]->(p)
            
            RETURN count(DISTINCT p) AS props_created, count(*) AS rels_created
            """
            
            result = session.run(query)
            stats = result.single()
            
            print(f"  ✓ Created {stats['props_created']} Property nodes")
            print(f"  ✓ Created {stats['rels_created']} HAS relationships")
        
        # Show what we created
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        result = session.run("MATCH (p:Property) RETURN count(p) as count")
        total_props = result.single()["count"]
        print(f"Total Property nodes: {total_props:,}")
        
        result = session.run("MATCH ()-[r:HAS]->() RETURN count(r) as count")
        total_rels = result.single()["count"]
        print(f"Total HAS relationships: {total_rels:,}")
        
        # Show sample
        print("\nSample Property nodes:")
        result = session.run("""
            MATCH (p:Property)
            RETURN p.name AS name, p.value AS value, count{(u)-[:HAS]->(p)} AS user_count
            ORDER BY user_count DESC
            LIMIT 10
        """)
        
        for i, record in enumerate(result, 1):
            print(f"  {i}. {record['name']}={record['value']}: {record['user_count']} users")
    
    driver.close()
    print("\n✓ Done!")


def create_gds_projection(projection_name):
    """Create a simple GDS projection."""
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print("\n" + "=" * 60)
    print("Creating GDS Projection")
    print("=" * 60)
    
    with driver.session() as session:
        
        # # Drop existing projection if it exists
        # try:
        #     session.run("CALL gds.graph.drop('user-props')")
        #     print("Dropped existing projection")
        # except:
        #     pass
        
        # Create projection
        query = f"""
        CALL gds.graph.project(
            '{projection_name}',
            ['{NODE_TYPE}', 'Property'],
            {{HAS: {{orientation: 'NATURAL'}}}}
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        
        result = session.run(query)
        stats = result.single()
        
        print(f"\n✓ Created projection: {stats['graphName']}")
        print(f"  - Nodes: {stats['nodeCount']:,}")
        print(f"  - Relationships: {stats['relationshipCount']:,}")
    
    driver.close()


def run_node_similarity():
    """Find similar users based on shared properties."""
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print("\n" + "=" * 60)
    print("Finding Similar Users")
    print("=" * 60)
    
    with driver.session() as session:
        
        query = """
        CALL gds.nodeSimilarity.stream('user-props', {topK: 5})
        YIELD node1, node2, similarity
        WITH gds.util.asNode(node1) AS user1, gds.util.asNode(node2) AS user2, similarity
        WHERE 'User' IN labels(user1)
        RETURN user1.id AS user1_id, user2.id AS user2_id, similarity
        ORDER BY similarity DESC
        LIMIT 20
        """
        
        result = session.run(query)
        
        print("\nTop 20 similar user pairs:")
        for i, record in enumerate(result, 1):
            print(f"  {i}. User {record['user1_id']} ↔ User {record['user2_id']}: {record['similarity']:.3f}")
    
    driver.close()


def run_node_centrality(projection_name):
    """Find the top nodes by degree centrality."""

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    print("\n" + "=" * 60)
    print(f"Finding Top {NODE_TYPE} by Degree Centrality")
    print("=" * 60)

    with driver.session() as session:
        query = f"""
        CALL gds.degree.stream('{projection_name}')
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS n, score
        RETURN labels(n) AS type, n.name AS name, score
        ORDER BY score ASC
        """

        result = session.run(query)

        print("\nTop 20 users by degree centrality:")
        for i, record in enumerate(result, 1):
            print(f"  {i}. {record['type']} {record['name']}: {record['score']:.3f}")

    driver.close()


# def cleanup():
#     """Delete all Property nodes and HAS relationships."""
#
#     driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
#
#     print("\n" + "=" * 60)
#     print("Cleanup")
#     print("=" * 60)
#
#     with driver.session() as session:
#         # Drop GDS projection
#         try:
#             session.run("CALL gds.graph.drop('user-props')")
#             print("✓ Dropped GDS projection")
#         except:
#             pass
#
#         # Delete Property nodes
#         result = session.run("MATCH (p:Property) DETACH DELETE p RETURN count(p) as deleted")
#         deleted = result.single()["deleted"]
#         print(f"✓ Deleted {deleted} Property nodes")
#
#     driver.close()


if __name__ == "__main__":
    # Run the workflow
    # create_property_nodes()
    # create_gds_projection(projection_name="team-props")
    run_node_centrality(projection_name="team-props")
    
    # Uncomment to cleanup when done:
    # cleanup()

