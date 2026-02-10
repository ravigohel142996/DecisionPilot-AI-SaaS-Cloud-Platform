# VisionPilot AI (Authentication Removed)

VisionPilot now runs as an **instant dashboard app**:
- no login
- no signup
- no users
- no tokens
- no auth routes

The frontend opens directly to the dashboard and only calls these backend routes:
- `GET /health`
- `GET /data`
- `POST /predict`
- `GET /dashboard`

## New Folder Structure

```text
backend/
  main.py
  requirements.txt
  .env.example
  Dockerfile
  render.yaml
  app/
    main.py
frontend/
  app.py
  streamlit_app.py
  api.py
  config.py
  requirements.txt
  Dockerfile
docs/
  DEPLOYMENT.md
.env.example
requirements.txt
data/
  demo_business_data.csv
```

## Full Cleaned Code

### `frontend/app.py`
```python
import pandas as pd
import plotly.express as px
import streamlit as st

from api import APIClient

st.set_page_config(page_title="VisionPilot AI", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #0b1220; color: #f8fafc; }
    .block-container { max-width: 1100px; padding-top: 1.2rem; }
    h1, h2, h3, p, span, label, div { color: #f8fafc !important; }
    [data-testid="stSidebar"] { background: #111827; }
    .metric-card {
        background: #111827;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.8rem 1rem;
    }
    @media (max-width: 768px) {
        .block-container { padding: 0.7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

client = APIClient()

with st.sidebar:
    st.markdown("## VisionPilot AI")
    st.caption(f"API endpoint: {client.base_url}")
    health_ok, _ = client.health()
    st.success("Backend online") if health_ok else st.warning("Backend offline")

st.title("Dashboard")
st.caption("Always-on analytics dashboard. No authentication required.")

dashboard_ok, dashboard = client.dashboard()
if not dashboard_ok:
    st.error("Dashboard is loading with fallback values.")
    dashboard = {
        "kpis": {"total_revenue": 0, "total_cost": 0, "total_profit": 0},
        "latest_points": [],
    }

kpis = dashboard.get("kpis", {})
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${kpis.get('total_revenue', 0):,.0f}")
col2.metric("Total Cost", f"${kpis.get('total_cost', 0):,.0f}")
col3.metric("Total Profit", f"${kpis.get('total_profit', 0):,.0f}")

st.markdown("### Trend Data")
data_ok, data_payload = client.data()
records = data_payload.get("records", []) if data_ok else dashboard.get("latest_points", [])

df = pd.DataFrame(records)
if not df.empty and {"revenue", "cost"}.issubset(df.columns):
    x_axis = "month" if "month" in df.columns else df.index
    fig = px.line(df, x=x_axis, y=["revenue", "cost"], markers=True, template="plotly_dark")
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No records yet.")

st.markdown("### Quick Prediction")
left, right = st.columns([2, 1])
with left:
    revenue = st.number_input("Revenue", min_value=0.0, value=120000.0, step=1000.0)
    cost = st.number_input("Cost", min_value=0.0, value=80000.0, step=1000.0)
    growth = st.slider("Expected growth rate", min_value=-0.2, max_value=1.0, value=0.12, step=0.01)
with right:
    st.write("")
    run = st.button("Run prediction", use_container_width=True)

if run:
    ok, prediction = client.predict(revenue, cost, growth)
    if ok:
        st.success("Prediction complete")
        p1, p2, p3 = st.columns(3)
        p1.metric("Current Profit", f"${prediction['profit']:,.0f}")
        p2.metric("Projected Revenue", f"${prediction['projected_revenue']:,.0f}")
        p3.metric("Projected Profit", f"${prediction['projected_profit']:,.0f}")
        st.caption(f"Risk level: {prediction['risk'].title()}")
    else:
        st.error(prediction["detail"])
```

### `backend/main.py`
```python
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
```

### `requirements.txt`
```text
-r backend/requirements.txt
```

## Deployment Steps

### Streamlit Cloud (Frontend)
1. App file: `frontend/app.py`
2. Optional secret:
   - `API_BASE_URL = "https://<your-render-backend>.onrender.com"`
3. Deploy.

### Render (Backend)
1. Root directory: `backend`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Health check path: `/health`
5. Optional env: `ALLOWED_ORIGINS=*`

No auth secrets are required.
