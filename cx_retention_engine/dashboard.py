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
        .stApp, .stApp p, .stApp label, .stApp span, .stApp div {
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
        section[data-testid="stSidebar"] * {
            color: var(--sidebar-ink);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaptionContainer { color: var(--sidebar-ink) !important; opacity: 1 !important; }
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
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: rgba(255,255,255,0.96) !important;
            border: 2px dashed rgba(12,92,114,0.24) !important;
            border-radius: 18px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
            color: #133247 !important;
            fill: #133247 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            background: #eaf4fb !important;
            border: 1px solid #cfe0ee !important;
            color: #133247 !important;
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
        }
        .stApp [data-baseweb="input"] > div,
        .stApp [data-baseweb="base-input"] > div,
        .stApp [data-baseweb="select"] > div,
        .stApp textarea,
        .stApp input {
            background: rgba(255,255,255,0.94) !important;
            border: 1px solid #cfdae9 !important;
            color: var(--ink) !important;
            border-radius: 18px !important;
            box-shadow: 0 10px 22px rgba(28,43,70,0.04);
        }
        .stApp [data-baseweb="base-input"] input,
        .stApp [data-baseweb="input"] input,
        .stApp textarea {
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
        }
        .stApp [data-baseweb="base-input"] [role="button"],
        .stApp [data-baseweb="input"] [role="button"] {
            background: #eef6fb !important;
            border-left: 1px solid #cfdae9 !important;
            border-radius: 16px !important;
            color: #1b5268 !important;
            min-width: 48px !important;
        }
        .stApp [data-baseweb="base-input"] [role="button"] *,
        .stApp [data-baseweb="input"] [role="button"] * {
            color: #1b5268 !important;
            fill: #1b5268 !important;
        }
        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            background: linear-gradient(180deg, #1e6f77 0%, #165a67 100%) !important;
            color: #f8fcff !important;
            border: 1px solid rgba(14,81,92,0.35) !important;
            border-radius: 16px !important;
            min-height: 46px !important;
            box-shadow: 0 12px 24px rgba(20,71,89,0.16);
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover {
            background: linear-gradient(180deg, #257d86 0%, #1a6674 100%) !important;
            border-color: rgba(14,81,92,0.42) !important;
        }
        .stButton > button *,
        .stDownloadButton > button *,
        button[kind="primary"] *,
        button[kind="secondary"] * {
            color: #f8fcff !important;
            fill: #f8fcff !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(255,255,255,0.97) !important;
            border: 2px dashed rgba(12,92,114,0.20) !important;
            border-radius: 20px !important;
            box-shadow: 0 14px 28px rgba(28,43,70,0.05);
        }
        [data-testid="stFileUploaderDropzone"] * {
            color: #16324a !important;
            fill: #16324a !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
            background: #edf6fb !important;
            border: 1px solid #cfe0ee !important;
            color: #16324a !important;
            border-radius: 14px !important;
        }
        [data-testid="stExpander"] {
            border: 1px solid var(--line) !important;
            border-radius: 18px !important;
            background: rgba(255,255,255,0.88) !important;
            box-shadow: 0 12px 24px rgba(28,43,70,0.05);
            overflow: hidden;
        }
        [data-testid="stExpander"] summary {
            background: rgba(247,250,255,0.94) !important;
            border-radius: 18px !important;
        }
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
        }
        [data-testid="stAlert"] {
            border-radius: 18px !important;
            border: 1px solid #dbe5f3 !important;
        }
        [data-testid="stAlert"] * {
            color: #1f2e43 !important;
        }
        div[data-testid="stCaptionContainer"] {
            color: var(--muted) !important;
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

        /* Sledgehammer override for sidebar radio text color to match Copilot's crisp white */
        section[data-testid="stSidebar"] [data-baseweb="radio"] p,
        section[data-testid="stSidebar"] [data-baseweb="radio"] span,
        section[data-testid="stSidebar"] [data-baseweb="radio"] div {
            color: #ffffff !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.8rem !important;
        }

        .auth-shell {
            padding: 1rem 0 2rem 0;
        }
        .auth-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.25rem;
        }
        .auth-stat {
            padding: 1rem;
            border-radius: 20px;
            border: 1px solid #d7e4f2;
            background: rgba(255,255,255,0.74);
        }
        .auth-stat-value {
            color: var(--ink);
            font-size: 1.8rem;
            font-weight: 900;
            line-height: 1;
        }
        .auth-stat-copy {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
            margin-top: 0.45rem;
            font-weight: 700;
        }
        .auth-hero {
            padding: 2rem 2.15rem;
            border-radius: 28px;
            border: 1px solid var(--line);
            background:
                radial-gradient(circle at top left, rgba(12,92,114,0.12), transparent 24%),
                radial-gradient(circle at top right, rgba(58,126,255,0.14), transparent 20%),
                linear-gradient(140deg, rgba(255,255,255,0.98), rgba(238,245,255,0.95));
            box-shadow: 0 24px 46px rgba(28,43,70,0.08);
        }
        .auth-kicker {
            display: inline-flex;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(12,92,114,0.08);
            color: var(--brand);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .auth-title {
            margin-top: 1rem;
            color: var(--ink);
            font-size: 3.2rem;
            line-height: 1;
            font-weight: 900;
            letter-spacing: -0.04em;
            max-width: 980px;
        }
        .auth-sub {
            margin-top: 1rem;
            max-width: 820px;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.65;
        }
        .auth-toggle-shell {
            margin-top: 1rem;
            padding: 0.95rem 1rem;
            border-radius: 20px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.88);
            box-shadow: 0 14px 28px rgba(28,43,70,0.05);
        }
        .auth-card {
            min-height: 150px;
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
            padding: 1.2rem 1.25rem 1rem 1.25rem;
            border-radius: 24px;
            border: 1px solid #d7e4f2;
            box-shadow: 0 18px 34px rgba(28,43,70,0.06);
        }
        .auth-card-demo {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,250,255,0.95));
        }
        .auth-card-premium {
            background:
                radial-gradient(circle at top right, rgba(12,92,114,0.12), transparent 24%),
                linear-gradient(145deg, rgba(241,250,247,0.98), rgba(238,245,255,0.96));
            border-color: #c6dfd8;
        }
        .auth-card-kicker {
            color: var(--brand);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .auth-card-title {
            margin-top: 0.7rem;
            color: #16324a;
            font-size: 1.45rem;
            font-weight: 800;
        }
        .auth-card-copy {
            margin-top: 0.5rem;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }
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


def render_sidebar_shell(user_name: str, role_label: str, copilot_url: str) -> str:
    """Render the branded top block of the sidebar (hero + account info only).
    Navigation is handled by st.radio in app.py.
    """
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
