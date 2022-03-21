from typing import Dict, Tuple

import pandas as pd
import plotly.express as px
from numerize import numerize as nz
from plotly.graph_objects import Figure


def plot_most_common(diary_df: pd.DataFrame, top_n=10) -> Figure:
    """group diary by food and return bar chart of top n most freq logged foods

    Args:
        diary_df (pd.DataFrame): diary dataframe with atleast food and date
        columns

    Returns:
        Figure: px.bar figure
    """
    most_common = (
        diary_df.groupby("food")
        .count()["date"]
        .sort_values(ascending=False)[0:top_n]
    )

    fig = px.bar(
        most_common,
        orientation="h",
        title="Most common diary entries",
        labels={"food": "diary entry", "value": "frequency"},
    )
    fig.update_layout(showlegend=False)

    return fig


def total_logged_days(diary_df: pd.DataFrame) -> pd.DataFrame:
    # return num of days logged
    return len(diary_df["date"].unique())


def plot_macro_trends(diary_df: pd.DataFrame):
    # plot macro intake over time
    pass


def plot_kcal_trends(diary_df: pd.DataFrame):
    # plot kcal intake over time
    pass


def most_common_macros(diary_df: pd.DataFrame) -> Dict[str, Tuple]:
    # return most common food item for each macro type
    food_totals_df = diary_df.groupby("food").sum()[
        [
            "calories_kcal",
            "carbs_g",
            "fat_g",
            "protein_g",
            "sugar_g",
            "fiber_g",
        ]
    ]

    top_cal_source = food_totals_df.sort_values(
        "calories_kcal", ascending=False
    ).iloc[0]
    top_carb_source = food_totals_df.sort_values(
        "carbs_g", ascending=False
    ).iloc[0]
    top_fat_source = food_totals_df.sort_values("fat_g", ascending=False).iloc[
        0
    ]
    top_protein_source = food_totals_df.sort_values(
        "protein_g", ascending=False
    ).iloc[0]

    return {
        "calories": (
            top_cal_source.name,
            int(top_cal_source["calories_kcal"]),
        ),
        "carbs": (top_carb_source.name, int(top_carb_source["carbs_g"])),
        "fats": (top_fat_source.name, int(top_fat_source["fat_g"])),
        "proteins": (
            top_protein_source.name,
            int(top_protein_source["protein_g"]),
        ),
    }


def total_macros(diary_df: pd.DataFrame):
    return {
        "Calories (kcal)": nz.numerize(int(diary_df["calories_kcal"].sum())),
        "Carbs (g)": nz.numerize(int(diary_df["carbs_g"].sum())),
        "Fats (g)": nz.numerize(int(diary_df["fat_g"].sum())),
        "Protein (g)": nz.numerize(int(diary_df["protein_g"].sum())),
    }
