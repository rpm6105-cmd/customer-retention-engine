import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
import plotly.express as px
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

# =============================
# UI POLISH
# =============================

st.markdown("""
<style>
.stApp {
    background-color: #F4F6F9;
}
h1, h2, h3 {
    color: #1F2937;
}
div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
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
        demo_user = st.text_input("Username")
        demo_pass = st.text_input("Password", type="password")

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
        option = st.radio("Select", ["Login", "Sign Up"])

        if option == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

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
            name = st.text_input("Name")
            company = st.text_input("Company")
            email = st.text_input("Email")
            place = st.text_input("Place")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")

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
# CUSTOMER & CSM SELECTION
# =============================

st.subheader("Customer Overview")

col1, col2 = st.columns(2)

with col1:
    selected_customer = st.selectbox("Select Customer", df["customer_name"])

with col2:
    if "owner" in df.columns:
        selected_csm = st.selectbox("Select CSM", df["owner"].unique())
    else:
        selected_csm = None

if selected_csm:
    df_filtered = df[df["owner"] == selected_csm]
else:
    df_filtered = df

st.dataframe(df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]])

# =============================
# HEALTH CHART
# =============================

st.subheader("Health Score Comparison")

fig = px.bar(
    df_filtered,
    x="customer_name",
    y="health_score",
    color="risk_level",
    color_discrete_map={
        "High Risk": "#EF4444",
        "Medium Risk": "#F59E0B",
        "Low Risk": "#10B981"
    }
)

fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig, use_container_width=True)

# =============================
# AI SUMMARY
# =============================

st.subheader("AI Executive Summary")

row = df[df["customer_name"] == selected_customer].iloc[0]

if st.session_state.user_type == "demo":
    st.info("🔒 Upgrade to Premium to unlock AI Executive Summary.")
else:
    try:
        prompt = f"""
        Customer: {selected_customer}
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

st.markdown("---")

# =============================
# CS INTELLIGENCE TOOLS
# =============================

st.header("Customer Success Intelligence Tools")

tool_tab = st.selectbox("Select Tool",
                        ["Renewal Forecast",
                         "GRR Exposure",
                         "Churn Impact Simulator",
                         "CSM Workload"])

if tool_tab == "Renewal Forecast":
    renewal_rate = st.slider("Expected Renewal Rate (%)", 50, 100, 85)
    total_revenue = df["plan_value"].sum()
    projected_revenue = total_revenue * (renewal_rate / 100)
    st.metric("Projected Renewal Revenue", f"${round(projected_revenue, 2)}")

elif tool_tab == "GRR Exposure":
    high_risk_revenue = df[df["risk_level"] == "High Risk"]["plan_value"].sum()
    total_revenue = df["plan_value"].sum()
    exposure = (high_risk_revenue / total_revenue) * 100 if total_revenue > 0 else 0
    st.metric("Revenue at Risk %", f"{round(exposure,1)}%")

elif tool_tab == "Churn Impact Simulator":
    churn_pct = st.slider("If X% of High-Risk Customers Churn", 0, 100, 30)
    high_risk_revenue = df[df["risk_level"] == "High Risk"]["plan_value"].sum()
    potential_loss = high_risk_revenue * (churn_pct / 100)
    st.metric("Potential Revenue Loss", f"${round(potential_loss,2)}")

elif tool_tab == "CSM Workload":
    if "owner" in df.columns:
        workload = df.groupby("owner")["customer_name"].count().reset_index()
        workload.columns = ["CSM", "Assigned Accounts"]

        fig2 = px.bar(workload, x="CSM", y="Assigned Accounts", color="CSM")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Upload dataset with owner column.")