from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components


def resolve_api_base_url() -> str:
    url = st.secrets.get("api_base_url") or os.getenv("API_BASE_URL") or "http://localhost:8000"
    return str(url).rstrip("/")


API_BASE_URL = resolve_api_base_url()

st.set_page_config(page_title="VisionPilot AI", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(circle at top, #10122b 0%, #080a1a 60%, #060714 100%); color: #e7ebff; }
      .glass {background: rgba(20, 26, 62, 0.45); border:1px solid rgba(132,145,255,0.35); border-radius:18px; padding: 1rem; backdrop-filter: blur(8px);}
      .neon {color:#8cb3ff; text-shadow:0 0 14px #5f82ff;}
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


with st.sidebar:
    st.caption(f"API endpoint: {API_BASE_URL}")
    if st.button("Sign out", use_container_width=True):
        st.session_state.token = None
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
        with st.form("register"):
            st.subheader("Create account")
            company = st.text_input("Company")
            name = st.text_input("Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["ceo", "cto", "manager", "analyst"])
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Register"):
                res = api_post("/auth/register", json={"company_name": company, "full_name": name, "email": email, "password": password, "role": role})
                if res.ok:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Registered successfully")
                else:
                    st.error(res.text)
    with c2:
        with st.form("login"):
            st.subheader("Sign in")
            email = st.text_input("Login email")
            password = st.text_input("Login password", type="password")
            if st.form_submit_button("Login"):
                res = api_post("/auth/login", json={"email": email, "password": password})
                if res.ok:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Login success")
                else:
                    st.error(res.text)

with dashboard_tab:
    if not st.session_state.token:
        st.info("Authenticate to access the dashboard.")
    else:
        profile = api_get("/auth/me", headers=auth_headers())
        if not profile.ok:
            st.error("Session expired.")
            st.stop()
        p = profile.json()
        st.markdown(f"<div class='glass'><b>{p['company_name']}</b> • role: {p['role'].upper()}</div>", unsafe_allow_html=True)
        render_three_scene()

        upload_file = st.file_uploader("Upload CSV/Excel dataset", type=["csv", "xlsx"])
        if upload_file and st.button("Run Auto-Clean + Feature Engineering"):
            result = api_post("/analysis/upload", files={"file": (upload_file.name, upload_file.getvalue(), "application/octet-stream")}, headers=auth_headers())
            if result.ok:
                st.success("Dataset processed and versioned")
                st.code(result.json()["summary"])
            else:
                st.error(result.text)

        metrics = api_get("/analysis/realtime", headers=auth_headers())
        decision = api_get("/intelligence/decision", headers=auth_headers())
        if metrics.ok:
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

        if decision.ok:
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
            sim = api_post("/intelligence/scenario", headers=auth_headers(), json={"budget_change_pct": budget, "demand_change_pct": demand, "hiring_change_pct": hiring, "iterations": 700})
            if sim.ok:
                st.json(sim.json())

        uploads = api_get("/analysis/uploads", headers=auth_headers())
        if uploads.ok:
            st.subheader("Executive Reports")
            for row in uploads.json().get("items", []):
                created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.write(row["filename"])
                c2.caption(created.strftime("%Y-%m-%d %H:%M"))
                report = api_get(f"/analysis/report/{row['id']}", headers=auth_headers())
                if report.ok:
                    c3.download_button("PDF", report.content, file_name=f"board-report-{row['id']}.pdf", mime="application/pdf", key=f"r{row['id']}")

with admin_tab:
    if not st.session_state.token:
        st.info("Login required")
    else:
        res = api_get("/admin/overview", headers=auth_headers())
        if res.ok:
            st.json(res.json())
        else:
            st.warning("Admin access requires CEO/CTO role")
