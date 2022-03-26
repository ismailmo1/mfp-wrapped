"""
Helper functions to plot and analyse myfitnesspal diary data
"""
from typing import Dict, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    """return num of days logged"""
    return len(diary_df["date"].unique())


def plot_macro_treemap(diary_df: pd.DataFrame, macro: str = "all") -> Figure:
    """
    plotly treemap of diary for macronutrient with hierarchy of food and date
    """
    macro_kcals = {"carbs_g": 4, "fat_g": 9, "protein_g": 4}

    # add kcal column for macros
    for key, val in macro_kcals.items():
        diary_df[key.split("_", maxsplit=1)[0] + "_kcal"] = diary_df[key] * val

    diary_df_kcals = diary_df[
        [
            "food",
            "calories_kcal",
            "carbs_kcal",
            "fat_kcal",
            "protein_kcal",
            "date",
        ]
    ]
    melted_df = diary_df_kcals.drop("calories_kcal", axis=1).melt(
        ["food", "date"]
    )
    melted_df = melted_df.rename({"value": "kcal"}, axis=1)
    melted_df["kcal"] = pd.to_numeric(melted_df["kcal"])
    # add meal counter - i.e. how many meals it was eaten for
    melted_df["meals"] = 1

    melted_df = melted_df.groupby(["food", "date", "variable"]).sum()
    melted_df = melted_df.reset_index()

    if macro == "all":
        path = [px.Constant("all"), "variable", "food", "date"]
    else:
        path = [px.Constant("all"), "food", "date"]
        melted_df = melted_df[melted_df["variable"] == f"{macro}_kcal"]

    return px.treemap(
        melted_df,
        path=path,
        values="kcal",
        hover_data=["meals"],
        title="Calorie Intake Breakdown",
    )


def plot_intake_goals(
    diary_df: pd.DataFrame, units: str = "calories", calories: bool = False
):
    """
    Plot bar chart of intake with line graph of goals by units 'kcal' or
    'grams'.
    To plot calories instead of macros pass 'calories = True'
    """
    diary_df["date"] = pd.to_datetime(diary_df["date"])
    macro_kcals = {"carbs": 4, "fat": 9, "protein": 4}
    macro_colours = {
        "carbs": "darkturquoise",
        "fat": "tomato",
        "protein": "mediumorchid",
        "calories": "darkorange",
    }
    # add kcal column for macros
    for key, val in macro_kcals.items():
        diary_df[key + "_kcal"] = diary_df[key + "_g"] * val
        diary_df["goal_" + key + "_kcal"] = (
            diary_df["goal_" + key + "_g"] * val
        )
    sum_cols = {
        col: "sum"
        for col in [
            "calories_kcal",
            "carbs_g",
            "fat_g",
            "protein_g",
            "carbs_kcal",
            "fat_kcal",
            "protein_kcal",
        ]
    }

    mean_cols = {
        col: "mean"
        for col in [
            "goal_calories_kcal",
            "goal_carbs_g",
            "goal_fat_g",
            "goal_protein_g",
            "goal_carbs_kcal",
            "goal_fat_kcal",
            "goal_protein_kcal",
        ]
    }
    agg_dict = {**sum_cols, **mean_cols}
    daily_data = diary_df.groupby("date").agg(agg_dict)
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
        if calories:
            customdata = None
            hovertemplate = None
        elif units == "grams":
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


def total_macros(diary_df: pd.DataFrame) -> Dict[str, int]:
    """
    Return totals for calories and each macro
    """
    return {
        "Calories (kcal)": nz.numerize(int(diary_df["calories_kcal"].sum())),
        "Carbs (g)": nz.numerize(int(diary_df["carbs_g"].sum())),
        "Fats (g)": nz.numerize(int(diary_df["fat_g"].sum())),
        "Protein (g)": nz.numerize(int(diary_df["protein_g"].sum())),
    }
