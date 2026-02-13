"""
Example usage of GDS Property Projection Manager.

This script demonstrates how to:
1. Connect to Neo4j
2. Create a graph projection with properties as nodes
3. Run graph analytics algorithms
4. Analyze results
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common import Neo4jConnector, Neo4jConfig
from gds_property_projection import GDSPropertyProjectionManager, PropertyProjectionConfig


def main():
    """Main example workflow."""
    
    # ========================================
    # 1. CONFIGURATION
    # ========================================
    
    # Neo4j connection configuration
    neo4j_config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password",
        database="neo4j"
    )
    
    # Property projection configuration
    projection_config = PropertyProjectionConfig(
        source_label="User",
        source_id_property="id",
        properties_to_project=["country", "age_group", "subscription_type", "interests"],
        property_node_label="Property",
        relationship_type="HAS",
        graph_name="user-property-graph",
        # Optional: Add filter for source nodes
        # source_filter="WHERE n.active = true AND n.created_date > date('2024-01-01')"
    )
    
    # ========================================
    # 2. CONNECT TO NEO4J
    # ========================================
    
    print("=" * 80)
    print("GDS PROPERTY PROJECTION - EXAMPLE USAGE")
    print("=" * 80)
    
    with Neo4jConnector(neo4j_config) as connector:
        
        # Initialize projection manager
        manager = GDSPropertyProjectionManager(connector, projection_config)
        
        # ========================================
        # 3. CHECK GDS AVAILABILITY
        # ========================================
        
        print("\n[1] Checking GDS availability...")
        if not manager.check_gds_available():
            print("ERROR: GDS library is not available. Please install Neo4j GDS plugin.")
            return
        
        # ========================================
        # 4. ANALYZE SOURCE DATA
        # ========================================
        
        print("\n[2] Analyzing source data...")
        source_count = manager.get_source_node_count()
        print(f"✓ Found {source_count:,} {projection_config.source_label} nodes")
        
        if source_count == 0:
            print("ERROR: No source nodes found. Please check your configuration.")
            return
        
        # ========================================
        # 5. CREATE GRAPH PROJECTION
        # ========================================
        
        print("\n[3] Creating graph projection...")
        projection_stats = manager.create_cypher_projection()
        
        if not projection_stats:
            print("ERROR: Failed to create projection")
            return
        
        # ========================================
        # 6. GET PROJECTION STATISTICS
        # ========================================
        
        print("\n[4] Getting projection statistics...")
        stats = manager.get_projection_stats()
        
        if stats.get('exists'):
            print(f"✓ Projection Statistics:")
            print(f"  - Total nodes: {stats['node_count']:,}")
            print(f"  - Total relationships: {stats['relationship_count']:,}")
            print(f"  - Memory usage: {stats['memory_usage']}")
            
            if 'degree_stats' in stats:
                deg = stats['degree_stats']
                print(f"  - Degree statistics:")
                print(f"    • Min: {deg['min_degree']}")
                print(f"    • Max: {deg['max_degree']}")
                print(f"    • Avg: {deg['avg_degree']:.2f}")
                print(f"    • Median: {deg['median_degree']}")
        
        # ========================================
        # 7. RUN GRAPH ANALYTICS
        # ========================================
        
        print("\n[5] Running graph analytics algorithms...")
        
        # Node Similarity - Find similar users based on shared properties
        print("\n  a) Node Similarity (finding similar users)...")
        similarity_results = manager.run_node_similarity(top_k=5, similarity_cutoff=0.3)
        
        if similarity_results:
            print(f"     Found {len(similarity_results)} similar node pairs")
            print("     Top 5 most similar pairs:")
            for i, result in enumerate(similarity_results[:5], 1):
                print(f"       {i}. User {result['node1_id']} ↔ User {result['node2_id']}: "
                      f"{result['similarity']:.3f}")
        
        # PageRank - Find influential users
        print("\n  b) PageRank (finding influential users)...")
        pagerank_results = manager.run_pagerank()
        
        if pagerank_results:
            print(f"     Top 10 users by PageRank:")
            for i, result in enumerate(pagerank_results[:10], 1):
                print(f"       {i}. User {result['node_id']}: {result['score']:.6f}")
        
        # Community Detection - Find user communities
        print("\n  c) Community Detection (Louvain)...")
        community_results = manager.run_community_detection(algorithm="louvain")
        
        if community_results:
            # Count communities
            communities = {}
            for result in community_results:
                comm_id = result['communityId']
                communities[comm_id] = communities.get(comm_id, 0) + 1
            
            print(f"     Found {len(communities)} communities")
            print(f"     Top 5 largest communities:")
            sorted_communities = sorted(communities.items(), key=lambda x: x[1], reverse=True)
            for i, (comm_id, size) in enumerate(sorted_communities[:5], 1):
                print(f"       {i}. Community {comm_id}: {size} users")
        
        # ========================================
        # 8. CLEANUP (OPTIONAL)
        # ========================================
        
        print("\n[6] Cleanup...")
        print("  Note: Projection is kept in memory for further analysis.")
        print("  To drop the projection, uncomment the line below:")
        print("  # manager.drop_projection()")
        
        # Uncomment to drop the projection
        # manager.drop_projection()
    
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()

