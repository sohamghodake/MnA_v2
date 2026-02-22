from pydantic import BaseModel, Field
from typing import Literal, Optional

class StrategyInput(BaseModel):
    objective: str = Field(..., description="Primary strategic goal, e.g., 'Vertical Integration'")
    time_horizon_months: int = Field(..., ge=1, le=120)
    risk_tolerance: Literal["low", "medium", "high"]
    capital_constraint: Optional[str] = "moderate"

class StrategyParser:
    @staticmethod
    def parse(json_input: dict) -> StrategyInput:
        return StrategyInput(**json_input)

    @staticmethod
    def to_prompt_context(strategy: StrategyInput) -> str:
        return (
            f"STRATEGIC CONTEXT:\n"
            f"- Objective: {strategy.objective}\n"
            f"- Time Horizon: {strategy.time_horizon_months} months\n"
            f"- Risk Tolerance: {strategy.risk_tolerance}\n"
            f"- Capital Constraint: {strategy.capital_constraint}\n"
        )
