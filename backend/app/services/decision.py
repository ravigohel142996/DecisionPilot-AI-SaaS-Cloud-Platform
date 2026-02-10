from __future__ import annotations

import numpy as np
import pandas as pd


def decision_intelligence(metrics: dict) -> dict:
    risk = metrics.get("risk_score", 0.0)
    profit = metrics.get("profit", 0.0)
    churn = metrics.get("churn_probability", 0.0)

    trend = "bullish" if profit > 0 and churn < 0.35 else "volatile" if risk < 65 else "bearish"

    recommendations = []
    if risk > 70:
        recommendations.append("Activate risk response playbook and freeze non-critical spend.")
    if churn > 0.4:
        recommendations.append("Prioritize retention campaigns for high-value customer cohorts.")
    if profit < 0:
        recommendations.append("Optimize COGS and renegotiate supplier contracts.")
    if not recommendations:
        recommendations.append("Maintain growth plan with phased hiring and market expansion.")

    scenario_impact = {
        "price_increase_3pct": round(profit * 1.03, 2),
        "marketing_boost_10pct": round(profit * 1.1 - 0.05 * risk, 2),
        "cost_reduction_5pct": round(profit + abs(metrics.get("cost", 0.0)) * 0.05, 2),
    }

    return {
        "risk_score": risk,
        "market_trend": trend,
        "recommendations": recommendations,
        "scenario_impact": scenario_impact,
    }


def simulate_scenario(metrics: dict, budget_change_pct: float, demand_change_pct: float, hiring_change_pct: float, iterations: int):
    base_revenue = metrics.get("revenue", 1.0)
    base_cost = metrics.get("cost", 1.0)
    rng = np.random.default_rng(42)

    samples = []
    for _ in range(max(50, iterations)):
        demand_noise = rng.normal(demand_change_pct / 100, 0.05)
        budget_noise = rng.normal(budget_change_pct / 100, 0.03)
        hiring_noise = rng.normal(hiring_change_pct / 100, 0.04)

        revenue = base_revenue * (1 + demand_noise + 0.4 * budget_noise)
        cost = base_cost * (1 + 0.5 * budget_noise + 0.6 * hiring_noise)
        samples.append(revenue - cost)

    s = pd.Series(samples)
    return {
        "expected_revenue": round(float(base_revenue * (1 + demand_change_pct / 100)), 2),
        "expected_profit": round(float(s.mean()), 2),
        "downside_risk": round(float(s.quantile(0.1)), 2),
        "upside_potential": round(float(s.quantile(0.9)), 2),
    }
