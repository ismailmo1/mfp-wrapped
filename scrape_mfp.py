import json
import os
from datetime import date

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


def extract_diary(logged_in_mfp_session: Session, date: date) -> pd.DataFrame:
    """extract dataframe of food diary from date

    Args:
        logged_in_mfp_session (Session): authenticated session on myfitnesspal
        (use login_mfp)
        date (date): date to extract food diary from

    Raises:
    Exception: if no tables found in diary html

    Returns:
        pd.DataFrame: food diary table extracted from html page into dataframe
        without cleansing
    """
    date_param = f"date={date.isoformat()}"
    res = logged_in_mfp_session.get(
        f"https://www.myfitnesspal.com/food/diary?{date_param}"
    )
    try:
        return pd.read_html(res.text, flavor="lxml")
    except ValueError:
        raise Exception(ValueError)


# load secrets from .env
load_dotenv()
username = os.getenv("MFP_USER")
password = os.getenv("MFP_PASS")

# create session
mfp_session = login_mfp(username, password)

# example usage
date_eg = date(2018, 2, 10)
print(extract_diary(mfp_session, date_eg))
