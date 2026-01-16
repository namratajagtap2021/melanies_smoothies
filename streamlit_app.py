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

