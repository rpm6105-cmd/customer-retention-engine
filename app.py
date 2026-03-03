import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
import hashlib
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

.ai-summary-card {
    margin-top: 10px;
    padding: 14px 16px;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: #ffffff;
    color: #1f2937;
    line-height: 1.5;
}

.ai-blur {
    filter: blur(5px);
    user-select: none;
}

.upgrade-note {
    margin-top: 8px;
    font-weight: 700;
    color: #9a3412;
}

.premium-hero {
    margin-top: 10px;
    margin-bottom: 12px;
    padding: 16px 18px;
    border-radius: 14px;
    border: 1px solid #bfd8f3;
    background: linear-gradient(130deg, #0f2a43 0%, #0f766e 45%, #1d4ed8 100%);
    color: #f8fbff;
}

.premium-hero-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.2px;
}

.premium-hero-sub {
    margin-top: 6px;
    opacity: 0.92;
}

.premium-chip-row {
    margin-top: 10px;
}

.premium-chip {
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Remove Streamlit top black header area */
header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
}

/* Uploader text/readability */
section[data-testid="stFileUploader"] small,
section[data-testid="stFileUploader"] span,
section[data-testid="stFileUploader"] p,
div[data-testid="stFileUploaderFileName"] {
    color: #0f172a !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

.premium-kpi {
    border: 1px solid #d8e8fb;
    border-radius: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #f3f9ff 100%);
    padding: 12px 14px;
    margin-bottom: 8px;
}

.premium-kpi-label {
    color: #35506b;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.premium-kpi-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
    margin-top: 2px;
}

.suggestion-card {
    margin-top: 10px;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid #c9ddf5;
    background: #f8fbff;
}

.suggestion-title {
    font-weight: 800;
    color: #0f4c5c;
    margin-bottom: 6px;
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

/* Password visibility icon contrast */
div[data-baseweb="input"] button,
div[data-baseweb="base-input"] button {
    opacity: 1 !important;
    color: #0f4c5c !important;
}
div[data-baseweb="input"] button svg,
div[data-baseweb="base-input"] button svg {
    fill: #0f4c5c !important;
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

    df_clean = assign_csm_fields(df_clean)
    return df_clean, None


def enrich_contract_fields(df_input: pd.DataFrame) -> pd.DataFrame:
    df_enriched = df_input.copy()
    hashes = df_enriched["customer_name"].astype(str).apply(lambda x: int(hashlib.sha256(x.encode("utf-8")).hexdigest(), 16))

    purchase_offsets = hashes % 720
    term_days = (hashes // 7 % 365) + 180

    purchase_dates = [date.today() - timedelta(days=int(v)) for v in purchase_offsets]
    renewal_dates = [purchase_dates[i] + timedelta(days=int(term_days.iloc[i])) for i in range(len(df_enriched))]
    auto_renew_opt_out = [bool((h // 11) % 2) for h in hashes]

    df_enriched["purchase_date"] = [d.strftime("%Y-%m-%d") for d in purchase_dates]
    df_enriched["renewal_date"] = [d.strftime("%Y-%m-%d") for d in renewal_dates]
    df_enriched["auto_renew_opt_out"] = auto_renew_opt_out
    return df_enriched


def assign_csm_fields(df_input: pd.DataFrame) -> pd.DataFrame:
    owners = ["Aisha", "Rahul", "David", "Nina", "Karthik", "Meera"]
    managers = ["Arjun", "Meera", "Sonia"]
    hashes = df_input["customer_name"].astype(str).apply(lambda x: int(hashlib.sha256(x.encode("utf-8")).hexdigest(), 16))

    df_assigned = df_input.copy()
    df_assigned["owner"] = [owners[h % len(owners)] for h in hashes]
    df_assigned["manager"] = [managers[(h // 5) % len(managers)] for h in hashes]
    return df_assigned


def recommend_options_for_row(row: pd.Series):
    risk = row.get("risk_level", "")
    health = float(row.get("health_score", 0))
    tickets = float(row.get("support_tickets", 0))
    plan = float(row.get("plan_value", 0))
    auto_opt_out = bool(row.get("auto_renew_opt_out", False))

    discount_score = 25
    upsell_score = 20
    enablement_score = 25

    if risk == "High Risk":
        discount_score += 40
        enablement_score += 25
        upsell_score -= 10
    elif risk == "Medium Risk":
        discount_score += 12
        enablement_score += 30
        upsell_score += 5
    else:
        upsell_score += 35
        enablement_score += 10

    if auto_opt_out:
        discount_score += 12
        enablement_score += 5

    if tickets >= 6:
        enablement_score += 20
        discount_score += 8
    elif tickets <= 2:
        upsell_score += 14

    if health >= 75:
        upsell_score += 18
    elif health <= 45:
        discount_score += 12
        enablement_score += 10

    if plan >= 1800:
        discount_score += 8
        upsell_score += 10

    renewal_raw = str(row.get("renewal_date", ""))
    try:
        renewal_dt = datetime.strptime(renewal_raw, "%Y-%m-%d").date()
    except ValueError:
        renewal_dt = date.today() + timedelta(days=90)

    option_deadlines = {
        "Upsell": renewal_dt - timedelta(days=75),
        "Discount Save": renewal_dt - timedelta(days=45),
        "Enablement Plan": renewal_dt - timedelta(days=60),
    }

    def deadline_text(strategy: str) -> str:
        act_before = option_deadlines[strategy]
        days_left = (act_before - date.today()).days
        return f"{act_before.strftime('%Y-%m-%d')} ({days_left} days left)"

    options = [
        {
            "strategy": "Upsell",
            "impact_score": int(max(0, min(100, upsell_score))),
            "play": "Propose premium tier + add-on bundle aligned to current usage depth.",
            "act_before": deadline_text("Upsell"),
        },
        {
            "strategy": "Discount Save",
            "impact_score": int(max(0, min(100, discount_score))),
            "play": "Offer targeted renewal discount tied to adoption milestones and auto-renew recovery.",
            "act_before": deadline_text("Discount Save"),
        },
        {
            "strategy": "Enablement Plan",
            "impact_score": int(max(0, min(100, enablement_score))),
            "play": "Run 30-day success plan with weekly training and executive check-ins.",
            "act_before": deadline_text("Enablement Plan"),
        },
    ]
    return sorted(options, key=lambda x: x["impact_score"], reverse=True)


def recommend_action_for_row(row: pd.Series) -> str:
    options = recommend_options_for_row(row)
    top = options[0]
    return f"{top['strategy']}: {top['play']}"


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


def build_ai_summary(df_input: pd.DataFrame, selected_row: pd.Series | None = None) -> str:
    if selected_row is None:
        selected_row = df_input.sort_values("priority_score", ascending=False).iloc[0]

    prompt = f"""
Act as a VP of Customer Success.
Write a concise 6-8 sentence account strategy summary.

Selected Account: {selected_row['customer_name']}
Health Score: {float(selected_row['health_score']):.1f}
Risk Level: {selected_row['risk_level']}
Support Tickets (30d): {int(selected_row['support_tickets'])}
Plan Value: {float(selected_row['plan_value']):.0f}
Auto Renew Opt-Out: {bool(selected_row['auto_renew_opt_out'])}
Renewal Date: {selected_row['renewal_date']}

Give: (1) top risk, (2) top opportunity, (3) immediate 30-day action plan.
Do not ask questions.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        text = (payload.get("response") or "").strip()
        if text:
            return text
    except Exception:
        pass

    options = recommend_options_for_row(selected_row)
    return (
        f"{selected_row['customer_name']} is currently tagged as {selected_row['risk_level']} with "
        f"a health score of {float(selected_row['health_score']):.1f}. The primary risk is renewal volatility "
        f"driven by support pressure and adoption depth. The best immediate strategy is {options[0]['strategy']}: "
        f"{options[0]['play']} Secondary option: {options[1]['strategy']} ({options[1]['impact_score']}/100 impact). "
        f"Third option: {options[2]['strategy']} ({options[2]['impact_score']}/100 impact). "
        "Execute weekly checkpoints for 30 days and track risk movement before renewal."
    )


def render_premium_command_center(df_input: pd.DataFrame, selected_row: pd.Series):
    health = float(selected_row["health_score"])
    tickets = int(selected_row["support_tickets"])
    plan_value = float(selected_row["plan_value"])
    renewal_date = str(selected_row["renewal_date"])
    auto_opt_out = bool(selected_row["auto_renew_opt_out"])

    st.markdown(
        """
        <div class="premium-hero">
            <div class="premium-hero-title">Premium CX Intelligence Command Center</div>
            <div class="premium-hero-sub">Focused account strategy workspace for selected customer.</div>
            <div class="premium-chip-row">
                <span class="premium-chip">Account Strategy</span>
                <span class="premium-chip">Renewal Window</span>
                <span class="premium-chip">Retention Playbook</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Customer Health</div><div class='premium-kpi-value'>{health:.1f}</div></div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Risk Level</div><div class='premium-kpi-value'>{escape(str(selected_row['risk_level']))}</div></div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Plan Value</div><div class='premium-kpi-value'>{plan_value:,.0f}</div></div>",
        unsafe_allow_html=True,
    )
    c4.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Renewal Date</div><div class='premium-kpi-value'>{renewal_date}</div></div>",
        unsafe_allow_html=True,
    )

    options = recommend_options_for_row(selected_row)
    suggestion = recommend_action_for_row(selected_row)
    st.markdown(
        f"""
        <div class="suggestion-card">
            <div class="suggestion-title">Suggested Play For {escape(str(selected_row['customer_name']))}</div>
            <div>{escape(suggestion)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    options_df = pd.DataFrame(options)
    options_df = options_df.rename(
        columns={
            "strategy": "Strategy",
            "impact_score": "Impact Score",
            "play": "Recommended Play",
            "act_before": "Act Before",
        }
    )
    st.dataframe(options_df, use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["Focus Areas", "Renewal Lens", "Delta Insights"])

    with tab1:
        focus_rows = [
            {"Focus Area": "Product Adoption", "Signal": "Low" if health < 55 else "Healthy", "What To Do": "Drive weekly usage milestones + role-based onboarding."},
            {"Focus Area": "Support Burden", "Signal": "High" if tickets >= 5 else "Controlled", "What To Do": "Resolve top recurring ticket themes before renewal cycle."},
            {"Focus Area": "Renewal Commitment", "Signal": "At Risk" if auto_opt_out else "Stable", "What To Do": "Confirm value recap and lock commercial terms early."},
        ]
        st.dataframe(pd.DataFrame(focus_rows), use_container_width=True)

    with tab2:
        c5, c6, c7 = st.columns(3)
        with c5:
            st.metric("Support Tickets (30d)", f"{tickets}")
        with c6:
            st.metric("Auto Renew Opt-Out", "Yes" if auto_opt_out else "No")
        with c7:
            st.metric("Primary Strategy", options[0]["strategy"])
        st.caption("Use 'Act Before' dates in strategy options to schedule interventions.")

    with tab3:
        previous_df = get_previous_snapshot_df()
        if previous_df is None or previous_df.empty:
            st.info("Upload a newer CSV later to unlock change tracking vs previous upload.")
        else:
            current_avg_health = float(df_input["health_score"].mean()) if len(df_input) else 0.0
            previous_avg_health = float(previous_df["health_score"].mean()) if len(previous_df) else 0.0
            health_delta = current_avg_health - previous_avg_health

            current_high = int((df_input["risk_level"] == "High Risk").sum())
            previous_high = int((previous_df["risk_level"] == "High Risk").sum())
            high_delta = current_high - previous_high

            current_risk_revenue = float(df_input[df_input["risk_level"] == "High Risk"]["plan_value"].sum())
            previous_risk_revenue = float(previous_df[previous_df["risk_level"] == "High Risk"]["plan_value"].sum())
            risk_rev_delta = current_risk_revenue - previous_risk_revenue

            d1, d2, d3 = st.columns(3)
            d1.metric("Avg Health Delta", f"{health_delta:+.1f}")
            d2.metric("High Risk Delta", f"{high_delta:+d}")
            d3.metric("Revenue-at-Risk Delta", f"{risk_rev_delta:+,.0f}")

            current_key = df_input[["customer_name", "priority_score", "risk_level"]].copy()
            previous_key = previous_df[["customer_name", "priority_score", "risk_level"]].copy()
            merged = current_key.merge(previous_key, on="customer_name", how="inner", suffixes=("_current", "_prev"))
            if len(merged) > 0:
                merged["priority_delta"] = merged["priority_score_current"] - merged["priority_score_prev"]
                merged["risk_changed"] = merged["risk_level_current"] != merged["risk_level_prev"]
                movers = merged.reindex(merged["priority_delta"].abs().sort_values(ascending=False).index).head(5)
                movers = movers.rename(
                    columns={
                        "customer_name": "Account",
                        "priority_score_prev": "Prev Priority",
                        "priority_score_current": "Current Priority",
                        "priority_delta": "Priority Delta",
                        "risk_level_prev": "Prev Risk",
                        "risk_level_current": "Current Risk",
                        "risk_changed": "Risk Changed",
                    }
                )
                st.caption("Top account-level movements (current upload vs previous upload)")
                st.dataframe(
                    movers[
                        [
                            "Account",
                            "Prev Priority",
                            "Current Priority",
                            "Priority Delta",
                            "Prev Risk",
                            "Current Risk",
                            "Risk Changed",
                        ]
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No overlapping account names found between current and previous uploads.")


def snapshot_fingerprint(df_input: pd.DataFrame) -> str:
    cols = ["customer_name", "logins_last_30_days", "support_tickets", "plan_value"]
    available_cols = [c for c in cols if c in df_input.columns]
    normalized = (
        df_input[available_cols]
        .copy()
        .sort_values(by="customer_name")
        .reset_index(drop=True)
        .to_csv(index=False)
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_previous_snapshot_df():
    previous_json = st.session_state.get("previous_snapshot_json")
    if not previous_json:
        return None
    try:
        return pd.read_json(previous_json)
    except Exception:
        return None


def update_snapshot_state(df_input: pd.DataFrame):
    required_cols = ["customer_name", "health_score", "risk_level", "priority_score", "plan_value"]
    snapshot_df = df_input[required_cols].copy()
    current_fp = snapshot_fingerprint(df_input)
    last_fp = st.session_state.get("current_snapshot_fp")

    if last_fp and current_fp != last_fp and st.session_state.get("current_snapshot_json"):
        st.session_state.previous_snapshot_json = st.session_state.current_snapshot_json

    st.session_state.current_snapshot_fp = current_fp
    st.session_state.current_snapshot_json = snapshot_df.to_json()


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

if "signup_success" not in st.session_state:
    st.session_state.signup_success = None

if "force_login_view" not in st.session_state:
    st.session_state.force_login_view = False

if "current_snapshot_fp" not in st.session_state:
    st.session_state.current_snapshot_fp = None

if "current_snapshot_json" not in st.session_state:
    st.session_state.current_snapshot_json = None

if "previous_snapshot_json" not in st.session_state:
    st.session_state.previous_snapshot_json = None

if "ai_summary_for_customer" not in st.session_state:
    st.session_state.ai_summary_for_customer = None

# =============================
# LOGIN PAGE
# =============================

if not st.session_state.logged_in:

    st.markdown("<h1 style='text-align:center;'>Customer Retention & Growth Engine</h1>", unsafe_allow_html=True)
    if st.session_state.force_login_view:
        st.session_state["premium_option"] = "Login"
        st.session_state.force_login_view = False
    option = st.radio("Premium Access", ["Login", "Sign Up"], key="premium_option", horizontal=True)

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)
        st.session_state.signup_success = None

    if option == "Login":
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚀 Try Demo")
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
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="premium_password")

            if st.button("Login Premium"):
                login_email = email.strip().lower()
                login_password = password.strip()
                c.execute("SELECT * FROM users WHERE email=? AND password=?", (login_email, login_password))
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
        _, col_mid, _ = st.columns([1, 1.2, 1])
        with col_mid:
            st.subheader("📂 Use My CSV (Premium)")
            name = st.text_input("Name", key="signup_name")
            company = st.text_input("Company", key="signup_company")
            email = st.text_input("Email", key="signup_email")
            place = st.text_input("Place", key="signup_place")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

            if st.button("Create Account"):
                signup_name = name.strip()
                signup_company = company.strip()
                signup_email = email.strip().lower()
                signup_place = place.strip()
                signup_password = password.strip()
                signup_confirm = confirm.strip()

                if not signup_name or not signup_email or not signup_password:
                    st.error("Name, Email, and Password are required")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        c.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                                  (signup_name, signup_company, signup_email, signup_place, signup_password))
                        conn.commit()
                        st.session_state.force_login_view = True
                        st.session_state.signup_success = "Account created successfully. Please login with Premium."
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Email already registered")
                    except Exception as err:
                        st.error(f"Account creation failed: {err}")

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

df = enrich_contract_fields(df)

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

if st.session_state.user_type == "premium":
    update_snapshot_state(df)

# =============================
# OVERVIEW
# =============================

st.subheader("Customer Overview")

if st.session_state.user_type == "premium":
    csm_options = sorted(df["owner"].dropna().unique().tolist())
    selected_csm = st.selectbox("Select CSM", csm_options)
    scoped_df = df[df["owner"] == selected_csm].copy()
    selected_customer = st.selectbox("Select Customer", scoped_df["customer_name"])
else:
    selected_customer = st.selectbox("Select Customer", df["customer_name"])
    scoped_df = df.copy()

selected_row = scoped_df[scoped_df["customer_name"] == selected_customer].iloc[0]
if st.session_state.get("ai_summary_for_customer") != selected_customer:
    st.session_state["ai_summary_text"] = None
    st.session_state["ai_summary_for_customer"] = selected_customer

# Premium view should focus selected customer only.
if st.session_state.user_type == "premium":
    render_customer_overview_table(
        scoped_df[scoped_df["customer_name"] == selected_customer][
            ["customer_name", "owner", "health_score", "risk_level", "priority_score"]
        ]
    )
else:
    render_customer_overview_table(
        df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]]
    )

st.markdown(
    f"""
    <div class='suggestion-card'>
        <div class='suggestion-title'>Contract Snapshot: {escape(str(selected_customer))}</div>
        <div>Purchase Date: <b>{escape(str(selected_row['purchase_date']))}</b></div>
        <div>Renewal Date: <b>{escape(str(selected_row['renewal_date']))}</b></div>
        <div>Auto Renew Opt-Out: <b>{'Yes' if bool(selected_row['auto_renew_opt_out']) else 'No'}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Premium-only advanced section
if st.session_state.user_type == "premium":
    render_premium_command_center(scoped_df, selected_row)

# =============================
# AI EXECUTIVE SUMMARY
# =============================

st.subheader("AI Executive Summary")

if st.session_state.user_type == "demo":
    st.markdown(
        """
        <div class="ai-summary-card">
            <div class="ai-blur">
                Churn risk is concentrated in low-engagement accounts with recurring support friction.
                Revenue at risk requires structured owner-led intervention, while healthy accounts show
                clear expansion potential. Priority focus should balance churn prevention and guided growth
                to stabilize renewals and improve net retention over the next cycle.
            </div>
            <div class="upgrade-note">Upgrade to Premium to unlock the full details.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    if st.button("Generate AI Executive Summary", type="secondary"):
        st.session_state["ai_summary_text"] = build_ai_summary(df, selected_row)
        st.session_state["ai_summary_for_customer"] = selected_customer
    ai_summary_text = st.session_state.get("ai_summary_text")
    if ai_summary_text:
        st.markdown(f"<div class='ai-summary-card'>{escape(ai_summary_text)}</div>", unsafe_allow_html=True)
    else:
        st.info("Click 'Generate AI Executive Summary' to view insights.")

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
