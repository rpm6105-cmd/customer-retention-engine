import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
import plotly.express as px
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

# =============================
# COOL SAAS UI THEME
# =============================

st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #F3F6FA;
    color: #1F2937;
}

/* Headings */
h1, h2, h3, h4 {
    color: #1E293B;
    font-weight: 600;
}

/* Labels */
label {
    color: #475569 !important;
    font-weight: 500;
}

/* Buttons */
button {
    background-color: #2563EB !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}
button:hover {
    background-color: #1D4ED8 !important;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 18px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

/* Fix DataFrame dark issue */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}
[data-testid="stDataFrame"] table {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}

</style>
""", unsafe_allow_html=True)

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

    st.markdown("<h1 style='text-align:center;'>Customer Retention & Growth Engine</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Demo Access")
        demo_user = st.text_input("Username", key="demo_user")
        demo_pass = st.text_input("Password", type="password", key="demo_password")

        if st.button("Login Demo"):
            if demo_user.lower() == "freeuser" and demo_pass == "123456":
                st.session_state.logged_in = True
                st.session_state.user_type = "demo"
                st.session_state.user_name = "Freeuser"
                st.rerun()
            else:
                st.error("Invalid Demo Credentials")

    with col2:
        st.subheader("📂 Use My CSV (Premium)")
        option = st.radio("Select", ["Login", "Sign Up"], key="premium_option")

        if option == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="premium_password")

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
            company = st.text_input("Company", key="signup_company")
            email = st.text_input("Email", key="signup_email")
            place = st.text_input("Place", key="signup_place")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

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
# HEADER
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
# DATA
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
# HEALTH
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
# OVERVIEW
# =============================

st.subheader("Customer Overview")

selected_customer = st.selectbox("Select Customer", df["customer_name"])
st.dataframe(
    df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]],
    use_container_width=True
)

# =============================
# TASK TRACKER (UNCHANGED)
# =============================

st.subheader("Task Tracker")

if selected_customer not in st.session_state.task_log:
    st.session_state.task_log[selected_customer] = []

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

        st.session_state.task_log[selected_customer].append(task)
        st.success("Task Created")

tasks = st.session_state.task_log[selected_customer]

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