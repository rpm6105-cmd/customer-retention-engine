from __future__ import annotations

import os

import pandas as pd
import requests


def _fallback_summary(df: pd.DataFrame) -> str:
    total = len(df)
    high_risk = int((df["Churn_Risk"] == "High Risk").sum()) if total else 0
    medium_risk = int((df["Churn_Risk"] == "Medium Risk").sum()) if total else 0
    arr_exposure = float(df.loc[df["Churn_Risk"] == "High Risk", "ARR"].sum()) if total else 0.0
    expansion = int((df["Expansion_Opportunity"] == "High Opportunity").sum()) if total else 0
    renewals = int(((df["Renewal_Days"] >= 0) & (df["Renewal_Days"] <= 90)).sum()) if total else 0
    return (
        f"{high_risk} accounts show high churn risk and {medium_risk} require closer monitoring. "
        f"ARR exposure is ${arr_exposure:,.0f}. {expansion} expansion opportunities are currently flagged, "
        f"and {renewals} renewals land inside the next 90 days. Focus the team on at-risk renewals first, "
        f"then drive product adoption and executive outreach on the highest-value accounts."
    )


def generate_ai_summary(df: pd.DataFrame) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or df.empty:
        return _fallback_summary(df)

    prompt = {
        "portfolio_size": int(len(df)),
        "high_risk_accounts": int((df["Churn_Risk"] == "High Risk").sum()),
        "medium_risk_accounts": int((df["Churn_Risk"] == "Medium Risk").sum()),
        "arr_exposure": float(df.loc[df["Churn_Risk"] == "High Risk", "ARR"].sum()),
        "expansion_opportunities": int((df["Expansion_Opportunity"] == "High Opportunity").sum()),
        "renewals_90_days": int(((df["Renewal_Days"] >= 0) & (df["Renewal_Days"] <= 90)).sum()),
        "avg_health": round(float(df["Health_Score"].mean()), 1),
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a SaaS customer success operations analyst. Write a concise executive retention summary in 2-3 sentences.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this retention portfolio: {prompt}",
                    },
                ],
                "temperature": 0.3,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return _fallback_summary(df)
