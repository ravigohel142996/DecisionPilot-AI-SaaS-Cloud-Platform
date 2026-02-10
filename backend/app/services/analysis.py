from __future__ import annotations

import io
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None


def load_dataframe(content: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(content))
    return pd.read_csv(io.BytesIO(content))


def auto_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean.columns = [c.strip().lower().replace(" ", "_") for c in clean.columns]
    for col in clean.select_dtypes(include=["object"]).columns:
        clean[col] = clean[col].fillna("unknown")
    numeric_cols = clean.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        imputer = SimpleImputer(strategy="median")
        clean[numeric_cols] = imputer.fit_transform(clean[numeric_cols])
    return clean


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "revenue" in out.columns and "cost" in out.columns:
        out["profit"] = out["revenue"] - out["cost"]
        out["margin_pct"] = np.where(out["revenue"] != 0, out["profit"] / out["revenue"], 0.0)
    if "employee_output" in out.columns and "employee_hours" in out.columns:
        out["employee_efficiency"] = np.where(out["employee_hours"] != 0, out["employee_output"] / out["employee_hours"], 0.0)
    return out


def summarize_csv(content: bytes, filename: str = "dataset.csv") -> tuple[pd.DataFrame, str, dict]:
    data = load_dataframe(content, filename)
    clean = feature_engineering(auto_clean_data(data))
    row_count, col_count = clean.shape
    numeric_columns = clean.select_dtypes(include=["number"]).columns.tolist()

    summary_lines = [
        f"Rows: {row_count}",
        f"Columns: {col_count}",
        f"Numeric columns: {', '.join(numeric_columns) if numeric_columns else 'None'}",
    ]

    if numeric_columns:
        describe = clean[numeric_columns].describe().round(2)
        for column in numeric_columns[:6]:
            summary_lines.append(
                f"{column}: mean={describe.at['mean', column]}, std={describe.at['std', column]}, max={describe.at['max', column]}"
            )

    metadata = {
        "numeric_features": numeric_columns,
        "categorical_features": clean.select_dtypes(exclude=["number"]).columns.tolist(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    return clean, "\n".join(summary_lines), metadata


def build_realtime_metrics(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include=["number"]).copy()
    if numeric.empty:
        return {
            "revenue": 0.0,
            "cost": 0.0,
            "profit": 0.0,
            "forecast_profit": 0.0,
            "churn_probability": 0.0,
            "employee_score": 0.0,
            "risk_score": 0.0,
            "generated_at": datetime.now(timezone.utc),
        }

    revenue = float(numeric.get("revenue", pd.Series([numeric.sum(axis=1).mean()])).mean())
    cost = float(numeric.get("cost", pd.Series([numeric.mean(axis=1).mean() * 0.6])).mean())
    profit = revenue - cost

    features = numeric.fillna(0.0)
    y_reg = features.sum(axis=1)

    if XGBRegressor and len(features) >= 20:
        reg_model = XGBRegressor(n_estimators=60, max_depth=3, learning_rate=0.08, random_state=42)
    else:
        reg_model = RandomForestRegressor(n_estimators=80, random_state=42)

    reg_model.fit(features, y_reg)
    forecast_profit = float(reg_model.predict(features.tail(1))[0] * 0.12)

    churn_target = (y_reg < y_reg.median()).astype(int)
    clf = LogisticRegression(max_iter=500)
    clf.fit(features, churn_target)
    churn_probability = float(clf.predict_proba(features.tail(1))[0][1])

    employee_score = float(np.clip(100 - (churn_probability * 70) + (profit / (revenue + 1) * 20), 0, 100))
    risk_score = float(np.clip(churn_probability * 100 + max(0.0, -profit), 0, 100))

    return {
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "profit": round(profit, 2),
        "forecast_profit": round(forecast_profit, 2),
        "churn_probability": round(churn_probability, 4),
        "employee_score": round(employee_score, 2),
        "risk_score": round(risk_score, 2),
        "generated_at": datetime.now(timezone.utc),
    }
