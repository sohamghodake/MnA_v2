from typing import List, Optional
from src.reasoning.llm import OllamaClient
from src.reasoning.strategy import StrategyInput

class GraphQueryGenerator:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
        self.schema_summary = (
            "Nodes: Company, Person, Contract, Risk, FinancialMetric, Assumption. "
            "Edges: ACQUIRED, HAS_RISK, HAS_REVENUE, EXECUTES, etc."
        )

    def generate_cypher(self, user_query: str, strategy: StrategyInput) -> str:
        """Translates user intent into a Temporal Cypher query."""
        system_prompt = (
            "You are a Cypher query generator for a Neo4j database. "
            f"Schema: {self.schema_summary}\n"
            "Rules:\n"
            "1. Use temporal filtering: Check valid_from/valid_to.\n"
            "2. Determine relevant time window from Strategy (months).\n"
            "3. RETURN strict JSON structures.\n"
            "4. NO DESTRUCTIVE OPERATIONS (MATCH only)."
        )
        
        user_prompt = (
            f"Strategy Objective: {strategy.objective}\n"
            f"Time Horizon: {strategy.time_horizon_months} months\n"
            f"User Query: {user_query}\n"
            "Generate Cypher query:"
        )
        
        # In a real app, we'd constrain this more or use a template
        cypher = self.llm.generate(user_prompt, system=system_prompt)
        # Naive extraction of code block
        if "```" in cypher:
            cypher = cypher.split("```")[1].replace("cypher", "").strip()
        return cypher
