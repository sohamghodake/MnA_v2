from typing import Dict, Any, List
from src.models.assumptions import AssumptionRegistry
from src.models.financials import CostSynergyModel, RevenueSynergyModel
from src.models.risk import RiskScorer
from src.graph.schema import Risk

class ModelRunner:
    def __init__(self):
        self.registry = AssumptionRegistry()
        self.cost_model = CostSynergyModel(self.registry)
        self.revenue_model = RevenueSynergyModel(self.registry)
        self.risk_model = RiskScorer(self.registry)

    def run_synergy_analysis(self, target_hc: int, acquirer_hc: int, target_rev: float, assumption_ids: Dict[str, str]) -> Dict[str, float]:
        """Runs synergy models given inputs and assumption IDs."""
        cost_savings = self.cost_model.calculate_headcount_savings(
            target_hc, acquirer_hc, assumption_ids['redundancy_rate']
        )
        revenue_uplift = self.revenue_model.calculate_cross_sell(
            target_rev, assumption_ids['cross_sell_rate']
        )
        return {
            "cost_synergies": cost_savings,
            "revenue_synergies": revenue_uplift,
            "total_synergies": cost_savings + revenue_uplift
        }

    def run_risk_analysis(self, risks: List[Risk]) -> Dict[str, Any]:
        """Runs risk scoring."""
        score = self.risk_model.calculate_deal_risk_score(risks)
        critical = self.risk_model.identify_critical_risks(risks)
        return {
            "total_risk_score": score,
            "critical_risk_count": len(critical),
            "critical_risks": [r.id for r in critical]
        }
