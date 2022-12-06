"""
Entry point for streamlit app
"""
import time
from datetime import datetime, timedelta

import streamlit as st
from app_utils import grab_mfp_data, show_metrics
from app_utils.cards import (
    generate_adherence_card,
    generate_days_tracked_card,
    generate_top_foods_card,
    generate_total_kcal_card,
)
from app_utils.plots import (
    plot_intake_goals,
    plot_macro_treemap,
    plot_most_common,
)
from myfitnesspal.analysis import (
    get_adherence_perc,
    get_intake_goals,
    get_longest_streaks,
    get_most_common,
    get_total_logged_days,
    total_macros,
    unpivot_food_macros,
)


def run_analysis():
    """
    main function to scrape mfp diaries and analyse data
    """

    try:
        start_time = time.perf_counter()

        diary_df = grab_mfp_data(start_date, end_date, mfp_user).copy()

        elapsed = time.perf_counter() - start_time
        st.text(
            f"grabbed data from {start_date} to {end_date} in {elapsed:.2f} "
            "seconds"
        )
    except ValueError:
        st.error(
            f"No Diary found for {mfp_user} - did you make the diary public?"
        )
        st.stop()

    num_days_tracked = get_total_logged_days(diary_df)
    total_num_days = (end_date - start_date).days + 1

    most_common_foods = get_most_common(diary_df)
    melted_food_df = unpivot_food_macros(
        diary_df,
    )
    intake_goals = get_intake_goals(diary_df)
    adherence_perc = get_adherence_perc(intake_goals)
    total_macro_metrics = total_macros(diary_df)
    longest_streak, longest_blank = get_longest_streaks(diary_df)
    kcal_card = generate_total_kcal_card(
        total_macro_metrics["Calories (kcal)"]
    )
    top5_card = generate_top_foods_card(
        most_common_foods[:5].to_dict()  # type:ignore
    )
    days_tracked_card = generate_days_tracked_card(
        num_days_tracked, total_num_days, longest_streak, longest_blank
    )
    adherence_card = generate_adherence_card(adherence_perc)
    col1, col2, col3, col4 = st.columns(4)

    col1.image(kcal_card)
    col2.image(top5_card)
    col3.image(days_tracked_card)
    col4.image(adherence_card)
    st.metric(
        "Total days logged",
        f"{num_days_tracked}/{total_num_days}",
    )

    st.header("Totals")
    show_metrics(total_macro_metrics)
    st.plotly_chart(
        plot_most_common(most_common_foods), use_container_width=True
    )

    st.plotly_chart(
        plot_macro_treemap(melted_food_df, st.session_state["selected_macro"]),
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
            intake_goals,
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
        ← Enter your mfp username in the sidebar (or use mine), make your diary public and
        let's see what you've been eating!"""  # noqa
    )

    with starter_img.expander("Preview"):
        st.image("images/himym.jpg", caption="what you can look forward to")

    if start_btn:
        starter_msg.empty()
        starter_img.empty()
        run_analysis()


st.set_page_config(  # type:ignore
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
            )  # type:ignore
        except ValueError:
            st.warning("you must pick a date range (start date - end date)!")

        start_btn = st.form_submit_button("Get Data")

if "welcomed" not in st.session_state:
    intial_page_load()
else:
    # run analysis if welcome page already viewed
    run_analysis()
