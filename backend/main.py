import os
from typing import Any, Literal

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_TITLE = "VisionPilot AI API"
APP_VERSION = "3.1.0"
DATA_FILE = os.getenv("DATA_FILE", "../data/demo_business_data.csv")

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = ["*"] if allowed_origins_env.strip() == "*" else [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    revenue: float = Field(ge=0)
    cost: float = Field(ge=0)
    growth_rate: float = Field(default=0.05, ge=-1, le=3)
    model_type: Literal["baseline", "conservative", "aggressive", "ai_ensemble"] = "baseline"


MODEL_PROFILES: dict[str, dict[str, float]] = {
    "baseline": {"growth_multiplier": 1.0, "risk_buffer": 1.0, "confidence": 0.86},
    "conservative": {"growth_multiplier": 0.78, "risk_buffer": 1.22, "confidence": 0.92},
    "aggressive": {"growth_multiplier": 1.35, "risk_buffer": 0.88, "confidence": 0.79},
    "ai_ensemble": {"growth_multiplier": 1.12, "risk_buffer": 0.95, "confidence": 0.9},
}


def _load_records(limit: int = 12) -> list[dict[str, Any]]:
    try:
        df = pd.read_csv(DATA_FILE)
        return df.head(limit).to_dict(orient="records")
    except Exception:
        return [
            {"month": "Jan", "revenue": 120000, "cost": 80000},
            {"month": "Feb", "revenue": 132000, "cost": 84000},
            {"month": "Mar", "revenue": 140000, "cost": 87000},
        ]


def _risk_band(margin: float, volatility_index: float) -> str:
    if margin >= 0.35 and volatility_index < 0.28:
        return "low"
    if margin >= 0.2 and volatility_index < 0.45:
        return "medium"
    return "high"


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "visionpilot-backend"}


@app.get("/data")
def get_data() -> dict[str, Any]:
    records = _load_records()
    return {"records": records, "count": len(records)}


@app.post("/predict")
def predict(payload: PredictRequest) -> dict[str, Any]:
    profile = MODEL_PROFILES[payload.model_type]

    profit = payload.revenue - payload.cost
    adjusted_growth = payload.growth_rate * profile["growth_multiplier"]
    projected_revenue = payload.revenue * (1 + adjusted_growth)
    projected_profit = projected_revenue - payload.cost

    margin = projected_profit / projected_revenue if projected_revenue else 0
    growth_volatility = abs(payload.growth_rate - adjusted_growth) * profile["risk_buffer"]
    cost_pressure = (payload.cost / payload.revenue - 0.5) * 0.6 if payload.revenue else 1
    volatility_index = max(growth_volatility + cost_pressure, 0)
    risk = _risk_band(margin, volatility_index)

    return {
        "model_type": payload.model_type,
        "profit": round(profit, 2),
        "projected_revenue": round(projected_revenue, 2),
        "projected_profit": round(projected_profit, 2),
        "profit_delta": round(projected_profit - profit, 2),
        "confidence": round(profile["confidence"], 2),
        "volatility_index": round(volatility_index, 2),
        "risk": risk,
    }


@app.get("/dashboard")
def dashboard() -> dict[str, Any]:
    records = _load_records(limit=6)
    total_revenue = sum(float(r.get("revenue", 0)) for r in records)
    total_cost = sum(float(r.get("cost", 0)) for r in records)
    return {
        "title": "VisionPilot AI Dashboard",
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_revenue - total_cost, 2),
        },
        "latest_points": records,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
