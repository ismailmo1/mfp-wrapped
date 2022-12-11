"""
Plot data from analysed myfitnesspal diary data
"""
from typing import Dict, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_most_common(most_common: pd.Series):
    """Return bar chart of top n most freq logged foods

    Args:
        most_common (pd.Series): Series of most common foods

    Returns:
        Figure: px.bar figure
    """

    fig = px.bar(
        most_common,
        orientation="h",
        title="Most common diary entries",
        labels={"food": "food name", "value": "number of entries"},
    )
    fig.update_layout(showlegend=False)

    return fig


def plot_macro_treemap(
    melted_df: pd.DataFrame, macro: str = "all", num_unique_foods=10
):
    """
    plotly treemap of diary for macronutrient with hierarchy of food and date
    """

    if macro == "all":
        path = [px.Constant("all"), "variable", "food", "date"]
    else:
        path = [px.Constant("all"), "food", "date"]
        melted_df = melted_df[melted_df["variable"] == f"{macro}_kcal"]
    # bin all non top num_unique_foods into 'other' category to reduce boxes
    # in treemap
    other_foods = list(
        melted_df["food"].value_counts()[num_unique_foods:].index
    )
    melted_df["food"] = melted_df["food"].replace(other_foods, "other")

    return px.treemap(
        melted_df,
        path=path,
        values="kcal",
        hover_data=["meals"],
        title="Calorie Intake Breakdown",
        color="variable",
        color_discrete_map={
            "(?)": "darkgrey",
            "carbs_kcal": "darkturquoise",
            "protein_kcal": "mediumorchid",
            "fat_kcal": "tomato",
        },
    )


def plot_intake_goals(
    daily_data: pd.DataFrame, units: str = "calories", calories: bool = False
):
    """
    Plot bar chart of intake with line graph of goals by units 'kcal' or
    'grams'.
    To plot calories instead of macros pass 'calories = True'
    """
    macro_colours = {
        "carbs": "darkturquoise",
        "fat": "tomato",
        "protein": "mediumorchid",
        "calories": "darkorange",
    }
    kcal_macro_cols = [
        col
        for col in daily_data.columns
        if "kcal" in col and "calories" not in col
    ]
    gram_macro_cols = [
        col
        for col in daily_data.columns
        if "_g" in col and "calories" not in col
    ]
    calorie_cols = [col for col in daily_data.columns if "calories" in col]
    fig = go.Figure()

    col = None

    if calories:
        cols = calorie_cols
        customdata = None
        hovertemplate = None
    elif units == "grams":
        cols = gram_macro_cols
    elif units == "calories":
        cols = kcal_macro_cols
    else:
        raise Exception(
            f"units must be either 'grams' or 'calories'!"
            f"('{units}' was passed)"
        )

    for col in cols:
        macro = col.split("_")[-2]
        color = macro_colours[macro]
        customdata = None
        hovertemplate = None
        if units == "grams":
            customdata = daily_data[macro + "_kcal"]
            hovertemplate = "%{customdata} kcal"
        elif units == "calories":
            customdata = daily_data[macro + "_g"]
            hovertemplate = "%{customdata}g"

        if "goal" in col:
            line = {"dash": "dash", "color": color}
            fig.add_trace(
                go.Scatter(
                    x=daily_data.index,
                    y=daily_data[col],
                    mode="lines",
                    name="goal",
                    line=line,
                    legendgroup=macro,
                )
            )
        else:
            fig.add_trace(
                go.Bar(
                    x=daily_data.index,
                    y=daily_data[col],
                    name=macro,
                    marker_color=color,
                    legendgroup=macro,
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                )
            )

    fig.update_layout(
        title="Actual Intake vs Goals",
        xaxis_title="Date",
        yaxis_title=units,
    )
    return fig


def most_common_macros(diary_df: pd.DataFrame) -> Dict[str, Tuple]:
    """
    return most common source for each macro type
    """
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
