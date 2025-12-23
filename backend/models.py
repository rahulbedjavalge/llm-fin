from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Ratios(BaseModel):
    gross_margin: float
    operating_margin: float
    net_margin: float
    debt_to_assets: float
    debt_to_equity: float
    receivables_turnover: float
    inventory_turnover: float
    cash_to_revenue: float
    current_assets_to_liabilities: float


class RedFlags(BaseModel):
    flags: List[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    ticker: Optional[str] = None
    period: Optional[str] = None
    ratios: Ratios
    red_flags: RedFlags


class BaselinePrediction(BaseModel):
    direction: str  # up | flat | down
    score: float


class LLMAnalysis(BaseModel):
    direction: str  # up | flat | down
    risk: str  # low | medium | high
    explanation: str


class AnalyzeResponse(BaseModel):
    llm: LLMAnalysis
    baseline: BaselinePrediction
    agreement: bool
    ratios: Ratios
    red_flags: RedFlags
