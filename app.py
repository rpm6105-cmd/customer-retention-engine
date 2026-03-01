import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

# =============================
# DATABASE
# =============================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    company TEXT,
    email TEXT PRIMARY KEY,
    place TEXT,
    password TEXT
)
""")
conn.commit()

# =============================
# SESSION STATE
# =============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "task_log" not in st.session_state:
    st.session_state.task_log = {}

# =============================
# LOGIN PAGE
# =============================

if not st.session_state.logged_in:

    st.markdown("""
    <h1 style='text-align:center;'>Customer Retention & Growth Engine</h1>
    <h4 style='text-align:center;color:gray;'>Revenue Risk Intelligence + Operational Execution</h4>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # DEMO LOGIN
    with col1:
        st.subheader("🚀 Demo Access")

        demo_user = st.text_input("Username", key="demo_user")
        demo_pass = st.text_input("Password", type="password", key="demo_pass")

        if st.button("Login Demo"):
            if demo_user.lower() == "freeuser" and demo_pass == "123456":
                st.session_state.logged_in = True
                st.session_state.user_type = "demo"
                st.session_state.user_name = "Freeuser"
                st.rerun()
            else:
                st.error("Invalid Demo Credentials")

    # PREMIUM LOGIN
    with col2:
        st.subheader("📂 Use My CSV (Premium)")

        option = st.radio("Select", ["Login", "Sign Up"], key="premium_option")

        if option == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login Premium"):
                c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
                user = c.fetchone()

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "premium"
                    st.session_state.user_name = user[0]
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

        else:
            name = st.text_input("Name", key="signup_name")
            company = st.text_input("Company Name", key="signup_company")
            email = st.text_input("Email", key="signup_email")
            place = st.text_input("Place", key="signup_place")
            password = st.text_input("Password", type="password", key="signup_pass")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

            if st.button("Create Account"):
                if password != confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        c.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                                  (name, company, email, place, password))
                        conn.commit()
                        st.success("Account created successfully. Please login.")
                    except:
                        st.error("Email already registered")

    st.stop()

# =============================
# APP HEADER
# =============================

colA, colB = st.columns([8, 1])

with colA:
    st.title("Customer Retention & Growth Engine")

with colB:
    st.write(f"👤 {st.session_state.user_name}")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.markdown("---")

# =============================
# LOAD DATA
# =============================

if st.session_state.user_type == "demo":

    df = pd.DataFrame({
        "customer_name": ["Alpha", "Beta", "Gamma", "Delta", "Omega"],
        "owner": ["Aisha", "Rahul", "Aisha", "David", "Rahul"],
        "manager": ["Meera", "Meera", "Arjun", "Arjun", "Meera"],
        "logins_last_30_days": [25, 5, 18, 3, 30],
        "support_tickets": [2, 7, 3, 8, 1],
        "plan_value": [1500, 900, 2000, 800, 3000]
    })

else:
    uploaded = st.file_uploader("Upload Customer CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        df["owner"] = "Assigned CSM"
        df["manager"] = "Manager"
    else:
        st.info("Upload CSV to continue.")
        st.stop()

# =============================
# HEALTH LOGIC
# =============================

def health_calc(row):
    login_score = min(row["logins_last_30_days"] * 2, 40)
    ticket_penalty = min(row["support_tickets"] * 4, 25)
    revenue_score = min(row["plan_value"] / 100, 35)
    score = login_score + revenue_score - ticket_penalty
    return max(min(score, 100), 5)

df["health_score"] = df.apply(health_calc, axis=1)

def risk_flag(score):
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    else:
        return "Low Risk"

df["risk_level"] = df["health_score"].apply(risk_flag)
df["priority_score"] = (100 - df["health_score"]) + (df["plan_value"] / 100)

# =============================
# MAIN DASHBOARD
# =============================

left, right = st.columns([2, 1])

with left:
    st.subheader("Customer Overview")
    st.dataframe(df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]])

    selected = st.selectbox("Select Account", df["customer_name"])
    row = df[df["customer_name"] == selected].iloc[0]

    st.write(f"Owner: {row['owner']} | Manager: {row['manager']}")

with right:
    st.subheader("AI Executive Summary")

    if st.session_state.user_type == "demo":
        st.info("🔒 Upgrade to Premium to unlock AI Executive Summary.")
    else:
        try:
            prompt = f"""
            Customer: {selected}
            Health Score: {row['health_score']}
            Risk Level: {row['risk_level']}
            Plan Value: {row['plan_value']}
            Provide executive summary and recommended actions.
            """

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.1", "prompt": prompt, "stream": False},
                timeout=5
            )

            st.write(response.json()["response"])

        except:
            st.warning("⚠ AI only works locally with Ollama running.")

st.markdown("---")

# =============================
# TASK TRACKER
# =============================

st.subheader("Task Tracker")

if selected not in st.session_state.task_log:
    st.session_state.task_log[selected] = []

with st.form("task_form", clear_on_submit=True):
    task_type = st.selectbox("Task Type",
                             ["Recovery Plan", "Product Training",
                              "Renewal Call", "Upsell Proposal",
                              "Feature Enablement", "Other"])
    notes = st.text_input("Notes")
    due = st.date_input("Due Date")

    submitted = st.form_submit_button("Create Task")

    if submitted:
        task_id = str(uuid.uuid4())[:8]
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        task = {
            "Task ID": task_id,
            "Task Type": task_type,
            "Notes": notes,
            "Created": created_time,
            "Due Date": due.strftime("%Y-%m-%d")
        }

        st.session_state.task_log[selected].append(task)
        st.success("Task Created")

tasks = st.session_state.task_log[selected]

if tasks:
    task_df = pd.DataFrame(tasks)

    def sla_status(due):
        today = date.today()
        due_date = datetime.strptime(due, "%Y-%m-%d").date()
        if due_date < today:
            return "Overdue"
        elif due_date == today:
            return "Due Today"
        elif due_date <= today + timedelta(days=2):
            return "Reminder Soon"
        else:
            return "On Track"

    task_df["SLA"] = task_df["Due Date"].apply(sla_status)
    st.dataframe(task_df, use_container_width=True)

else:
    st.info("No tasks yet.")