from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from src.config import settings
from src.graph.schema import TemporalNode, Relationship

class GraphConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j.uri,
            auth=(settings.neo4j.user, settings.neo4j.password)
        )

    def close(self):
        self.driver.close()

    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def add_node(self, node: TemporalNode):
        """Adds a node to the graph, merging on ID."""
        query = (
            f"MERGE (n:{node.label} {{id: $id}}) "
            f"SET n += $properties"
        )
        self.run_query(query, {"id": node.id, "properties": node.model_dump(exclude={"label"})})

    def add_relationship(self, source_id: str, target_id: str, relation_type: str, properties: Dict = None):
        """Adds a relationship between two existing nodes."""
        query = (
            f"MATCH (source {{id: $source_id}}), (target {{id: $target_id}}) "
            f"MERGE (source)-[r:{relation_type}]->(target) "
            f"SET r += $properties"
        )
        self.run_query(query, {
            "source_id": source_id, 
            "target_id": target_id, 
            "properties": properties or {}
        })

    def clear_database(self):
        """Dangerous! Clears the entire graph."""
        if settings.environment != "production":
            self.run_query("MATCH (n) DETACH DELETE n")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        query = "MATCH (n {id: $id}) RETURN n"
        results = self.run_query(query, {"id": node_id})
        return results[0]['n'] if results else None
