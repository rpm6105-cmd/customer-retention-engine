import streamlit as st
import pandas as pd
import sqlite3
import uuid
from html import escape
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

# =============================
# COOL SAAS UI THEME
# =============================

st.markdown("""
<style>
:root {
    --bg-start: #f7f4ec;
    --bg-end: #e9f0f7;
    --surface: #ffffff;
    --surface-soft: #f8fafc;
    --ink: #152238;
    --muted: #516077;
    --line: #d6deea;
    --brand: #0f766e;
    --brand-hover: #0b5f5a;
    --danger: #b42318;
    --danger-hover: #8f1f17;
}

/* Background */
.stApp {
    background:
        radial-gradient(circle at 10% 10%, #fff8e8 0%, transparent 30%),
        radial-gradient(circle at 90% 0%, #dff1ff 0%, transparent 34%),
        linear-gradient(160deg, var(--bg-start), var(--bg-end));
    color: var(--ink);
}

/* Headings */
h1, h2, h3, h4 {
    color: var(--ink);
    font-weight: 700;
    letter-spacing: -0.01em;
}

h3 {
    color: #0f4c5c !important;
}

/* Labels */
label {
    color: var(--muted) !important;
    font-weight: 600;
}

/* Main content card */
.block-container {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding-top: 2.2rem;
    padding-bottom: 2.2rem;
    box-shadow: 0 24px 48px rgba(15, 35, 62, 0.08);
}

/* Buttons (danger/primary) */
button[kind="primary"] {
    background-color: #b42318 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #b42318 !important;
    font-weight: 600 !important;
}
button[kind="primary"]:hover {
    background-color: #8f1f17 !important;
    border-color: #8f1f17 !important;
}

/* Buttons (default/secondary) */
.stButton > button, .stDownloadButton > button, .stForm button, button[kind="secondary"] {
    background-color: var(--brand) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid var(--brand) !important;
    font-weight: 600 !important;
}
button[kind="secondary"]:hover, .stButton > button:hover, .stDownloadButton > button:hover, .stForm button:hover {
    background-color: var(--brand-hover) !important;
    border-color: var(--brand-hover) !important;
}

/* Ensure all Streamlit button variants keep readable text */
.stFileUploader button:hover {
    background-color: #0b5f5a !important;
    border-color: #0b5f5a !important;
    color: #ffffff !important;
}

/* Streamlit sometimes colors inner label nodes separately; force white labels */
.stButton > button *,
.stDownloadButton > button *,
.stFileUploader button *,
.stForm button *,
button[kind="primary"] *,
button[kind="secondary"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.danger-zone {
    margin-top: 10px;
    margin-bottom: 8px;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid #fecaca;
    background: #fef2f2;
    color: #7f1d1d;
    font-weight: 600;
}

/* Keep disabled buttons readable */
button:disabled,
button:disabled * {
    color: #d1d5db !important;
}


/* Metric cards */
div[data-testid="metric-container"] {
    background: var(--surface);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid var(--line);
    box-shadow: 0 8px 18px rgba(20, 35, 58, 0.06);
}

/* Forms and expanders */
div[data-testid="stForm"], div[data-testid="stExpander"] {
    background: var(--surface-soft);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 14px;
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: #ffffff !important;
    color: var(--ink) !important;
    border-color: var(--line) !important;
}

/* Ensure typed text is dark in all input fields */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] input {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}

/* Placeholder color */
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* Date input */
div[data-testid="stDateInput"] input {
    background: #ffffff !important;
    color: var(--ink) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    border: 1px solid var(--line);
}
[data-testid="stDataFrame"] table {
    background-color: #FFFFFF !important;
    color: var(--ink) !important;
}

/* Radio text fix */
div[role="radiogroup"] label p {
    color: var(--ink) !important;
}

/* Checkbox label readability */
div[data-testid="stCheckbox"] label p {
    color: var(--ink) !important;
    font-weight: 600 !important;
}

/* Checkbox box style: white default, black when checked */
div[data-testid="stCheckbox"] [role="checkbox"] {
    background: #ffffff !important;
    border: 1.5px solid #111827 !important;
    border-radius: 4px !important;
}

div[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] {
    background: #111827 !important;
    border-color: #111827 !important;
}

div[data-testid="stCheckbox"] [role="checkbox"] svg {
    fill: #111827 !important;
}

div[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] svg {
    fill: #ffffff !important;
}

/* Customer overview table and risk badges */
.overview-table-wrap {
    margin-top: 8px;
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    background: #ffffff;
}

.overview-table {
    width: 100%;
    border-collapse: collapse;
}

.overview-table th, .overview-table td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #ebeff5;
    color: #1f2937;
}

.overview-table th {
    background: #f3f7fb;
    color: #0f4c5c;
    font-weight: 700;
}

.risk-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

.risk-high {
    background: #fee2e2;
    color: #b42318;
}

.risk-medium {
    background: #fef3c7;
    color: #92400e;
}

.risk-low {
    background: #dcfce7;
    color: #166534;
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

c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    user_key TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    due_date TEXT NOT NULL
)
""")
conn.commit()


def validate_and_prepare_customer_df(raw_df: pd.DataFrame):
    required_cols = ["customer_name", "logins_last_30_days", "support_tickets", "plan_value"]
    missing = [col for col in required_cols if col not in raw_df.columns]
    if missing:
        return None, f"Missing required columns: {', '.join(missing)}"

    df_clean = raw_df.copy()
    df_clean = df_clean[required_cols]
    df_clean = df_clean.dropna(subset=["customer_name"])
    df_clean["customer_name"] = df_clean["customer_name"].astype(str).str.strip()
    df_clean = df_clean[df_clean["customer_name"] != ""]

    numeric_cols = ["logins_last_30_days", "support_tickets", "plan_value"]
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    invalid_numeric = df_clean[numeric_cols].isna().any(axis=1).sum()
    if invalid_numeric > 0:
        return None, (
            "Some rows have invalid numbers in "
            f"{', '.join(numeric_cols)}. Fix the CSV and upload again."
        )

    if len(df_clean) == 0:
        return None, "CSV has no valid customer rows after cleaning."

    df_clean["owner"] = "Assigned CSM"
    df_clean["manager"] = "Manager"
    return df_clean, None


def get_user_key() -> str:
    return st.session_state.get("user_email") or f"demo:{st.session_state.get('user_name', 'freeuser')}"


def load_tasks_for_customer(user_key: str, customer_name: str):
    rows = c.execute(
        """
        SELECT task_id, task_type, notes, created_at, due_date
        FROM tasks
        WHERE user_key = ? AND customer_name = ?
        ORDER BY due_date ASC, created_at DESC
        """,
        (user_key, customer_name),
    ).fetchall()

    return [
        {
            "Task ID": row[0],
            "Task Type": row[1],
            "Notes": row[2],
            "Created": row[3],
            "Due Date": row[4],
        }
        for row in rows
    ]


def create_task(user_key: str, customer_name: str, task_type: str, notes: str, due_date: str):
    task_id = str(uuid.uuid4())[:8]
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute(
        """
        INSERT INTO tasks (task_id, user_key, customer_name, task_type, notes, created_at, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, user_key, customer_name, task_type, notes, created_time, due_date),
    )
    conn.commit()


def update_task(task_id: str, user_key: str, customer_name: str, task_type: str, notes: str, due_date: str):
    c.execute(
        """
        UPDATE tasks
        SET task_type = ?, notes = ?, due_date = ?
        WHERE task_id = ? AND user_key = ? AND customer_name = ?
        """,
        (task_type, notes, due_date, task_id, user_key, customer_name),
    )
    conn.commit()


def delete_task(task_id: str, user_key: str, customer_name: str):
    c.execute(
        """
        DELETE FROM tasks
        WHERE task_id = ? AND user_key = ? AND customer_name = ?
        """,
        (task_id, user_key, customer_name),
    )
    conn.commit()


def render_customer_overview_table(df_input: pd.DataFrame):
    rows = []
    for _, row in df_input.sort_values(by="priority_score", ascending=False).iterrows():
        risk = str(row["risk_level"])
        if risk == "High Risk":
            badge_class = "risk-badge risk-high"
        elif risk == "Medium Risk":
            badge_class = "risk-badge risk-medium"
        else:
            badge_class = "risk-badge risk-low"

        rows.append(
            "<tr>"
            f"<td>{escape(str(row['customer_name']))}</td>"
            f"<td>{escape(str(row['owner']))}</td>"
            f"<td>{float(row['health_score']):.1f}</td>"
            f"<td><span class=\"{badge_class}\">{escape(risk)}</span></td>"
            f"<td>{float(row['priority_score']):.1f}</td>"
            "</tr>"
        )

    header = (
        "<thead><tr>"
        "<th>Customer</th>"
        "<th>Owner</th>"
        "<th>Health Score</th>"
        "<th>Risk Level</th>"
        "<th>Priority Score</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='overview-table-wrap'><table class='overview-table'>"
        + header
        + body
        + "</table></div>",
        unsafe_allow_html=True,
    )


def render_task_table(df_input: pd.DataFrame):
    rows = []
    for _, row in df_input.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(row['Task ID']))}</td>"
            f"<td>{escape(str(row['Task Type']))}</td>"
            f"<td>{escape(str(row['Notes'] or ''))}</td>"
            f"<td>{escape(str(row['Created']))}</td>"
            f"<td>{escape(str(row['Due Date']))}</td>"
            f"<td>{escape(str(row['SLA']))}</td>"
            "</tr>"
        )

    header = (
        "<thead><tr>"
        "<th>Task ID</th>"
        "<th>Task Type</th>"
        "<th>Notes</th>"
        "<th>Created</th>"
        "<th>Due Date</th>"
        "<th>SLA</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='overview-table-wrap'><table class='overview-table'>"
        + header
        + body
        + "</table></div>",
        unsafe_allow_html=True,
    )


# =============================
# SESSION STATE
# =============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

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
                st.session_state.user_email = "demo@local"
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
                    st.session_state.user_email = user[2]
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
        raw_df = pd.read_csv(uploaded)
        df, error_msg = validate_and_prepare_customer_df(raw_df)
        if error_msg:
            st.error(error_msg)
            st.stop()
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
render_customer_overview_table(
    df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]]
)

# =============================
# TASK TRACKER (UNCHANGED)
# =============================

st.subheader("Task Tracker")
user_key = get_user_key()

with st.form("task_form", clear_on_submit=True):
    task_type = st.selectbox("Task Type",
                             ["Recovery Plan", "Product Training",
                              "Renewal Call", "Upsell Proposal",
                              "Feature Enablement", "Other"])
    notes = st.text_input("Notes")
    due = st.date_input("Due Date")

    submitted = st.form_submit_button("Create Task", type="secondary")

    if submitted:
        create_task(
            user_key=user_key,
            customer_name=selected_customer,
            task_type=task_type,
            notes=notes.strip(),
            due_date=due.strftime("%Y-%m-%d"),
        )
        st.success("Task Created and saved")

tasks = load_tasks_for_customer(user_key, selected_customer)

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
    render_task_table(task_df[["Task ID", "Task Type", "Notes", "Created", "Due Date", "SLA"]])

    st.markdown("### Manage Existing Task")
    task_options = list(range(len(tasks)))
    selected_task_index = st.selectbox(
        "Select task to edit/delete",
        task_options,
        format_func=lambda i: tasks[i]["Task Type"],
    )
    selected_task = tasks[selected_task_index]

    current_due = datetime.strptime(selected_task["Due Date"], "%Y-%m-%d").date()

    with st.form("edit_task_form"):
        edit_task_type = st.selectbox(
            "Task Type (Edit)",
            ["Recovery Plan", "Product Training", "Renewal Call", "Upsell Proposal", "Feature Enablement", "Other"],
            index=["Recovery Plan", "Product Training", "Renewal Call", "Upsell Proposal", "Feature Enablement", "Other"].index(
                selected_task["Task Type"]
            ) if selected_task["Task Type"] in ["Recovery Plan", "Product Training", "Renewal Call", "Upsell Proposal", "Feature Enablement", "Other"] else 5,
        )
        edit_notes = st.text_input("Notes (Edit)", value=selected_task["Notes"] or "")
        edit_due = st.date_input("Due Date (Edit)", value=current_due)
        delete_confirm = st.checkbox("I confirm I want to permanently delete this task")

        st.markdown("<div class='danger-zone'>Danger Zone: deleting a task is permanent.</div>", unsafe_allow_html=True)

        col_upd, col_del = st.columns(2)
        update_submitted = col_upd.form_submit_button("Update Task", type="secondary")
        delete_submitted = col_del.form_submit_button("Delete Task", type="primary")

        if update_submitted:
            update_task(
                task_id=selected_task["Task ID"],
                user_key=user_key,
                customer_name=selected_customer,
                task_type=edit_task_type,
                notes=edit_notes.strip(),
                due_date=edit_due.strftime("%Y-%m-%d"),
            )
            st.success("Task updated")
            st.rerun()

        if delete_submitted:
            if not delete_confirm:
                st.error("Please check the delete confirmation box before deleting.")
            else:
                delete_task(
                    task_id=selected_task["Task ID"],
                    user_key=user_key,
                    customer_name=selected_customer,
                )
                st.success("Task deleted")
                st.rerun()
else:
    st.info("No tasks yet.")
