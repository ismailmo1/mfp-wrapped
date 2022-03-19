from datetime import datetime, timedelta

import streamlit as st

from app_utils import load_mfp_data

with st.sidebar:
    mfp_user = st.text_input(
        "myfitnesspal username", "ismailmo1", placeholder="username"
    )
    today = datetime.now().date()
    try:
        start_date, end_date = st.date_input(
            "Date range to analyse",
            value=(today - timedelta(weeks=1), today),
            max_value=today,
        )
    except ValueError:
        st.warning("you must pick a date range (two dates)!")
    st.caption("Don't forget to make your diary public!")

    start_btn = st.button("Get Data")

st.title("myfitnesspal wrapped 🌯")


if start_btn:
    diary_df = load_mfp_data(start_date, end_date)
    st.write(f"{len(diary_df)} food entries")

    # st.write(df_21)
    col_1, col_2, col_3, col_4 = st.columns(4)

    col_1.metric("Calories", diary_df["calories_kcal"].sum(), delta="100%")
    col_2.metric("Carbs", diary_df["carbs_g"].sum(), delta="100%")
    col_3.metric("Fats", diary_df["fat_g"].sum(), delta="100%")
    col_4.metric("Protein", diary_df["protein_g"].sum(), delta="100%")

    st.header("most common food entries")

    st.bar_chart(
        diary_df.groupby("food")
        .count()["date"]
        .sort_values(ascending=False)[0:10]
    )
