import os
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from myfitnesspal import diary_scraping

load_dotenv()

st.title("Seven years of Ismail trying not be fat")

prog_bar = st.progress(0)


def load_mfp_data(start_date: date, end_date: date):
    diary_df = pd.DataFrame()
    progress = 0
    for df in diary_scraping.get_diary_data(
        start_date,
        end_date,
        public=False,
        user=os.environ["MFP_USER"],
        pwd=os.environ["MFP_PASS"],
    ):
        progress += 1
        prog_bar.progress(progress)
        diary_df = pd.concat([diary_df, df], axis=0, join="outer")

    return diary_df


diary_df = load_mfp_data(date(2021, 1, 1), date(2021, 1, 10))
st.write(diary_df)


# st.write(df_21)
# col_1, col_2, col_3, col_4 = st.columns(4)

# col_1.metric("Calories", df_21["calories_kcal"].sum(), delta="100%")
# col_2.metric("Carbs", df_21["carbs_g"].sum(), delta="100%")
# col_3.metric("Fats", df_21["fat_g"].sum(), delta="100%")
# col_4.metric("Protein", df_21["protein_g"].sum(), delta="100%")

# st.header("most common food entries")

# st.bar_chart(
#     df_21.groupby("food").count()["date"].sort_values(ascending=False)[0:10]
# )
