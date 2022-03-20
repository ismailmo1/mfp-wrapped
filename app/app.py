from datetime import datetime, timedelta

import streamlit as st
from numerize import numerize as nz

from app_utils import load_mfp_data
from myfitnesspal.analysis import plot_most_common, total_logged_days

st.set_page_config("Wrapped", page_icon="burrito.png")

with st.sidebar:
    mfp_user = st.text_input(
        "myfitnesspal username", "ismailmo1", placeholder="username"
    )
    st.caption("Don't forget to make your diary public!")
    today = datetime.now().date()
    try:
        start_date, end_date = st.date_input(
            "Date range to analyse",
            value=(today - timedelta(weeks=1), today),
            max_value=today,
        )
    except ValueError:
        st.warning("you must pick a date range (start date - end date)!")

    start_btn = st.button("Get Data")

st.title("myfitnesspal wrapped 🌯")

starter_msg = st.empty()
starter_img = st.empty()

starter_msg.markdown(
    """Inspired by Spotify's [Wrapped]\
(https://en.wikipedia.org/wiki/Spotify_Wrapped) marketing campaign

← Enter your mfp username in the sidebar, make your diary public and
let's see what you've been eating!"""
)

with starter_img.expander("Analysis awaits!"):
    st.image("himym.jpg", caption="what you can look forward to")

if start_btn:
    starter_msg.empty()
    starter_img.empty()
    diary_df = load_mfp_data(start_date, end_date)
    st.metric(
        "Total days logged",
        f"{total_logged_days(diary_df)}/{(end_date-start_date).days +1}",
    )

    st.write(f"{len(diary_df)} total food line entries")

    # st.write(df_21)
    col_1, col_2, col_3, col_4 = st.columns(4)

    col_1.metric(
        "Calories (kcal)", nz.numerize(int(diary_df["calories_kcal"].sum()))
    )
    col_2.metric("Carbs (g)", nz.numerize(int(diary_df["carbs_g"].sum())))
    col_3.metric("Fats (g)", nz.numerize(int(diary_df["fat_g"].sum())))
    col_4.metric("Protein (g)", nz.numerize(int(diary_df["protein_g"].sum())))

    st.plotly_chart(plot_most_common(diary_df), use_container_width=True)
