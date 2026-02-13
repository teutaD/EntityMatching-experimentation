from neo4j import GraphDatabase

URI = "bolt://44.204.34.69"
AUTH = ("neo4j", "decibels-defenses-president")

LABEL = "Stream"
BATCH_SIZE = 1000
TARGET_KEYS = ["total_view_count", "followers", "description", "id", "createdAt"]

def fetch_batch(tx, label, skip, limit):
    query = f"""
    MATCH (n:`{label}`)
    RETURN elementId(n) AS eid, properties(n) AS props
    ORDER BY elementId(n)
    SKIP $skip LIMIT $limit
    """
    return list(tx.run(query, skip=skip, limit=limit))

def ingest_properties(tx, label, batch):
    query = f"""
    UNWIND $batch AS row
    MATCH (n:`{label}`) WHERE elementId(n) = row.eid
    WITH n, row.props AS props
    UNWIND $keys AS k
    WITH n, k, props[k] AS v
    WHERE v IS NOT NULL
    MERGE (p:Property {{key: k, value: v}})
    MERGE (n)-[:HAS]->(p)
    """
    tx.run(query, batch=batch, keys=TARGET_KEYS)

def main():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver:
        with driver.session() as session:
            skip = 0
            while True:
                records = session.execute_read(fetch_batch, LABEL, skip, BATCH_SIZE)
                if not records:
                    break

                batch = [{"eid": r["eid"], "props": r["props"]} for r in records]
                session.execute_write(ingest_properties, LABEL, batch)

                skip += BATCH_SIZE

if __name__ == "__main__":
    main()