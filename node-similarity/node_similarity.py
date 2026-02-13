from neo4j import GraphDatabase

URI = "bolt://44.204.34.69"
AUTH = ("neo4j", "decibels-defenses-president")

# Use the existing in-memory projection
GRAPH_NAME = "graph-with-component_ids"

# Filter to Stream nodes only
NODE_LABELS = ["Stream"]

# Output file
OUTPUT_PATH = "node_similarity.txt"


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver:
        with driver.session() as session:
            result = session.run(
                "CALL gds.nodeSimilarity.stream($name, { "
                "  nodeLabels: $labels "
                "}) "
                "YIELD node1, node2, similarity "
                "WHERE similarity > 0 "
                "RETURN gds.util.asNode(node1).id AS node1_id, "
                "       gds.util.asNode(node1).component_id_2 AS node1_component_id_2, "
                "       gds.util.asNode(node2).id AS node2_id, "
                "       gds.util.asNode(node2).component_id_2 AS node2_component_id_2, "
                "       similarity "
                "ORDER BY similarity DESC",
                name=GRAPH_NAME,
                labels=NODE_LABELS,
            )

            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                for record in result:
                    f.write(
                        f"{record['node1_id']}\t{record['node1_component_id_2']}\t"
                        f"{record['node2_id']}\t{record['node2_component_id_2']}\t"
                        f"{record['similarity']}\n"
                    )


if __name__ == "__main__":
    main()
