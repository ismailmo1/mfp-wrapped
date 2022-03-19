from datetime import datetime, timedelta

import streamlit as st
from numerize import numerize as nz

from app_utils import load_mfp_data
from myfitnesspal.analysis import plot_most_common

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

    col_1.metric(
        "Calories (kcal)", nz.numerize(int(diary_df["calories_kcal"].sum()))
    )
    col_2.metric("Carbs (g)", nz.numerize(int(diary_df["carbs_g"].sum())))
    col_3.metric("Fats (g)", nz.numerize(int(diary_df["fat_g"].sum())))
    col_4.metric("Protein (g)", nz.numerize(int(diary_df["protein_g"].sum())))

    st.plotly_chart(plot_most_common(diary_df), use_container_width=True)
