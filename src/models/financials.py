from typing import Dict, List
import pandas as pd
import numpy as np
from src.models.assumptions import AssumptionRegistry

class FinancialModel:
    def __init__(self, registry: AssumptionRegistry):
        self.registry = registry
        self.name = "GenericModel"

class CostSynergyModel(FinancialModel):
    def __init__(self, registry: AssumptionRegistry):
        super().__init__(registry)
        self.name = "CostSynergyModel"

    def calculate_headcount_savings(self, target_hc: int, acquirer_hc: int, assumption_id: str) -> float:
        """Calculates savings based on redundancy assumption."""
        redundancy_rate = float(self.registry.get(assumption_id, self.name) or 0.0)
        # Simple deterministic calculation
        reduction = (target_hc + acquirer_hc) * redundancy_rate
        avg_cost = 150000 # placeholder or another assumption
        return reduction * avg_cost

class RevenueSynergyModel(FinancialModel):
    def __init__(self, registry: AssumptionRegistry):
        super().__init__(registry)
        self.name = "RevenueSynergyModel"

    def calculate_cross_sell(self, target_revenue: float, overlap_assumption_id: str) -> float:
        """Calculates revenue uplift from cross-selling."""
        uplift_pct = float(self.registry.get(overlap_assumption_id, self.name) or 0.0)
        return target_revenue * uplift_pct
