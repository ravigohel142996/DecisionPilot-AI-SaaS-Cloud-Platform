# VisionPilot AI Deployment Guide

## 1) Backend (FastAPI)
1. Provision Postgres (Supabase recommended).
2. Set environment variables from `backend/.env.example`.
3. Build and run:
   ```bash
   docker build -f backend/Dockerfile -t visionpilot-api .
   docker run --env-file backend/.env -p 8000:8000 visionpilot-api
   ```

## 2) Frontend (Streamlit Cloud or container)
1. Set `API_BASE_URL` to deployed backend URL.
2. Deploy with:
   ```bash
   docker build -f frontend/Dockerfile -t visionpilot-ui .
   docker run -e API_BASE_URL=https://api.yourdomain.com -p 8501:8501 visionpilot-ui
   ```

## 3) Streamlit Cloud
- Use `frontend/streamlit_app.py` as app entrypoint.
- Add secrets:
  - `api_base_url`

## 4) Supabase Configuration
- Create project/database.
- Put Supabase Postgres URL in `DATABASE_URL`.
- Configure auth provider settings in Supabase dashboard.

## 5) Production Hardening
- Rotate `SECRET_KEY`.
- Restrict CORS to production domains.
- Run behind TLS reverse proxy.
- Add error/metrics exporters (Prometheus/OpenTelemetry).
