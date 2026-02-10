import os
from typing import Any

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_TITLE = "VisionPilot AI API"
APP_VERSION = "3.0.0"
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


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "visionpilot-backend"}


@app.get("/data")
def get_data() -> dict[str, Any]:
    records = _load_records()
    return {"records": records, "count": len(records)}


@app.post("/predict")
def predict(payload: PredictRequest) -> dict[str, Any]:
    profit = payload.revenue - payload.cost
    projected_revenue = payload.revenue * (1 + payload.growth_rate)
    projected_profit = projected_revenue - payload.cost
    risk = "low" if projected_profit >= profit else "medium"

    return {
        "profit": round(profit, 2),
        "projected_revenue": round(projected_revenue, 2),
        "projected_profit": round(projected_profit, 2),
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
