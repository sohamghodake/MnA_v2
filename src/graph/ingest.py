from typing import List, Dict, Any
from src.graph.connector import GraphConnector
from src.graph.schema import TemporalNode
from src.graph.ontology import Ontology

class IngestionPipeline:
    def __init__(self, connector: GraphConnector):
        self.connector = connector

    def ingest_nodes(self, nodes: List[TemporalNode]):
        """Ingests a list of nodes after internal validation."""
        for node in nodes:
            # Pydantic validation happens at instantiation, 
            # but we can add extra checks here if needed.
            self.connector.add_node(node)

    def ingest_relationships(self, relationships: List[Dict[str, Any]]):
        """
        Ingests relationships.
        Expected format: {'source_type': 'Company', 'target_type': 'Risk', 
                          'source_id': '...', 'target_id': '...', 'type': 'HAS_RISK'}
        """
        for rel in relationships:
            # Validate against Ontology
            Ontology.validate_relationship(
                rel['source_type'], 
                rel['target_type'], 
                rel['type']
            )
            
            self.connector.add_relationship(
                rel['source_id'],
                rel['target_id'],
                rel['type'],
                rel.get('properties', {})
            )
