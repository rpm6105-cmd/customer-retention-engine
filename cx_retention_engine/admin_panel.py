from __future__ import annotations

import pandas as pd
import streamlit as st

from cx_retention_engine.data_loader import assign_customers, create_user, list_assignments, list_users, store_master_dataset, validate_dataset


def render_admin_panel(current_df: pd.DataFrame, user_email: str) -> None:
    st.subheader("Admin Panel")

    with st.expander("Upload or Refresh Master Dataset", expanded=True):
        upload = st.file_uploader("Upload Master CSV", type=["csv"], key="admin_master_upload")
        if upload is not None:
            raw_df = pd.read_csv(upload)
            validated, error = validate_dataset(raw_df)
            if error:
                st.error(error)
            else:
                store_master_dataset(validated, upload.name, user_email)
                st.success("Master dataset uploaded successfully.")
                st.rerun()
        if st.button("Refresh Data", key="admin_refresh_data"):
            st.rerun()

    with st.expander("Manage Users", expanded=False):
        users_df = list_users()
        st.dataframe(users_df, use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", key="admin_user_name")
            company = st.text_input("Company", key="admin_user_company")
            email = st.text_input("Email", key="admin_user_email")
        with c2:
            place = st.text_input("Place", key="admin_user_place")
            password = st.text_input("Password", type="password", key="admin_user_password")
            if st.button("Create User", key="admin_create_user"):
                ok, role, message = create_user(name, company, email, place, password)
                if ok:
                    st.success(f"User created with {role.upper()} role.")
                    st.rerun()
                else:
                    st.error(message)

    with st.expander("Assign Customers to CSM", expanded=False):
        users_df = list_users()
        csm_users = users_df[users_df["role"].str.lower() == "csm"]
        if csm_users.empty:
            st.info("Create at least one CSM user first.")
        else:
            account_options = current_df[["Customer_ID", "Account_Name"]].drop_duplicates().sort_values("Account_Name")
            selected_accounts = st.multiselect(
                "Select Accounts",
                account_options["Customer_ID"].tolist(),
                format_func=lambda customer_id: f"{customer_id} | {account_options.loc[account_options['Customer_ID'] == customer_id, 'Account_Name'].iloc[0]}",
                key="admin_assign_accounts",
            )
            user_options = {
                f"{row['name']} ({row['email']})": row["email"] for _, row in csm_users.iterrows()
            }
            selected_user = st.selectbox("Assign To", list(user_options.keys()), key="admin_assign_user")
            if st.button("Assign Selected Accounts", key="admin_assign_button"):
                if not selected_accounts:
                    st.warning("Select at least one account.")
                else:
                    assign_customers(current_df, selected_accounts, user_options[selected_user], user_email)
                    st.success("Accounts assigned successfully.")
                    st.rerun()

        assignments_df = list_assignments()
        if not assignments_df.empty:
            st.markdown("### Current Assignments")
            st.dataframe(assignments_df, use_container_width=True, hide_index=True)
