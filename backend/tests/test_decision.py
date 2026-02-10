from app.services.decision import decision_intelligence, simulate_scenario


def test_decision_intelligence_returns_recommendations():
    out = decision_intelligence({"risk_score": 80, "profit": -10, "churn_probability": 0.52, "cost": 100})
    assert out["market_trend"] in {"bearish", "volatile", "bullish"}
    assert len(out["recommendations"]) >= 1


def test_simulate_scenario_has_expected_fields():
    sim = simulate_scenario({"revenue": 200, "cost": 120}, 5, 10, 2, 100)
    assert {"expected_revenue", "expected_profit", "downside_risk", "upside_potential"}.issubset(sim.keys())
