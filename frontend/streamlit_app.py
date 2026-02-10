from __future__ import annotations

import os
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="VisionPilot AI | SaaS Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)


def resolve_api_base_url() -> str:
    url = st.secrets.get("api_base_url") or os.getenv("API_BASE_URL") or "https://visionpilot-backend.onrender.com"
    return str(url).rstrip("/")


API_BASE_URL = resolve_api_base_url()

st.markdown(
    """
<style>
:root {
    color-scheme: dark;
}

body, .stApp {
    background-color: #0f172a;
    color: #e5e7eb;
}

h1, h2, h3, h4, h5, h6, label, p, span, div {
    color: #e5e7eb !important;
}

h1 { font-size: 2.35rem !important; }
h2 { font-size: 1.9rem !important; }
p, label, span, div, .stMarkdown { font-size: 1.08rem !important; }

input, select, textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: #1e293b !important;
    color: #e5e7eb !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 8px !important;
    min-height: 44px;
}

.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg,#38bdf8,#818cf8) !important;
    color: #020617 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 1rem !important;
    min-height: 44px;
}

.AuthBox, .glass {
    background: rgba(15, 23, 42, 0.85);
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #38bdf8;
    box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
    margin-bottom: 1rem;
}

.neon {
    color: #8cb3ff;
    text-shadow: 0 0 14px #5f82ff;
}

[data-testid="stAlert"] {
    font-size: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 class='neon'>VisionPilot AI • 3D Decision Intelligence Platform</h1>", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state.token = None


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


def api_post(path: str, **kwargs):
    return requests.post(f"{API_BASE_URL}{path}", timeout=60, **kwargs)


def api_get(path: str, **kwargs):
    return requests.get(f"{API_BASE_URL}{path}", timeout=60, **kwargs)


def parse_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            if "error" in payload:
                return str(payload["error"])
            if "detail" in payload:
                return str(payload["detail"])
    except ValueError:
        pass
    return response.text.strip() or "Something went wrong. Please try again."


def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))


def password_strength(password: str) -> tuple[int, str]:
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1

    labels = {0: "Very weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very strong"}
    return score, labels.get(score, "Unknown")


with st.sidebar:
    st.caption(f"API endpoint: {API_BASE_URL}")
    if st.button("Sign out", use_container_width=True):
        st.session_state.token = None
        st.toast("Signed out")
        st.rerun()


def render_three_scene():
    scene_html = """
    <div id='container' style='width:100%;height:360px;'></div>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(70, 2.2, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setSize(840, 360); document.getElementById('container').appendChild(renderer.domElement);

    const materials = [
      new THREE.MeshStandardMaterial({color:0x4d6bff, emissive:0x203eaa}),
      new THREE.MeshStandardMaterial({color:0x8b5cf6, emissive:0x301469}),
      new THREE.MeshStandardMaterial({color:0x22d3ee, emissive:0x0b4e5a})
    ];
    for(let i=0;i<3;i++){
      const cube = new THREE.Mesh(new THREE.BoxGeometry(1.1,1.1,1.1), materials[i]);
      cube.position.set(i*1.8-1.8,0,0); scene.add(cube);
    }
    const pyramid = new THREE.Mesh(new THREE.ConeGeometry(0.8,1.8,4), new THREE.MeshStandardMaterial({color:0x8b5cf6, wireframe:false}));
    pyramid.position.set(2.8,0,0); scene.add(pyramid);

    const light = new THREE.PointLight(0xffffff, 1.1); light.position.set(2,3,4); scene.add(light);
    camera.position.z = 6;

    function animate(){ requestAnimationFrame(animate); scene.children.forEach((o,idx)=>{o.rotation.y += 0.008+idx*0.002; o.rotation.x +=0.003;}); renderer.render(scene,camera);} animate();
    </script>
    """
    components.html(scene_html, height=380)


login_tab, dashboard_tab, admin_tab = st.tabs(["Authentication", "3D Dashboard", "Admin Panel"])

with login_tab:
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.markdown('<div class="AuthBox">', unsafe_allow_html=True)
            with st.form("register"):
                st.subheader("Create account")
                company = st.text_input("Company")
                name = st.text_input("Name")
                email = st.text_input("Email")
                role = st.selectbox("Role", ["ceo", "cto", "manager", "analyst"])
                password = st.text_input("Password", type="password")
                score, strength = password_strength(password)
                st.progress(min(score / 5, 1.0), text=f"Password strength: {strength}")

                if st.form_submit_button("Register"):
                    if not company.strip() or not name.strip() or not email.strip() or not password:
                        st.error("All registration fields are required.")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    elif score < 3:
                        st.warning("Use a stronger password (8+ chars, mixed case, number, symbol).")
                    else:
                        try:
                            with st.spinner("Creating your account..."):
                                res = api_post(
                                    "/auth/register",
                                    json={
                                        "company_name": company.strip(),
                                        "full_name": name.strip(),
                                        "email": email.strip().lower(),
                                        "password": password,
                                        "role": role,
                                    },
                                )
                            if res.ok:
                                st.success("Account created successfully! Please sign in with your new credentials.")
                            else:
                                st.error(parse_error_message(res))
                        except Exception:
                            st.error("Cannot reach the server right now. Please try again later.")
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        with st.container():
            st.markdown('<div class="AuthBox">', unsafe_allow_html=True)
            with st.form("login"):
                st.subheader("Sign in")
                email = st.text_input("Login email")
                password = st.text_input("Login password", type="password")
                if st.form_submit_button("Login"):
                    if not email.strip() or not password:
                        st.error("Both email and password are required.")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    else:
                        try:
                            with st.spinner("Signing in..."):
                                res = api_post("/auth/login", json={"email": email.strip().lower(), "password": password})
                            if res.ok:
                                st.session_state.token = res.json()["access_token"]
                                st.success("Login successful. Welcome back!")
                                st.toast("Logged in successfully")
                            else:
                                st.error(parse_error_message(res))
                        except Exception:
                            st.error("Cannot reach the server right now. Please try again later.")
            st.markdown("</div>", unsafe_allow_html=True)

with dashboard_tab:
    if not st.session_state.token:
        st.info("Authenticate to access the dashboard.")
    else:
        try:
            with st.spinner("Loading profile..."):
                profile = api_get("/auth/me", headers=auth_headers())
        except Exception:
            st.error("Cannot reach the server right now. Please try again later.")
            st.stop()

        if not profile.ok:
            st.error(parse_error_message(profile))
            st.stop()

        p = profile.json()
        st.markdown(f"<div class='glass'><b>{p['company_name']}</b> • role: {p['role'].upper()}</div>", unsafe_allow_html=True)
        render_three_scene()

        upload_file = st.file_uploader("Upload CSV/Excel dataset", type=["csv", "xlsx"])
        if upload_file and st.button("Run Auto-Clean + Feature Engineering"):
            try:
                with st.spinner("Analyzing dataset..."):
                    result = api_post(
                        "/analysis/upload",
                        files={"file": (upload_file.name, upload_file.getvalue(), "application/octet-stream")},
                        headers=auth_headers(),
                    )
                if result.ok:
                    st.success("Dataset processed and versioned")
                    st.toast("Analysis complete")
                    st.code(result.json()["summary"])
                else:
                    st.error(parse_error_message(result))
            except Exception:
                st.error("Cannot reach the server right now. Please try again later.")

        try:
            metrics = api_get("/analysis/realtime", headers=auth_headers())
            decision = api_get("/intelligence/decision", headers=auth_headers())
        except Exception:
            st.error("Cannot reach the server right now. Please try again later.")
            metrics = decision = None

        if metrics and metrics.ok:
            data = metrics.json()
            a, b, c, d = st.columns(4)
            a.metric("Revenue", f"${data['revenue']:,.2f}")
            b.metric("Profit", f"${data['profit']:,.2f}")
            c.metric("Forecast Profit", f"${data['forecast_profit']:,.2f}")
            d.metric("Churn", f"{data['churn_probability']*100:.1f}%")

            df = pd.DataFrame(
                [
                    {"kpi": "Revenue", "value": data["revenue"]},
                    {"kpi": "Cost", "value": data["cost"]},
                    {"kpi": "Profit", "value": data["profit"]},
                    {"kpi": "Risk Score", "value": data["risk_score"]},
                ]
            )
            fig = px.bar(df, x="kpi", y="value", color="kpi", title="Live KPI Pulse", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        if decision and decision.ok:
            d_payload = decision.json()
            st.subheader("AI Decision Engine")
            st.write("Market trend:", d_payload["market_trend"])
            for rec in d_payload["recommendations"]:
                st.write("-", rec)

        st.subheader("Scenario Simulator")
        x1, x2, x3 = st.columns(3)
        budget = x1.slider("Budget change %", -20, 30, 5)
        demand = x2.slider("Demand change %", -20, 40, 8)
        hiring = x3.slider("Hiring change %", -20, 30, 3)
        if st.button("Run Monte Carlo"):
            try:
                with st.spinner("Running simulation..."):
                    sim = api_post(
                        "/intelligence/scenario",
                        headers=auth_headers(),
                        json={
                            "budget_change_pct": budget,
                            "demand_change_pct": demand,
                            "hiring_change_pct": hiring,
                            "iterations": 700,
                        },
                    )
                if sim.ok:
                    st.toast("Simulation complete")
                    st.json(sim.json())
                else:
                    st.error(parse_error_message(sim))
            except Exception:
                st.error("Cannot reach the server right now. Please try again later.")

        try:
            uploads = api_get("/analysis/uploads", headers=auth_headers())
        except Exception:
            uploads = None

        if uploads and uploads.ok:
            st.subheader("Executive Reports")
            for row in uploads.json().get("items", []):
                created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                col_name, col_date, col_action = st.columns([4, 2, 2])
                col_name.write(row["filename"])
                col_date.caption(created.strftime("%Y-%m-%d %H:%M"))
                try:
                    report = api_get(f"/analysis/report/{row['id']}", headers=auth_headers())
                    if report.ok:
                        col_action.download_button(
                            "PDF",
                            report.content,
                            file_name=f"board-report-{row['id']}.pdf",
                            mime="application/pdf",
                            key=f"r{row['id']}",
                        )
                except Exception:
                    st.warning("Could not load report file.")

with admin_tab:
    if not st.session_state.token:
        st.info("Login required")
    else:
        try:
            with st.spinner("Loading admin overview..."):
                res = api_get("/admin/overview", headers=auth_headers())
            if res.ok:
                st.json(res.json())
            else:
                st.warning(parse_error_message(res))
        except Exception:
            st.error("Cannot reach the server right now. Please try again later.")
