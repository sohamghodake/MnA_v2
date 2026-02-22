from typing import Dict, Any, Optional
from src.reasoning.llm import OllamaClient
from src.reasoning.strategy import StrategyInput
from src.reasoning.graph_query import GraphQueryGenerator
from src.reasoning.validation import OutputValidator
from src.reasoning.prompts import REPORT_PROMPTS
from src.graph.connector import GraphConnector
from src.models.runner import ModelRunner


class ReasoningOrchestrator:
    def __init__(self):
        self.llm = OllamaClient()
        self.graph_query = GraphQueryGenerator(self.llm)
        self.validator = OutputValidator()
        self.graph_db = GraphConnector()
        self.models = ModelRunner()

    def generate_reports(
        self,
        strategy: StrategyInput,
        user_query: str,
        deal_type: str = "acquisition",
        company_a_name: str = "Company A",
        company_b_name: str = "Company B",
        company_a_role: str = "Acquirer",
        company_b_role: str = "Acquiree",
        company_a_text: str = "",
        company_b_text: str = "",
    ) -> Dict[str, str]:
        """
        Generates all four report types using LLM reasoning grounded on
        the provided company documents, graph data, and strategy context.
        Returns a dict mapping report_type_key -> report markdown string.
        """
        # 1. Try to generate a Cypher query and retrieve graph data
        try:
            cypher = self.graph_query.generate_cypher(user_query, strategy)
            graph_data = self.graph_db.run_query(cypher)
        except Exception:
            graph_data = []

        # 2. Run quantitative models (placeholder — no input mapping yet)
        model_results = {}

        # 3. Build shared context strings
        context_str = str(graph_data) if graph_data else "No graph data available."
        model_str = str(model_results) if model_results else "No model outputs available."
        strategy_str = (
            f"Objective: {strategy.objective}\n"
            f"Time Horizon: {strategy.time_horizon_months} months\n"
            f"Risk Tolerance: {strategy.risk_tolerance}"
        )

        deal_type_label = deal_type.capitalize()
        a_label = f"{company_a_name} ({company_a_role})"
        b_label = f"{company_b_name} ({company_b_role})"

        # 4. Generate each report type
        reports: Dict[str, str] = {}
        for report_key, prompt_template in REPORT_PROMPTS.items():
            system_prompt = prompt_template.format(
                company_a_text=f"Company: {a_label}\n\n{company_a_text or 'No document provided.'}",
                company_b_text=f"Company: {b_label}\n\n{company_b_text or 'No document provided.'}",
                deal_type=deal_type_label,
                strategy_context=strategy_str,
                context_data=context_str,
                model_outputs=model_str,
            )

            report_draft = self.llm.generate(
                prompt=f"Analyst instruction: {user_query}",
                system=system_prompt,
            )
            reports[report_key] = report_draft

        return reports

    def close(self):
        self.graph_db.close()
