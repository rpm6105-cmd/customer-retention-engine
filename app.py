from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from cx_retention_engine.ai_summary import generate_ai_summary
from cx_retention_engine.admin_panel import render_admin_panel
from cx_retention_engine.auth import init_auth_state, render_login_shell
from cx_retention_engine.dashboard import build_overview_charts, inject_styles, render_data_quality_summary, render_metric_row, render_page_header, render_sidebar_shell
from cx_retention_engine.data_loader import (
    build_sample_csv,
    generate_sample_dataset,
    get_assignment_map,
    init_database,
    list_users,
    load_master_dataset,
    apply_assignments,
    filter_dataset_for_user,
    update_user_password,
    update_user_profile,
)
from cx_retention_engine.health_model import enrich_dataset
from cx_retention_engine.tasks import load_tasks, render_task_tracker

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide", initial_sidebar_state="expanded")
inject_styles()
init_database()
init_auth_state()

if not st.session_state.logged_in:
    render_login_shell()

COPILOT_URL = "https://customer-success-ai-copilot.streamlit.app"
MODULES = [
    "Customer Overview",
    "Portfolio Snapshot",
    "Renewal & Risk Watch",
    "Priority Accounts",
    "Account Center",
    "Task Tracker",
    "Data Quality Check",
    "Admin Panel",
]


def get_role_label() -> str:
    if st.session_state.user_type == "demo":
        return "Demo access"
    return "Admin access" if st.session_state.user_role == "admin" else "CSM access"


def load_dataset() -> tuple[pd.DataFrame, dict | None, str]:
    if st.session_state.user_type == "demo":
        return enrich_dataset(generate_sample_dataset()), {"source_name": "Generated sample dataset", "updated_by": "System", "updated_at": "Live"}, "demo"
    master_df, meta = load_master_dataset()
    if master_df is None:
        st.warning("No master dataset uploaded yet. Please ask an admin to upload the company master CSV.")
        return pd.DataFrame(), None, "empty"
    return enrich_dataset(apply_assignments(master_df)), meta, "premium"


def build_data_quality(df: pd.DataFrame) -> dict[str, int]:
    users = list_users()
    owner_names = set(users["name"].astype(str).str.strip().str.lower())
    renewal = pd.to_datetime(df["Renewal_Date"], errors="coerce")
    return {
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_accounts": int(df["Customer_ID"].astype(str).duplicated().sum()),
        "invalid_renewals": int(renewal.isna().sum()),
        "incorrect_csm_assignments": int((~df["CSM_Owner"].astype(str).str.lower().isin(owner_names)).sum()),
    }


def render_overview(df: pd.DataFrame) -> None:
    render_page_header(
        "Customer Overview",
        "Monitor customer health, renewal concentration, and portfolio-level retention signals.",
    )
    cards = [
        ("Total ARR", f"${df['ARR'].sum():,.0f}", "Current recurring revenue managed in scope"),
        ("Total Customers", f"{len(df)}", "Customer accounts visible in current scope"),
        ("At Risk Accounts", f"{int((df['Churn_Risk'] == 'High Risk').sum())}", "Accounts needing immediate intervention"),
        ("Healthy Accounts", f"{int((df['Health_Category'] == 'Healthy').sum())}", "Accounts with strong usage and sentiment"),
        ("Upcoming Renewals", f"{int(((df['Renewal_Days'] >= 0) & (df['Renewal_Days'] <= 90)).sum())}", "Renewals inside the next 90 days"),
    ]
    render_metric_row(cards)
    charts = build_overview_charts(df)
    c1, c2 = st.columns(2)
    c1.plotly_chart(charts[0], use_container_width=True)
    c2.plotly_chart(charts[1], use_container_width=True)
    c3, c4 = st.columns(2)
    c3.plotly_chart(charts[2], use_container_width=True)
    c4.plotly_chart(charts[3], use_container_width=True)
    c5, c6 = st.columns(2)
    c5.plotly_chart(charts[4], use_container_width=True)
    c6.plotly_chart(charts[5], use_container_width=True)


def render_portfolio_snapshot(df: pd.DataFrame) -> None:
    render_page_header(
        "CSM Lead Portfolio Snapshot",
        "Compare the health, ARR coverage, risk exposure, and renewal pipeline across CSM portfolios.",
    )
    rollup = df.groupby("CSM_Owner", as_index=False).agg(
        total_arr=("ARR", "sum"),
        accounts=("Customer_ID", "count"),
        avg_health=("Health_Score", "mean"),
        renewal_pipeline=("Renewal_Days", lambda s: int(((s >= 0) & (s <= 90)).sum())),
        risk_accounts=("Churn_Risk", lambda s: int((s == "High Risk").sum())),
    )
    for row in rollup.itertuples(index=False):
        st.markdown(
            f"""
            <div style='padding:18px 18px 16px 18px;border:1px solid #dbe5f3;border-radius:20px;background:rgba(255,255,255,0.92);box-shadow:0 14px 24px rgba(28,43,70,0.06);margin-bottom:12px'>
                <div style='font-size:20px;font-weight:800;color:#162033'>{row.CSM_Owner}</div>
                <div style='margin-top:10px;color:#5c687d;line-height:1.7'>ARR Managed: <b>${row.total_arr:,.0f}</b><br/>Accounts: <b>{row.accounts}</b><br/>Average Health: <b>{row.avg_health:.1f}</b><br/>Renewal Pipeline: <b>{row.renewal_pipeline}</b><br/>Risk Accounts: <b>{row.risk_accounts}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    chart = px.bar(rollup, x="CSM_Owner", y="total_arr", color="risk_accounts", title="CSM portfolio comparison")
    st.plotly_chart(chart, use_container_width=True)


def render_risk_watch(df: pd.DataFrame) -> None:
    render_page_header(
        "Renewal & Risk Watch",
        "Spot accounts with near-term renewals, declining engagement, or elevated churn risk.",
    )
    risk_df = df[(df["Renewal_Days"] <= 90) | (df["Health_Score"] < 55) | (df["Last_Login_Days_Ago"] > 25)].copy()
    st.dataframe(
        risk_df[["Account_Name", "CSM_Owner", "ARR", "Health_Score", "Churn_Risk", "Renewal_Date", "Renewal_Days", "Support_Tickets_Last_30_Days", "Next_Best_Action"]],
        use_container_width=True,
        hide_index=True,
    )


def render_priority_accounts(df: pd.DataFrame) -> None:
    render_page_header(
        "Priority Accounts This Week",
        "Generate a weekly action list based on renewal timing, support burden, and health deterioration.",
    )
    priority = df.sort_values(["Priority_Score", "ARR"], ascending=[False, False]).head(12)
    st.dataframe(
        priority[["Account_Name", "CSM_Owner", "ARR", "Health_Score", "Churn_Risk", "Renewal_Date", "Priority_Score", "Next_Best_Action"]],
        use_container_width=True,
        hide_index=True,
    )


def render_account_center(df: pd.DataFrame, tasks_df: pd.DataFrame) -> None:
    render_page_header(
        "Account Center",
        "Open a detailed customer view with health, usage, support load, renewal timing, and active tasks.",
    )
    account = st.selectbox("Select Account", df["Account_Name"].sort_values().tolist(), key="account_center_select")
    row = df[df["Account_Name"] == account].iloc[0]
    render_metric_row(
        [
            ("Health Score", f"{row['Health_Score']:.1f}", row["Health_Category"]),
            ("ARR", f"${row['ARR']:,.0f}", row["Plan_Type"]),
            ("Renewal", str(row["Renewal_Date"]), f"{int(row['Renewal_Days'])} days remaining"),
            ("Support Tickets", str(int(row['Support_Tickets_Last_30_Days'])), "Last 30 days"),
        ]
    )
    st.markdown(
        f"""
        <div class='section-card'>
          <div style='font-weight:800;color:#162033;margin-bottom:0.65rem'>Account Metadata</div>
          <div style='color:#5c687d;line-height:1.75'>
            Customer ID: <b>{row['Customer_ID']}</b><br/>
            Assigned CSM: <b>{row['CSM_Owner']}</b><br/>
            Active Users: <b>{int(row['Active_Users'])}</b><br/>
            Monthly Logins: <b>{int(row['Monthly_Logins'])}</b><br/>
            Feature Usage Score: <b>{row['Feature_Usage_Score']:.1f}</b><br/>
            CSAT: <b>{row['CSAT']:.1f}</b><br/>
            NPS: <b>{row['NPS']:.1f}</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    open_tasks = tasks_df[tasks_df["account_name"] == account] if not tasks_df.empty else pd.DataFrame()
    if not open_tasks.empty:
        st.markdown("### Open Tasks")
        st.dataframe(open_tasks[["task_type", "owner_email", "due_date", "status", "notes"]], use_container_width=True, hide_index=True)


def render_ai_summary_section(df: pd.DataFrame) -> None:
    render_page_header(
        "AI Executive Summary",
        "Generate an executive-ready retention summary for leadership review.",
    )
    if st.button("Generate AI Executive Summary", key="generate_ai_summary"):
        st.session_state["retention_ai_summary"] = generate_ai_summary(df)
    if st.session_state.get("retention_ai_summary"):
        st.markdown(
            f"<div class='section-card' style='line-height:1.7;color:#334155'>{st.session_state['retention_ai_summary']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Generate the summary to view executive insights.")


def render_sidebar(df: pd.DataFrame, meta: dict | None, current_module: str) -> None:
    role_label = get_role_label()
    with st.sidebar:
        st.markdown(
            render_sidebar_shell(st.session_state.user_name, role_label, COPILOT_URL),
            unsafe_allow_html=True,
        )
        if meta:
            st.caption(f"Data source: {meta['source_name']}")
        plan_options = ["All"] + sorted(df["Plan_Type"].astype(str).unique().tolist())
        risk_options = ["All", "High Risk", "Medium Risk", "Low Risk"]
        owner_options = ["All"] + sorted(df["CSM_Owner"].astype(str).unique().tolist())
        
        st.markdown("<div class='nav-shell'><div class='nav-title'>Workspace Modules</div></div>", unsafe_allow_html=True)
        selected_module = st.radio("Module", MODULES, index=MODULES.index(current_module), key="selected_module")
        
        st.markdown("### Portfolio Controls")
        st.selectbox("Filter by plan", plan_options, key="filter_plan")
        st.selectbox("Filter by churn risk", risk_options, key="filter_risk")
        st.selectbox("Filter by owner", owner_options, key="filter_owner")
        if st.session_state.user_type == "premium":
            with st.expander("Open Account Center", expanded=False):
                st.markdown("**Edit Profile**")
                with st.form("profile_form"):
                    name = st.text_input("Name", value=st.session_state.user_name)
                    company = st.text_input("Company")
                    place = st.text_input("Place")
                    if st.form_submit_button("Save Profile"):
                        update_user_profile(st.session_state.user_email, name.strip(), company.strip(), place.strip())
                        st.session_state.user_name = name.strip() or st.session_state.user_name
                        st.success("Profile updated.")
                st.markdown("**Change Password**")
                with st.form("password_form"):
                    current_password = st.text_input("Current Password", type="password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm New Password", type="password")
                    if st.form_submit_button("Change Password"):
                        if not new_password.strip() or new_password.strip() != confirm_password.strip():
                            st.error("New passwords do not match.")
                        else:
                            update_user_password(st.session_state.user_email, new_password.strip())
                            st.success("Password changed.")
        if st.button("Logout", key="logout_button", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return selected_module


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    plan = st.session_state.get("filter_plan", "All")
    risk = st.session_state.get("filter_risk", "All")
    owner = st.session_state.get("filter_owner", "All")
    if plan != "All":
        filtered = filtered[filtered["Plan_Type"] == plan]
    if risk != "All":
        filtered = filtered[filtered["Churn_Risk"] == risk]
    if owner != "All":
        filtered = filtered[filtered["CSM_Owner"] == owner]
    return filtered


df, meta, mode = load_dataset()
if df.empty and st.session_state.user_type == "premium":
    current_module = render_sidebar(pd.DataFrame({"Plan_Type": [], "Churn_Risk": [], "CSM_Owner": []}), meta, "Admin Panel")
    render_page_header("Admin Setup Needed", "Upload the first master dataset to start the retention workspace.")
    if st.session_state.user_role == "admin":
        render_admin_panel(generate_sample_dataset(20), st.session_state.user_email)
    st.stop()

if mode == "premium":
    df = filter_dataset_for_user(df, st.session_state.user_email, st.session_state.user_role)
    if df.empty:
        render_sidebar(pd.DataFrame({"Plan_Type": ["All"], "Churn_Risk": ["All"], "CSM_Owner": ["All"]}), meta, "Customer Overview")
        st.warning("No accounts are assigned to this CSM yet. Please contact your admin.")
        st.stop()

current_module = render_sidebar(df, meta, st.session_state.get("selected_module", MODULES[0]))
filtered_df = apply_sidebar_filters(df)
all_tasks = load_tasks()
visible_tasks = all_tasks if st.session_state.user_role == "admin" or st.session_state.user_type == "demo" else all_tasks[all_tasks["owner_email"].str.lower() == st.session_state.user_email.lower()]

if current_module == "Customer Overview":
    render_overview(filtered_df)
elif current_module == "Portfolio Snapshot":
    render_portfolio_snapshot(filtered_df)
elif current_module == "Renewal & Risk Watch":
    render_risk_watch(filtered_df)
elif current_module == "Priority Accounts":
    render_priority_accounts(filtered_df)
elif current_module == "Account Center":
    render_account_center(filtered_df, visible_tasks)
elif current_module == "Task Tracker":
    render_task_tracker(filtered_df, visible_tasks, st.session_state.user_email)
elif current_module == "Data Quality Check":
    render_page_header("Data Quality Check", "Audit the master customer dataset for gaps, duplicates, and operational issues.")
    render_data_quality_summary(build_data_quality(filtered_df))
elif current_module == "Admin Panel":
    render_page_header("Admin Panel", "Manage users, upload master data, and assign customer ownership.")
    if st.session_state.user_role == "admin":
        render_admin_panel(filtered_df, st.session_state.user_email)
    else:
        st.warning("Admin Panel is available only for Admin users.")

if current_module != "Task Tracker":
    render_ai_summary_section(filtered_df)
