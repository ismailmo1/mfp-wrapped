from datetime import datetime, timedelta

import streamlit as st

from app_utils import load_mfp_data, show_metrics
from myfitnesspal.analysis import (
    plot_macro_treemap,
    plot_most_common,
    total_logged_days,
    total_macros,
)

st.set_page_config("Wrapped", page_icon="burrito.png", layout="wide")

with st.sidebar:
    mfp_user = st.text_input(
        "myfitnesspal username", "ismailmo", placeholder="username"
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
    diary_df = load_mfp_data(start_date, end_date, mfp_user)
    st.metric(
        "Total days logged",
        f"{total_logged_days(diary_df)}/{(end_date-start_date).days +1}",
    )

    st.header("Totals")
    show_metrics(total_macros(diary_df))
    st.plotly_chart(plot_most_common(diary_df), use_container_width=True)
    st.plotly_chart(plot_macro_treemap(diary_df), use_container_width=True)
