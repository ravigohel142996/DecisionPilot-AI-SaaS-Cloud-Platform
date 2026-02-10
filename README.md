# VisionPilot AI - 3D Decision Intelligence Platform

Production-ready authentication starter for **FastAPI + Streamlit** with Render/Streamlit Cloud deployment support.

## Folder Structure

```text
backend/
  main.py
  database.py
  models.py
  auth.py
  requirements.txt
frontend/
  app.py
  auth_ui.py
  api.py
  config.py
  requirements.txt
.env.example
runtime.txt
README.md
```

## Backend (FastAPI)

### Features
- `/auth/register` with duplicate-user prevention
- `/auth/login` returning JWT bearer token
- `/auth/me` protected profile endpoint
- `/health` health check for deployment monitoring
- SQLite (default) via SQLAlchemy
- Password hashing with `passlib[bcrypt]`
- JWT auth with `python-jose`
- CORS configured from env (`ALLOWED_ORIGINS`)
- Security headers middleware
- Structured logging + global exception handling

### Run backend locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend (Streamlit)

### Features
- Dark, high-contrast UI
- Login/Register forms with input validation
- Loading spinners + success/error alerts
- API timeout and offline handling
- Token stored in Streamlit session state
- Dashboard only visible after login

### Run frontend locally

```bash
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run app.py
```

## Deployment Steps

### Render (Backend)
1. Create new **Web Service** from repo.
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example` (set strong `SECRET_KEY`).
6. Health check path: `/health`

### Streamlit Cloud (Frontend)
1. Create app from repo.
2. Main file path: `frontend/app.py`
3. Add secrets:
   - `API_BASE_URL = "https://<your-render-backend>.onrender.com"`
   - `REQUEST_TIMEOUT_SECONDS = "20"`

## Testing Steps

### API smoke test

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Demo User","email":"demo@example.com","password":"DemoPass#123"}'
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"DemoPass#123"}'
```

## Troubleshooting Guide

- **404 / Not Found for signup/login**
  - Verify backend is running and paths are exactly `/auth/register` and `/auth/login`.
- **Server offline on frontend**
  - Confirm `API_BASE_URL` points to live backend URL.
  - Check Render service logs and `/health` endpoint.
- **Login fails**
  - Ensure same email casing (system normalizes to lowercase).
  - Confirm user exists and password is 8+ chars.
- **CORS errors**
  - Set `ALLOWED_ORIGINS` to frontend domain(s), comma-separated.
- **Invalid token / session reset**
  - Ensure `SECRET_KEY` is stable across backend restarts.
- **Text contrast issues**
  - UI style is high-contrast dark mode; clear browser cache if stale CSS appears.
