from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f7f3ea;
            --bg-accent: #edf4ff;
            --surface: rgba(255,255,255,0.88);
            --surface-strong: #ffffff;
            --ink: #162033;
            --muted: #5c687d;
            --line: #dbe5f3;
            --brand: #0c5c72;
            --brand-soft: #e8f4f8;
            --sidebar-ink: #eef7ff;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, #fff8ea 0%, transparent 32%),
                radial-gradient(circle at top right, #ddeeff 0%, transparent 28%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-accent) 100%);
            color: var(--ink);
        }
        [data-testid="stHeader"] { background: transparent; height: 0; }
        [data-testid="collapsedControl"] {
            display: flex !important;
            position: fixed;
            top: 0.9rem;
            left: 0.9rem;
            z-index: 1001;
            border-radius: 999px;
            background: rgba(255,255,255,0.92);
            border: 1px solid #dbe5f3;
            box-shadow: 0 10px 20px rgba(32,49,79,0.12);
        }
        [data-testid="collapsedControl"] svg { fill: var(--brand); }
        [data-testid="stSidebarNav"] { display:none !important; }
        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top right, rgba(135,199,219,0.24), transparent 32%),
                linear-gradient(180deg, #10364a 0%, #0d2232 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaptionContainer { color: var(--sidebar-ink) !important; }
        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-baseweb="input"] > div,
        section[data-testid="stSidebar"] [data-baseweb="base-input"] > div {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
        }
        section[data-testid="stSidebar"] .stButton > button,
        section[data-testid="stSidebar"] .stDownloadButton > button,
        section[data-testid="stSidebar"] button[kind="primary"],
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255,255,255,0.14) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            color: #f8fcff !important;
            border-radius: 16px !important;
            min-height: 46px !important;
        }
        section[data-testid="stSidebar"] button * { color: #f8fcff !important; fill: #f8fcff !important; }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
        }
        .hero-card {
            padding: 1.2rem 1.35rem;
            border: 1px solid var(--line);
            border-radius: 20px;
            background:
                radial-gradient(circle at top right, rgba(102,165,197,0.18), transparent 28%),
                linear-gradient(135deg, rgba(255,255,255,0.96), rgba(240,247,255,0.92));
            box-shadow: 0 18px 32px rgba(31,49,82,0.08);
            margin-bottom: 1rem;
        }
        .hero-title { font-size: 2rem; font-weight: 800; color: var(--ink); margin: 0; }
        .hero-sub { color: var(--muted); margin-top: 0.35rem; margin-bottom: 0; font-size: 1rem; }
        .metric-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: var(--surface);
            box-shadow: 0 14px 24px rgba(27,44,73,0.06);
        }
        .metric-label { font-size: 0.78rem; text-transform: uppercase; color: var(--muted); font-weight: 700; letter-spacing: 0.06em; }
        .metric-value { font-size: 2rem; line-height: 1.05; color: var(--ink); font-weight: 800; margin-top: 0.35rem; }
        .metric-note { color: var(--muted); font-size: 0.85rem; margin-top: 0.35rem; }
        .section-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: rgba(255,255,255,0.8);
        }
        .sidebar-shell { padding: 0.55rem 0.15rem 1rem 0.15rem; }
        .sidebar-hero {
            padding: 1rem;
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 0.85rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .sidebar-kicker { font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; opacity: 0.85; font-weight: 700; color: #eef7ff; }
        .sidebar-title { font-size: 1.25rem; font-weight: 800; line-height: 1.1; margin-top: 0.35rem; color: #f8fcff; }
        .sidebar-copy { font-size: 0.88rem; line-height: 1.45; opacity: 0.92; margin-top: 0.45rem; color: #d8e8f7; }
        .sidebar-chip-row { display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.75rem; }
        .sidebar-badge { padding:0.45rem 0.7rem; border-radius:999px; background:rgba(255,255,255,0.10); border:1px solid rgba(255,255,255,0.12); color:#eef7ff; font-weight:700; }
        .sidebar-account { margin-top:0.85rem; padding:0.9rem 1rem; border-radius:18px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.10); }
        .sidebar-account-label { font-size:0.72rem; text-transform:uppercase; letter-spacing:0.12em; opacity:0.82; font-weight:700; color:#eef7ff; }
        .sidebar-account-name { margin-top:0.4rem; font-size:1.2rem; font-weight:800; color:#f8fcff; }
        .sidebar-account-role { margin-top:0.28rem; font-size:0.85rem; opacity:0.92; color:#d8e8f7; }
        .nav-shell { margin-top:0.9rem; margin-bottom:1rem; }
        .nav-title { font-size:0.74rem; text-transform:uppercase; letter-spacing:0.12em; opacity:0.82; font-weight:700; margin-bottom:0.55rem; color:#eef7ff; }
        .nav-link { display:block; margin-bottom:0.55rem; padding:0.8rem 0.9rem; border-radius:16px; border:1px solid rgba(255,255,255,0.12); background:rgba(255,255,255,0.08); color:#f4f9ff !important; font-size:0.92rem; font-weight:700; text-decoration:none !important; }
        .nav-link:hover { border-color:rgba(255,255,255,0.22); box-shadow:0 10px 22px rgba(4,15,31,0.24); }
        .dataframe, [data-testid="stPlotlyChart"] {
            border: 1px solid #d8e5f2;
            border-radius: 20px;
            background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(248,251,255,0.95));
            box-shadow: 0 14px 24px rgba(28,43,70,0.06);
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class=\"hero-card\">
          <p class=\"hero-title\">{escape(title)}</p>
          <p class=\"hero-sub\">{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, note) in zip(cols, items):
        col.markdown(
            f"""
            <div class=\"metric-card\">
              <div class=\"metric-label\">{escape(label)}</div>
              <div class=\"metric-value\">{escape(value)}</div>
              <div class=\"metric-note\">{escape(note)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_shell(user_name: str, role_label: str, nav_items: list[str], current_module: str, copilot_url: str) -> str:
    nav_markup = "".join(
        f"<div class='nav-link' style='opacity:{'1' if item == current_module else '0.86'}'>{escape(item)}</div>" for item in nav_items
    )
    return f"""
    <div class='sidebar-shell'>
      <div class='sidebar-hero'>
        <div class='sidebar-kicker'>Customer Success Workspace</div>
        <div class='sidebar-title'>CX Retention Engine</div>
        <div class='sidebar-copy'>Track renewal risk, assign ownership, and guide retention execution from one premium workspace.</div>
        <div class='sidebar-chip-row'>
          <span class='sidebar-badge'>Retention Ops</span>
          <span class='sidebar-badge'>Risk Watch</span>
          <span class='sidebar-badge'>AI Linked</span>
        </div>
      </div>
      <div class='sidebar-account'>
        <div class='sidebar-account-label'>Signed In As</div>
        <div class='sidebar-account-name'>{escape(user_name)}</div>
        <div class='sidebar-account-role'>{escape(role_label)}</div>
      </div>
      <div class='nav-shell'>
        <div class='nav-title'>Workspace Modules</div>
        {nav_markup}
      </div>
      <div class='nav-shell'>
        <a class='nav-link' href='{escape(copilot_url)}' target='_blank'>Open Customer Success AI Copilot</a>
      </div>
    </div>
    """


def render_data_quality_summary(summary: dict[str, int]) -> None:
    items = [
        ("Missing Values", str(summary["missing_values"]), "Rows with nulls or incomplete data"),
        ("Duplicate Accounts", str(summary["duplicate_accounts"]), "Repeated account or customer records"),
        ("Invalid Renewals", str(summary["invalid_renewals"]), "Rows with bad or missing renewal dates"),
        ("Bad Assignment", str(summary["incorrect_csm_assignments"]), "Customers assigned to unknown CSM owners"),
    ]
    render_metric_row(items)
    st.markdown(
        f"""
        <div class='section-card' style='margin-top:1rem'>
          <div style='font-weight:800;color:#162033;margin-bottom:0.45rem'>Suggested Fixes</div>
          <div style='color:#5c687d;line-height:1.6'>
            Standardize CSM owner names against the active user list, clean renewal date formatting, and remove duplicate customer rows before the next portfolio refresh.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_overview_charts(df: pd.DataFrame) -> list:
    csat_df = df.groupby("Plan_Type", as_index=False)["CSAT"].mean()
    return [
        px.histogram(df, x="Health_Score", color="Health_Category", title="Health distribution"),
        px.bar(df.groupby("Plan_Type", as_index=False)["ARR"].sum(), x="Plan_Type", y="ARR", title="ARR by plan"),
        px.line(csat_df, x="Plan_Type", y="CSAT", markers=True, title="CSAT trend by plan"),
        px.bar(df.groupby("CSM_Owner", as_index=False)["ARR"].sum(), x="CSM_Owner", y="ARR", title="ARR by CSM"),
        px.histogram(df, x="Renewal_Days", nbins=20, title="Renewal pipeline (days to renewal)"),
        px.bar(df.groupby("Account_Name", as_index=False)["Support_Tickets_Last_30_Days"].sum().sort_values("Support_Tickets_Last_30_Days", ascending=False).head(10), x="Account_Name", y="Support_Tickets_Last_30_Days", title="Support ticket trends"),
    ]
