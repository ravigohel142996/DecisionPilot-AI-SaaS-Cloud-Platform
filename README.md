# VisionPilot AI — Advanced 3D Decision Intelligence Platform

VisionPilot AI is a modular enterprise platform that blends **real-time analytics**, **3D business intelligence**, and an **AI decision engine** for executive planning.

## Core Stack
- **Frontend:** Streamlit + Plotly + Three.js (embedded) + PyThreeJS dependency
- **Backend:** FastAPI
- **Database:** PostgreSQL (Supabase-compatible)
- **ML:** Scikit-learn + XGBoost (fallback-aware)
- **Auth:** JWT-ready with Supabase environment hooks
- **Deployment:** Docker + Streamlit Cloud friendly

## Features Implemented
1. **Authentication + Roles**
   - Email/password auth
   - Roles: `ceo`, `cto`, `manager`, `analyst`
   - Session via JWT bearer tokens

2. **3D Business Intelligence Dashboard**
   - Interactive animated Three.js KPI cubes + revenue pyramid
   - Plotly live KPI pulse chart
   - Dark neon glassmorphism UI

3. **Real-Time Analytics API**
   - Revenue/cost/profit tracking
   - Profit forecasting
   - Churn probability and employee score outputs

4. **AI Decision Engine**
   - Risk score interpretation
   - Strategy recommendations
   - Market trend signal
   - Scenario impact mapping

5. **Data Management**
   - CSV/Excel upload
   - Auto-cleaning + feature engineering
   - Dataset version records

6. **Executive Reports**
   - Auto-generated board-ready PDF reports
   - KPI table + risk alerts + recommendation section

7. **Scenario Simulator**
   - Monte Carlo what-if simulation
   - Budget / demand / hiring impact forecasting

8. **Admin Panel**
   - User + subscription overview
   - API latency monitoring snapshot
   - Billing events count

---

## Project Structure
```text
backend/
  app/
    api/                # auth, analysis, intelligence, admin routes
    core/               # config + security
    db/                 # SQLAlchemy session
    models/             # multi-tenant entities + metrics tables
    schemas/            # Pydantic contracts
    services/           # analytics, decisioning, reporting, subscription logic
  tests/                # service-level tests
frontend/
  streamlit_app.py      # futuristic dashboard UI
scripts/
  seed_sample_users.py  # demo user seeding
data/
  demo_business_data.csv
Dockerfiles + docker-compose.yml
requirements.txt
docs/DEPLOYMENT.md
```

## Quick Start
```bash
pip install -r requirements.txt
cp backend/.env.example backend/.env  # if not present, create based on docs
docker compose up --build
```

- API: http://localhost:8000
- Streamlit UI: http://localhost:8501

## Demo Credentials (after seeding)
Run:
```bash
PYTHONPATH=backend python scripts/seed_sample_users.py
```

Users (password for all: `VisionPilot#2026`):
- ceo@visionpilot.ai
- cto@visionpilot.ai
- manager@visionpilot.ai
- analyst@visionpilot.ai

## Supabase Notes
Set these in backend environment for Supabase-hosted Postgres/Auth alignment:
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`

See full deployment checklist in `docs/DEPLOYMENT.md`.


## Frontend ↔ Backend API Configuration
Set this environment variable for Streamlit (local or Streamlit Cloud):

```bash
API_BASE_URL=https://visionpilot-backend.onrender.com
```

The frontend automatically falls back to this hosted endpoint when the variable is not set.

## Production Readiness Checklist
- Deploy backend with `backend/render.yaml` (or Dockerfile) and configure persistent Postgres.
- Keep `SECRET_KEY` and `DATABASE_URL` in secure environment variables.
- Set `ALLOWED_ORIGINS=*` (or explicit domains) for CORS based on your security posture.
- Set Streamlit secret/environment variable `API_BASE_URL` to the backend service URL.
- Health check endpoint: `/health`.
