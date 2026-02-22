from typing import Dict, List, Set
from .schema import Company, Person, Contract, Risk, FinancialMetric, Assumption

class Ontology:
    """Enforces strict rules on graph structure."""
    
    ALLOWED_RELATIONSHIPS = {
        ("Company", "Risk"): ["HAS_RISK"],
        ("Risk", "Contract"): ["DERIVED_FROM"],
        ("Company", "Contract"): ["EXECUTED"],
        ("Company", "FinancialMetric"): ["REPORTED"],
        ("Company", "Company"): ["ACQUIRED", "PARTNER_WITH", "COMPETES_WITH", "SUPPLIES"],
        ("Person", "Company"): ["WORKS_FOR", "MANAGES"],
        ("Assumption", "Risk"): ["TRIGGERED_BY"],
        ("Assumption", "FinancialMetric"): ["INFLUENCES"],
        ("Contract", "Company"): ["INVOLVES"],
    }

    REQUIRED_PROPERTIES = {
        "Risk": ["severity", "probability"],
        "Contract": ["value", "expiration_date"],
        "FinancialMetric": ["value", "period"],
    }

    @classmethod
    def validate_relationship(cls, source_type: str, target_type: str, relation_type: str) -> bool:
        allowed = cls.ALLOWED_RELATIONSHIPS.get((source_type, target_type), [])
        if relation_type not in allowed:
            raise ValueError(f"Relationship '{relation_type}' not allowed between {source_type} and {target_type}")
        return True

    @classmethod
    def validate_node(cls, node_type: str, properties: Dict) -> bool:
        required = cls.REQUIRED_PROPERTIES.get(node_type, [])
        missing = [p for p in required if p not in properties or properties[p] is None]
        if missing:
            raise ValueError(f"Node type '{node_type}' missing required properties: {missing}")
        return True
