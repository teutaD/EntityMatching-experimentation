"""
Example usage of Materialized Property Projection.

This approach creates actual Property nodes in the database,
which is more practical for persistent analysis and easier querying.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common import Neo4jConnector, Neo4jConfig
from gds_property_projection import PropertyProjectionConfig
from gds_property_projection.materialized_projection import MaterializedPropertyProjection
from gds_property_projection.projection_manager import GDSPropertyProjectionManager


def main():
    """Main example workflow for materialized projection."""
    
    print("=" * 80)
    print("MATERIALIZED PROPERTY PROJECTION - EXAMPLE")
    print("=" * 80)
    
    # ========================================
    # 1. CONFIGURATION
    # ========================================
    
    neo4j_config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password",
        database="neo4j"
    )
    
    projection_config = PropertyProjectionConfig(
        source_label="User",
        source_id_property="id",
        properties_to_project=["country", "age_group", "subscription_type"],
        property_node_label="Property",
        relationship_type="HAS",
        graph_name="user-property-materialized"
    )
    
    with Neo4jConnector(neo4j_config) as connector:
        
        # ========================================
        # 2. CREATE MATERIALIZED PROPERTY NODES
        # ========================================
        
        print("\n[1] Creating physical Property nodes in database...")
        mat_manager = MaterializedPropertyProjection(connector, projection_config)
        
        # This creates actual nodes in Neo4j
        creation_stats = mat_manager.create_property_nodes(batch_size=10000)
        
        print(f"\n✓ Created materialized graph:")
        print(f"  - Property nodes: {creation_stats['properties_created']:,}")
        print(f"  - HAS relationships: {creation_stats['relationships_created']:,}")
        
        # ========================================
        # 3. ANALYZE PROPERTY DISTRIBUTIONS
        # ========================================
        
        print("\n[2] Analyzing property distributions...")
        for prop_name in projection_config.properties_to_project:
            print(f"\n  Property: {prop_name}")
            distribution = mat_manager.get_property_distribution(prop_name)
            
            if distribution:
                print(f"    Top 5 values:")
                for i, item in enumerate(distribution[:5], 1):
                    print(f"      {i}. {item['value']}: {item['count']} users")
        
        # ========================================
        # 4. CREATE GDS PROJECTION
        # ========================================
        
        print("\n[3] Creating GDS projection over materialized graph...")
        projection_stats = mat_manager.create_gds_projection()
        
        # ========================================
        # 5. RUN ANALYTICS
        # ========================================
        
        print("\n[4] Running graph analytics...")
        
        # Use the standard GDS manager for analytics
        gds_manager = GDSPropertyProjectionManager(connector, projection_config)
        
        # Node Similarity
        print("\n  a) Finding similar users...")
        similarity_results = gds_manager.run_node_similarity(top_k=5, similarity_cutoff=0.3)
        
        if similarity_results:
            print(f"     Top 5 similar user pairs:")
            for i, result in enumerate(similarity_results[:5], 1):
                print(f"       {i}. User {result['node1_id']} ↔ User {result['node2_id']}: "
                      f"{result['similarity']:.3f}")
        
        # Community Detection
        print("\n  b) Detecting communities...")
        community_results = gds_manager.run_community_detection(algorithm="louvain")
        
        if community_results:
            communities = {}
            for result in community_results:
                comm_id = result['communityId']
                communities[comm_id] = communities.get(comm_id, 0) + 1
            
            print(f"     Found {len(communities)} communities")
            sorted_communities = sorted(communities.items(), key=lambda x: x[1], reverse=True)
            for i, (comm_id, size) in enumerate(sorted_communities[:5], 1):
                print(f"       {i}. Community {comm_id}: {size} users")
        
        # ========================================
        # 6. CUSTOM QUERIES ON MATERIALIZED GRAPH
        # ========================================
        
        print("\n[5] Running custom queries on materialized graph...")
        
        # Example: Find users who share the most properties
        query = f"""
        MATCH (u1:{projection_config.source_label})-[:{projection_config.relationship_type}]->(p:{projection_config.property_node_label})
              <-[:{projection_config.relationship_type}]-(u2:{projection_config.source_label})
        WHERE id(u1) < id(u2)
        WITH u1, u2, count(p) AS shared_properties
        ORDER BY shared_properties DESC
        LIMIT 10
        RETURN 
            u1.{projection_config.source_id_property} AS user1,
            u2.{projection_config.source_id_property} AS user2,
            shared_properties
        """
        
        shared_props = connector.execute_query(query)
        if shared_props:
            print("     Top 10 user pairs with most shared properties:")
            for i, result in enumerate(shared_props, 1):
                print(f"       {i}. User {result['user1']} & User {result['user2']}: "
                      f"{result['shared_properties']} shared properties")
        
        # ========================================
        # 7. CLEANUP OPTIONS
        # ========================================
        
        print("\n[6] Cleanup options...")
        print("  The Property nodes are now in your database.")
        print("  Options:")
        print("    1. Keep them for persistent analysis")
        print("    2. Drop GDS projection only: mat_manager.drop_projection()")
        print("    3. Delete Property nodes: mat_manager.delete_property_nodes()")
        
        # Uncomment to cleanup:
        # mat_manager.drop_projection()
        # mat_manager.delete_property_nodes()
    
    print("\n" + "=" * 80)
    print("MATERIALIZED PROJECTION EXAMPLE COMPLETED!")
    print("=" * 80)
    print("\nNext steps:")
    print("  - Query Property nodes directly in Neo4j Browser")
    print("  - Run additional GDS algorithms")
    print("  - Integrate with your application")


if __name__ == "__main__":
    main()

