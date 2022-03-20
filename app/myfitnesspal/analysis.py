from typing import Dict

import pandas as pd
import plotly.express as px
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


def most_common_macros(diary_df: pd.DataFrame, macro: str) -> Dict[str, str]:
    # return most common food item for each macro type
    pass
