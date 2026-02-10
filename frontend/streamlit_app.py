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
    page_title="VisionPilot AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def resolve_api_base_url() -> str:
    url = (
        st.secrets.get("API_BASE_URL")
        or st.secrets.get("api_base_url")
        or os.getenv("API_BASE_URL")
        or "https://visionpilot-backend.onrender.com"
    )
    return str(url).rstrip("/")


API_BASE_URL = resolve_api_base_url()

st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #020024);
    color: white;
}

h1, h2, h3, h4, h5, h6, label, p, span, div {
    color: #F8FAFC !important;
}

h1 { font-size: 2.3rem !important; }
h2 { font-size: 1.8rem !important; }
p, label, span, div, .stMarkdown { font-size: 1.02rem !important; }

input, select, textarea {
    background: #020617 !important;
    color: white !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 8px !important;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background: #0f172a !important;
    color: #F8FAFC !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 8px !important;
}

.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, #38BDF8, #818CF8) !important;
    color: black !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 1rem !important;
}

.auth-card, .glass {
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(12px);
    padding: 24px;
    border-radius: 15px;
    border: 1px solid #38BDF8;
    box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
    margin-bottom: 1rem;
}

.neon { color: #8cb3ff; text-shadow: 0 0 14px #5f82ff; }
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


def api_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail.strip():
                return detail
    except Exception:
        pass

    if response.status_code == 401:
        return "Invalid email or password."
    if response.status_code == 422:
        return "Please review the form fields and try again."
    if 500 <= response.status_code < 600:
        return "Server error. Please try again shortly."
    return f"Request failed ({response.status_code})."


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

    labels = {
        0: "Very weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong",
        5: "Very strong",
    }
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
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
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
                    if not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    elif score < 3:
                        st.warning("Use a stronger password (8+ chars, mixed case, number, symbol).")
                    else:
                        try:
                            with st.spinner("Creating your account..."):
                                res = api_post(
                                    "/auth/register",
                                    json={
                                        "company_name": company,
                                        "full_name": name,
                                        "email": email,
                                        "password": password,
                                        "role": role,
                                    },
                                )
                            if res.status_code == 200:
                                st.session_state.token = res.json()["access_token"]
                                st.success("Account Created")
                                st.toast("Welcome to VisionPilot AI")
                                st.balloons()
                            else:
                                st.error(api_error_message(res))
                        except requests.RequestException:
                            st.error("Could not reach the API server. Please try again later.")
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        with st.container():
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            with st.form("login"):
                st.subheader("Sign in")
                email = st.text_input("Login email")
                password = st.text_input("Login password", type="password")
                if st.form_submit_button("Login"):
                    if not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    else:
                        try:
                            with st.spinner("Signing in..."):
                                res = api_post("/auth/login", json={"email": email, "password": password})
                            if res.status_code == 200:
                                st.session_state.token = res.json()["access_token"]
                                st.success("Login success")
                                st.toast("Logged in successfully")
                            else:
                                st.error(api_error_message(res))
                        except requests.RequestException:
                            st.error("Could not reach the API server. Please try again later.")
            st.markdown("</div>", unsafe_allow_html=True)

with dashboard_tab:
    if not st.session_state.token:
        st.info("Authenticate to access the dashboard.")
    else:
        try:
            with st.spinner("Loading profile..."):
                profile = api_get("/auth/me", headers=auth_headers())
        except Exception:
            st.error("Server offline. Try later.")
            st.stop()

        if not profile.ok:
            st.error("Session expired.")
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
                    st.error(result.text)
            except Exception:
                st.error("Server offline. Try later.")

        try:
            metrics = api_get("/analysis/realtime", headers=auth_headers())
            decision = api_get("/intelligence/decision", headers=auth_headers())
        except Exception:
            st.error("Server offline. Try later.")
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
                    st.error(sim.text)
            except Exception:
                st.error("Server offline. Try later.")

        try:
            uploads = api_get("/analysis/uploads", headers=auth_headers())
        except Exception:
            uploads = None

        if uploads and uploads.ok:
            st.subheader("Executive Reports")
            for row in uploads.json().get("items", []):
                created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.write(row["filename"])
                c2.caption(created.strftime("%Y-%m-%d %H:%M"))
                try:
                    report = api_get(f"/analysis/report/{row['id']}", headers=auth_headers())
                    if report.ok:
                        c3.download_button(
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
                st.warning("Admin access requires CEO/CTO role")
        except Exception:
            st.error("Server offline. Try later.")
