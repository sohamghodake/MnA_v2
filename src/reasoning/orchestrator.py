from typing import Dict, Any, List
from src.reasoning.llm import OllamaClient
from src.reasoning.strategy import StrategyInput
from src.reasoning.graph_query import GraphQueryGenerator
from src.reasoning.validation import OutputValidator
from src.reasoning.prompts import SYSTEM_PROMPT_TEMPLATE
from src.graph.connector import GraphConnector
from src.models.runner import ModelRunner
from src.graph.schema import Risk

class ReasoningOrchestrator:
    def __init__(self):
        self.llm = OllamaClient()
        self.graph_query = GraphQueryGenerator(self.llm)
        self.validator = OutputValidator()
        self.graph_db = GraphConnector()
        self.models = ModelRunner()

    def generate_report(self, strategy: StrategyInput, user_query: str) -> str:
        # 1. Generate Cypher
        cypher = self.graph_query.generate_cypher(user_query, strategy)
        
        # 2. Retrieve from Graph
        graph_data = self.graph_db.run_query(cypher)
        
        # 3. Detect Risks & Run Models (Simplified logic)
        # In a real app, we'd parse the graph data to find Risk nodes
        # For now, let's assume we fetch all risks associated with the deal
        # This is a placeholder for more complex graph parsing logic
        
        # Mocking model run based on graph data availability
        # We need logic to map graph data to model inputs
        model_results = {}
        
        # 4. Synthesize Prompt
        context_str = str(graph_data)
        model_str = str(model_results)
        strategy_str = f"Objective: {strategy.objective}"
        
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context_data=context_str,
            model_outputs=model_str,
            strategy_context=strategy_str
        )
        
        # 5. Generate with LLM
        report_draft = self.llm.generate(user_query, system=prompt)
        
        # 6. Validate
        # Collect all valid numbers and refs from context
        valid_refs = set()
        valid_numbers = set()
        
        # Helper to recursively extract numbers and IDs
        def extract_from_json(data):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == 'id' and isinstance(v, str):
                        valid_refs.add(v)
                    extract_from_json(v)
            elif isinstance(data, list):
                for item in data:
                    extract_from_json(item)
            elif isinstance(data, (int, float)):
                valid_numbers.add(float(data))
                
        extract_from_json(graph_data)
        
        # Also include any numbers from strategy input (like horizon months)
        valid_numbers.add(float(strategy.time_horizon_months))
        
        if self.validator.validate(report_draft, valid_numbers, valid_refs):
            return report_draft
        else:
            return "Report generation failed validation. Please refine parameters or data."

    def close(self):
        self.graph_db.close()
