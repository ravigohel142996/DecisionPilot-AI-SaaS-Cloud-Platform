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
