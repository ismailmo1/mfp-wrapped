import time
from datetime import date

import pandas as pd
import streamlit as st

st.title("Seven years of Ismail trying not be fat")

prog_bar = st.progress(0)


@st.cache
def load_mfp_data(start_date: date, end_date: date):
    # code taken from food eda notebook
    food_df = pd.read_csv("myfitnesspal/mfp-extract-2021.csv", index_col=0)
    # reset index so each line has unique index (i.e. indices not
    # restarted from 0 for each new day)
    food_df.reset_index(drop=True, inplace=True)
    # drop all rows containing column headers are repeated
    # (i.e. where dataframe is appended)
    food_df.drop(food_df[food_df["food"] == "food"].index, inplace=True)
    macro_cols = [
        "carbs_g",
        "fat_g",
        "protein_g",
        "goal_carbs_g",
        "goal_fat_g",
        "goal_protein_g",
    ]
    food_df[macro_cols] = food_df[macro_cols].applymap(
        lambda x: x.split("  ")[0]
    )

    # convert datatypes
    numeric_cols = [
        col for col in food_df.columns if "_g" in col or "calories" in col
    ]
    food_df[numeric_cols] = food_df[numeric_cols].apply(pd.to_numeric)
    food_df["date"] = pd.to_datetime(food_df["date"])

    return food_df


for i in range(0, 101):
    prog_bar.progress(i)
    time.sleep(0.01)

df_21 = load_mfp_data(date(2021, 1, 1), date(2021, 12, 31))

st.write(df_21)

col_1, col_2, col_3, col_4 = st.columns(4)

col_1.metric("Calories", df_21["calories_kcal"].sum(), delta="100%")
col_2.metric("Carbs", df_21["carbs_g"].sum(), delta="100%")
col_3.metric("Fats", df_21["fat_g"].sum(), delta="100%")
col_4.metric("Protein", df_21["protein_g"].sum(), delta="100%")

st.header("most common food entries")

st.bar_chart(
    df_21.groupby("food").count()["date"].sort_values(ascending=False)[0:10]
)
