"""
Helper functions to analyse myfitnesspal diary data
"""
from typing import Dict, Tuple

import pandas as pd


def get_most_common(diary_df: pd.DataFrame, top_n=10) -> pd.Series:
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
    return most_common


def get_total_logged_days(diary_df: pd.DataFrame) -> int:
    """return num of days logged"""
    return len(diary_df["date"].unique())


def unpivot_food_macros(diary_df: pd.DataFrame) -> pd.DataFrame:
    """
    unpivot food entries so each row is a single macronutrient, food and date
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

    return melted_df


def get_intake_goals(diary_df: pd.DataFrame):
    """
    Get nutrition intake goals and actuals by units 'kcal' and 'grams'.
    """
    diary_df["date"] = pd.to_datetime(diary_df["date"])
    macro_kcals = {"carbs": 4, "fat": 9, "protein": 4}

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

    return daily_data


def total_macros(diary_df: pd.DataFrame) -> Dict[str, int]:
    """
    Return totals for calories and each macro
    """
    return {
        "Calories (kcal)": int(diary_df["calories_kcal"].sum()),
        "Carbs (g)": int(diary_df["carbs_g"].sum()),
        "Fats (g)": int(diary_df["fat_g"].sum()),
        "Protein (g)": int(diary_df["protein_g"].sum()),
    }


def get_longest_streaks(diary_df: pd.DataFrame) -> Tuple[int, int]:
    """Calculate longest tracking streak and blank

    Args:
        diary_df (pd.DataFrame): scraped diary

    Returns:
        Tuple[int, int]: Longest tracked streak, longest blank
    """
    diary_df = diary_df.drop_duplicates(subset="date")
    diary_df["tracked"] = True
    min_date = diary_df["date"].min()
    max_date = diary_df["date"].max()
    all_dates = pd.Series(pd.date_range(min_date, max_date), name="all_dates")

    streak_df = diary_df.merge(
        all_dates, how="outer", right_on="all_dates", left_on="date"
    ).fillna(False)

    streak_df = (
        streak_df.set_index("all_dates", drop=True)
        .drop("date", axis=1)
        .sort_index()
    )
    streak_df["start_of_streak"] = streak_df["tracked"].ne(
        streak_df["tracked"].shift()
    )
    streak_df["streak_id"] = streak_df["start_of_streak"].cumsum()
    streak_df["streak_counter"] = streak_df.groupby("streak_id").cumcount() + 1

    non_tracked_days = streak_df.loc[streak_df["tracked"] == False, :]  # noqa
    tracked_days = streak_df.loc[streak_df["tracked"] == True, :]  # noqa

    longest_tracked_streak = tracked_days["streak_counter"].max()
    longest_blank_streak = non_tracked_days["streak_counter"].max()

    if pd.isnull(longest_blank_streak):
        longest_blank_streak = 0
    if pd.isnull(longest_tracked_streak):
        longest_tracked_streak = 0

    return (longest_tracked_streak, longest_blank_streak)


def get_adherence_perc(
    intake_goals: pd.DataFrame, perc_tolerance: float = 0.1
) -> float:

    total_days = len(intake_goals)

    kcal_goals = intake_goals.loc[:, ["calories_kcal", "goal_calories_kcal"]]
    kcal_goals["upper_kcal_tol"] = kcal_goals["goal_calories_kcal"] * (
        1 + perc_tolerance
    )
    kcal_goals["lower_kcal_tol"] = kcal_goals["goal_calories_kcal"] * (
        1 - perc_tolerance
    )

    kcal_goals["within_tolerance"] = (
        kcal_goals["calories_kcal"] < kcal_goals["upper_kcal_tol"]
    ) & (kcal_goals["calories_kcal"] > kcal_goals["lower_kcal_tol"])

    adhered_days = kcal_goals["within_tolerance"].sum()

    return adhered_days / total_days
