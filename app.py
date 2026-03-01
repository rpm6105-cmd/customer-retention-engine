import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

# =============================
# DATABASE (Premium Users)
# =============================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    company TEXT,
    place TEXT,
    email TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# =============================
# SESSION STATE
# =============================

defaults = {
    "authenticated": False,
    "user_type": None,
    "username": None,
    "task_log": {},
    "health_history": {},
    "task_counter": 1
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# LOGIN SYSTEM
# =============================

if not st.session_state.authenticated:

    st.title("Customer Retention & Growth Engine")

    access = st.radio("Choose Access", ["Demo Login", "Use My CSV"])

    # -------- DEMO --------
    if access == "Demo Login":
        user = st.text_input("Username", key="demo_user")
        pwd = st.text_input("Password", type="password", key="demo_pwd")

        if st.button("Login Demo"):
            if user == "freeuser" and pwd == "123456":
                st.session_state.authenticated = True
                st.session_state.user_type = "demo"
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    # -------- PREMIUM --------
    else:
        mode = st.radio("Select Option", ["Login", "Signup"])

        if mode == "Signup":
            name = st.text_input("Name", key="signup_name")
            company = st.text_input("Company", key="signup_company")
            place = st.text_input("Place", key="signup_place")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pwd")

            if st.button("Create Account"):
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                              (name, company, place, email, password))
                    conn.commit()
                    st.success("Account created. Please login.")
                except:
                    st.error("Email already exists.")

        else:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pwd")

            if st.button("Login Premium"):
                c.execute("SELECT * FROM users WHERE email=? AND password=?",
                          (email, password))
                result = c.fetchone()
                if result:
                    st.session_state.authenticated = True
                    st.session_state.user_type = "premium"
                    st.session_state.username = result[0]
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.stop()

# =============================
# HEADER
# =============================

col1, col2 = st.columns([6,2])
with col1:
    st.markdown("## Customer Retention & Growth Engine")
with col2:
    st.markdown(f"👤 **{st.session_state.username}**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("---")

# =============================
# DATA SOURCE
# =============================

if st.session_state.user_type == "demo":
    df = pd.DataFrame({
        "customer_name": ["Alpha", "Beta", "Gamma", "Delta", "Omega"],
        "logins_last_30_days": [25, 8, 18, 5, 30],
        "support_tickets": [2, 6, 3, 7, 1],
        "plan_value": [1500, 900, 2000, 800, 3000],
        "owner": ["Aisha", "Rahul", "Aisha", "David", "Rahul"],
        "manager": ["Meera", "Meera", "Arjun", "Arjun", "Meera"]
    })
else:
    uploaded = st.file_uploader("Upload Customer CSV", type=["csv"])
    if uploaded is None:
        st.stop()
    df = pd.read_csv(uploaded)

# =============================
# HEALTH ENGINE
# =============================

def calc_health(r):
    login = min(r["logins_last_30_days"] * 2, 40)
    penalty = min(r["support_tickets"] * 4, 25)
    revenue = min(r["plan_value"]/100, 35)
    return max(min(login + revenue - penalty, 100),5)

df["health_score"] = df.apply(calc_health, axis=1)

def risk(s):
    if s < 40: return "High Risk"
    elif s < 70: return "Medium Risk"
    return "Low Risk"

df["risk_level"] = df["health_score"].apply(risk)

# =============================
# OVERVIEW + AI SIDE BY SIDE
# =============================

left, right = st.columns([3,3])

with left:
    st.subheader("Customer Overview")

    if st.session_state.user_type == "demo":

        customer_to_owner = dict(zip(df["customer_name"], df["owner"]))
        owner_to_customers = df.groupby("owner")["customer_name"].apply(list).to_dict()

        owners = sorted(df["owner"].unique())
        selected_owner = st.selectbox("Select CSM", owners)

        customer_list = owner_to_customers[selected_owner]
        selected = st.selectbox("Select Account", customer_list)

        actual_owner = customer_to_owner[selected]
        if selected_owner != actual_owner:
            selected_owner = actual_owner

        row = df[df["customer_name"] == selected].iloc[0]

        st.markdown(f"### Owner: {row['owner']} | Manager: {row['manager']}")

    else:
        selected = st.selectbox("Select Account", df["customer_name"])
        row = df[df["customer_name"] == selected].iloc[0]

    st.dataframe(
        df[["customer_name","health_score","risk_level"]],
        use_container_width=True
    )

with right:
    st.subheader("AI Executive Summary")

    if st.session_state.user_type == "demo":
        st.info("🔒 Upgrade to Premium to unlock AI Executive Summary and Recommended Actions.")
    else:
        prompt = f"""
        Customer: {selected}
        Health Score: {row['health_score']}
        Risk Level: {row['risk_level']}
        Plan Value: {row['plan_value']}

        Provide executive summary and recommended actions.
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            }
        )

        st.write(response.json()["response"])

# =============================
# WEEK VIEW
# =============================

st.markdown("---")

if selected not in st.session_state.health_history:
    base = row["health_score"]
    st.session_state.health_history[selected] = [
        max(min(base + np.random.randint(-8,8),100),5) for _ in range(6)
    ]

week = st.selectbox("Select Week", [f"Week {i}" for i in range(1,7)])
idx = int(week.split()[1]) - 1
st.metric("Health Score", st.session_state.health_history[selected][idx])

# =============================
# TASK TRACKER
# =============================

st.markdown("---")
st.subheader("Task Tracker")

with st.form("task_form", clear_on_submit=True):
    task_type = st.selectbox("Task Type",
        ["Recovery Plan","Training","Escalation","Renewal","Upsell","Enablement","Other"]
    )
    notes = st.text_input("Notes")
    due = st.date_input("Due Date", value=date.today())
    submit = st.form_submit_button("Create Task")

    if submit:
        task_id = f"TASK-{st.session_state.task_counter:04d}"
        st.session_state.task_counter += 1

        entry = {
            "Task ID": task_id,
            "Task Type": task_type,
            "Notes": notes,
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Due Date": due.strftime("%Y-%m-%d")
        }

        st.session_state.task_log.setdefault(selected, []).append(entry)
        st.success(f"{task_id} created.")

if selected in st.session_state.task_log:

    header = st.columns([1.5,2,3,2,2,2])
    header[0].markdown("**Task ID**")
    header[1].markdown("**Task Type**")
    header[2].markdown("**Notes**")
    header[3].markdown("**Created**")
    header[4].markdown("**Due Date**")
    header[5].markdown("**SLA**")

    for t in st.session_state.task_log[selected]:

        cols = st.columns([1.5,2,3,2,2,2])
        cols[0].write(t["Task ID"])
        cols[1].write(t["Task Type"])
        cols[2].write(t["Notes"])
        cols[3].write(t["Created"])
        cols[4].write(t["Due Date"])

        due_date = datetime.strptime(t["Due Date"], "%Y-%m-%d").date()
        today = date.today()

        if due_date < today:
            cols[5].write("🔴 Overdue")
        elif due_date <= today + timedelta(days=2):
            cols[5].write("🟡 Reminder")
        else:
            cols[5].write("🔵 On Track")

else:
    st.info("No tasks created yet.")