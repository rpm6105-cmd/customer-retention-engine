from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


HEALTH_LABELS = {
    "Healthy": "Healthy",
    "Neutral": "Neutral",
    "At Risk": "At Risk",
}


def _normalize_score(series: pd.Series, floor: float = 0, ceiling: float = 100) -> pd.Series:
    return series.clip(lower=floor, upper=ceiling)


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    login_max = max(float(work["Monthly_Logins"].max()), 1.0)
    active_max = max(float(work["Active_Users"].max()), 1.0)
    ticket_max = max(float(work["Support_Tickets_Last_30_Days"].max()), 1.0)

    work["Engagement_Score"] = _normalize_score(
        ((work["Monthly_Logins"] / login_max) * 55) + ((work["Active_Users"] / active_max) * 45)
    )

    work["Health_Score"] = _normalize_score(
        (0.35 * work["Feature_Usage_Score"])
        + (0.25 * (work["CSAT"] * 10))
        + (0.20 * np.clip(work["NPS"], 0, 100))
        + (0.20 * work["Engagement_Score"])
    )

    work["Health_Category"] = np.select(
        [work["Health_Score"] >= 75, work["Health_Score"] >= 50],
        [HEALTH_LABELS["Healthy"], HEALTH_LABELS["Neutral"]],
        default=HEALTH_LABELS["At Risk"],
    )

    renewal_dt = pd.to_datetime(work["Renewal_Date"], errors="coerce")
    work["Renewal_Days"] = (renewal_dt.dt.date - date.today()).apply(lambda d: d.days if pd.notna(d) else 999)

    high_risk_mask = (
        (work["Feature_Usage_Score"] < 40)
        | (work["Monthly_Logins"] < (login_max * 0.15))
        | (work["Support_Tickets_Last_30_Days"] >= max(6, ticket_max * 0.5))
        | (work["CSAT"] < 6)
        | (work["Last_Login_Days_Ago"] > 30)
        | (work["Health_Score"] < 45)
    )
    medium_risk_mask = (
        (work["Health_Score"] < 65)
        | (work["Renewal_Days"] <= 90)
        | (work["Support_Tickets_Last_30_Days"] >= 4)
    )
    work["Churn_Risk"] = np.select(
        [high_risk_mask, medium_risk_mask],
        ["High Risk", "Medium Risk"],
        default="Low Risk",
    )

    work["Expansion_Score"] = _normalize_score(
        (0.30 * work["Feature_Usage_Score"])
        + (0.20 * (work["CSAT"] * 10))
        + (0.20 * np.clip(work["NPS"], 0, 100))
        + (0.15 * ((work["Active_Users"] / active_max) * 100))
        + (0.15 * (100 - ((work["Support_Tickets_Last_30_Days"] / ticket_max) * 100)))
    )
    work["Expansion_Opportunity"] = np.where(work["Expansion_Score"] >= 80, "High Opportunity", "Watch")

    work["Health_Risk_Weight"] = work["Churn_Risk"].map({"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}).fillna(1)
    work["Priority_Score"] = (
        (100 - work["Health_Score"])
        + (work["Health_Risk_Weight"] * 18)
        + (120 - work["Renewal_Days"].clip(lower=0, upper=120))
        + (work["Support_Tickets_Last_30_Days"] * 3)
    )

    work["Next_Best_Action"] = work.apply(recommend_action, axis=1)
    return work


def recommend_action(row: pd.Series) -> str:
    if row["Churn_Risk"] == "High Risk":
        return "Schedule Executive Business Review"
    if row["Feature_Usage_Score"] < 50:
        return "Provide product training"
    if row["Expansion_Score"] >= 82:
        return "Recommend upsell"
    if row["Health_Score"] >= 78:
        return "Introduce premium plan"
    return "Run success check-in"
