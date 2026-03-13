import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
import hashlib
import os
from html import escape
from datetime import datetime, date, timedelta
from io import StringIO
import textwrap
import urllib.parse
from pathlib import Path

st.set_page_config(page_title="Customer Retention & Growth Engine", layout="wide")

CSM_AI_COPILOT_URL = os.getenv(
    "CSM_AI_COPILOT_URL",
    "https://customer-success-ai-copilot.streamlit.app",
)

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
    --copilot-start: #eef6ff;
    --copilot-end: #f6fbff;
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

/* Streamlit sometimes colors inner label nodes separately; force white labels */
.stButton > button *,
.stDownloadButton > button *,
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

/* Alert cards (success/info/warning/error) */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid #d6e3f1 !important;
    box-shadow: none !important;
}

.stSuccess {
    background: linear-gradient(180deg, #f3fbf7 0%, #ebf8f2 100%) !important;
    border-color: #b7e4cf !important;
}

.stInfo {
    background: linear-gradient(180deg, #f4f9ff 0%, #edf6ff 100%) !important;
    border-color: #c9def7 !important;
}

.stWarning {
    background: linear-gradient(180deg, #fffdf4 0%, #fff9e8 100%) !important;
    border-color: #f2dfaa !important;
}

.stError {
    background: linear-gradient(180deg, #fff5f5 0%, #ffecec 100%) !important;
    border-color: #f5c2c2 !important;
}

div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] li,
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] span {
    color: #1f2937 !important;
    font-weight: 600 !important;
    background: transparent !important;
    -webkit-text-fill-color: #1f2937 !important;
}

div[data-testid="stAlert"] code {
    background: transparent !important;
    color: #1f2937 !important;
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

.header-hero {
    padding: 28px 30px;
    border-radius: 24px;
    border: 1px solid #cae0f6;
    background:
        radial-gradient(circle at top left, rgba(14, 116, 144, 0.14), transparent 24%),
        radial-gradient(circle at right center, rgba(29, 78, 216, 0.10), transparent 20%),
        linear-gradient(145deg, #f7fbff 0%, #eef6ff 52%, #f9fcff 100%);
    box-shadow: 0 24px 46px rgba(22, 65, 110, 0.10);
}

.header-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(15, 118, 110, 0.10);
    color: #0f766e;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.header-title {
    margin-top: 18px;
    color: #0f2442;
    font-size: 58px;
    line-height: 1.02;
    font-weight: 900;
    letter-spacing: -0.03em;
}

.header-subtitle {
    margin-top: 14px;
    max-width: 860px;
    color: #425b74;
    font-size: 18px;
    line-height: 1.55;
}

.header-chip-row {
    margin-top: 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.header-chip {
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid #d7e6f7;
    color: #214866;
    font-size: 13px;
    font-weight: 700;
}

.account-panel {
    padding: 22px 22px 18px 22px;
    border-radius: 22px;
    border: 1px solid #d4e4f4;
    background: linear-gradient(180deg, #ffffff 0%, #f6fbff 100%);
    box-shadow: 0 18px 34px rgba(21, 61, 104, 0.08);
}

.account-panel-shell {
    padding: 0 0 14px 0;
    border-radius: 22px;
    border: 1px solid #d4e4f4;
    background: linear-gradient(180deg, #ffffff 0%, #f6fbff 100%);
    box-shadow: 0 18px 34px rgba(21, 61, 104, 0.08);
    overflow: hidden;
}

.account-panel-label {
    color: #0f766e;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.account-panel-name {
    margin-top: 8px;
    color: #0f2442;
    font-size: 19px;
    font-weight: 800;
    line-height: 1.3;
}

.account-panel-role {
    margin-top: 6px;
    color: #53708c;
    font-size: 14px;
    font-weight: 700;
}

.account-panel-spacer {
    height: 10px;
}

.landing-hero {
    margin-top: 8px;
    padding: 34px 36px;
    border-radius: 28px;
    border: 1px solid #c8dbef;
    background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 24%),
        radial-gradient(circle at right top, rgba(29, 78, 216, 0.18), transparent 22%),
        linear-gradient(140deg, #fbfdff 0%, #eef6ff 48%, #f5fbff 100%);
    box-shadow: 0 30px 60px rgba(18, 57, 100, 0.12);
}

.landing-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(15, 118, 110, 0.10);
    color: #0f766e;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.landing-title {
    margin-top: 18px;
    color: #0f2442;
    font-size: 60px;
    line-height: 1.02;
    font-weight: 900;
    letter-spacing: -0.04em;
    max-width: 980px;
}

.landing-subtitle {
    margin-top: 16px;
    max-width: 860px;
    color: #47627d;
    font-size: 19px;
    line-height: 1.6;
}

.landing-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.landing-chip {
    padding: 9px 13px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid #d4e3f2;
    color: #214866;
    font-size: 13px;
    font-weight: 700;
}

.landing-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-top: 24px;
}

.landing-stat-card {
    padding: 18px 18px 16px 18px;
    border-radius: 20px;
    border: 1px solid #d6e6f6;
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(10px);
}

.landing-stat-value {
    color: #0f2442;
    font-size: 30px;
    font-weight: 900;
    line-height: 1;
}

.landing-stat-label {
    margin-top: 8px;
    color: #4f6a86;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.4;
}

.auth-toggle-wrap {
    margin-top: 18px;
    margin-bottom: 12px;
    padding: 14px 16px;
    border-radius: 18px;
    border: 1px solid #d7e4f3;
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    box-shadow: 0 16px 32px rgba(18, 57, 100, 0.06);
}

.auth-toggle-wrap label {
    color: #35506b !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.auth-toggle-wrap div[role="radiogroup"] {
    gap: 12px !important;
}

.auth-toggle-wrap div[role="radiogroup"] label {
    min-width: 120px;
    justify-content: center !important;
    padding: 10px 16px !important;
    border-radius: 999px !important;
    border: 1px solid #d5e3f1 !important;
    background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%) !important;
    box-shadow: 0 10px 20px rgba(18, 57, 100, 0.06);
}

.auth-toggle-wrap div[role="radiogroup"] label:has(input:checked) {
    border-color: #0f766e !important;
    background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 100%) !important;
}

.auth-toggle-wrap div[role="radiogroup"] label:has(input:checked) * {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.auth-card {
    min-height: 140px;
    margin-top: 8px;
    margin-bottom: 12px;
    padding: 20px 20px 14px 20px;
    border-radius: 22px;
    border: 1px solid #d5e3f1;
    box-shadow: 0 20px 40px rgba(18, 57, 100, 0.08);
}

.auth-card-demo {
    background:
        radial-gradient(circle at top left, rgba(29, 78, 216, 0.08), transparent 26%),
        linear-gradient(180deg, #ffffff 0%, #f4fbff 100%);
    border-color: #cfe0f4;
}

.auth-card-premium {
    background:
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.18), transparent 26%),
        linear-gradient(145deg, #effaf6 0%, #eef6ff 100%);
    border-color: #b9dccf;
    box-shadow: 0 24px 46px rgba(15, 118, 110, 0.10);
}

.auth-card-kicker {
    color: #0f766e;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.auth-card-title {
    margin-top: 10px;
    color: #123a58;
    font-size: 22px;
    font-weight: 800;
}

.auth-card-copy {
    margin-top: 8px;
    color: #4a657f;
    font-size: 14px;
    line-height: 1.55;
}

.auth-accent-demo {
    margin-top: 14px;
    color: #1d4ed8;
    font-size: 13px;
    font-weight: 700;
}

.auth-accent-premium {
    margin-top: 14px;
    color: #0f766e;
    font-size: 13px;
    font-weight: 700;
}

.signup-shell {
    margin-top: 10px;
    padding: 24px 26px 16px 26px;
    border-radius: 24px;
    border: 1px solid #d5e3f1;
    background:
        radial-gradient(circle at top right, rgba(29, 78, 216, 0.12), transparent 24%),
        linear-gradient(145deg, #ffffff 0%, #f5faff 100%);
    box-shadow: 0 22px 44px rgba(18, 57, 100, 0.08);
}

.data-status-card {
    margin-top: 14px;
    margin-bottom: 8px;
    padding: 14px 16px;
    border-radius: 16px;
    border: 1px solid #bde6d5;
    background: linear-gradient(180deg, #f3fff8 0%, #ebfbf3 100%);
    color: #14532d;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 12px 24px rgba(20, 83, 45, 0.07);
}

.account-action-stack {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 0;
    padding: 0 18px 0 18px;
}

.account-toolbar-label {
    color: #53708c;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: 6px;
    padding: 0 18px;
}

/* Remove Streamlit top black header area */
header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
}

/* Lock uploaded file row readability */
div[data-testid="stFileUploaderFile"] {
    background: #ffffff !important;
    border: 1px solid #d7e3f3 !important;
    border-radius: 10px !important;
}

div[data-testid="stFileUploaderFile"] *,
div[data-testid="stFileUploaderFileName"],
div[data-testid="stFileUploaderFileData"] {
    color: #0f172a !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="base-input"] > div {
    border-radius: 16px !important;
    border: 1px solid #cddced !important;
    background: #ffffff !important;
    box-shadow: 0 8px 18px rgba(18, 57, 100, 0.04) !important;
    overflow: hidden !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    color: #0f172a !important;
    font-weight: 600 !important;
}

div[data-baseweb="base-input"] {
    background: transparent !important;
}

div[data-baseweb="base-input"] button {
    margin: 0 8px 0 0 !important;
    border-radius: 999px !important;
    background: rgba(15, 118, 110, 0.10) !important;
    border: 0 !important;
    min-width: 34px !important;
    width: 34px !important;
    height: 34px !important;
    box-shadow: none !important;
}

div[data-baseweb="base-input"] button:hover {
    background: rgba(15, 118, 110, 0.16) !important;
}

div[data-baseweb="base-input"] button svg {
    fill: #0f766e !important;
}

div[data-baseweb="input"] {
    background: transparent !important;
}

div[data-baseweb="base-input"] > div::before,
div[data-baseweb="input"] > div::before,
div[data-baseweb="base-input"] > div::after,
div[data-baseweb="input"] > div::after {
    display: none !important;
}

.help-widget {
    position: fixed;
    right: 16px;
    bottom: 16px;
    width: 320px;
    z-index: 99999;
    border: 1px solid #bfd8f3;
    border-radius: 12px;
    background: #ffffff;
    box-shadow: 0 10px 24px rgba(20, 35, 58, 0.18);
    font-size: 13px;
}

.help-head {
    padding: 10px 12px;
    background: #e8f2ff;
    border-bottom: 1px solid #cfe0f5;
    font-weight: 800;
    color: #0f4c5c;
}

.help-body {
    padding: 10px 12px;
}

.help-download-wrap {
    margin-top: 8px;
}

.csv-popup-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.35);
    z-index: 100000;
}

.csv-popup-card {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(560px, 90vw);
    background: #ffffff;
    border: 2px solid #ef4444;
    border-radius: 14px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.25);
    z-index: 100001;
    padding: 16px 18px;
}

.csv-popup-title {
    color: #991b1b;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 6px;
}

.csv-popup-body {
    color: #1f2937;
    line-height: 1.5;
}

/* Premium strategy table */
.strategy-table-wrap {
    margin-top: 10px;
    border: 1px solid #b9d7f2;
    border-radius: 12px;
    overflow: hidden;
    background: #ffffff;
}

.strategy-table {
    width: 100%;
    border-collapse: collapse;
}

.strategy-table th, .strategy-table td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #e4edf8;
    color: #1f2937;
    vertical-align: top;
}

.strategy-table th {
    background: #eef6ff;
    color: #1d4c7c;
    font-weight: 800;
}

.impact-pill {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    color: #0f172a;
    background: #dbeafe;
}

.premium-kpi {
    border: 1px solid #d8e8fb;
    border-radius: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #f3f9ff 100%);
    padding: 12px 14px;
    margin-bottom: 8px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 10px;
    margin-top: 6px;
    margin-bottom: 8px;
}

.kpi-grid.kpi-grid-5 {
    grid-template-columns: repeat(5, minmax(0, 1fr));
}

.kpi-grid.kpi-grid-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.kpi-card {
    border: 1px solid #d8e8fb;
    border-radius: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #f3f9ff 100%);
    padding: 12px 14px;
}

.kpi-card-label {
    color: #35506b !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.kpi-card-value {
    color: #0f172a !important;
    font-size: 36px;
    font-weight: 800;
    line-height: 1.05;
    margin-top: 4px;
}

.data-source-badge {
    display: inline-block;
    margin-top: 4px;
    padding: 6px 12px;
    border-radius: 999px;
    background: linear-gradient(180deg, #eef6ff 0%, #e6f2ff 100%);
    border: 1px solid #c9def7;
    color: #1d4c7c;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.2px;
}

.meta-card {
    margin-top: 8px;
    margin-bottom: 10px;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid #cfe0f5;
    background: linear-gradient(180deg, #f8fcff 0%, #f1f8ff 100%);
    color: #1f2937;
    font-size: 13px;
    font-weight: 600;
}

.priority-table-wrap {
    margin-top: 8px;
    border: 1px solid #bfd8f3;
    border-radius: 12px;
    overflow: hidden;
    background: #ffffff;
}

.light-table-wrap {
    margin-top: 8px;
    border: 1px solid #bfd8f3;
    border-radius: 12px;
    overflow: hidden;
    background: #ffffff;
}

.light-table {
    width: 100%;
    border-collapse: collapse;
}

.light-table th, .light-table td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #e4edf8;
    color: #1f2937;
    vertical-align: middle;
}

.light-table th {
    background: #eef6ff;
    color: #1d4c7c;
    font-weight: 800;
}

.priority-table {
    width: 100%;
    border-collapse: collapse;
}

.priority-table th, .priority-table td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #e4edf8;
    color: #1f2937;
    vertical-align: middle;
}

.priority-table th {
    background: #eef6ff;
    color: #1d4c7c;
    font-weight: 800;
}

.days-overdue {
    color: #b42318;
    font-weight: 700;
}

.days-upcoming {
    color: #166534;
    font-weight: 700;
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

.copilot-link-card {
    margin-top: 12px;
    margin-bottom: 14px;
    padding: 24px 24px 22px 24px;
    border-radius: 18px;
    border: 1px solid #8dbce8;
    background:
        radial-gradient(circle at top right, rgba(18, 86, 121, 0.16), transparent 28%),
        linear-gradient(135deg, #ebf6ff 0%, #f8fbff 52%, #eef8ff 100%);
    box-shadow: 0 22px 42px rgba(29, 76, 124, 0.14);
    position: relative;
    overflow: hidden;
}

.copilot-link-card::after {
    content: "Premium Workspace";
    position: absolute;
    top: 14px;
    right: 18px;
    padding: 5px 11px;
    border-radius: 999px;
    background: rgba(15, 76, 92, 0.10);
    color: #0d4250;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.02em;
}

.copilot-link-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(15, 118, 110, 0.10);
    color: #0f766e;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.copilot-link-title {
    font-size: 28px;
    font-weight: 800;
    color: #113a58;
    margin-bottom: 10px;
}

.copilot-link-copy {
    color: #36506a;
    margin-bottom: 14px;
    line-height: 1.55;
    max-width: 860px;
    font-size: 16px;
}

.copilot-link-note {
    color: #0f4c5c;
    font-size: 14px;
    font-weight: 700;
    margin-top: 2px;
}

.copilot-link-cta-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(141, 188, 232, 0.55);
}

.copilot-link-cta-copy {
    color: #214866;
    font-size: 14px;
    font-weight: 700;
}

.copilot-link-cta-copy strong {
    color: #0f2f4a;
}


.suggestion-title {
    font-weight: 800;
    color: #0f4c5c;
    margin-bottom: 6px;
}

.premium-zone {
    border: 1px solid #b9d7f2;
    border-radius: 14px;
    background: linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%);
    padding: 12px;
    margin-top: 10px;
}

.focus-item {
    border: 1px solid #d6e6f8;
    border-radius: 10px;
    padding: 10px;
    background: #ffffff;
    margin-bottom: 8px;
}

.focus-title {
    font-weight: 800;
    color: #1d4c7c;
}

.focus-signal {
    font-size: 12px;
    color: #475569;
    margin-top: 2px;
}

.focus-action {
    margin-top: 5px;
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

/* Hard override so metric numbers never appear greyed out */
div[data-testid="metric-container"] * {
    color: #0f172a !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #334155 !important;
    opacity: 1 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] * {
    color: #0f172a !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

/* Compatibility selectors for different Streamlit metric DOM versions */
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] label *,
div[data-testid="metric-container"] p,
div[data-testid="metric-container"] p *,
div[data-testid="metric-container"] span,
div[data-testid="metric-container"] span * {
    color: #0f172a !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="metric-container"] [data-testid="stMetricLabel"] *,
div[data-testid="metric-container"] [data-testid="stMetricDelta"] * {
    color: #334155 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #334155 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #0f4c5c !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] > div,
div[data-testid="metric-container"] [data-testid="stMetricValue"] div,
div[data-testid="metric-container"] [data-testid="stMetricValue"] p,
div[data-testid="metric-container"] [data-testid="stMetricValue"] span {
    color: #0f172a !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #0f172a !important;
}

/* Tab and caption readability */
button[role="tab"] {
    color: #1f2937 !important;
    font-weight: 700 !important;
}

div[data-testid="stCaptionContainer"] {
    color: #334155 !important;
}

/* Forms and expanders */
div[data-testid="stForm"], div[data-testid="stExpander"] {
    background: var(--surface-soft);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 14px;
}

/* Expander header readability */
div[data-testid="stExpander"] summary {
    background: #eef6ff !important;
    color: #0f4c5c !important;
    border: 1px solid #cfe0f5 !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    font-weight: 800 !important;
}

div[data-testid="stExpander"] summary * {
    color: #0f4c5c !important;
    fill: #0f4c5c !important;
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


def ensure_schema_migrations():
    user_cols = [row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()]
    if "role" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'csm'")
        c.execute("UPDATE users SET role = 'csm' WHERE role IS NULL OR role = ''")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_assignments (
            customer_name TEXT PRIMARY KEY,
            assigned_email TEXT NOT NULL,
            assigned_by TEXT,
            assigned_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS master_dataset (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            source_name TEXT,
            csv_text TEXT NOT NULL,
            updated_by TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()


def email_domain(email: str) -> str:
    parts = (email or "").split("@")
    return parts[1].lower().strip() if len(parts) == 2 else ""


def get_same_domain_users(user_email: str, include_admin: bool = True):
    domain = email_domain(user_email)
    if not domain:
        return []
    if include_admin:
        rows = c.execute(
            "SELECT name, email, role FROM users WHERE lower(email) LIKE ? ORDER BY name ASC",
            (f"%@{domain}",),
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT name, email, role FROM users WHERE role = 'csm' AND lower(email) LIKE ? ORDER BY name ASC",
            (f"%@{domain}",),
        ).fetchall()
    return rows


def get_assignment_map() -> dict:
    rows = c.execute("SELECT customer_name, assigned_email FROM customer_assignments").fetchall()
    return {str(r[0]): str(r[1]).lower() for r in rows}


def upsert_customer_assignment(customer_name: str, assigned_email: str, assigned_by: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """
        INSERT INTO customer_assignments (customer_name, assigned_email, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(customer_name)
        DO UPDATE SET assigned_email=excluded.assigned_email, assigned_by=excluded.assigned_by, assigned_at=excluded.assigned_at
        """,
        (customer_name, assigned_email.lower(), assigned_by.lower(), now),
    )
    conn.commit()


def apply_assignment_overlay(df_input: pd.DataFrame) -> pd.DataFrame:
    df_out = df_input.copy()
    assignment_map = get_assignment_map()
    if not assignment_map:
        df_out["assigned_email"] = ""
        return df_out

    df_out["assigned_email"] = df_out["customer_name"].map(assignment_map).fillna("")
    user_rows = c.execute("SELECT email, name FROM users").fetchall()
    name_map = {str(r[0]).lower(): str(r[1]) for r in user_rows}
    mask = df_out["assigned_email"] != ""
    df_out.loc[mask, "owner"] = df_out.loc[mask, "assigned_email"].map(name_map).fillna(df_out.loc[mask, "owner"])
    return df_out


def filter_visible_accounts(df_input: pd.DataFrame, user_email: str, user_role: str) -> pd.DataFrame:
    if user_role == "admin":
        return df_input.copy()
    email = (user_email or "").lower().strip()
    if not email:
        return df_input.iloc[0:0].copy()
    if "assigned_email" not in df_input.columns:
        return df_input.iloc[0:0].copy()
    return df_input[df_input["assigned_email"].str.lower() == email].copy()


ensure_schema_migrations()
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


def validate_required_columns(df_input: pd.DataFrame, required_cols: list, label: str):
    missing = [c for c in required_cols if c not in df_input.columns]
    if missing:
        return f"{label} is missing required columns: {', '.join(missing)}"
    return None


def show_csv_error_popup(message: str):
    st.markdown(
        f"""
        <div class="csv-popup-backdrop"></div>
        <div class="csv-popup-card">
          <div class="csv-popup-title">Incorrect CSV format</div>
          <div class="csv-popup-body">
            Incorrect format, refer <b>Self Help</b> to see the CSV format and then reupload.<br/><br/>
            <b>Details:</b> {escape(message)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_empty_csv_template(headers: list[str]) -> str:
    return ",".join(headers) + "\n"


def build_csv_download_data_uri(headers: list[str]) -> str:
    csv_text = build_empty_csv_template(headers)
    return "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_text)


def save_master_dataset(csv_text: str, source_name: str, updated_by: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """
        INSERT INTO master_dataset (id, source_name, csv_text, updated_by, updated_at)
        VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id)
        DO UPDATE SET source_name=excluded.source_name, csv_text=excluded.csv_text, updated_by=excluded.updated_by, updated_at=excluded.updated_at
        """,
        (source_name, csv_text, updated_by, now),
    )
    conn.commit()


def load_master_dataset_from_db():
    row = c.execute(
        "SELECT source_name, csv_text, updated_by, updated_at FROM master_dataset WHERE id = 1"
    ).fetchone()
    if not row:
        return None, None, None
    source_name, csv_text, _updated_by, _updated_at = row
    try:
        full_df = pd.read_csv(StringIO(csv_text))
        prepared, error_msg = prepare_integrated_customer_df(full_df)
        if error_msg:
            return None, None, error_msg
        return prepared, f"DB Master ({source_name})", None
    except Exception as err:
        return None, None, str(err)


def get_master_dataset_meta():
    row = c.execute(
        "SELECT source_name, updated_by, updated_at FROM master_dataset WHERE id = 1"
    ).fetchone()
    if not row:
        return None
    return {
        "source_name": row[0] or "master.csv",
        "updated_by": row[1] or "system",
        "updated_at": row[2] or "unknown",
    }


def load_master_dataset_for_admin():
    db_df, db_source, db_error = load_master_dataset_from_db()
    if db_df is not None:
        return db_df, db_source, None
    if db_error:
        return None, None, db_error

    candidates = [
        Path(__file__).resolve().parent / "cx_retention_customers_full_dataset.csv",
        Path.home() / "Downloads" / "cx_retention_customers_full_dataset.csv",
    ]
    for path in candidates:
        if path.exists():
            try:
                full_df = pd.read_csv(path)
                prepared, error_msg = prepare_integrated_customer_df(full_df)
                if error_msg:
                    continue
                # Seed DB master when local file is available.
                save_master_dataset(full_df.to_csv(index=False), path.name, "system")
                return prepared, str(path), None
            except Exception as err:
                return None, None, str(err)
    return None, None, None


def build_weekly_focus_report(df_input: pd.DataFrame, top_action_df: pd.DataFrame) -> str:
    total_accounts = int(len(df_input))
    high_risk = int((df_input["risk_level"] == "High Risk").sum()) if total_accounts else 0
    medium_risk = int((df_input["risk_level"] == "Medium Risk").sum()) if total_accounts else 0
    revenue_at_risk = float(df_input[df_input["risk_level"] == "High Risk"]["plan_value"].sum()) if total_accounts else 0.0

    owner_top = (
        df_input.groupby("owner", as_index=False)
        .agg(
            accounts=("customer_name", "count"),
            high_risk=("risk_level", lambda s: int((s == "High Risk").sum())),
        )
        .sort_values(["high_risk", "accounts"], ascending=[False, False])
        .head(5)
    )

    buffer = StringIO()
    buffer.write("WEEKLY CSM FOCUS REPORT\n")
    buffer.write("=======================\n\n")
    buffer.write("PORTFOLIO SUMMARY\n")
    buffer.write("-----------------\n")
    buffer.write(f"Total Accounts      : {total_accounts}\n")
    buffer.write(f"High Risk Accounts  : {high_risk}\n")
    buffer.write(f"Medium Risk Accounts: {medium_risk}\n")
    buffer.write(f"Revenue At Risk     : {revenue_at_risk:,.0f}\n\n")

    buffer.write("TOP OWNER FOCUS\n")
    buffer.write("---------------\n")
    if len(owner_top) == 0:
        buffer.write("No owner data available.\n\n")
    else:
        for _, row in owner_top.iterrows():
            buffer.write(
                f"- {row['owner']}: {int(row['high_risk'])} high-risk out of {int(row['accounts'])} accounts\n"
            )
        buffer.write("\n")

    buffer.write("PRIORITY ACCOUNT ACTIONS (TOP 10)\n")
    buffer.write("---------------------------------\n")
    if len(top_action_df) == 0:
        buffer.write("No priority accounts identified.\n")
    else:
        for _, row in top_action_df.head(10).iterrows():
            buffer.write(
                f"- {row['Customer']} | Owner: {row['CSM Owner']} | Risk: {row['Risk']} | "
                f"Act Before: {row['Act Before']} | Action: {row['Recommended Action']}\n"
            )
    return buffer.getvalue()


def prepare_multisource_customer_df(
    customers_df: pd.DataFrame,
    feature_adoption_df: pd.DataFrame,
    usage_df: pd.DataFrame,
    subscriptions_df: pd.DataFrame,
):
    err = validate_required_columns(
        customers_df,
        ["customer_id", "company_name", "account_owner", "customer_since"],
        "new_customers.csv",
    )
    if err:
        return None, err

    err = validate_required_columns(
        feature_adoption_df,
        ["customer_id", "adoption_percentage", "last_used_days"],
        "feature_adoption.csv",
    )
    if err:
        return None, err

    err = validate_required_columns(
        usage_df,
        ["customer_id", "month", "login_frequency", "renewal_risk_score", "health_score", "shadow_it_apps_detected"],
        "usage_metrics.csv",
    )
    if err:
        return None, err

    err = validate_required_columns(
        subscriptions_df,
        ["customer_id", "annual_contract_value", "contract_start", "contract_end", "renewal_status"],
        "subscriptions.csv",
    )
    if err:
        return None, err

    base = customers_df.copy()
    base["customer_id"] = base["customer_id"].astype(str).str.strip()
    base["company_name"] = base["company_name"].astype(str).str.strip()

    usage = usage_df.copy()
    usage["customer_id"] = usage["customer_id"].astype(str).str.strip()
    usage["month_dt"] = pd.to_datetime(usage["month"], errors="coerce")
    usage = usage.sort_values(["customer_id", "month_dt"])
    latest_usage = usage.groupby("customer_id", as_index=False).tail(1)

    adoption = feature_adoption_df.copy()
    adoption["customer_id"] = adoption["customer_id"].astype(str).str.strip()
    adoption["adoption_percentage"] = pd.to_numeric(adoption["adoption_percentage"], errors="coerce")
    adoption["last_used_days"] = pd.to_numeric(adoption["last_used_days"], errors="coerce")
    adoption_agg = (
        adoption.groupby("customer_id", as_index=False)
        .agg(
            avg_adoption_pct=("adoption_percentage", "mean"),
            stale_features=("last_used_days", lambda s: int((s.fillna(0) > 30).sum())),
        )
    )

    subs = subscriptions_df.copy()
    subs["customer_id"] = subs["customer_id"].astype(str).str.strip()
    subs["annual_contract_value"] = pd.to_numeric(subs["annual_contract_value"], errors="coerce")

    merged = base.merge(
        latest_usage[
            [
                "customer_id",
                "month",
                "login_frequency",
                "renewal_risk_score",
                "health_score",
                "shadow_it_apps_detected",
                "unused_licenses",
                "active_users",
            ]
        ],
        on="customer_id",
        how="left",
    ).merge(
        adoption_agg,
        on="customer_id",
        how="left",
    ).merge(
        subs[
            [
                "customer_id",
                "annual_contract_value",
                "contract_start",
                "contract_end",
                "renewal_status",
                "plan_type",
                "total_licenses",
            ]
        ],
        on="customer_id",
        how="left",
    )

    # Keep all customers from base and fill defaults for missing linked rows.
    merged["login_frequency"] = pd.to_numeric(merged["login_frequency"], errors="coerce").fillna(20)
    merged["renewal_risk_score"] = pd.to_numeric(merged["renewal_risk_score"], errors="coerce").fillna(35)
    merged["shadow_it_apps_detected"] = pd.to_numeric(merged["shadow_it_apps_detected"], errors="coerce").fillna(0)
    merged["avg_adoption_pct"] = pd.to_numeric(merged["avg_adoption_pct"], errors="coerce").fillna(50)
    merged["annual_contract_value"] = pd.to_numeric(merged["annual_contract_value"], errors="coerce").fillna(50000)
    merged["health_score"] = pd.to_numeric(merged["health_score"], errors="coerce").fillna(65)

    # Map to app-required schema.
    out = pd.DataFrame()
    out["customer_id"] = merged["customer_id"]
    out["customer_name"] = merged["company_name"]
    out["owner"] = merged["account_owner"].fillna("Assigned CSM")
    out["manager"] = "Manager"
    out["logins_last_30_days"] = merged["login_frequency"].round(0).astype(int)
    out["support_tickets"] = (
        (merged["renewal_risk_score"] / 12)
        + (merged["shadow_it_apps_detected"] / 2)
        + ((100 - merged["avg_adoption_pct"]) / 25)
    ).round(0).clip(lower=0).astype(int)
    out["plan_value"] = merged["annual_contract_value"].round(0).astype(int)

    # Extra useful fields for premium views.
    out["industry"] = merged.get("industry", "Unknown")
    out["segment"] = merged.get("segment", "Unknown")
    out["region"] = merged.get("region", "Unknown")
    out["customer_since"] = merged.get("customer_since", "")
    out["avg_adoption_pct"] = merged["avg_adoption_pct"].round(1)
    out["renewal_status"] = merged["renewal_status"].fillna("Active")
    out["plan_type"] = merged.get("plan_type", "Standard").fillna("Standard")
    out["contract_start"] = merged["contract_start"].fillna("")
    out["contract_end"] = merged["contract_end"].fillna("")
    out["reporting_month"] = merged["month"].fillna("N/A")

    return out, None


def prepare_integrated_customer_df(full_df: pd.DataFrame):
    required = [
        "customer_id",
        "company_name",
        "industry",
        "segment",
        "employees",
        "region",
        "plan_type",
        "contract_start",
        "contract_end",
        "annual_contract_value",
        "total_licenses",
        "active_users",
        "login_frequency",
        "unused_licenses",
        "shadow_it_apps_detected",
        "engagement_score",
        "renewal_risk_score",
        "health_score",
        "feature_adoption_score",
    ]
    copilot_required = [
        "Account_Name",
        "ARR",
        "Active_Users",
        "Monthly_Logins",
        "Feature_Usage_Score",
        "Support_Tickets_Last_30_Days",
        "CSAT",
        "NPS",
        "Last_Login_Days_Ago",
        "Renewal_Date",
        "Plan_Type",
    ]

    if all(col in full_df.columns for col in copilot_required):
        df = full_df.copy()
        df["Account_Name"] = df["Account_Name"].astype(str).str.strip()
        numeric_cols = [
            "ARR",
            "Active_Users",
            "Monthly_Logins",
            "Feature_Usage_Score",
            "Support_Tickets_Last_30_Days",
            "CSAT",
            "NPS",
            "Last_Login_Days_Ago",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        renewal_dates = pd.to_datetime(df["Renewal_Date"], errors="coerce")
        if renewal_dates.isna().any():
            return None, "Renewal_Date must be a valid date column."

        df["customer_id"] = [
            f"COPILOT-{str(i + 1).zfill(4)}"
            for i in range(len(df))
        ]
        df["company_name"] = df["Account_Name"]
        df["industry"] = "SaaS"
        df["segment"] = df["ARR"].apply(
            lambda value: "Enterprise" if value >= 150000 else ("Mid-Market" if value >= 50000 else "SMB")
        )
        df["employees"] = (df["Active_Users"] * 6).round(0).clip(lower=10).astype(int)
        df["region"] = "North America"
        df["plan_type"] = df["Plan_Type"]
        df["contract_end"] = renewal_dates.dt.strftime("%Y-%m-%d")
        df["contract_start"] = (renewal_dates - pd.to_timedelta(365, unit="D")).dt.strftime("%Y-%m-%d")
        df["annual_contract_value"] = df["ARR"].round(0).astype(int)
        df["active_users"] = df["Active_Users"].round(0).astype(int)
        df["total_licenses"] = (df["Active_Users"] * 1.15).round(0).clip(lower=df["Active_Users"]).astype(int)
        df["login_frequency"] = df["Monthly_Logins"].round(0).astype(int)
        df["unused_licenses"] = (df["total_licenses"] - df["active_users"]).clip(lower=0).astype(int)
        df["shadow_it_apps_detected"] = (
            (df["Support_Tickets_Last_30_Days"] / 2).round(0).clip(lower=0).astype(int)
        )
        df["engagement_score"] = (
            0.6 * (100 - (df["Last_Login_Days_Ago"].clip(0, 60) / 60 * 100))
            + 0.4 * ((df["Monthly_Logins"] / df["Monthly_Logins"].max()) * 100).fillna(50)
        ).clip(5, 100)
        df["feature_adoption_score"] = df["Feature_Usage_Score"].clip(0, 100)
        df["health_score"] = (
            0.35 * df["Feature_Usage_Score"]
            + 0.25 * ((df["CSAT"] / 10) * 100)
            + 0.20 * (((df["NPS"] + 100) / 200) * 100)
            + 0.20 * df["engagement_score"]
        ).clip(5, 100)
        df["renewal_risk_score"] = (
            100
            - (
                0.45 * df["health_score"]
                + 0.25 * df["feature_adoption_score"]
                + 0.15 * (100 - df["Support_Tickets_Last_30_Days"].clip(0, 12) / 12 * 100)
                + 0.15 * (100 - df["Last_Login_Days_Ago"].clip(0, 60) / 60 * 100)
            )
        ).clip(5, 95)
        full_df = df[required].copy()

    err = validate_required_columns(full_df, required, "cx_retention_customers_full_dataset.csv")
    if err:
        return None, err

    df = full_df.copy()
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df["company_name"] = df["company_name"].astype(str).str.strip()

    numeric_cols = [
        "annual_contract_value",
        "login_frequency",
        "shadow_it_apps_detected",
        "renewal_risk_score",
        "health_score",
        "feature_adoption_score",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["annual_contract_value"] = df["annual_contract_value"].fillna(50000)
    df["login_frequency"] = df["login_frequency"].fillna(20)
    df["shadow_it_apps_detected"] = df["shadow_it_apps_detected"].fillna(0)
    df["renewal_risk_score"] = df["renewal_risk_score"].fillna(35)
    df["feature_adoption_score"] = df["feature_adoption_score"].fillna(50)
    df["health_score"] = df["health_score"].fillna(65)

    out = pd.DataFrame()
    out["customer_id"] = df["customer_id"]
    out["customer_name"] = df["company_name"]
    out["logins_last_30_days"] = df["login_frequency"].round(0).astype(int)
    out["support_tickets"] = (
        (df["renewal_risk_score"] / 12)
        + (df["shadow_it_apps_detected"] / 2)
        + ((100 - df["feature_adoption_score"]) / 25)
    ).round(0).clip(lower=0).astype(int)
    out["plan_value"] = df["annual_contract_value"].round(0).astype(int)
    out["industry"] = df["industry"]
    out["segment"] = df["segment"]
    out["region"] = df["region"]
    out["plan_type"] = df["plan_type"]
    out["contract_start"] = df["contract_start"]
    out["contract_end"] = df["contract_end"]
    out["feature_adoption_score"] = df["feature_adoption_score"]
    out["avg_adoption_pct"] = df["feature_adoption_score"].round(1)
    out["reporting_month"] = "Latest"
    out["renewal_status"] = "Active"
    out = assign_csm_fields(out)
    return out, None


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


def get_user_profile(email: str):
    row = c.execute(
        "SELECT name, company, place FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    return row


def update_user_profile(email: str, name: str, company: str, place: str):
    c.execute(
        """
        UPDATE users
        SET name = ?, company = ?, place = ?
        WHERE email = ?
        """,
        (name, company, place, email),
    )
    conn.commit()


def update_user_password(email: str, new_password: str):
    c.execute(
        """
        UPDATE users
        SET password = ?
        WHERE email = ?
        """,
        (new_password, email),
    )
    conn.commit()


def build_presentation_report(selected_row: pd.Series, options: list, ai_summary_text: str | None) -> str:
    def summary_points(text: str | None) -> list[str]:
        if not text:
            return ["Summary not generated yet. Use 'Generate AI Executive Summary' in the app."]
        lines = [seg.strip() for seg in text.replace("\n", " ").split(".") if seg.strip()]
        return lines[:4] if lines else [text.strip()]

    buffer = StringIO()
    buffer.write("CX ACCOUNT STRATEGY REPORT\n")
    buffer.write("==========================\n\n")
    buffer.write("ACCOUNT SNAPSHOT\n")
    buffer.write("----------------\n")
    buffer.write(f"Account Name         : {selected_row['customer_name']}\n")
    buffer.write(f"CSM Owner            : {selected_row['owner']}\n")
    buffer.write(f"Risk Level           : {selected_row['risk_level']}\n")
    buffer.write(f"Health Score         : {float(selected_row['health_score']):.1f}\n")
    buffer.write(f"Support Tickets (30d): {int(selected_row['support_tickets'])}\n")
    buffer.write(f"Plan Value           : {float(selected_row['plan_value']):,.0f}\n")
    buffer.write(f"Purchase Date        : {selected_row['purchase_date']}\n")
    buffer.write(f"Renewal Date         : {selected_row['renewal_date']}\n")
    buffer.write(f"Auto Renew Opt-Out   : {'Yes' if bool(selected_row['auto_renew_opt_out']) else 'No'}\n\n")

    buffer.write("TOP 3 RECOMMENDED PLAYS\n")
    buffer.write("-----------------------\n")
    for idx, opt in enumerate(options, start=1):
        buffer.write(f"{idx}. {opt['strategy']}\n")
        buffer.write(f"   Impact Score : {opt['impact_score']}/100\n")
        buffer.write(f"   Act Before   : {opt['act_before']}\n")
        buffer.write(f"   Play         : {opt['play']}\n")
    buffer.write("\n")

    buffer.write("AI EXECUTIVE SUMMARY (KEY POINTS)\n")
    buffer.write("---------------------------------\n")
    for point in summary_points(ai_summary_text):
        buffer.write(f"- {point}\n")

    return buffer.getvalue()


def build_simple_pdf_from_text(text: str) -> bytes:
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    wrapped_lines = []
    for raw in text.splitlines():
        parts = textwrap.wrap(raw, width=95) or [""]
        wrapped_lines.extend(parts)

    lines_per_page = 45
    pages = [wrapped_lines[i:i + lines_per_page] for i in range(0, len(wrapped_lines), lines_per_page)] or [[""]]

    objects = []
    kids_refs = []

    # 1: Catalog, 2: Pages, 3: Font
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(None)  # Pages placeholder
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    obj_num = 4
    for page_lines in pages:
        page_obj = obj_num
        content_obj = obj_num + 1
        kids_refs.append(f"{page_obj} 0 R")

        stream_lines = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
        for line in page_lines:
            stream_lines.append(f"({esc(line)}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        stream_bytes = stream.encode("latin-1", errors="replace")

        page_dict = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj} 0 R >>"
        )
        content_dict = f"<< /Length {len(stream_bytes)} >>\nstream\n{stream}\nendstream"

        objects.append(page_dict)
        objects.append(content_dict)
        obj_num += 2

    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids_refs)}] /Count {len(kids_refs)} >>"

    pdf = "%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf.encode("latin-1", errors="replace")))
        pdf += f"{i} 0 obj\n{obj}\nendobj\n"

    xref_start = len(pdf.encode("latin-1", errors="replace"))
    pdf += f"xref\n0 {len(objects)+1}\n"
    pdf += "0000000000 65535 f \n"
    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n"
    pdf += f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF"

    return pdf.encode("latin-1", errors="replace")


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


def render_strategy_table(options: list):
    rows = []
    for opt in options:
        rows.append(
            "<tr>"
            f"<td>{escape(opt['strategy'])}</td>"
            f"<td><span class='impact-pill'>{int(opt['impact_score'])}/100</span></td>"
            f"<td>{escape(opt['play'])}</td>"
            f"<td>{escape(opt['act_before'])}</td>"
            "</tr>"
        )

    header = (
        "<thead><tr>"
        "<th>Strategy</th>"
        "<th>Impact Score</th>"
        "<th>Recommended Play</th>"
        "<th>Act Before</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='strategy-table-wrap'><table class='strategy-table'>"
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


def render_premium_command_center(df_input: pd.DataFrame, selected_row: pd.Series | None, selected_customer_label: str):
    is_all_customers = selected_row is None
    if is_all_customers:
        health = float(df_input["health_score"].mean()) if len(df_input) else 0.0
        tickets = int(df_input["support_tickets"].mean()) if len(df_input) else 0
        plan_value = float(df_input["plan_value"].sum()) if len(df_input) else 0.0
        next_renewal = min(df_input["renewal_date"].tolist()) if len(df_input) else "-"
        renewal_date = str(next_renewal)
        auto_opt_out = bool(df_input["auto_renew_opt_out"].sum() > 0) if len(df_input) else False
        top_idx = df_input["priority_score"].idxmax() if len(df_input) else None
        focus_row = df_input.loc[top_idx] if top_idx is not None else None
        avg_adoption = float(df_input["avg_adoption_pct"].mean()) if "avg_adoption_pct" in df_input.columns and len(df_input) else 0.0
        report_month = str(df_input["reporting_month"].mode().iloc[0]) if "reporting_month" in df_input.columns and len(df_input) else "N/A"
    else:
        health = float(selected_row["health_score"])
        tickets = int(selected_row["support_tickets"])
        plan_value = float(selected_row["plan_value"])
        renewal_date = str(selected_row["renewal_date"])
        auto_opt_out = bool(selected_row["auto_renew_opt_out"])
        focus_row = selected_row
        avg_adoption = float(selected_row.get("avg_adoption_pct", 0))
        report_month = str(selected_row.get("reporting_month", "N/A"))

    st.markdown(
        """
        <div class="premium-hero">
            <div class="premium-hero-title">Premium CX Intelligence Command Center</div>
            <div class="premium-hero-sub">Now analyzing: """ + escape(str(selected_customer_label)) + """</div>
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
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Risk Level</div><div class='premium-kpi-value'>{escape(str(focus_row['risk_level']) if focus_row is not None else '-')}</div></div>",
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
    c5, c6 = st.columns(2)
    c5.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Avg Adoption %</div><div class='premium-kpi-value'>{avg_adoption:.1f}</div></div>",
        unsafe_allow_html=True,
    )
    c6.markdown(
        f"<div class='premium-kpi'><div class='premium-kpi-label'>Reporting Month</div><div class='premium-kpi-value'>{escape(report_month)}</div></div>",
        unsafe_allow_html=True,
    )

    options = recommend_options_for_row(focus_row) if focus_row is not None else []
    suggestion = recommend_action_for_row(focus_row) if focus_row is not None else "No recommendation available."
    st.markdown(
        f"""
        <div class="premium-zone suggestion-card">
            <div class="suggestion-title">Suggested Play For {escape(str(selected_customer_label))}</div>
            <div>{escape(suggestion)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if options:
        render_strategy_table(options)
        report_target = focus_row if is_all_customers else selected_row
        report_text = build_presentation_report(
            report_target,
            options,
            st.session_state.get("ai_summary_text"),
        )
        report_pdf = build_simple_pdf_from_text(report_text)
        file_label = "all_customers" if is_all_customers else str(selected_row["customer_name"])
        st.download_button(
            "Download Presentation Report",
            data=report_pdf,
            file_name=f"{file_label}_cx_strategy_report.pdf",
            mime="application/pdf",
        )

    tab1, tab2, tab3 = st.tabs(["Focus Areas", "Renewal Lens", "Delta Insights"])

    with tab1:
        focus_rows = [
            {"Focus Area": "Product Adoption", "Signal": "Low" if health < 55 else "Healthy", "What To Do": "Drive weekly usage milestones + role-based onboarding."},
            {"Focus Area": "Support Burden", "Signal": "High" if tickets >= 5 else "Controlled", "What To Do": "Resolve top recurring ticket themes before renewal cycle."},
            {"Focus Area": "Renewal Commitment", "Signal": "At Risk" if auto_opt_out else "Stable", "What To Do": "Confirm value recap and lock commercial terms early."},
        ]
        focus_html = "<div class='premium-zone'>"
        for row in focus_rows:
            focus_html += (
                "<div class='focus-item'>"
                f"<div class='focus-title'>{escape(row['Focus Area'])}</div>"
                f"<div class='focus-signal'>Signal: {escape(row['Signal'])}</div>"
                f"<div class='focus-action'>{escape(row['What To Do'])}</div>"
                "</div>"
            )
        focus_html += "</div>"
        st.markdown(focus_html, unsafe_allow_html=True)

    with tab2:
        c5, c6, c7 = st.columns(3)
        c5.markdown(
            f"<div class='premium-kpi'><div class='premium-kpi-label'>Support Tickets (30d)</div><div class='premium-kpi-value'>{tickets}</div></div>",
            unsafe_allow_html=True,
        )
        c6.markdown(
            f"<div class='premium-kpi'><div class='premium-kpi-label'>Auto Renew Opt-Out</div><div class='premium-kpi-value'>{'Yes' if auto_opt_out else 'No'}</div></div>",
            unsafe_allow_html=True,
        )
        c7.markdown(
            f"<div class='premium-kpi'><div class='premium-kpi-label'>Primary Strategy</div><div class='premium-kpi-value'>{escape(options[0]['strategy']) if options else '-'}</div></div>",
            unsafe_allow_html=True,
        )
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


def build_data_quality_summary(df_input: pd.DataFrame, source_name: str) -> dict:
    total_rows = int(len(df_input))
    total_columns = int(len(df_input.columns))
    missing_cells = int(df_input.isna().sum().sum())
    duplicate_customers = 0
    if "customer_name" in df_input.columns:
        duplicate_customers = int(df_input["customer_name"].astype(str).str.strip().duplicated().sum())
    invalid_renewal_dates = 0
    if "renewal_date" in df_input.columns:
        parsed = pd.to_datetime(df_input["renewal_date"], errors="coerce")
        invalid_renewal_dates = int(parsed.isna().sum())
    return {
        "source_name": source_name,
        "total_rows": total_rows,
        "total_columns": total_columns,
        "missing_cells": missing_cells,
        "duplicate_customers": duplicate_customers,
        "invalid_renewal_dates": invalid_renewal_dates,
        "quality_score": max(0, 100 - (missing_cells // 5) - (duplicate_customers * 5) - (invalid_renewal_dates * 3)),
    }


def render_data_quality_panel(summary: dict):
    st.subheader("Data Quality Check")
    st.caption(f"Latest upload: {summary['source_name']}")
    cards = [
        ("Rows", f"{summary['total_rows']:,}"),
        ("Columns", f"{summary['total_columns']}"),
        ("Missing Cells", f"{summary['missing_cells']:,}"),
        ("Duplicate Accounts", f"{summary['duplicate_customers']:,}"),
        ("Invalid Renewal Dates", f"{summary['invalid_renewal_dates']:,}"),
        ("Quality Score", f"{summary['quality_score']}/100"),
    ]
    html = "<div class='kpi-grid'>"
    for label, value in cards:
        html += (
            "<div class='kpi-card'>"
            f"<div class='kpi-card-label'>{escape(label)}</div>"
            f"<div class='kpi-card-value'>{escape(str(value))}</div>"
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("---")


def build_action_table(df_input: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    work = df_input.copy()
    work["renewal_dt"] = pd.to_datetime(work["renewal_date"], errors="coerce")
    today = pd.Timestamp(date.today())
    work["days_to_renewal"] = (work["renewal_dt"] - today).dt.days
    work["days_to_renewal"] = work["days_to_renewal"].fillna(9999).astype(int)
    work["risk_weight"] = work["risk_level"].map({"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}).fillna(1)
    work["urgency_score"] = (
        work["priority_score"].astype(float)
        + (work["risk_weight"] * 20)
        + (120 - work["days_to_renewal"].clip(lower=0, upper=120))
    )
    top = work.sort_values("urgency_score", ascending=False).head(limit).copy()
    top["Act Before"] = top["renewal_dt"].apply(
        lambda d: (d - pd.Timedelta(days=30)).strftime("%Y-%m-%d") if pd.notna(d) else "-"
    )
    top["Recommended Action"] = top.apply(
        lambda r: recommend_options_for_row(r)[0]["strategy"] if pd.notna(r.get("renewal_dt")) else "Enablement Plan",
        axis=1,
    )
    return top[
        [
            "customer_name",
            "owner",
            "risk_level",
            "plan_value",
            "renewal_date",
            "days_to_renewal",
            "Act Before",
            "Recommended Action",
            "urgency_score",
        ]
    ].rename(
        columns={
            "customer_name": "Customer",
            "owner": "CSM Owner",
            "risk_level": "Risk",
            "plan_value": "Plan Value",
            "renewal_date": "Renewal Date",
            "days_to_renewal": "Days To Renewal",
            "urgency_score": "Urgency Score",
        }
    )


def render_renewal_risk_widgets(df_input: pd.DataFrame):
    today = date.today()
    renewal_dates = pd.to_datetime(df_input["renewal_date"], errors="coerce")
    days_out = (renewal_dates.dt.date - today).apply(lambda d: d.days if pd.notna(d) else None)
    high_risk_count = int((df_input["risk_level"] == "High Risk").sum())
    high_risk_revenue = float(df_input[df_input["risk_level"] == "High Risk"]["plan_value"].sum())
    next_30 = int(((days_out >= 0) & (days_out <= 30)).sum())
    next_60 = int(((days_out >= 0) & (days_out <= 60)).sum())
    next_90 = int(((days_out >= 0) & (days_out <= 90)).sum())

    st.subheader("Renewal & Risk Watch")
    cards = [
        ("High Risk Accounts", f"{high_risk_count}"),
        ("Revenue At Risk", f"{high_risk_revenue:,.0f}"),
        ("Renewals in 30 Days", f"{next_30}"),
        ("Renewals in 60 Days", f"{next_60}"),
        ("Renewals in 90 Days", f"{next_90}"),
    ]
    html = "<div class='kpi-grid kpi-grid-5'>"
    for label, value in cards:
        html += (
            "<div class='kpi-card'>"
            f"<div class='kpi-card-label'>{escape(label)}</div>"
            f"<div class='kpi-card-value'>{escape(str(value))}</div>"
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("---")


def render_priority_accounts_table(df_input: pd.DataFrame):
    rows = []
    for _, row in df_input.iterrows():
        risk = str(row["Risk"])
        if risk == "High Risk":
            badge_class = "risk-badge risk-high"
        elif risk == "Medium Risk":
            badge_class = "risk-badge risk-medium"
        else:
            badge_class = "risk-badge risk-low"

        days = int(row["Days To Renewal"])
        if days < 0:
            days_text = f"<span class='days-overdue'>Overdue by {abs(days)}d</span>"
        else:
            days_text = f"<span class='days-upcoming'>{days}d left</span>"

        rows.append(
            "<tr>"
            f"<td>{escape(str(row['Customer']))}</td>"
            f"<td>{escape(str(row['CSM Owner']))}</td>"
            f"<td><span class='{badge_class}'>{escape(risk)}</span></td>"
            f"<td>{float(row['Plan Value']):,.0f}</td>"
            f"<td>{escape(str(row['Renewal Date']))}</td>"
            f"<td>{days_text}</td>"
            f"<td>{escape(str(row['Act Before']))}</td>"
            f"<td>{escape(str(row['Recommended Action']))}</td>"
            f"<td>{float(row['Urgency Score']):.1f}</td>"
            "</tr>"
        )

    header = (
        "<thead><tr>"
        "<th>Customer</th>"
        "<th>CSM Owner</th>"
        "<th>Risk</th>"
        "<th>Plan Value</th>"
        "<th>Renewal Date</th>"
        "<th>Time To Renewal</th>"
        "<th>Act Before</th>"
        "<th>Recommended Action</th>"
        "<th>Urgency Score</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='priority-table-wrap'><table class='priority-table'>"
        + header
        + body
        + "</table></div>",
        unsafe_allow_html=True,
    )


def render_owner_rollup_table(df_input: pd.DataFrame):
    rows = []
    for _, row in df_input.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(row['CSM Owner']))}</td>"
            f"<td>{int(row['Accounts'])}</td>"
            f"<td>{int(row['High Risk'])}</td>"
            f"<td>{float(row['Avg Health']):.1f}</td>"
            f"<td>{float(row['Total ACV']):,.0f}</td>"
            "</tr>"
        )
    header = (
        "<thead><tr>"
        "<th>CSM Owner</th>"
        "<th>Accounts</th>"
        "<th>High Risk</th>"
        "<th>Avg Health</th>"
        "<th>Total ACV</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='light-table-wrap'><table class='light-table'>"
        + header
        + body
        + "</table></div>",
        unsafe_allow_html=True,
    )


def render_assignment_table(df_input: pd.DataFrame):
    rows = []
    for _, row in df_input.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(row['Customer']))}</td>"
            f"<td>{escape(str(row['Assigned To']))}</td>"
            f"<td>{escape(str(row['Role']))}</td>"
            "</tr>"
        )
    header = (
        "<thead><tr>"
        "<th>Customer</th>"
        "<th>Assigned To</th>"
        "<th>Role</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(rows) + "</tbody>"
    st.markdown(
        "<div class='light-table-wrap'><table class='light-table'>"
        + header
        + body
        + "</table></div>",
        unsafe_allow_html=True,
    )


def build_portfolio_report(
    df_input: pd.DataFrame,
    top_action_df: pd.DataFrame,
    selected_csm: str,
    selected_segment: str,
    selected_region: str,
    selected_plan: str,
) -> str:
    def fixed_row(values, widths):
        out = []
        for val, w in zip(values, widths):
            txt = str(val)
            if len(txt) > w:
                txt = txt[: w - 3] + "..."
            out.append(txt.ljust(w))
        return " | ".join(out)

    total_accounts = int(len(df_input))
    high_risk_accounts = int((df_input["risk_level"] == "High Risk").sum()) if total_accounts else 0
    revenue_at_risk = float(df_input[df_input["risk_level"] == "High Risk"]["plan_value"].sum()) if total_accounts else 0.0
    avg_health = float(df_input["health_score"].mean()) if total_accounts else 0.0

    renewal_dates = pd.to_datetime(df_input["renewal_date"], errors="coerce")
    days_to_renewal = (renewal_dates.dt.date - date.today()).apply(lambda d: d.days if pd.notna(d) else None)
    renewals_60 = int(((days_to_renewal >= 0) & (days_to_renewal <= 60)).sum())

    owner_rollup = (
        df_input.groupby("owner", as_index=False)
        .agg(
            accounts=("customer_name", "count"),
            high_risk=("risk_level", lambda s: int((s == "High Risk").sum())),
            avg_health=("health_score", "mean"),
            plan_value=("plan_value", "sum"),
        )
        .sort_values(["high_risk", "accounts", "plan_value"], ascending=[False, False, False])
    )

    buffer = StringIO()
    buffer.write("CX PORTFOLIO MBR REPORT\n")
    buffer.write("=======================\n\n")
    buffer.write("FILTER SUMMARY\n")
    buffer.write("--------------\n")
    buffer.write(f"CSM Filter     : {selected_csm}\n")
    buffer.write(f"Segment Filter : {selected_segment}\n")
    buffer.write(f"Region Filter  : {selected_region}\n")
    buffer.write(f"Plan Filter    : {selected_plan}\n\n")

    buffer.write("PORTFOLIO KPI SNAPSHOT\n")
    buffer.write("----------------------\n")
    buffer.write(f"Total Accounts         : {total_accounts}\n")
    buffer.write(f"High Risk Accounts     : {high_risk_accounts}\n")
    buffer.write(f"Revenue At Risk        : {revenue_at_risk:,.0f}\n")
    buffer.write(f"Average Health Score   : {avg_health:.1f}\n")
    buffer.write(f"Renewals in 60 Days    : {renewals_60}\n\n")

    buffer.write("CSM PERFORMANCE ROLLUP\n")
    buffer.write("----------------------\n")
    if len(owner_rollup) == 0:
        buffer.write("No owner-level rows in current filter scope.\n\n")
    else:
        widths = [16, 9, 9, 10, 14]
        buffer.write(fixed_row(["Owner", "Accounts", "HighRisk", "AvgHealth", "TotalACV"], widths) + "\n")
        buffer.write("-" * 68 + "\n")
        for _, row in owner_rollup.iterrows():
            buffer.write(
                fixed_row(
                    [
                        row["owner"],
                        int(row["accounts"]),
                        int(row["high_risk"]),
                        f"{float(row['avg_health']):.1f}",
                        f"{float(row['plan_value']):,.0f}",
                    ],
                    widths,
                )
                + "\n"
            )
        buffer.write("\n")

    buffer.write("PRIORITY ACCOUNTS THIS WEEK\n")
    buffer.write("---------------------------\n")
    if len(top_action_df) == 0:
        buffer.write("No priority accounts found in current scope.\n")
    else:
        widths = [18, 12, 9, 12, 12, 16]
        buffer.write(
            fixed_row(
                ["Customer", "Owner", "Risk", "Renewal", "ActBefore", "Action"],
                widths,
            )
            + "\n"
        )
        buffer.write("-" * 92 + "\n")
        for idx, row in top_action_df.head(10).iterrows():
            buffer.write(
                fixed_row(
                    [
                        f"{idx + 1}. {row['Customer']}",
                        row["CSM Owner"],
                        row["Risk"],
                        row["Renewal Date"],
                        row["Act Before"],
                        row["Recommended Action"],
                    ],
                    widths,
                )
                + "\n"
            )
    return buffer.getvalue()


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

if "user_role" not in st.session_state:
    st.session_state.user_role = None

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

    st.markdown(
        """
        <div class='landing-hero'>
            <div class='landing-kicker'>Customer Success Platform</div>
            <div class='landing-title'>Customer Retention &amp; Growth Engine</div>
            <div class='landing-subtitle'>
                A premium workspace for Customer Success teams to track risk, organize account ownership,
                and move from reactive updates to proactive retention execution.
            </div>
            <div class='landing-chip-row'>
                <div class='landing-chip'>Portfolio Visibility</div>
                <div class='landing-chip'>Renewal Risk Tracking</div>
                <div class='landing-chip'>CSM Assignment</div>
                <div class='landing-chip'>AI Copilot Connected</div>
            </div>
            <div class='landing-stat-grid'>
                <div class='landing-stat-card'>
                    <div class='landing-stat-value'>1</div>
                    <div class='landing-stat-label'>Shared workspace for retention reviews, owner updates, and leadership visibility</div>
                </div>
                <div class='landing-stat-card'>
                    <div class='landing-stat-value'>3</div>
                    <div class='landing-stat-label'>Core decisions in one flow: prioritize, assign, and take action</div>
                </div>
                <div class='landing-stat-card'>
                    <div class='landing-stat-value'>24/7</div>
                    <div class='landing-stat-label'>Portfolio access for CSM leads and assigned team members</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.force_login_view:
        st.session_state["premium_option"] = "Login"
        st.session_state.force_login_view = False
    st.markdown("<div class='auth-toggle-wrap'>", unsafe_allow_html=True)
    option = st.radio("Premium Access", ["Login", "Sign Up"], key="premium_option", horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)
        st.session_state.signup_success = None

    if option == "Login":
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div class='auth-card auth-card-demo'>
                    <div class='auth-card-kicker'>Explore The Product</div>
                    <div class='auth-card-title'>Try Demo</div>
                    <div class='auth-card-copy'>
                        Enter the guided demo environment to review the experience, dashboards, and workflow
                        without setting up your own account.
                    </div>
                    <div class='auth-accent-demo'>Best for quick walkthroughs and interface previews</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            demo_user = st.text_input("Username", key="demo_user")
            demo_pass = st.text_input("Password", type="password", key="demo_password")

            if st.button("Login Demo"):
                if demo_user.lower() == "freeuser" and demo_pass == "123456":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "demo"
                    st.session_state.user_name = "Freeuser"
                    st.session_state.user_email = "demo@local"
                    st.session_state.user_role = "demo"
                    st.rerun()
                else:
                    st.error("Invalid Demo Credentials")

        with col2:
            st.markdown(
                """
                <div class='auth-card auth-card-premium'>
                    <div class='auth-card-kicker'>Premium Workspace</div>
                    <div class='auth-card-title'>Use My CSV</div>
                    <div class='auth-card-copy'>
                        Sign in to access the full retention workspace with uploads, customer assignment,
                        risk monitoring, and premium analytics.
                    </div>
                    <div class='auth-accent-premium'>Best for live account review, ownership, and executive retention workflows</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="premium_password")

            if st.button("Login Premium"):
                login_email = email.strip().lower()
                login_password = password.strip()
                c.execute(
                    "SELECT name, company, email, place, password, COALESCE(role, 'csm') FROM users WHERE email=? AND password=?",
                    (login_email, login_password),
                )
                user = c.fetchone()
                if user:
                    domain = email_domain(login_email)
                    if domain:
                        admin_count = c.execute(
                            "SELECT COUNT(*) FROM users WHERE role='admin' AND lower(email) LIKE ?",
                            (f"%@{domain}",),
                        ).fetchone()[0]
                        if admin_count == 0:
                            c.execute("UPDATE users SET role='admin' WHERE email=?", (login_email,))
                            conn.commit()
                            user = (user[0], user[1], user[2], user[3], user[4], "admin")
                    st.session_state.logged_in = True
                    st.session_state.user_type = "premium"
                    st.session_state.user_name = user[0]
                    st.session_state.user_email = user[2]
                    st.session_state.user_role = user[5] or "csm"
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    else:
        _, col_mid, _ = st.columns([1, 1.2, 1])
        with col_mid:
            st.markdown(
                """
                <div class='signup-shell'>
                    <div class='auth-card-kicker'>Premium Onboarding</div>
                    <div class='auth-card-title'>Create your Customer Success workspace</div>
                    <div class='auth-card-copy'>
                        Set up a premium account for your company domain and start managing customer health,
                        assignments, and retention workflows in one place.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
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
                elif "@" not in signup_email:
                    st.error("Please enter a valid company email.")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        domain = email_domain(signup_email)
                        admin_count = c.execute(
                            "SELECT COUNT(*) FROM users WHERE role='admin' AND lower(email) LIKE ?",
                            (f"%@{domain}",),
                        ).fetchone()[0]
                        signup_role = "admin" if admin_count == 0 else "csm"
                        c.execute(
                            "INSERT INTO users (name, company, email, place, password, role) VALUES (?,?,?,?,?,?)",
                            (signup_name, signup_company, signup_email, signup_place, signup_password, signup_role),
                        )
                        conn.commit()
                        st.session_state.force_login_view = True
                        st.session_state.signup_success = (
                            "Account created successfully. "
                            + ("You are set as Admin for your company domain. " if signup_role == "admin" else "")
                            + "Please login with Premium."
                        )
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Email already registered")
                    except Exception as err:
                        st.error(f"Account creation failed: {err}")

    st.stop()

# =============================
# HEADER
# =============================

colA, colB = st.columns([7, 3])

with colA:
    st.markdown(
        """
        <div class='header-hero'>
            <div class='header-kicker'>Premium CX Workspace</div>
            <div class='header-title'>Customer Retention &amp; Growth Engine</div>
            <div class='header-subtitle'>
                Centralize account health, renewal risk, customer ownership, and action planning in one
                workspace built for CSM leads and frontline execution.
            </div>
            <div class='header-chip-row'>
                <div class='header-chip'>Retention Operations</div>
                <div class='header-chip'>Renewal Visibility</div>
                <div class='header-chip'>CSM Assignment Control</div>
                <div class='header-chip'>AI Copilot Connected</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.user_type == "premium":
        master_meta = get_master_dataset_meta()
        if master_meta:
            st.markdown(
                f"<span class='data-source-badge'>Data Source: Company Master ({escape(str(master_meta['source_name']))})</span>",
                unsafe_allow_html=True,
            )

with colB:
    if st.session_state.user_type == "demo":
        role_label = "Demo"
    else:
        role_label = "Admin" if st.session_state.get("user_role") == "admin" else "CSM"
    st.markdown("<div class='account-panel-shell'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='account-panel'>
            <div class='account-panel-label'>Signed In As</div>
            <div class='account-panel-name'>{escape(str(st.session_state.user_name))}</div>
            <div class='account-panel-role'>{escape(role_label)} access</div>
            <div class='account-panel-spacer'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='account-toolbar-label'>Quick Actions</div>", unsafe_allow_html=True)
    st.markdown("<div class='account-action-stack'>", unsafe_allow_html=True)
    if st.session_state.user_type == "premium" and st.session_state.user_email:
        with st.popover("Open Account Center"):
            profile = get_user_profile(st.session_state.user_email)
            current_name = profile[0] if profile else st.session_state.user_name
            current_company = profile[1] if profile else ""
            current_place = profile[2] if profile else ""

            st.markdown("**Edit Profile**")
            with st.form("edit_profile_form"):
                new_name = st.text_input("Name", value=current_name)
                new_company = st.text_input("Company", value=current_company)
                new_place = st.text_input("Place", value=current_place)
                save_profile = st.form_submit_button("Save Profile", type="secondary")
                if save_profile:
                    update_user_profile(
                        st.session_state.user_email,
                        new_name.strip(),
                        new_company.strip(),
                        new_place.strip(),
                    )
                    st.session_state.user_name = new_name.strip() or st.session_state.user_name
                    st.success("Profile updated.")

            st.markdown("**Settings (Change Password)**")
            with st.form("change_password_form"):
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                confirm_pwd = st.text_input("Confirm New Password", type="password")
                change_pwd = st.form_submit_button("Change Password", type="secondary")
                if change_pwd:
                    db_row = c.execute(
                        "SELECT password FROM users WHERE email = ?",
                        (st.session_state.user_email,),
                    ).fetchone()
                    if not db_row or db_row[0] != current_pwd.strip():
                        st.error("Current password is incorrect.")
                    elif not new_pwd.strip():
                        st.error("New password cannot be empty.")
                    elif new_pwd.strip() != confirm_pwd.strip():
                        st.error("New passwords do not match.")
                    else:
                        update_user_password(st.session_state.user_email, new_pwd.strip())
                        st.success("Password changed successfully.")

    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Self-help floating widget (bottom-right) - render before data gating
template_headers = [
    "customer_id",
    "company_name",
    "industry",
    "segment",
    "employees",
    "region",
    "plan_type",
    "contract_start",
    "contract_end",
    "annual_contract_value",
    "total_licenses",
    "active_users",
    "login_frequency",
    "unused_licenses",
    "shadow_it_apps_detected",
    "engagement_score",
    "renewal_risk_score",
    "health_score",
    "feature_adoption_score",
]
template_href = build_csv_download_data_uri(template_headers)

st.markdown(
    f"""
    <details class="help-widget" open>
      <summary class="help-head">Self Help</summary>
      <div class="help-body">
        <b>CSV Format & Templates</b><br/>
        <a href="{template_href}" download="cx_retention_customers_full_dataset_template.csv">Download CSV Template</a><br/><br/>
        <b>What is AI Executive Summary?</b><br/>
        A quick account-level strategy summary with top risk, opportunity, and immediate actions.<br/><br/>
        <b>What is Focus Area?</b><br/>
        Priority zones for the selected customer: adoption, support burden, and renewal commitment.<br/><br/>
        <b>What is Premium CX Intelligence Command Center?</b><br/>
        The premium decision workspace that shows strategy options, impact scores, act-before dates, and delta insights.
      </div>
    </details>
    """,
    unsafe_allow_html=True,
)

# =============================
# DATA
# =============================

if st.session_state.user_type == "demo":
    df = pd.DataFrame({
        "customer_name": ["Alpha", "Beta", "Gamma", "Delta", "Omega"],
        "owner": ["Aisha", "Rahul", "Aisha", "David", "Rahul"],
        "manager": ["Meera", "Meera", "Arjun", "Arjun", "Meera"],
        "segment": ["SMB", "Mid-Market", "Enterprise", "SMB", "Enterprise"],
        "region": ["North America", "EMEA", "APAC", "North America", "EMEA"],
        "plan_type": ["Starter", "Growth", "Enterprise", "Starter", "Enterprise"],
        "logins_last_30_days": [25, 5, 18, 3, 30],
        "support_tickets": [2, 7, 3, 8, 1],
        "plan_value": [1500, 900, 2000, 800, 3000]
    })
else:
    master_df, master_path, master_error = load_master_dataset_for_admin()
    if master_df is not None:
        df = master_df
        st.session_state["last_upload_quality"] = build_data_quality_summary(df, Path(master_path).name)
        st.markdown(
            f"<div class='data-status-card'>Master dataset ready: DB Master ({escape(Path(master_path).name)})</div>",
            unsafe_allow_html=True,
        )
    else:
        if master_error:
            st.warning(f"Master dataset could not be loaded: {master_error}")
        is_admin_user = st.session_state.get("user_role") == "admin"
        if is_admin_user:
            st.info("No master dataset found. Upload once as CSM Lead to set company master data.")
            up_full = st.file_uploader(
                "Upload Master CSV (CSM Lead)",
                type=["csv"],
                key="up_full_dataset",
            )
            if up_full:
                full_df = pd.read_csv(up_full)
                df, error_msg = prepare_integrated_customer_df(full_df)
                if error_msg:
                    show_csv_error_popup(error_msg)
                    st.stop()

                save_master_dataset(
                    csv_text=full_df.to_csv(index=False),
                    source_name=up_full.name,
                    updated_by=st.session_state.user_email or "admin",
                )
                st.session_state["last_upload_quality"] = build_data_quality_summary(df, up_full.name)
                st.success(
                    f"Master dataset saved and loaded: {len(df)} customers."
                )
            else:
                st.stop()
        else:
            st.warning("Master CSV not found yet. Ask your CSM Lead (Admin) to upload the company master dataset.")
            st.stop()

df = enrich_contract_fields(df)
df = apply_assignment_overlay(df)

if st.session_state.user_type == "premium":
    master_meta = get_master_dataset_meta()
    if master_meta:
        st.markdown(
            f"""
            <div class="meta-card">
              Master Dataset: <b>{escape(str(master_meta['source_name']))}</b><br/>
              Last Updated By: <b>{escape(str(master_meta['updated_by']))}</b><br/>
              Last Updated At: <b>{escape(str(master_meta['updated_at']))}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

if st.session_state.user_type == "premium" and st.session_state.get("user_role") == "admin":
    with st.expander("Admin Access - Assign Customers to CSM", expanded=True):
        team_rows = get_same_domain_users(st.session_state.user_email, include_admin=True)
        if len(team_rows) == 0:
            st.info("No team members found in your domain yet.")
        else:
            assignment_customers = st.multiselect(
                "Select Customer(s)",
                sorted(df["customer_name"].astype(str).tolist()),
                key="admin_assign_customers",
            )
            member_labels = {
                f"{name} ({email}) - {role.upper()}": email
                for name, email, role in team_rows
            }
            selected_member_label = st.selectbox(
                "Assign To",
                list(member_labels.keys()),
                key="admin_assign_member",
            )
            if st.button("Assign Selected Customers", key="admin_assign_btn"):
                if not assignment_customers:
                    st.warning("Select at least one customer to assign.")
                else:
                    assignee_email = member_labels[selected_member_label]
                    for customer_name in assignment_customers:
                        upsert_customer_assignment(
                            customer_name=str(customer_name),
                            assigned_email=assignee_email,
                            assigned_by=st.session_state.user_email,
                        )
                    st.success(f"{len(assignment_customers)} customer(s) assigned to {selected_member_label}.")
                    st.rerun()

        assign_map = get_assignment_map()
        if len(assign_map) > 0:
            assigned_rows = []
            name_rows = c.execute("SELECT email, name, role FROM users").fetchall()
            meta = {str(r[0]).lower(): {"name": str(r[1]), "role": str(r[2])} for r in name_rows}
            for cust in sorted(df["customer_name"].astype(str).tolist()):
                email = assign_map.get(cust, "")
                if email:
                    info = meta.get(email, {"name": "Unknown", "role": "csm"})
                    assigned_rows.append(
                        {
                            "Customer": cust,
                            "Assigned To": f"{info['name']} ({email})",
                            "Role": str(info["role"]).upper(),
                        }
                    )
            if assigned_rows:
                st.caption("Current assignments in this uploaded dataset")
                render_assignment_table(pd.DataFrame(assigned_rows))
        else:
            st.caption("No assignments yet. Assign customers to control CSM visibility.")

if st.session_state.user_type == "premium" and st.session_state.get("user_role") != "admin":
    st.info("Admin access is available only for CSM Lead accounts. Assigned customers are shown for your login.")
    df = filter_visible_accounts(df, st.session_state.user_email, st.session_state.get("user_role", "csm"))
    if len(df) == 0:
        st.warning("No customers assigned to your account yet. Please contact your CSM Lead (Admin).")
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

if st.session_state.user_type == "premium":
    if st.session_state.get("last_upload_quality"):
        render_data_quality_panel(st.session_state["last_upload_quality"])
    update_snapshot_state(df)

# =============================
# OVERVIEW
# =============================

st.subheader("Customer Overview")

if st.session_state.user_type == "premium":
    is_admin = st.session_state.get("user_role") == "admin"
    csm_options = ["All CSM"] + sorted(df["owner"].dropna().unique().tolist())
    segment_options = ["All Segments"] + sorted(df["segment"].dropna().astype(str).unique().tolist())
    region_options = ["All Regions"] + sorted(df["region"].dropna().astype(str).unique().tolist())
    plan_options = ["All Plans"] + sorted(df["plan_type"].dropna().astype(str).unique().tolist())

    if is_admin:
        f1, f2, f3, f4 = st.columns(4)
        selected_csm = f1.selectbox("Select CSM", csm_options, key="premium_csm_select")
        selected_segment = f2.selectbox("Select Segment", segment_options, key="premium_segment_select")
        selected_region = f3.selectbox("Select Region", region_options, key="premium_region_select")
        selected_plan = f4.selectbox("Select Plan", plan_options, key="premium_plan_select")
    else:
        f1, f2, f3 = st.columns(3)
        selected_csm = st.session_state.user_name or "My Accounts"
        selected_segment = f1.selectbox("Select Segment", segment_options, key="premium_segment_select")
        selected_region = f2.selectbox("Select Region", region_options, key="premium_region_select")
        selected_plan = f3.selectbox("Select Plan", plan_options, key="premium_plan_select")

    scoped_df = df.copy()
    if is_admin and selected_csm != "All CSM":
        scoped_df = scoped_df[scoped_df["owner"] == selected_csm]
    if selected_segment != "All Segments":
        scoped_df = scoped_df[scoped_df["segment"] == selected_segment]
    if selected_region != "All Regions":
        scoped_df = scoped_df[scoped_df["region"] == selected_region]
    if selected_plan != "All Plans":
        scoped_df = scoped_df[scoped_df["plan_type"] == selected_plan]

    customer_options = ["All Customers"] + scoped_df["customer_name"].tolist()
    selected_customer = st.selectbox("Select Customer", customer_options, key="premium_customer_select")
else:
    selected_customer = st.selectbox("Select Customer", df["customer_name"], key="demo_customer_select")
    scoped_df = df.copy()
    selected_csm = "Demo Scope"
    selected_segment = "All Segments"
    selected_region = "All Regions"
    selected_plan = "All Plans"

selected_row = None if selected_customer == "All Customers" else scoped_df[scoped_df["customer_name"] == selected_customer].iloc[0]
summary_key = f"{selected_csm}:{selected_customer}" if st.session_state.user_type == "premium" else selected_customer
if st.session_state.get("ai_summary_for_customer") != summary_key:
    st.session_state["ai_summary_text"] = None
    st.session_state["ai_summary_for_customer"] = summary_key

if st.session_state.user_type == "premium":
    st.subheader("CSM Lead Portfolio Snapshot")
    portfolio_total = int(len(scoped_df))
    portfolio_high = int((scoped_df["risk_level"] == "High Risk").sum()) if portfolio_total else 0
    portfolio_medium = int((scoped_df["risk_level"] == "Medium Risk").sum()) if portfolio_total else 0
    portfolio_revenue_at_risk = float(scoped_df[scoped_df["risk_level"] == "High Risk"]["plan_value"].sum()) if portfolio_total else 0
    snapshot_cards = [
        ("Accounts in Scope", f"{portfolio_total}"),
        ("High Risk", f"{portfolio_high}"),
        ("Medium Risk", f"{portfolio_medium}"),
        ("Revenue At Risk", f"{portfolio_revenue_at_risk:,.0f}"),
    ]
    snapshot_html = "<div class='kpi-grid kpi-grid-4'>"
    for label, value in snapshot_cards:
        snapshot_html += (
            "<div class='kpi-card'>"
            f"<div class='kpi-card-label'>{escape(label)}</div>"
            f"<div class='kpi-card-value'>{escape(str(value))}</div>"
            "</div>"
        )
    snapshot_html += "</div>"
    st.markdown(snapshot_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class='copilot-link-card'>
            <div class='copilot-link-kicker'>Shared Intelligence Layer</div>
            <div class='copilot-link-title'>Open Customer Success AI Copilot</div>
            <div class='copilot-link-copy'>
                Explore your customer portfolio through the AI Copilot to surface churn signals,
                spot expansion potential, and review guided recommendations for the next best move.
            </div>
            <div class='copilot-link-note'>Use this when you want a faster executive view of what needs attention, what can expand, and what action a CSM should take next.</div>
            <div class='copilot-link-cta-row'>
                <div class='copilot-link-cta-copy'><strong>Best for:</strong> churn review, expansion review, and AI-guided account actions.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(
        "Open CSM AI Copilot",
        CSM_AI_COPILOT_URL,
        type="primary",
        width="stretch",
    )

    owner_rollup = (
        scoped_df.groupby("owner", as_index=False)
        .agg(
            accounts=("customer_name", "count"),
            high_risk=("risk_level", lambda s: int((s == "High Risk").sum())),
            avg_health=("health_score", "mean"),
            revenue=("plan_value", "sum"),
        )
        .sort_values(["high_risk", "accounts", "revenue"], ascending=[False, False, False])
        if len(scoped_df)
        else pd.DataFrame(columns=["owner", "accounts", "high_risk", "avg_health", "revenue"])
    )
    st.caption("Owner rollup for leadership visibility")
    owner_rollup_view = owner_rollup.rename(
        columns={
            "owner": "CSM Owner",
            "accounts": "Accounts",
            "high_risk": "High Risk",
            "avg_health": "Avg Health",
            "revenue": "Total ACV",
        }
    )
    render_owner_rollup_table(owner_rollup_view)
    st.markdown("---")

    render_renewal_risk_widgets(scoped_df)
    st.subheader("Priority Accounts This Week")
    top_action_df = build_action_table(scoped_df, limit=10)
    render_priority_accounts_table(top_action_df)
    st.download_button(
        "Download Top 10 Action List",
        data=top_action_df.to_csv(index=False).encode("utf-8"),
        file_name="top_10_accounts_needing_action.csv",
        mime="text/csv",
    )
    weekly_focus_report = build_weekly_focus_report(scoped_df, top_action_df)
    st.download_button(
        "Download Weekly CSM Focus Report (PDF)",
        data=build_simple_pdf_from_text(weekly_focus_report),
        file_name="weekly_csm_focus_report.pdf",
        mime="application/pdf",
    )
    portfolio_report = build_portfolio_report(
        scoped_df,
        top_action_df,
        selected_csm=selected_csm,
        selected_segment=selected_segment,
        selected_region=selected_region,
        selected_plan=selected_plan,
    )
    st.download_button(
        "Download Portfolio MBR (PDF)",
        data=build_simple_pdf_from_text(portfolio_report),
        file_name="portfolio_mbr_report.pdf",
        mime="application/pdf",
    )
    st.markdown("---")

# Premium view should focus selected customer only.
if st.session_state.user_type == "premium":
    premium_overview_df = scoped_df if selected_customer == "All Customers" else scoped_df[scoped_df["customer_name"] == selected_customer]
    render_customer_overview_table(
        premium_overview_df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]]
    )
else:
    render_customer_overview_table(
        df[["customer_name", "owner", "health_score", "risk_level", "priority_score"]]
    )

st.markdown(
    f"""
    <div class='suggestion-card'>
        <div class='suggestion-title'>Contract Snapshot: {escape(str(selected_customer))}</div>
        <div>Purchase Date: <b>{escape(str(selected_row['purchase_date']) if selected_row is not None else 'Mixed')}</b></div>
        <div>Renewal Date: <b>{escape(str(selected_row['renewal_date']) if selected_row is not None else 'Multiple')}</b></div>
        <div>Auto Renew Opt-Out: <b>{('Yes' if bool(selected_row['auto_renew_opt_out']) else 'No') if selected_row is not None else 'Mixed'}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Premium-only advanced section
if st.session_state.user_type == "premium":
    render_premium_command_center(scoped_df, selected_row, selected_customer)

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
        summary_df = scoped_df if st.session_state.user_type == "premium" else df
        st.session_state["ai_summary_text"] = build_ai_summary(summary_df, selected_row)
        st.session_state["ai_summary_for_customer"] = summary_key
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
