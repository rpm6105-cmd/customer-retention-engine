from __future__ import annotations

from datetime import date, datetime
import uuid

import pandas as pd
import streamlit as st

from cx_retention_engine.data_loader import get_connection

TASK_STATUSES = ["Open", "In Progress", "Completed"]
TASK_TYPES = ["Renewal Review", "Success Plan", "Executive Touchpoint", "Product Training", "Upsell Follow-up"]


def load_tasks() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY due_date ASC, created_at DESC", conn)
    conn.close()
    return df


def create_task(customer_id: str, account_name: str, task_type: str, owner_email: str, due_date: str, status: str, notes: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (task_id, customer_id, account_name, task_type, owner_email, due_date, status, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            uuid.uuid4().hex[:8],
            customer_id,
            account_name,
            task_type,
            owner_email,
            due_date,
            status,
            notes,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def update_task_status(task_id: str, status: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()


def render_task_tracker(accounts_df: pd.DataFrame, visible_tasks: pd.DataFrame, current_email: str) -> None:
    st.subheader("Task Tracker")
    options = accounts_df[["Customer_ID", "Account_Name"]].drop_duplicates().sort_values("Account_Name")
    with st.expander("Create Task", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            selected_label = st.selectbox(
                "Account",
                [f"{row.Customer_ID} | {row.Account_Name}" for row in options.itertuples(index=False)],
                key="task_account_select",
            )
            task_type = st.selectbox("Task Type", TASK_TYPES, key="task_type_select")
            due = st.date_input("Due Date", value=date.today(), key="task_due_date")
        with c2:
            status = st.selectbox("Status", TASK_STATUSES, key="task_status_select")
            notes = st.text_area("Notes", key="task_notes")
            if st.button("Create Task", key="task_create_btn"):
                customer_id, account_name = [part.strip() for part in selected_label.split("|")]
                create_task(customer_id, account_name, task_type, current_email, due.isoformat(), status, notes.strip())
                st.success("Task created.")
                st.rerun()

    if visible_tasks.empty:
        st.info("No tasks available in the current scope.")
        return

    st.markdown("### Task Table")
    st.dataframe(
        visible_tasks[["account_name", "task_type", "owner_email", "due_date", "status", "notes"]].rename(
            columns={
                "account_name": "Account",
                "task_type": "Task Type",
                "owner_email": "Owner",
                "due_date": "Due Date",
                "status": "Status",
                "notes": "Notes",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Kanban")
    cols = st.columns(3)
    for idx, status in enumerate(TASK_STATUSES):
        with cols[idx]:
            st.markdown(f"**{status}**")
            subset = visible_tasks[visible_tasks["status"] == status]
            if subset.empty:
                st.caption("No tasks")
            for row in subset.itertuples(index=False):
                st.markdown(
                    f"""
                    <div style='padding:12px 14px;margin-bottom:10px;border-radius:16px;border:1px solid #dbe5f3;background:#ffffff;box-shadow:0 10px 18px rgba(28,43,70,0.05)'>
                        <div style='font-weight:800;color:#162033'>{row.account_name}</div>
                        <div style='margin-top:4px;color:#526177;font-size:13px'>{row.task_type}</div>
                        <div style='margin-top:6px;color:#6a7a90;font-size:12px'>Due {row.due_date}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                new_status = st.selectbox(
                    f"Status for {row.task_id}",
                    TASK_STATUSES,
                    index=TASK_STATUSES.index(row.status),
                    key=f"status_{row.task_id}",
                    label_visibility="collapsed",
                )
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Update", key=f"update_{row.task_id}"):
                        update_task_status(row.task_id, new_status)
                        st.rerun()
                with b2:
                    if st.button("Delete", key=f"delete_{row.task_id}"):
                        delete_task(row.task_id)
                        st.rerun()
