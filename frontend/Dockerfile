FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir streamlit requests pandas plotly pythreejs
COPY frontend/streamlit_app.py /app/streamlit_app.py
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
