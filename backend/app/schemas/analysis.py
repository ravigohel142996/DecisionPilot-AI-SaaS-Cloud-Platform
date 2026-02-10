from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: int
    summary: str
    created_at: datetime
    dataset_version: str


class UploadListItem(BaseModel):
    id: int
    filename: str
    created_at: datetime


class UploadListResponse(BaseModel):
    items: list[UploadListItem]


class RealtimeAnalyticsResponse(BaseModel):
    revenue: float
    cost: float
    profit: float
    forecast_profit: float
    churn_probability: float
    employee_score: float
    risk_score: float
    generated_at: datetime


class DecisionResponse(BaseModel):
    risk_score: float
    market_trend: str
    recommendations: list[str]
    scenario_impact: dict[str, float]


class ScenarioRequest(BaseModel):
    budget_change_pct: float = 0.0
    demand_change_pct: float = 0.0
    hiring_change_pct: float = 0.0
    iterations: int = 500


class ScenarioResponse(BaseModel):
    expected_revenue: float
    expected_profit: float
    downside_risk: float
    upside_potential: float


class DatasetVersionResponse(BaseModel):
    version_label: str
    rows_count: int
    columns_count: int
    metadata: dict
    created_at: datetime
