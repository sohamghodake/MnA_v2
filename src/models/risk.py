from typing import List, Dict
from src.graph.schema import Risk
from src.models.assumptions import AssumptionRegistry

class RiskScorer:
    def __init__(self, registry: AssumptionRegistry):
        self.registry = registry
        self.name = "RiskScorer"
        self.severity_weights = {
            "critical": 10.0,
            "high": 7.0,
            "medium": 4.0,
            "low": 1.0
        }

    def calculate_deal_risk_score(self, risks: List[Risk]) -> float:
        """Calculates a weighted risk score for a list of Risk nodes."""
        total_score = 0.0
        for risk in risks:
            weight = self.severity_weights.get(risk.severity, 0.0)
            # Probability-weighted impact
            impact = weight * risk.probability
            total_score += impact
        return total_score

    def identify_critical_risks(self, risks: List[Risk], threshold: float = 8.0) -> List[Risk]:
        """Returns risks exceeding a severity*prob threshold."""
        critical = []
        for risk in risks:
            weight = self.severity_weights.get(risk.severity, 0.0)
            if (weight * risk.probability) >= threshold:
                critical.append(risk)
        return critical
