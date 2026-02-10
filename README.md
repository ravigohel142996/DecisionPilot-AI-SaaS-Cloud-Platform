# DecisionPilot AI SaaS Cloud Platform

A deployment-ready SaaS foundation for DecisionPilot AI using **FastAPI + Streamlit + PostgreSQL (Supabase-compatible)**.

## Implemented capabilities

- **Secure user authentication** (email/password + bcrypt password hashing + JWT tokens)
- **Company workspace isolation** (all uploads scoped by `company_id`)
- **Cloud PostgreSQL ready** (`DATABASE_URL` supports Supabase Postgres)
- **CSV upload with automatic KPI summary analysis**
- **Executive PDF report generation** from analyzed CSV uploads
- **Subscription-ready architecture** (`subscription_tier`, `subscription_status`, `billing_events`)
- **Production-oriented UI** using Streamlit tabs, authenticated flows, and report download links

## Architecture

- `backend/app/main.py` - FastAPI app, CORS, health endpoint, startup DB schema creation
- `backend/app/api/` - Authentication and analysis/report endpoints
- `backend/app/models/entities.py` - SQLAlchemy models for multi-tenant SaaS data
- `backend/app/services/` - CSV analysis + PDF rendering services
- `frontend/streamlit_app.py` - SaaS dashboard UI for register/login/upload/report

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Services:
- API: http://localhost:8000
- UI: http://localhost:8501
- Postgres: localhost:5432

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
pip install streamlit requests
streamlit run frontend/streamlit_app.py
```

## Core API endpoints

- `POST /auth/register` - Create company + owner user
- `POST /auth/login` - Obtain bearer token
- `GET /auth/me` - Current profile + subscription info
- `POST /analysis/upload` - Upload CSV and store analysis summary
- `GET /analysis/report/{upload_id}` - Download executive PDF (company-scoped)

## Supabase deployment notes

1. Create a Supabase project.
2. Copy the PostgreSQL connection string into `DATABASE_URL`.
3. Set secure `SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_ANON_KEY` in environment variables.
4. Deploy backend (e.g., Render/Fly/EC2) and Streamlit frontend separately.
5. Configure CORS origins (`ALLOWED_ORIGINS`) with deployed frontend domains.

## Security and scalability notes

- Passwords are hashed with bcrypt.
- JWT bearer auth is required for protected endpoints.
- Data access for uploads/reports enforces company-level checks.
- Business logic is isolated in service modules.
- Subscription fields and billing event table enable Stripe/webhook integrations without reworking core data model.

