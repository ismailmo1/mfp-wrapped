import json
from datetime import date, timedelta

import pandas as pd
import requests
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
        df["food"].apply(lambda x: "quick tools" in str(x).lower())
    ].index
    meal_title_row_idx = df[df["food"].apply(lambda x: len(str(x)) == 1)].index
    non_food_row_idx = non_food_row_idx.append(meal_title_row_idx)
    df.drop(non_food_row_idx, inplace=True)
    df.dropna(axis=(0), how="all", inplace=True)
    df.dropna(axis=(1), how="all", inplace=True)

    # add daily goal columns
    daily_goals_df = df[
        df["food"].apply(lambda x: "daily goal" in str(x).lower())
    ]
    new_cols = ["food"]

    # name goals with prefix "goal_"
    for col in daily_goals_df.columns[1:]:
        new_cols.append("goal_" + str(col).split(" ")[0].lower())

    daily_goals_df.columns = new_cols

    # add daily goals columsn to df
    new_df = pd.concat([df, daily_goals_df])
    new_df.fillna(method="bfill", inplace=True)

    # drop last 5 rows - non food items
    cleaned_df = new_df.drop(new_df.index[-5:]).reset_index(drop=True)
    macro_cols = [
        "carbs_g",
        "fat_g",
        "protein_g",
        "goal_carbs_g",
        "goal_fat_g",
        "goal_protein_g",
    ]
    cleaned_df[macro_cols] = cleaned_df[macro_cols].applymap(
        lambda x: x.split("  ")[0]
    )

    # convert datatypes
    numeric_cols = [
        col for col in cleaned_df.columns if "_g" in col or "calories" in col
    ]
    cleaned_df[numeric_cols] = cleaned_df[numeric_cols].apply(pd.to_numeric)

    cleaned_df["food"] = cleaned_df["food"].apply(
        lambda x: "".join(str(x).split(",")[:-1])
    )
    cleaned_df["qty"] = cleaned_df["food"].apply(
        lambda x: "".join(str(x).split(",")[-1])
    )

    return cleaned_df


def extract_diary(
    logged_in_mfp_session: Session, diary_date: date, user: str = None
) -> pd.DataFrame:
    """extract dataframe of food diary from date.

    Args:
        logged_in_mfp_session (Session): authenticated session on myfitnesspal
        (use login_mfp if diary not public)
        date (date): date to extract food diary from

    Raises:
    Exception: if no tables found in diary html

    Returns:
        pd.DataFrame: food diary table extracted from html page into dataframe
        dataframe is cleaned so each row is 1 food entry
        date is added as an extra column to the dataframe
        all other data (macro targets, totals etc) is added as a column.
    """
    date_param = f"date={diary_date.isoformat()}"

    if user:
        url = f"https://www.myfitnesspal.com/food/diary/{user}?{date_param}"
    else:
        url = f"https://www.myfitnesspal.com/food/diary?{date_param}"

    res = logged_in_mfp_session.get(url)
    try:
        html_df = pd.read_html(res.text, flavor="lxml")[0]
        clean_df = clean_mfp_extract(html_df)
        clean_df["date"] = diary_date
        return clean_df
    except ValueError as error:
        raise ValueError("No diary table found for {diary_date}!") from error


def get_diary_data(
    start_date: date,
    end_date: date,
    public: bool = True,
    user: str = None,
    pwd: str = None,
) -> pd.DataFrame:

    if public:
        mfp_session = Session()
    else:
        if user and pwd:
            # create session
            mfp_session = login_mfp(user, pwd)
        else:
            raise Exception(
                "You must provide a username and password for private diaries"
            )

    while start_date <= end_date:
        diary_df = extract_diary(mfp_session, start_date, user)
        start_date += timedelta(days=1)
        yield diary_df
