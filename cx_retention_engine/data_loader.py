from __future__ import annotations

from datetime import date, timedelta
from io import StringIO
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "cx_retention_engine.db"

REQUIRED_COLUMNS = [
    "Account_Name",
    "Customer_ID",
    "CSM_Owner",
    "ARR",
    "Plan_Type",
    "Active_Users",
    "Monthly_Logins",
    "Feature_Usage_Score",
    "Support_Tickets_Last_30_Days",
    "CSAT",
    "NPS",
    "Last_Login_Days_Ago",
    "Renewal_Date",
]

RETENTION_MASTER_COLUMNS = [
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

def _normalize_retention_master(df_input: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    missing = [column for column in RETENTION_MASTER_COLUMNS if column not in df_input.columns]
    if missing:
        return None, f"Missing required columns: {', '.join(missing)}"

    df = df_input[RETENTION_MASTER_COLUMNS].copy()
    df["company_name"] = df["company_name"].astype(str).str.strip()
    df = df[df["company_name"] != ""]

    numeric_columns = [
        "annual_contract_value",
        "active_users",
        "login_frequency",
        "feature_adoption_score",
        "renewal_risk_score",
        "health_score",
        "shadow_it_apps_detected",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[numeric_columns].isna().any().any():
        return None, "Some numeric fields could not be parsed. Please check the uploaded CSV."

    renewal_dates = pd.to_datetime(df["contract_end"], errors="coerce")
    if renewal_dates.isna().any():
        return None, "contract_end must be a valid date column."

    normalized = pd.DataFrame()
    normalized["Account_Name"] = df["company_name"]
    normalized["Customer_ID"] = df["customer_id"].astype(str).str.strip()
    normalized["CSM_Owner"] = "Unassigned"
    normalized["ARR"] = df["annual_contract_value"].round(0).astype(int)
    normalized["Plan_Type"] = df["plan_type"].astype(str)
    normalized["Active_Users"] = df["active_users"].round(0).astype(int)
    normalized["Monthly_Logins"] = df["login_frequency"].round(0).astype(int)
    normalized["Feature_Usage_Score"] = df["feature_adoption_score"].clip(0, 100).round(1)
    normalized["Support_Tickets_Last_30_Days"] = (
        (df["renewal_risk_score"] / 12)
        + (df["shadow_it_apps_detected"] / 2)
        + ((100 - df["feature_adoption_score"]) / 25)
    ).round(0).clip(lower=0).astype(int)
    normalized["CSAT"] = (df["health_score"].clip(0, 100) / 10).round(1).clip(0, 10)
    normalized["NPS"] = ((df["engagement_score"].clip(0, 100) - 50) * 2).round(1).clip(-100, 100)
    normalized["Last_Login_Days_Ago"] = (
        30 - ((df["login_frequency"] / df["login_frequency"].max()) * 25).fillna(12)
    ).round(0).clip(lower=0, upper=60).astype(int)
    normalized["Renewal_Date"] = renewal_dates.dt.strftime("%Y-%m-%d")

    empty_mask = (normalized["Customer_ID"] == "") | (normalized["Customer_ID"] == "nan")
    if empty_mask.any():
        normalized.loc[empty_mask, "Customer_ID"] = [f"CX-A{i:04d}" for i in range(1, empty_mask.sum() + 1)]

    return normalized[REQUIRED_COLUMNS].reset_index(drop=True), None

DEFAULT_ADMIN = {
    "name": "Rohith PM",
    "company": "RPM",
    "email": "rpm6105@gmail.com",
    "place": "India",
    "password": "123456",
    "role": "admin",
}


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def init_database() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            company TEXT,
            email TEXT PRIMARY KEY,
            place TEXT,
            password TEXT,
            role TEXT DEFAULT 'csm'
        )
        """
    )
    cur.execute(
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
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_assignments (
            customer_id TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            assigned_email TEXT NOT NULL,
            assigned_by TEXT,
            assigned_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            owner_email TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    seed_default_admin(conn)
    conn.close()


def seed_default_admin(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    existing = cur.execute(
        "SELECT email FROM users WHERE lower(email) = ?",
        (DEFAULT_ADMIN["email"],),
    ).fetchone()
    payload = (
        DEFAULT_ADMIN["name"],
        DEFAULT_ADMIN["company"],
        DEFAULT_ADMIN["place"],
        DEFAULT_ADMIN["password"],
        DEFAULT_ADMIN["role"],
        DEFAULT_ADMIN["email"],
    )
    if existing:
        cur.execute(
            """
            UPDATE users
            SET name = ?, company = ?, place = ?, password = ?, role = ?
            WHERE lower(email) = ?
            """,
            payload,
        )
    else:
        cur.execute(
            """
            INSERT INTO users (name, company, email, place, password, role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                DEFAULT_ADMIN["name"],
                DEFAULT_ADMIN["company"],
                DEFAULT_ADMIN["email"],
                DEFAULT_ADMIN["place"],
                DEFAULT_ADMIN["password"],
                DEFAULT_ADMIN["role"],
            ),
        )
    conn.commit()


def email_domain(email: str) -> str:
    parts = (email or "").split("@")
    return parts[1].lower().strip() if len(parts) == 2 else ""


def list_users() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT name, company, email, place, role FROM users ORDER BY role DESC, name ASC",
        conn,
    )
    conn.close()
    return df


def get_user_by_credentials(email: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT name, company, email, place, password, COALESCE(role, 'csm') FROM users WHERE lower(email)=? AND password=?",
        (email.strip().lower(), password.strip()),
    ).fetchone()
    conn.close()
    return row


def create_user(name: str, company: str, email: str, place: str, password: str) -> tuple[bool, str, str]:
    conn = get_connection()
    cur = conn.cursor()
    login_email = email.strip().lower()
    domain = email_domain(login_email)
    admin_count = cur.execute(
        "SELECT COUNT(*) FROM users WHERE role='admin' AND lower(email) LIKE ?",
        (f"%@{domain}",),
    ).fetchone()[0]
    role = "admin" if admin_count == 0 else "csm"
    try:
        cur.execute(
            "INSERT INTO users (name, company, email, place, password, role) VALUES (?, ?, ?, ?, ?, ?)",
            (name.strip(), company.strip(), login_email, place.strip(), password.strip(), role),
        )
        conn.commit()
        return True, role, ""
    except sqlite3.IntegrityError:
        return False, role, "Email already registered"
    finally:
        conn.close()


def update_user_profile(email: str, name: str, company: str, place: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE users SET name = ?, company = ?, place = ? WHERE lower(email) = ?",
        (name, company, place, email.lower()),
    )
    conn.commit()
    conn.close()


def update_user_password(email: str, password: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password = ? WHERE lower(email) = ?",
        (password, email.lower()),
    )
    conn.commit()
    conn.close()


def generate_sample_dataset(num_accounts: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    owners = ["Aisha", "Rahul", "Meera", "Karthik", "David", "Nina"]
    plans = ["Starter", "Growth", "Enterprise"]
    rows = []
    today = date.today()
    for idx in range(1, num_accounts + 1):
        plan = rng.choice(plans, p=[0.35, 0.4, 0.25])
        arr = int(rng.integers(9000, 210000))
        active_users = int(rng.integers(8, 950))
        feature_usage = float(np.clip(rng.normal(68, 18), 8, 98))
        csat = float(np.clip(rng.normal(7.4, 1.3), 3.5, 10))
        nps = float(np.clip(rng.normal(42, 24), -10, 95))
        monthly_logins = int(np.clip(active_users * rng.uniform(0.7, 4.5), 12, 4500))
        last_login_days = int(np.clip(rng.normal(14, 12), 0, 75))
        tickets = int(np.clip(rng.poisson(3), 0, 18))
        renewal_date = today + timedelta(days=int(rng.integers(5, 365)))
        rows.append(
            {
                "Account_Name": f"Account_{idx:03d}",
                "Customer_ID": f"CX-{idx:04d}",
                "CSM_Owner": str(rng.choice(owners)),
                "ARR": arr,
                "Plan_Type": plan,
                "Active_Users": active_users,
                "Monthly_Logins": monthly_logins,
                "Feature_Usage_Score": round(feature_usage, 1),
                "Support_Tickets_Last_30_Days": tickets,
                "CSAT": round(csat, 1),
                "NPS": round(nps, 1),
                "Last_Login_Days_Ago": last_login_days,
                "Renewal_Date": renewal_date.isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_sample_csv() -> bytes:
    return generate_sample_dataset(25).to_csv(index=False).encode("utf-8")


def validate_dataset(df_input: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    if all(column in df_input.columns for column in RETENTION_MASTER_COLUMNS):
        return _normalize_retention_master(df_input)

    df = df_input.copy()
    
    if "Customer_ID" not in df.columns:
        if "customer_id" in df.columns:
            df["Customer_ID"] = df["customer_id"].astype(str).str.strip()
        else:
            df["Customer_ID"] = [f"CX-P{i:04d}" for i in range(1, len(df) + 1)]
            
    if "CSM_Owner" not in df.columns:
        df["CSM_Owner"] = "Unassigned"

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return None, "Missing required columns: " + ", ".join(missing)

    normalized = df[REQUIRED_COLUMNS].copy()
    normalized["Account_Name"] = normalized["Account_Name"].astype(str).str.strip()
    normalized["Customer_ID"] = normalized["Customer_ID"].astype(str).str.strip()
    normalized["CSM_Owner"] = normalized["CSM_Owner"].astype(str).str.strip()
    normalized["Plan_Type"] = normalized["Plan_Type"].astype(str).str.strip()
    numeric_columns = [
        "ARR",
        "Active_Users",
        "Monthly_Logins",
        "Feature_Usage_Score",
        "Support_Tickets_Last_30_Days",
        "CSAT",
        "NPS",
        "Last_Login_Days_Ago",
    ]
    for col in numeric_columns:
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
    normalized["Renewal_Date"] = pd.to_datetime(normalized["Renewal_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return normalized, None


def store_master_dataset(df: pd.DataFrame, source_name: str, updated_by: str) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO master_dataset (id, source_name, csv_text, updated_by, updated_at)
        VALUES (1, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            source_name=excluded.source_name,
            csv_text=excluded.csv_text,
            updated_by=excluded.updated_by,
            updated_at=datetime('now')
        """,
        (source_name, df.to_csv(index=False), updated_by),
    )
    conn.commit()
    conn.close()


def load_master_dataset() -> tuple[pd.DataFrame | None, dict | None]:
    conn = get_connection()
    row = conn.execute(
        "SELECT source_name, csv_text, updated_by, updated_at FROM master_dataset WHERE id = 1"
    ).fetchone()
    conn.close()
    if not row:
        return None, None
    df = pd.read_csv(StringIO(row[1]))
    meta = {
        "source_name": row[0],
        "updated_by": row[2],
        "updated_at": row[3],
    }
    return df, meta


def get_assignment_map() -> dict[str, str]:
    conn = get_connection()
    rows = conn.execute("SELECT customer_id, assigned_email FROM customer_assignments").fetchall()
    conn.close()
    return {str(customer_id): str(email).lower() for customer_id, email in rows}


def list_assignments() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT customer_id, account_name, assigned_email, assigned_by, assigned_at FROM customer_assignments ORDER BY account_name ASC",
        conn,
    )
    conn.close()
    return df


def assign_customers(df: pd.DataFrame, customer_ids: list[str], assigned_email: str, assigned_by: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    for customer_id in customer_ids:
        match = df[df["Customer_ID"] == customer_id]
        if match.empty:
            continue
        account_name = str(match.iloc[0]["Account_Name"])
        cur.execute(
            """
            INSERT INTO customer_assignments (customer_id, account_name, assigned_email, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(customer_id) DO UPDATE SET
                account_name=excluded.account_name,
                assigned_email=excluded.assigned_email,
                assigned_by=excluded.assigned_by,
                assigned_at=datetime('now')
            """,
            (customer_id, account_name, assigned_email.lower(), assigned_by.lower()),
        )
    conn.commit()
    conn.close()


def apply_assignments(df: pd.DataFrame) -> pd.DataFrame:
    assignments = list_assignments()
    if assignments.empty:
        output = df.copy()
        output["Assigned_Email"] = ""
        return output
    merged = df.merge(assignments[["customer_id", "assigned_email"]], left_on="Customer_ID", right_on="customer_id", how="left")
    merged = merged.drop(columns=["customer_id"])
    merged = merged.rename(columns={"assigned_email": "Assigned_Email"})
    merged["Assigned_Email"] = merged["Assigned_Email"].fillna("")
    return merged


def filter_dataset_for_user(df: pd.DataFrame, user_email: str, role: str) -> pd.DataFrame:
    if role == "admin" or role == "demo":
        return df.copy()
    if "Assigned_Email" not in df.columns:
        return df.iloc[0:0].copy()
    return df[df["Assigned_Email"].str.lower() == user_email.lower()].copy()
