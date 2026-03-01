import requests
import json

import pandas as pd

df = pd.read_csv("customers.csv")

def calculate_health(row):
    score = 0
    score += min(row["logins_last_30_days"] * 2, 40)
    score -= min(row["support_tickets"] * 5, 30)
    score += min(row["plan_value"] / 50, 30)
    return max(min(score, 100), 0)

df["health_score"] = df.apply(calculate_health, axis=1)

def risk_flag(score):
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    else:
        return "Low Risk"

df["risk_level"] = df["health_score"].apply(risk_flag)

def expansion_flag(row):
    if row["health_score"] >= 65 and row["support_tickets"] <= 2:
        return "Expansion Candidate"
    return "None"

df["expansion_opportunity"] = df.apply(expansion_flag, axis=1)

print("\nCustomer Intelligence Report:\n")
print(df[[
    "customer_name",
    "health_score",
    "risk_level",
    "expansion_opportunity"
]])

df.to_csv("customer_report.csv", index=False)

total_customers = len(df)
high_risk = len(df[df["risk_level"] == "High Risk"])
expansion = len(df[df["expansion_opportunity"] == "Expansion Candidate"])

print("\nExecutive Summary:")
print(f"Total Customers: {total_customers}")
print(f"High Risk Accounts: {high_risk}")
print(f"Expansion Opportunities: {expansion}")

# ----- AI Executive Summary via Ollama -----

prompt = f"""
Act as a VP of Customer Success.
Write a concise 6-8 sentence executive summary.

Report:
Total Customers: {total_customers}
High Risk Accounts: {high_risk}
Expansion Opportunities: {expansion}

Analyze risk concentration, revenue impact, and suggest top 2 strategic priorities.
Do not ask questions.
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False
    }
)

result = response.json()
ai_summary = result["response"]

print("\nAI Strategic Executive Summary:\n")
print(ai_summary)