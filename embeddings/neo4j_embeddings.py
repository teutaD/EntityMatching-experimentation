from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

URI = "bolt://44.204.34.69"
AUTH = ("neo4j", "decibels-defenses-president")

# Projected graph name in GDS
GRAPH_NAME = "graph-with-component_ids"
LABELS = ["Stream", "Game"]
REL_TYPES = ["MODERATOR", "VIP", "CHATTER"]


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver:
        with driver.session() as session:
            # Drop if exists to allow re-runs
            session.run(
                "CALL gds.graph.exists($name) YIELD exists "
                "WITH exists WHERE exists "
                "CALL gds.graph.drop($name) YIELD graphName "
                "RETURN graphName",
                name=GRAPH_NAME,
            )

            # Project filtered graph: only nodes with component_id_2
            session.run(
                """
                CALL gds.graph.project.cypher(
                  $name,
                  'MATCH (n)
                   WHERE n.component_id_2 IS NOT NULL
                     AND any(l IN labels(n) WHERE l IN $labels)
                   RETURN id(n) AS id, labels(n) AS labels',
                  'MATCH (n)-[r]-(m)
                   WHERE n.component_id_2 IS NOT NULL AND m.component_id_2 IS NOT NULL
                     AND any(l IN labels(n) WHERE l IN $labels)
                     AND any(l IN labels(m) WHERE l IN $labels)
                     AND type(r) IN $rel_types
                   RETURN id(n) AS source, id(m) AS target, type(r) AS type',
                  { parameters: { rel_types: $rel_types, labels: $labels } }
                )
                """,
                name=GRAPH_NAME,
                rel_types=REL_TYPES,
                labels=LABELS,
            )

            # Estimate memory before running FastRP + KNN
            try:
                est = session.run(
                    "CALL gds.fastRP.mutate.estimate($name, { "
                    "  nodeLabels: ['Stream'], "
                    "  mutateProperty: 'embedding', "
                    "  embeddingDimension: 128 "
                    "}) "
                    "YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory",
                    name=GRAPH_NAME,
                ).single()
                if est:
                    print(
                        "FastRP estimate:",
                        f"nodes={est['nodeCount']}",
                        f"rels={est['relationshipCount']}",
                        f"bytesMin={est['bytesMin']}",
                        f"bytesMax={est['bytesMax']}",
                        f"requiredMemory={est['requiredMemory']}",
                    )
            except Exception as e:
                print("FastRP estimate failed:", e)

            # Compute FastRP embeddings in-memory (no DB write)
            session.run(
                "CALL gds.fastRP.mutate($name, { "
                "  nodeLabels: ['Stream'], "
                "  mutateProperty: 'embedding', "
                "  embeddingDimension: 128 "
                "}) "
                "YIELD nodePropertiesWritten",
                name=GRAPH_NAME,
            )

            try:
                est = session.run(
                    "CALL gds.knn.stream.estimate($name, { "
                    "  topK: 10, "
                    "  nodeLabels: ['Stream'], "
                    "  nodeProperties: ['embedding'] "
                    "}) "
                    "YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory",
                    name=GRAPH_NAME,
                ).single()
                if est:
                    print(
                        "KNN estimate:",
                        f"nodes={est['nodeCount']}",
                        f"rels={est['relationshipCount']}",
                        f"bytesMin={est['bytesMin']}",
                        f"bytesMax={est['bytesMax']}",
                        f"requiredMemory={est['requiredMemory']}",
                    )
            except Exception as e:
                print("KNN estimate failed:", e)

            # KNN over Stream nodes using the FastRP embedding
            result = session.run(
                "CALL gds.knn.stream($name, { "
                "  topK: 10, "
                "  nodeLabels: ['Stream'], "
                "  nodeProperties: ['embedding'] "
                "}) "
                "YIELD node1, node2, similarity "
                "WHERE similarity > 0 "
                "RETURN gds.util.asNode(node1).id AS node1_id, "
                "       gds.util.asNode(node2).id AS node2_id, "
                "       similarity, "
                "       gds.util.asNode(node1).component_id_2 AS component_id_node_1, "
                "       gds.util.asNode(node2).component_id_2 AS component_id_node_2 "
                "ORDER BY similarity DESC ",
                name=GRAPH_NAME,
            )
            with open("knn_results.txt", "w", encoding="utf-8") as f:
                for record in result:
                    f.write(f"{record['node1_id']}\t{record['node2_id']}\t{record['similarity']}"
                            f"\t{record['component_id_node_1'],record['component_id_node_2']}\n")


if __name__ == "__main__":
    main()
