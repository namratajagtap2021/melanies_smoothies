'''
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("🧋 Customize Your Smoothie!")

st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

session = get_active_session()

# Get the list of fruit names as plain Python strings for multiselect options
fruit_options_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)
fruit_options = fruit_options_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

if ingredients_list:
    # Join ingredients into a single string for storage
    ingredients_string = " ".join(ingredients_list).strip()
    st.write(ingredients_string)

    # Build a safe INSERT statement that matches TWO columns
    insert_sql = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(insert_sql)  # optional: for debugging; remove once verified

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        # Basic validation before insert
        if not name_on_order.strip():
            st.error("Please enter a name for the smoothie before submitting.")
        else:
            # Execute the insert
            session.sql(insert_sql).collect()
            st.success("Your Smoothie is ordered! ✅")

'''

# -*- coding: utf-8 -*-
import streamlit as st
import os
from snowflake.snowpark.functions import col

# Try to get active session (works in Snowsight / Streamlit in Snowflake)
def get_session():
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        # Fallback: build a session from environment variables (for local/Codespaces)
        from snowflake.snowpark import Session
        from dotenv import load_dotenv
        load_dotenv()

        acct = os.getenv("SNOW_ACCOUNT")
        user = os.getenv("SNOW_USER")
        pwd = os.getenv("SNOW_PASSWORD")
        role = os.getenv("SNOW_ROLE", "ACCOUNTADMIN")
        wh   = os.getenv("SNOW_WAREHOUSE", "COMPUTE_WH")
        db   = os.getenv("SNOW_DATABASE", "SMOOTHIES")
        sch  = os.getenv("SNOW_SCHEMA", "PUBLIC")

        missing = [k for k,v in {
            "SNOW_ACCOUNT":acct,
            "SNOW_USER":user,
            "SNOW_PASSWORD":pwd
        }.items() if not v]
        if missing:
            st.error(
                "🚨 No Snowflake session found and required env vars are missing: "
                + ", ".join(missing)
                + "\n\nRun this app in **Snowflake Snowsight** (preferred), "
                  "or create a `.env` with your Snowflake credentials."
            )
            st.stop()

        return Session.builder.configs({
            "account": acct,
            "user": user,
            "password": pwd,
            "role": role,
            "warehouse": wh,
            "database": db,
            "schema": sch
        }).create()

st.title("🧋 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

# Create/get session
session = get_session()

# Fetch fruit options
fruit_options_df = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"))
           .to_pandas()
)
fruit_options = fruit_options_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list).strip()
    st.write(ingredients_string)

    # Simple sanitization to avoid quote issues in literals
    safe_ingredients = ingredients_string.replace("'", "''")
    safe_name = (name_on_order or "").replace("'", "''")

    insert_sql = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
    """
    st.code(insert_sql, language="sql")

    if st.button("Submit Order"):
        if not safe_name.strip():
            st.error("Please enter a name for the smoothie before submitting.")
        else:
            try:
                session.sql(insert_sql).collect()
                st.success("Your Smoothie is ordered! ✅")
            except Exception as e:
                st.error(f"Insert failed: {e}")

