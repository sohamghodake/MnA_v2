from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class TemporalNode(BaseModel):
    """Base class for all nodes with temporal validity and source tracking."""
    id: str
    name: str
    source_id: str = Field(..., description="Document ID where this fact was found")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of extraction")
    valid_from: Optional[date] = Field(None, description="Start date of validity")
    valid_to: Optional[date] = Field(None, description="End date of validity")
    as_of_date: date = Field(default_factory=date.today, description="Date when this fact was recorded")

class Company(TemporalNode):
    label: Literal["Company"] = "Company"
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class Person(TemporalNode):
    label: Literal["Person"] = "Person"
    role: Optional[str] = None

class Contract(TemporalNode):
    label: Literal["Contract"] = "Contract"
    value: Optional[float] = None
    currency: str = "USD"
    expiration_date: Optional[date] = None

class Risk(TemporalNode):
    label: Literal["Risk"] = "Risk"
    severity: Literal["low", "medium", "high", "critical"]
    probability: float = Field(..., ge=0.0, le=1.0)
    description: str

class FinancialMetric(TemporalNode):
    label: Literal["FinancialMetric"] = "FinancialMetric"
    metric_name: str
    value: float
    unit: str
    period: str  # e.g., "Q4 2023", "FY 2022"

class Assumption(TemporalNode):
    label: Literal["Assumption"] = "Assumption"
    category: Literal["strategic", "financial", "market"]
    value: str
    sensitivity_level: Literal["low", "medium", "high"]

# Relationships
class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict = {}
