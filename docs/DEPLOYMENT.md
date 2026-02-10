# VisionPilot AI Deployment Guide (No Authentication)

## Backend on Render
1. Create a new **Web Service** from this repo.
2. Set **Root Directory** to `backend`.
3. Build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Optional env var: `ALLOWED_ORIGINS=*`.
6. Health check path: `/health`.

## Frontend on Streamlit Cloud
1. Create app from this repo.
2. Set **Main file path** to `frontend/app.py`.
3. Add one secret (optional if local default works):
   ```toml
   API_BASE_URL = "https://<your-render-backend>.onrender.com"
   ```
4. Deploy. The app opens directly to dashboard without login.
