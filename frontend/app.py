import pandas as pd
import plotly.express as px
import streamlit as st

from api import APIClient

st.set_page_config(page_title="VisionPilot AI", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 0%, #1f2937 0%, #0b1220 30%, #050b17 100%);
        color: #e2e8f0;
    }
    .block-container {
        max-width: 1250px;
        padding-top: 1.1rem;
        padding-bottom: 1.4rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.2);
    }
    .hero-card {
        background: linear-gradient(110deg, rgba(56, 189, 248, 0.16) 0%, rgba(96, 165, 250, 0.12) 45%, rgba(14, 116, 144, 0.05) 100%);
        border: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: 16px;
        padding: 1.15rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(2, 6, 23, 0.45);
    }
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        box-shadow: 0 8px 24px rgba(2, 6, 23, 0.36);
    }
    div[data-testid="stMetricValue"] { color: #f8fafc; }
    .section-title {
        margin-top: 0.8rem;
        margin-bottom: 0.55rem;
        font-size: 0.95rem;
        letter-spacing: 0.09em;
        color: #cbd5e1;
        text-transform: uppercase;
        font-weight: 600;
    }
    @media (max-width: 768px) {
        .block-container { padding: 0.65rem; }
        .hero-card { padding: 0.9rem 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

client = APIClient()

MODEL_OPTIONS = {
    "Baseline Forecast": "baseline",
    "Conservative Shield Model": "conservative",
    "Growth Accelerator Model": "aggressive",
    "AI Ensemble Model": "ai_ensemble",
}

with st.sidebar:
    st.markdown("## VisionPilot AI")
    st.caption("Industrial Decision Intelligence Console")
    st.caption(f"API endpoint: {client.base_url}")

    health_ok, _ = client.health()
    st.success("Backend online") if health_ok else st.warning("Backend offline")

    st.markdown("---")
    st.markdown("### Prediction Controls")
    model_label = st.selectbox("Select Forecast Model", list(MODEL_OPTIONS.keys()))
    selected_model = MODEL_OPTIONS[model_label]

    scenario_horizon = st.select_slider("Planning Horizon", options=["30 days", "60 days", "90 days", "180 days"], value="90 days")
    optimization_goal = st.radio("Optimization Priority", ["Profit", "Resilience", "Balanced"], horizontal=False)
    page = st.radio("Workspace", ["Dashboard", "Requirements & Updates"], index=0)

if page == "Dashboard":
    st.markdown(
        """
        <div class="hero-card">
            <h2 style="margin:0;">Industrial Control Center</h2>
            <p style="margin:0.35rem 0 0 0; color:#cbd5e1;">
                Unified financial telemetry, risk visibility, and model-driven prediction in one executive-grade workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dashboard_ok, dashboard = client.dashboard()
    if not dashboard_ok:
        st.error("Dashboard is loading with fallback values.")
        dashboard = {
            "kpis": {"total_revenue": 0, "total_cost": 0, "total_profit": 0},
            "latest_points": [],
        }

    kpis = dashboard.get("kpis", {})
    profit_margin = (kpis.get("total_profit", 0) / kpis.get("total_revenue", 1)) * 100 if kpis.get("total_revenue", 0) else 0
    cost_ratio = (kpis.get("total_cost", 0) / kpis.get("total_revenue", 1)) * 100 if kpis.get("total_revenue", 0) else 0

    st.markdown('<div class="section-title">System KPI Grid</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${kpis.get('total_revenue', 0):,.0f}")
    col2.metric("Total Cost", f"${kpis.get('total_cost', 0):,.0f}", delta=f"{cost_ratio:.1f}% of revenue")
    col3.metric("Total Profit", f"${kpis.get('total_profit', 0):,.0f}", delta=f"{profit_margin:.1f}% margin")
    col4.metric("Planning Horizon", scenario_horizon)

    st.markdown('<div class="section-title">Operational Trend Intelligence</div>', unsafe_allow_html=True)
    data_ok, data_payload = client.data()
    records = data_payload.get("records", []) if data_ok else dashboard.get("latest_points", [])

    df = pd.DataFrame(records)
    if not df.empty and {"revenue", "cost"}.issubset(df.columns):
        df["profit"] = df["revenue"] - df["cost"]
        x_axis = "month" if "month" in df.columns else df.index

        chart_col, table_col = st.columns([2.2, 1])
        with chart_col:
            fig = px.line(
                df,
                x=x_axis,
                y=["revenue", "cost", "profit"],
                markers=True,
                template="plotly_dark",
                color_discrete_map={"revenue": "#38bdf8", "cost": "#f97316", "profit": "#22c55e"},
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=10),
                legend_title_text="",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.5)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with table_col:
            st.markdown("#### Recent Signals")
            signal_df = (
                df[[x_axis, "revenue", "cost", "profit"]].tail(5)
                if x_axis in df.columns
                else df[["revenue", "cost", "profit"]].tail(5)
            )
            st.dataframe(signal_df, use_container_width=True, hide_index=True)
    else:
        st.info("No records yet.")

    st.markdown('<div class="section-title">Model Studio</div>', unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        revenue = st.number_input("Revenue", min_value=0.0, value=120000.0, step=1000.0)
        cost = st.number_input("Cost", min_value=0.0, value=80000.0, step=1000.0)
        growth = st.slider("Expected growth rate", min_value=-0.2, max_value=1.2, value=0.12, step=0.01)
    with right:
        st.write("")
        st.markdown(f"**Model:** {model_label}")
        st.markdown(f"**Goal:** {optimization_goal}")
        run = st.button("Run industrial prediction", use_container_width=True)

    if run:
        ok, prediction = client.predict(revenue, cost, growth, selected_model)
        if ok:
            st.success("Prediction complete")
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Current Profit", f"${prediction['profit']:,.0f}")
            p2.metric("Projected Revenue", f"${prediction['projected_revenue']:,.0f}")
            p3.metric("Projected Profit", f"${prediction['projected_profit']:,.0f}", delta=f"${prediction['profit_delta']:,.0f}")
            p4.metric("Model Confidence", f"{prediction['confidence'] * 100:.0f}%")

            comp_df = pd.DataFrame(
                {
                    "Metric": ["Current Profit", "Projected Profit"],
                    "Amount": [prediction["profit"], prediction["projected_profit"]],
                }
            )
            comp_fig = px.bar(
                comp_df,
                x="Metric",
                y="Amount",
                color="Metric",
                template="plotly_dark",
                color_discrete_map={"Current Profit": "#0ea5e9", "Projected Profit": "#22c55e"},
            )
            comp_fig.update_layout(margin=dict(l=20, r=20, t=25, b=20), showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(comp_fig, use_container_width=True)

            st.caption(
                f"Risk level: {prediction['risk'].title()} • Volatility Index: {prediction['volatility_index']:.2f} • Model: {prediction['model_type']}"
            )
        else:
            st.error(prediction["detail"])
else:
    st.markdown(
        """
        <div class="hero-card">
            <h2 style="margin:0;">Requirements & Update Center</h2>
            <p style="margin:0.35rem 0 0 0; color:#cbd5e1;">
                Review what is required for high-quality forecasts and the latest platform updates in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    req_col, notes_col = st.columns([1.2, 1])
    with req_col:
        st.markdown('<div class="section-title">Required Inputs</div>', unsafe_allow_html=True)
        st.markdown(
            """
            - **Revenue:** Latest observed revenue value.
            - **Cost:** Matching operating cost for the same period.
            - **Expected growth rate:** Scenario assumption from -20% to +120%.
            - **Forecast model:** Select the model in the sidebar.
            - **Optimization priority:** Choose Profit, Resilience, or Balanced.
            - **Planning horizon:** Choose the intended decision window.
            """
        )

    with notes_col:
        st.markdown('<div class="section-title">Latest Updates</div>', unsafe_allow_html=True)
        st.markdown(
            """
            1. Added this dedicated **Requirements & Updates** workspace.
            2. Dashboard remains available through the sidebar workspace selector.
            3. Updated onboarding guidance for prediction controls.
            4. Streamlined quick review for operators before running simulations.
            """
        )

    st.info("Tip: Use the Dashboard page to run predictions after validating all required inputs here.")
