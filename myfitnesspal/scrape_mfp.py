import json
import os
from datetime import date, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv
from requests import Session


def login_mfp(username: str, password: str) -> Session:
    """login user to myfitnesspal

    Args:
        username (str): username to login
        password (str): password for login

    Raises:
        Exception: if "account/logout" isn't found in response text which
        would've indicated a successful login

    Returns:
        Session: logged in user session
    """
    # login to myfitness pal
    session = requests.session()

    # grab csrf token
    csrf_res = session.get("https://www.myfitnesspal.com/api/auth/csrf")
    csrf_token = json.loads(csrf_res.text)["csrfToken"]

    # send credentials
    session.post(
        "https://www.myfitnesspal.com/api/auth/callback/credentials?",
        data={
            "username": username,
            "password": password,
            "csrfToken": csrf_token,
            "callbackUrl": "https://www.myfitnesspal.com/account/login",
            "redirect": "false",
            "json": "true",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    # get session
    session.get("https://www.myfitnesspal.com/api/auth/session")

    # check if login successful
    res = session.get("https://www.myfitnesspal.com/")

    if res.text.find("/account/logout") > 0:
        print("logged in successfully!")
        return session
    else:
        raise Exception("login failed!")


def clean_mfp_extract(df: pd.DataFrame) -> pd.DataFrame:
    # cleanup column names
    df.columns = [
        "food",
        *[str(col).lower().replace("  ", "_") for col in df.iloc[0][1:]],
    ]
    df.drop(0, inplace=True)

    # remove junk rows with no food data
    non_food_row_idx = df[
        df["food"].apply(
            lambda x: "Add Food  Quick Tools  Quick add calories" in str(x)
        )
    ].index
    meal_title_row_idx = df[df["food"].apply(lambda x: len(str(x)) == 1)].index
    non_food_row_idx = non_food_row_idx.append(meal_title_row_idx)
    df.drop(non_food_row_idx, inplace=True)
    df.dropna(axis=(0), how="all", inplace=True)
    df.dropna(axis=(1), how="all", inplace=True)

    # add daily goal columns
    daily_goals_df = df[df["food"] == "Your Daily Goal"]
    new_cols = []

    # name goals with prefix "goal_"
    for col in daily_goals_df.columns[1:]:
        new_cols.append("goal_" + str(col).split(" ")[0].lower())
    daily_goals_df.columns = new_cols

    # add daily goals columsn to df
    new_df = pd.concat([df, daily_goals_df])
    new_df.fillna(method="bfill", inplace=True)

    # drop last 5 rows - non food items
    cleaned_df = new_df.drop(new_df.index[-5:]).reset_index(drop=True)
    return cleaned_df


def extract_diary(logged_in_mfp_session: Session, date: date) -> pd.DataFrame:
    """extract dataframe of food diary from date.

    Args:
        logged_in_mfp_session (Session): authenticated session on myfitnesspal
        (use login_mfp)
        date (date): date to extract food diary from

    Raises:
    Exception: if no tables found in diary html

    Returns:
        pd.DataFrame: food diary table extracted from html page into dataframe
        dataframe is cleaned so each row is 1 food entry
        date is added as an extra column to the dataframe
        all other data (macro targets, totals etc) is added as a column.
    """
    date_param = f"date={date.isoformat()}"
    res = logged_in_mfp_session.get(
        f"https://www.myfitnesspal.com/food/diary?{date_param}"
    )
    try:
        df = pd.read_html(res.text, flavor="lxml")[0]
        clean_df = clean_mfp_extract(df)
        clean_df["date"] = date
        return clean_df
    except ValueError:
        raise Exception(ValueError)


def get_year_diary(year):
    # load secrets from .env
    load_dotenv()
    username = os.getenv("MFP_USER")
    password = os.getenv("MFP_PASS")

    # create session
    mfp_session = login_mfp(username, password)

    # example usage
    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)
    while start_date < end_date:
        print(f"extracting diary for {start_date}")
        diary_df = extract_diary(mfp_session, start_date)
        with open(f"mfp-extract-{year}.csv", "a") as f:
            diary_df.to_csv(f)
        start_date += timedelta(days=1)


if __name__ == "__main__":
    get_year_diary(2021)
