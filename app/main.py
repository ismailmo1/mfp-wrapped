"""
Entry point for streamlit app
"""
from datetime import datetime, timedelta

import streamlit as st

from app_utils import load_mfp_data, show_metrics
from myfitnesspal.analysis import (
    plot_intake_goals,
    plot_macro_treemap,
    plot_most_common,
    total_logged_days,
    total_macros,
)


def run_analysis():
    """
    main function to scrape mfp diaries and analyse data
    """

    try:
        st.session_state["diary_df"] = load_mfp_data(
            start_date, end_date, mfp_user
        ).copy()
    except ValueError:
        st.error(
            f"No Diary found for {mfp_user} - did you make the diary public?"
        )
        st.stop()
    diary_df = st.session_state["diary_df"]

    st.metric(
        "Total days logged",
        f"{total_logged_days(diary_df)}/{(end_date-start_date).days +1}",
    )

    st.header("Totals")
    show_metrics(total_macros(diary_df))
    st.plotly_chart(plot_most_common(diary_df), use_container_width=True)

    st.plotly_chart(
        plot_macro_treemap(diary_df, st.session_state["selected_macro"]),
        use_container_width=True,
    )
    st.radio(
        "View breakdown for:",
        ["all", "carbs", "fat", "protein"],
        key="selected_macro",
    )
    # css to center input elements
    st.write(
        """<style>
        div.row-widget.stRadio > div,
        div.row-widget.stRadio > label,
        div.row-widget.stCheckbox > label{
            flex-direction:row;justify-content:center;
            }
        .st-dw{padding-right:5%};
        </style><hr>""",
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        plot_intake_goals(
            diary_df,
            calories=st.session_state["show_calories"],
            units=st.session_state["selected_intake_units"],
        ),
        use_container_width=True,
    )
    radio_col_1, radio_col_2 = st.columns(2)
    with radio_col_1:
        st.checkbox(
            "Show total calories",
            key="show_calories",
            disabled=st.session_state["selected_intake_units"] == "grams"
            and not st.session_state["show_calories"],  # NOQA
            value=st.session_state["show_calories"],
        )
    with radio_col_2:
        st.radio(
            "show in units of:",
            ["grams", "calories"],
            key="selected_intake_units",
            disabled=st.session_state["show_calories"],
        )


def intial_page_load():
    """
    run on initial page load
    """
    st.session_state["welcomed"] = True
    # calorie breakdown option
    st.session_state["selected_macro"] = "all"
    # intake vs goals chart option
    st.session_state["show_calories"] = False
    st.session_state["selected_intake_units"] = "calories"

    starter_msg = st.empty()
    starter_img = st.empty()

    starter_msg.markdown(
        """Inspired by Spotify's
         [Wrapped](https://en.wikipedia.org/wiki/Spotify_Wrapped)
         marketing campaign  
        ← Enter your mfp username in the sidebar, make your diary public and
        let's see what you've been eating!"""  # noqa
    )

    with starter_img.expander("Preview"):
        st.image("images/himym.jpg", caption="what you can look forward to")

    if start_btn:
        starter_msg.empty()
        starter_img.empty()
        run_analysis()


st.set_page_config(
    "mfp wrapped",
    page_icon="images/mfp-icon.png",
    layout="wide",
    menu_items={
        "Get Help": "https://www.linkedin.com/in/ismailmo-chem/",
        "Report a bug": "https://github.com/ismailmo1/mfp-wrapped/issues",
        "About": "Developed by [Ismail](https://github.com/ismailmo1)\n"
        "---\n"
        "Send me a [message](mailto:ismailmo4@gmail.com) if you have any ideas"
        "or suggestions!",
    },
)
st.title("myfitnesspal wrapped 🌯")
with st.sidebar:
    with st.form("data_input"):
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

        start_btn = st.form_submit_button("Get Data")

if "welcomed" not in st.session_state:
    intial_page_load()
else:
    # run analysis if welcome page already viewed
    run_analysis()
