from neo4j import GraphDatabase

URI = "bolt://44.204.34.69"
AUTH = ("neo4j", "decibels-defenses-president")

# Projected graph name in GDS
GRAPH_NAME = "node-embedding-graph"

USER_LABEL = "Stream"
PROPERTY_LABEL = "Property"
REL_TYPE = "HAS"


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver:
        with driver.session() as session:
            # # Drop if exists to allow re-runs
            # session.run(
            #     "CALL gds.graph.exists($name) YIELD exists "
            #     "WITH exists WHERE exists "
            #     "CALL gds.graph.drop($name) YIELD graphName "
            #     "RETURN graphName",
            #     name=GRAPH_NAME,
            # )
            #
            # # Project User-Property graph
            # session.run(
            #     "CALL gds.graph.project(\n"
            #     "  $name,\n"
            #     "  [$user_label, $property_label],\n"
            #     "  {\n"
            #     "    HAS: {\n"
            #     "      type: $rel_type,\n"
            #     "      orientation: 'UNDIRECTED'\n"
            #     "    }\n"
            #     "  }\n"
            #     ")",
            #     name=GRAPH_NAME,
            #     user_label=USER_LABEL,
            #     property_label=PROPERTY_LABEL,
            #     rel_type=REL_TYPE,
            # )

            # memory_estimate = session.run("CALL gds.wcc.write.estimate($name, { writeProperty: 'component' }) "
            #                   "YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory",
            #                   name=GRAPH_NAME)
            # print(f"Memory estimate: nodeCount	relationshipCount	bytesMin	bytesMax	requiredMemory")
            # memory_estimate=memory_estimate.single()
            # print("        "+memory_estimate["nodeCount"]+"	"+memory_estimate["relationshipCount"]+"	"+memory_estimate["bytesMin"]+"	"+memory_estimate["bytesMax"]+"	"+memory_estimate["requiredMemory"]+"	")
            # Stream WCC, attach component_id to Stream nodes in components size > 1,
            # and show counts per componentId
            result = session.run(
                "CALL gds.wcc.stream($name) "
                "YIELD nodeId, componentId "
                "WITH gds.util.asNode(nodeId) AS n, componentId "
                "WHERE n:Stream "
                "WITH componentId, collect(n) AS nodes, count(*) AS size "
                "WHERE size > 1 "
                "UNWIND nodes AS n "
                "SET n.component_id_2 = componentId "
                "RETURN componentId, size "
                "ORDER BY size DESC, componentId ASC",
                name=GRAPH_NAME,
            )
            for record in result:
                print(record["componentId"], record["size"])


if __name__ == "__main__":
    main()
